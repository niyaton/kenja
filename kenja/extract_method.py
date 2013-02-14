from git import Repo
import singles
from historage import *
from gitdiff import GitDiffParser
from collections import defaultdict

if __name__ == '__main__':
    historage = Repo('~/kenja_test/columba_distilled/1302122318/base_repo')
    #historage = Repo('~/jEdit/base_repo')

    extract_method_information = []
    extract_method_revisions = set()

    parser = GitDiffParser()
    for commit in historage.iter_commits(historage.head):
        for p in commit.parents:
            extracted_method_candidates = defaultdict(list)

            diff_index = p.diff(commit, create_patch=True)

            added_lines_dict = {}

            for diff in diff_index.iter_change_type('A'):
                if is_method_body(diff.b_blob.path):
                    method = get_method(diff.b_blob.path)
                    method_name = method[:method.index(r'(')]
                    num_args = len(method[method.index(r'('):].split(r','))
                    c = get_class(diff.b_blob.path)
                    extracted_method_candidates[c].append(method_name)
                    (deleted_lines, added_lines) = parser.parse(diff.diff)
                    if (c, method_name, num_args) in added_lines_dict.keys():
                        # TODO support method overloads completely
                        #print "Oops!"
                        continue
                    added_lines_dict[(c, method_name, num_args)] = added_lines

            for diff in diff_index.iter_change_type('M'):
                if not is_method_body(diff.b_blob.path):
                    continue
                c = get_class(diff.b_blob.path)
                if c not in extracted_method_candidates.keys():
                    continue
                (deleted_lines, added_lines) = parser.parse(diff.diff)
                if not(deleted_lines and added_lines):
                    continue
                m = get_method(diff.b_blob.path)
                method_name = m[:m.index(r'(')]
                for method in extracted_method_candidates[c]:
                    for lineno, line in added_lines:
                        if method in line:
                            #extract_method_information.append((commit.hexsha, commit.message, c, m, method, line))
                            extract_method_revisions.add(commit.hexsha)
                            tmp = line[line.rindex(method):]
                            num_args = len(tmp[tmp.index(r'('):tmp.index(r')')].split(r','))

                            #print c, method, num_args
                            if (c, method, num_args) not in added_lines_dict.keys():
                                # TODO support method overloads completely
                                #print "can't calculate similarity"
                                extract_method_information.append((commit.hexsha, commit.message, c, m, method, line, -1))
                            else:
                                script = ""
                                for l in deleted_lines:
                                    script = '\n'.join([script, l[1]])
                                #script += "\n"
                                script2 = ""
                                for l in added_lines_dict[(c, method, num_args)]:
                                    script2 = '\n'.join([script2, l[1]])
                                #script2 += "\n"
                                #print script, script2
                                sim = singles.calculate_similarity(script, script2)
                                extract_method_information.append((commit.hexsha, commit.message, c, m, method, line, sim))
                                #print deleted_lines, added_lines_dict[(c, method, num_args)]
                            break # One method call is enough to judge as a candidate

    for info in extract_method_information:
        print '"%s","%s","%s","%s","%s","%s","%s"' % info

    print 'candidates:', len(extract_method_information)
    print 'candidate revisions:', len(extract_method_revisions)
