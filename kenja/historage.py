from git import Repo
import os
import re
from collections import defaultdict

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
                b_blob_index += 1
            elif line[0] == '-':
                deleted_lines.append((a_blob_index, line[1:]))
                a_blob_index += 1
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

def get_method(path):
    splited_path = path.split('/')
    mt_index = splited_path.index('[MT]')
    assert mt_index +1 <= len(splited_path)
    return splited_path[mt_index + 1]

if __name__ == '__main__':
    historage = Repo('~/kenja_test/columba_distilled/1302090100/base_repo')
    num_extract_method_candidates = 0
    num_extract_method_candidates2 = 0
    num_extracted_method_candidates = 0
    num_extract_method_candidate_revsions = 0

    parser = GitDiffParser()

    for commit in historage.iter_commits(historage.head):
        #print commit.hexsha
        for p in commit.parents:
            method_added = False

            added_method = []
            changed_method = []
            method_changed_class = set()
            method_added_class = set()
            extract_method_target_candidates = []
            extracted_method_candidates = defaultdict(list)
            extracted_method_candidates2 = set()
            extract_method_pair_candidates = []

            diff_index = p.diff(commit, create_patch=True)

            for diff in diff_index.iter_change_type('A'):
                if is_method_body(diff.b_blob.path):
                    added_method.append(diff.b_blob)
                    method = get_method(diff.b_blob.path)
                    method_name = method[:method.index(r'(')]
                    #extracted_method_candidates.append(method_name)
                    c = get_class(diff.b_blob.path)
                    extracted_method_candidates[c].append(method_name)
                    method_added_class.add(c)

            for diff in diff_index.iter_change_type('M'):
                if is_method_body(diff.b_blob.path):
                    changed_method.append(diff.b_blob)
                    c = get_class(diff.b_blob.path)
                    if c not in method_added_class:
                        continue
                    (deleted_lines, added_lines) = parser.parse(diff.diff)
                    if deleted_lines and added_lines:
                        #method_changed_class.add(c)
                        m = get_method(diff.b_blob.path)
                        extract_method_target_candidates.append(m)
                        for lineno, line in added_lines:
                            for method in extracted_method_candidates[c]:
                                if method in line:
                                    method_changed_class.add(c)
                                    extract_method_pair_candidates.append((c, m, method, line))
                                    extracted_method_candidates2.add(method)
                                    break

            if added_method and changed_method:
                num_extract_method_candidates += len(method_changed_class)
                num_extract_method_candidates2 += len(extract_method_pair_candidates)
                num_extracted_method_candidates += len(extracted_method_candidates2)
                if extract_method_pair_candidates:
                    print commit.hexsha
                    print 'extracted candidates2:'
                    for candidate in extract_method_pair_candidates:
                        print candidate
                    num_extract_method_candidate_revsions += 1

    print 'candidate classes:', num_extract_method_candidates
    print 'candidate pairs:', num_extract_method_candidates2
    print 'extracted candidate method:', num_extracted_method_candidates
    print 'candidate revisions:', num_extract_method_candidate_revsions
