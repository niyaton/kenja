from __future__ import absolute_import
import re
from itertools import ifilter
from git import Repo


class GitDiffParser:
    # header_regex = re.compile(r'^diff --git (a/)+(.*) (b/)+(.*)$')

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
            # if line[0] == 'd' and line[1] == 'i':
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


def check_same_repository(a_repo_path, b_repo_path):
    a_repo = Repo(a_repo_path)
    b_repo = Repo(b_repo_path)
    if check_branches(a_repo, b_repo) and check_tags(a_repo, b_repo) and check_commits(a_repo, b_repo):
        return False
    else:
        return True


def check_branches(a_repo, b_repo):
    a_branches = set([branch.name for branch in a_repo.branches])
    b_branches = set([branch.name for branch in b_repo.branches])
    a_branch_hexshas = set([branch.commit.hexsha for branch in a_repo.branches])
    b_branch_hexshas = set([branch.commit.hexsha for branch in b_repo.branches])
    same_branches = a_branches == b_branches and a_branch_hexshas == b_branch_hexshas
    print 'check branches : %s' % (same_branches)
    return same_branches


def check_tags(a_repo, b_repo):
    a_tags = set([tag.name for tag in a_repo.tags])
    b_tags = set([tag.name for tag in b_repo.tags])
    a_tag_hexshas = set([tag.object.hexsha for tag in a_repo.tags])
    b_tag_hexshas = set([tag.object.hexsha for tag in b_repo.tags])
    same_tags = a_tags == b_tags and a_tag_hexshas == b_tag_hexshas
    print 'check tags : %s' % (same_tags)
    return same_tags


def check_commits(a_repo, b_repo):
    for branch_i, a_branch in enumerate(a_repo.branches):
        b_branch = b_repo.branches[branch_i]
        if len(a_branch.commit.parents) != len(b_branch.commit.parents):
            return False
        a_parents = list(a_branch.commit.parents)
        b_parents = list(b_branch.commit.parents)
        while a_parents:
            a_parent = a_parents.pop(0)
            b_parent = next(ifilter(lambda c: c.hexsha == a_parent.hexsha, b_parents), None)
            if b_parent == None:
                print 'check commits : %s not in %s' % (a_parent, b_repo)
                return False
            elif not(check_commit(a_parent, b_parent)):
                print 'check commits : %s and %s' % (a_parent, b_parent)
                return False
            a_parents.extend(a_parent.parents)
            b_parents.extend(b_parent.parents)
    print 'check commits : True'
    return True


def check_commit(a_commit, b_commit):
    return a_commit.hexsha == b_commit.hexsha and a_commit.tree.hexsha == b_commit.tree.hexsha


if __name__ == '__main__':
    import sys
    if(len(sys.argv) != 3):
        print("{0} {1} {2}".format(sys.argv[0], "a_repo", "b_repo"))
    check_same_repository(sys.argv[1], sys.argv[2])
