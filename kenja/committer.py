import shutil
import os
from subprocess import check_output
from git import Blob
from git import Repo
from itertools import count
from itertools import izip
from gittools import (
                            commit_from_binsha,
                            mktree,
                            mktree_from_iter,
                            write_tree
                    )

from multiprocessing import (
                                Pool,
                                cpu_count
                            )

class SyntaxTreesCommitterBase:
    def __init__(self, org_repo, syntax_trees_dir):
        self.org_repo = org_repo
        self.syntax_trees_dir = syntax_trees_dir

    def is_completed_parse(self, blob):
        path = os.path.join(self.syntax_trees_dir, blob.hexsha)
        cmd = ['find', path, '-type', 'f']
        output = check_output(cmd)
        if len(output) == 0:
            #print 'Interface?:', blob.path
            pass
        return len(output) > 0

    def get_normalized_path(self, path):
        return path.replace("/", "_")

    def commit_syntax_trees(self, repo, changed_commits):
        start_commit = self.org_repo.commit(changed_commits.pop(0))
        total_commits = len(changed_commits)
        print '[00/%d] first commit to: %s' % (total_commits, repo.git_dir)
        self.construct_from_commit(repo, start_commit)

        for (num, commit_hexsha) in izip(count(1), changed_commits):
            print '[%d/%d] commit to: %s' % (num, total_commits, repo.git_dir)
            commit = self.org_repo.commit(commit_hexsha)
            self.apply_change(repo, commit)



class SyntaxTreesCommitter(SyntaxTreesCommitterBase):
    def __init__(self, org_repo, syntax_trees_dir):
        SyntaxTreesCommitterBase.__init__(self, org_repo, syntax_trees_dir)

    def remove_files(self, repo, index, removed_files):
        kwargs = {"r" : True}
        if len(removed_files) == 0:
            return
        index.remove(removed_files, **kwargs)
        index.write()

        for p in removed_files:
            shutil.rmtree(os.path.join(repo.working_dir, p))

    def add_files(self, repo, index, added_files):
        if len(added_files) == 0:
            return

        for path, hexsha in added_files.items():
            src = os.path.join(self.syntax_trees_dir, hexsha)
            dst = os.path.join(repo.working_dir, path)
            shutil.copytree(src, dst)

        repo.git.add(added_files.keys())
        index.update()

    def construct_from_commit(self, repo, commit):
        added_files = {}
        for entry in commit.tree.traverse():
            if not isinstance(entry, Blob):
                continue

            if not entry.name.endswith('.java'):
                continue
            if self.is_completed_parse(entry):
                added_files[self.get_normalized_path(entry.path)] = entry.hexsha

        self.add_files(repo, repo.index, added_files)
        repo.index.commit(commit.hexsha)

    def apply_change(self, new_repo, commit):
        assert len(commit.parents) < 2 # Not support branched repository

        index = new_repo.index
        removed_files = []
        added_files = {}
        for p in commit.parents:
            for diff in p.diff(commit):
                if(diff.a_blob):
                    if not diff.a_blob.name.endswith(".java"):
                        continue
                    if self.is_completed_parse(diff.a_blob):
                        removed_files.append(self.get_normalized_path(diff.a_blob.path))

                if(diff.b_blob):
                    if not diff.b_blob.name.endswith(".java"):
                        continue
                    if self.is_completed_parse(diff.b_blob):
                        added_files[self.get_normalized_path(diff.b_blob.path)] = diff.b_blob.hexsha


            self.remove_files(new_repo, index, removed_files)
            self.add_files(new_repo, index, added_files)

        if len(index.diff(None, staged=True)):
            index.commit(commit.hexsha)


class FastSyntaxTreesCommitter(SyntaxTreesCommitterBase):
    def __init__(self, org_repo, syntax_trees_dir):
        SyntaxTreesCommitterBase.__init__(self, org_repo, syntax_trees_dir)
        self.previous_top_tree = {}

    def construct_from_commit(self, repo, commit):
        for entry in commit.tree.traverse():
            if not isinstance(entry, Blob):
                continue

            if not entry.name.endswith('.java'):
                continue

            if self.is_completed_parse(entry):
                (mode, binsha) = self.write_syntax_tree(repo, entry)
                path = self.get_normalized_path(entry.path)
                self.previous_top_tree[path] = (mode, binsha)

        (mode, binsha) = mktree_from_iter(repo.odb, self.iter_object_info())
        commit_from_binsha(repo, binsha, commit.hexsha)

    def write_syntax_tree(self, repo, blob):
        src = os.path.join(self.syntax_trees_dir, blob.hexsha)
        return write_tree(repo.odb, src)

    def apply_change(self, new_repo, commit):
        assert len(commit.parents) < 2 # Not support branched repository

        changed = False
        for p in commit.parents:
            for diff in p.diff(commit):
                if(diff.a_blob):
                    if not diff.a_blob.name.endswith(".java"):
                        continue
                    if self.is_completed_parse(diff.a_blob):
                        path = self.get_normalized_path(diff.a_blob.path)
                        self.previous_top_tree.pop(path)
                        changed = True

                if(diff.b_blob):
                    if not diff.b_blob.name.endswith(".java"):
                        continue
                    if self.is_completed_parse(diff.b_blob):
                        path = self.get_normalized_path(diff.b_blob.path)
                        (mode, binsha) = self.write_syntax_tree(new_repo, diff.b_blob)
                        self.previous_top_tree[path] = (mode, binsha)
                        changed = True

        if changed:
            (mode, binsha) = mktree_from_iter(new_repo.odb, self.iter_object_info())
            commit_from_binsha(new_repo, binsha, commit.hexsha)

    def iter_object_info(self):
        for (name, (mode, binsha)) in self.previous_top_tree.items():
            yield mode, binsha, name

def commit_syntax_trees_worker(repo_dir, org_repo_dir, changed_commits, syntax_trees_dir, syntax_trees_committer):
    repo = Repo(repo_dir)
    org_repo = Repo(org_repo_dir)
    committer = syntax_trees_committer(org_repo, syntax_trees_dir)
    committer.commit_syntax_trees(repo, changed_commits)

class SyntaxTreesParallelCommitter:
    def __init__(self, syntax_trees_dir, org_repo_dir, syntax_trees_committer, processes=None):
        self.syntax_trees_dir = syntax_trees_dir
        self.org_repo_dir = org_repo_dir
        self.processes = processes if processes else cpu_count()
        self.pool = Pool(self.processes)
        self.closed = False
        self.syntax_trees_committer = syntax_trees_committer

    def commit_syntax_trees_parallel(self, repo_dir, changed_commits):
        args = [repo_dir, self.org_repo_dir, changed_commits, self.syntax_trees_dir, self.syntax_trees_committer]
        if(self.closed):
            self.pool = Pool(self.processes)
            self.closed = False

        self.pool.apply_async(commit_syntax_trees_worker, args=args)

    def join(self):
        self.pool.close()
        self.closed = True
        self.pool.join()
        self.pool = None
