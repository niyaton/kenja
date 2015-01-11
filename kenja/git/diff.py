from __future__ import absolute_import
import re
from kenja.historage import get_org_commit
from git import Repo
from logging import getLogger

logger = getLogger(__name__)


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
    check_branches(a_repo, b_repo)
    check_tags(a_repo, b_repo)
    check_commits(a_repo, b_repo)


def check_branches(a_repo, b_repo):
    a_branches = set([(b.name, b.commit.hexsha) for b in a_repo.branches])
    b_branches = set([(b.name, b.commit.hexsha) for b in b_repo.branches])
    logger.info('check branches : {0}'.format(a_branches == b_branches))
    return a_branches == b_branches


def check_tags(a_repo, b_repo):
    a_tags = set([(tag.name, tag.object.hexsha) for tag in a_repo.tags])
    b_tags = set([(tag.name, tag.object.hexsha) for tag in b_repo.tags])
    logger.info('check tags : {}'.format(a_tags == b_tags))
    return a_tags == b_tags


def split_notes_from_refs(repo):
    note_rev = 'refs/notes/commits'
    refs = [ref for ref in repo.refs if ref.path != note_rev]
    try:
        notes = repo.commit(note_rev)
    except Exception:
        print('{0} is not historage'.format(repo))
        raise

    return (refs, notes)


def merge_commits_with_org_commit(a_commits, b_commits):
    commits = {}
    for commit in a_commits:
        org_commit = get_org_commit(commit)
        commits[org_commit] = (commit, None)

    for commit in b_commits:
        org_commit = get_org_commit(commit)
        if org_commit in commits:
            commits[org_commit] = (commits[org_commit][0], commit)
        else:
            commits[org_commit] = (None, commit)

    # return list of (a_commit, b_commit, org_commit)
    return [value + (key,) for key, value in commits.items()]


def check_commits(a_repo, b_repo):
    a_heads, a_notes = split_notes_from_refs(a_repo)
    b_heads, b_notes = split_notes_from_refs(b_repo)

    a_commits = [head.commit for head in a_heads]
    b_commits = [head.commit for head in b_heads]
    commits = merge_commits_with_org_commit(a_commits, b_commits)

    visited = set()
    while commits:
        a_commit, b_commit, org_commit = commits.pop(0)
        if org_commit in visited:
            continue

        logger.debug('[a_commit, b_commit, org_commit]: {0}, {1}, {2}'.format(a_commit, b_commit, org_commit))
        if a_commit:
            a_parents = a_commit.parents
        else:
            logger.error("{0} does not contain {1}".format(a_repo.git_dir, org_commit))
            a_parents = []

        if b_commit:
            b_parents = b_commit.parents
        else:
            logger.error("{0} does not contain {1}".format(b_repo.git_dir, org_commit))
            b_parents = []

        logger.debug("org_commit: {}".format(org_commit))

        commits.extend(merge_commits_with_org_commit(a_parents, b_parents))

        visited.add(org_commit)


def main():
    import argparse
    from logging import basicConfig, DEBUG
    basicConfig(level=DEBUG)

    parser = argparse.ArgumentParser(description='test historage equivalence')
    parser.add_argument('a_repo', help='path of historage')
    parser.add_argument('b_repo', help='path of historage')
    args = parser.parse_args()

    check_same_repository(args.a_repo, args.b_repo)


if __name__ == '__main__':
    main()
