from git import Repo
import os
import re

class GitDiffParser:

    #header_regex = re.compile(r'^diff --git (a/)+(.*) (b/)+(.*)$')

    header_a_blob_regex = re.compile(r'^--- (a/)?(.*)$')
    header_b_blob_regex = re.compile(r'^\+\+\+ (b/)?(.*)$')

    head_lineno_regex = re.compile(r'^@@ \-(\d+),?\d* \+(\d+),?\d* @@')

    def parse(self, diff_str):
        lines = diff_str.splitlines()

        a_blob_index = 0
        b_blob_index = 0
        deleted_lines = []
        added_lines = []
        while(lines):
            line = lines.pop(0)
            #if line[0] == 'd' and line[1] == 'i':
            #    print line
            if line[0] == '-':
                match = self.header_a_blob_regex.match(line)
            elif line[0] == '+':
                match = self.header_b_blob_regex.match(line)
            if line[0] == '@':
                match = self.head_lineno_regex.match(line)

                a_blob_index = int(match.group(1))
                b_blob_index = int(match.group(2))

                break

        while(lines):
            line = lines.pop(0)
            if line[0] == '+':
                added_lines.append((b_blob_index, line[1:]))
                a_blob_index += 1
            elif line[0] == '-':
                deleted_lines.append((a_blob_index, line[1:]))
                b_blob_index += 1
            elif line[0] == '@':
                match = self.head_lineno_regex.match(line)
                a_blob_index = int(match.group(1))
                b_blob_index = int(match.group(2))

        return (deleted_lines, added_lines)


def is_method_body(path):
    if os.path.basename(path) != 'body':
        return False
    dirname = os.path.basename(os.path.dirname(os.path.dirname(path)))
    return dirname == '[MT]'

def is_method_parameters(path):
    if os.path.basename(path) != 'parameters':
        return False
    dirname = os.path.basename(os.path.dirname(os.path.dirname(path)))
    return dirname == '[MT]'

def get_class(path):
    splited_path = path.split('/')
    cn_index = splited_path.index('[CN]')
    assert cn_index +1 <= len(splited_path)
    return splited_path[cn_index + 1]

if __name__ == '__main__':
    historage = Repo('~/kenja_test/columba_distilled/1302090100/base_repo')
    num_extract_method_candidates = 0
    num_extract_method_candidate_revsions = 0

    parser = GitDiffParser()

    for commit in historage.iter_commits(historage.head):
        print commit.hexsha
        for p in commit.parents:
            method_added = False

            added_method = []
            changed_method = []
            method_changed_class = set()
            method_added_class = set()

            diff_index = p.diff(commit, create_patch=True)

            for diff in diff_index.iter_change_type('A'):
                if is_method_body(diff.b_blob.path):
                    added_method.append(diff.b_blob)
                    method_added_class.add(get_class(diff.b_blob.path))

            for diff in diff_index.iter_change_type('M'):
                if is_method_body(diff.b_blob.path):
                    changed_method.append(diff.b_blob)
                    #print '%s %s' %(diff.a_blob.hexsha, diff.b_blob.hexsha)
                    #method_changed_class.append(get_class(diff.b_blob.path))
                    (deleted_lines, added_lines) = parser.parse(diff.diff)
                    if deleted_lines:
                        method_changed_class.add(get_class(diff.b_blob.path))
                    #print type(diff.diff)

            if len(added_method) > 0 and len(changed_method) > 0:
                print commit.hexsha
                s = method_added_class.intersection(method_added_class)
                num_extract_method_candidates += len(s)
                num_extract_method_candidate_revsions += 1
                #print method_changed_class
                #print method_added_class
                #print s

            #if len(added_method) > 0:
            #    print 'added to:', method_added_class
                #print 'Commit added one more method: %s' % (commit.hexsha)
            #if len(changed_method) > 0:
            #    print 'changed to:', method_changed_class
                #print 'Commit changed one more method: %s ' % (commit.hexsha)

    print 'candidates:', num_extract_method_candidates
    print 'candidate revisions:', num_extract_method_candidate_revsions
