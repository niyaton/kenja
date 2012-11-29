from git import Repo
import os

class CommitList:

    def __init__(self, repo):
        self.repo = repo

    def print_all_blob_hashes(self):
        hashes = set()
        for commit in self.repo.iter_commits(self.repo.head):
            for p in commit.parents:
                diff = p.diff(commit)
                for change in diff.iter_change_type("M"):
                    if change.b_blob.name.endswith(".java"):
                        hashes.add(change.b_blob.hexsha)
                for change in diff.iter_change_type("A"):
                    if change.b_blob.name.endswith(".java"):
                        hashes.add(change.b_blob.hexsha)

        for h in hashes:
            print h

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Edit distance calculator')
    parser.add_argument('org_git_dir')

    args = parser.parse_args()
    
    git_dir = args.org_git_dir
    if not os.path.isdir(git_dir):
        print "%s is not a directory" % (git_dir)

    repo = Repo(git_dir)
    
    cl = CommitList(repo)
    cl.print_all_blob_hashes()
