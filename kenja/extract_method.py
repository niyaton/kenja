from git import Repo
import singles
from historage import *
from gitdiff import GitDiffParser
from collections import defaultdict

def detect_extract_method(historage):
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
                            extracted_method_name = line[line.rindex(method):]
                            num_args = len(extracted_method_name[extracted_method_name.index(r'('):extracted_method_name.index(r')')].split(r','))

                            #print c, method, num_args
                            if (c, method, num_args) not in added_lines_dict.keys():
                                # TODO support method overloads completely
                                #print "can't calculate similarity"
                                extract_method_information.append((commit.hexsha, commit.message, c, m, method, line, -1))
                            else:
                                script = '\n'.join([l[1] for l in deleted_lines])

                                extracted_lines = added_lines_dict[(c, method, num_args)]
                                script2 = '\n'.join([l[1] for l in extracted_lines])

                                #print script, script2
                                sim = singles.calculate_similarity(script, script2)
                                extract_method_information.append((commit.hexsha, commit.message, c, m, method, line, sim))
                                #print deleted_lines, added_lines_dict[(c, method, num_args)]
                            break # One method call is enough to judge as a candidate

    return extract_method_information

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Extract Method Detector')
    parser.add_argument('historage_dir',
            help='path of historage repository dir')
    args = parser.parse_args()

    historage = Repo(args.historage_dir)
    extract_method_information = detect_extract_method(historage)

    candidate_revisions = set()
    for info in extract_method_information:
        candidate_revisions.add(info[0])
        print '"%s","%s","%s","%s","%s","%s","%s"' % info

    print 'candidates:', len(extract_method_information)
    print 'candidate revisions:', len(candidate_revisions)
