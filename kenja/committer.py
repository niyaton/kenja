from __future__ import absolute_import
import os
from copy import deepcopy
from subprocess import check_output
from git.repo import Repo
from git.objects import Blob
from multiprocessing import (
    Pool,
    cpu_count
    )
from kenja.git.tree_contents import SortedTreeContents
from kenja.git.util import (
    commit_from_binsha,
    mktree_from_iter,
    write_syntax_tree_from_file,
    tree_mode,
    create_note
    )

class SyntaxTreesCommitter:
    def __init__(self, org_repo, new_repo, syntax_trees_dir):
        self.org_repo = org_repo
        self.new_repo = new_repo
        self.syntax_trees_dir = syntax_trees_dir
        self.old2new = {}
        self.sorted_tree_contents = {}
        self.blob2tree = {}

    def is_completed_parse(self, blob):
        path = os.path.join(self.syntax_trees_dir, blob.hexsha)
        cmd = ['find', path, '-type', 'f']
        output = check_output(cmd)
        if len(output) == 0:
            #print 'Interface?:', blob.path
            pass
        return len(output) > 0

    def is_commit_target(self, blob):
        if blob is None or not blob.name.endswith('.java'):
            return False
        return self.is_completed_parse(blob)

    def get_normalized_path(self, path):
        # TODO We cannot avoid conflict of normalized path such as following patterns:
        # a: foo/bar_/hoge.java
        # b: foo/bar/_hoge.java
        # but we consider that strange name pattern is rarely case.
        path = path.replace("_", "__")
        return path.replace("/", "_")

    def add_changed_blob(self, blob):
        if blob.hexsha in self.blob2tree:
            return self.blob2tree[blob.hexsha]

        binsha = self.write_syntax_tree(self.new_repo, blob)
        self.blob2tree[blob.hexsha] = binsha
        return self.blob2tree[blob.hexsha]

    def write_syntax_tree(self, repo, blob):
        src = os.path.join(self.syntax_trees_dir, blob.hexsha)
        return write_syntax_tree_from_file(repo.odb, src)[1]

    def commit(self, org_commit, tree_contents):
        (mode, binsha) = mktree_from_iter(self.new_repo.odb, tree_contents)

        parents = [self.old2new[parent.hexsha] for parent in org_commit.parents]

        result = commit_from_binsha(self.new_repo, binsha, org_commit, parents)

        note_message = str(org_commit.hexsha)
        create_note(self.new_repo, note_message)
        return result

    def apply_change(self, commit):
        if commit.parents:
            tree_contents = self.create_tree_contents(commit.parents[0], commit)
        else:
            tree_contents = self.create_tree_contents_from_commit(commit)

        new_commit = self.commit(commit, tree_contents)
        self.old2new[commit.hexsha] = new_commit.hexsha
        self.sorted_tree_contents[new_commit.hexsha] = tree_contents

    def create_tree_contents_from_commit(self, commit):
        tree_contents = SortedTreeContents()

        for entry in commit.tree.traverse():
            if isinstance(entry, Blob) and self.is_commit_target(entry):
                path = self.get_normalized_path(entry.path)
                binsha = self.add_changed_blob(entry)
                tree_contents.insert(tree_mode, binsha, path)

        return tree_contents

    def create_tree_contents(self, parent, commit):
        converted_parent_hexsha = self.old2new[parent.hexsha]
        tree_contents = deepcopy(self.sorted_tree_contents[converted_parent_hexsha])

        for diff in parent.diff(commit):
            is_a_target = self.is_commit_target(diff.a_blob)
            is_b_target = self.is_commit_target(diff.b_blob)
            if is_a_target and not is_b_target:
                # Blob was removed
                name = self.get_normalized_path(diff.a_blob.path)
                tree_contents.remove(name)
            elif is_b_target:
                name = self.get_normalized_path(diff.b_blob.path)
                binsha = self.add_changed_blob(diff.b_blob)
                if is_a_target:
                    # Blob was changed
                    tree_contents.replace(tree_mode, binsha, name)
                else:
                    # Blob was created
                    tree_contents.insert(tree_mode, binsha, name)
        return tree_contents

    def create_heads(self):
        for head in self.org_repo.heads:
            hexsha = head.commit.hexsha
            if hexsha in self.old2new:
                if head.name == 'master':
                    master = self.new_repo.heads.master
                    master.set_reference(self.old2new[hexsha])
                else:
                    self.new_repo.create_head(head.name, commit=self.old2new[hexsha])

    def create_tags(self):
        for tag_ref in self.org_repo.tags:
            hexsha = tag_ref.commit.hexsha
            if hexsha in self.old2new:
                self.new_repo.create_tag(tag_ref.name, ref=self.old2new[hexsha])


def commit_syntax_trees_worker(repo_dir, org_repo_dir, changed_commits, syntax_trees_dir, syntax_trees_committer):
    repo = Repo(repo_dir)
    org_repo = Repo(org_repo_dir)
    committer = syntax_trees_committer(org_repo, repo, syntax_trees_dir)
    committer.commit_syntax_trees(changed_commits)


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
