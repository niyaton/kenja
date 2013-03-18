from __future__ import absolute_import
import shutil
import os
from copy import deepcopy
from bisect import bisect_left
from subprocess import check_output
from git.repo import Repo
from git.objects import Blob
from itertools import (count, izip, chain)
from kenja.git.util import (
                            tree_mode,
                            commit_from_binsha,
                            mktree_from_iter,
                            write_tree
                    )
from multiprocessing import (
                                Pool,
                                cpu_count
                            )
from kenja.git.submodule import (
                                store_submodule_config,
                                get_submodule_tree_content
                    )

class SyntaxTreesCommitter:
    def __init__(self, org_repo, new_repo, syntax_trees_dir):
        self.org_repo = org_repo
        self.new_repo = new_repo
        self.syntax_trees_dir = syntax_trees_dir
        self.old2new = {}
        self.top_tree_binshas = {} # sorted tree contents of previous commits
        self.top_tree_names = {} # sorted paths of top tree.
        self.blob2tree = {}

        self.create_submodule_info()

    def is_completed_parse(self, blob):
        path = os.path.join(self.syntax_trees_dir, blob.hexsha)
        cmd = ['find', path, '-type', 'f']
        output = check_output(cmd)
        if len(output) == 0:
            #print 'Interface?:', blob.path
            pass
        return len(output) > 0

    def is_commit_target(self, blob):
        if not blob.name.endswith('.java'):
            return False
        return self.is_completed_parse(blob)

    def get_normalized_path(self, path):
        return path.replace("/", "_")

    def add_changed_blob(self, blob):
        if blob.hexsha in self.blob2tree:
            return self.blob2tree[blob.hexsha]

        binsha = self.write_syntax_tree(self.new_repo, blob)
        self.blob2tree[blob.hexsha] = binsha
        return self.blob2tree[blob.hexsha]

    def commit(self, org_commit, tree_contents):
        submodule_info = [self.gitmodules_info]
        submodule_info.append(get_submodule_tree_content(org_commit.hexsha, 'org_repo'))

        (mode, binsha) = mktree_from_iter(self.new_repo.odb, chain(tree_contents, submodule_info))

        parents = [self.old2new[parent.hexsha] for parent in org_commit.parents]

        message = org_commit.message.encode(org_commit.encoding)
        return commit_from_binsha(self.new_repo, binsha, message, parents)

    def iter_tree_contents(self, binshas, names):
        for binsha, name in izip(binshas, names):
            yield (tree_mode, binsha, name)

    def create_submodule_info(self):
        mode, binsha = store_submodule_config(self.new_repo.odb, 'original', 'org_repo', self.org_repo.git_dir)
        self.gitmodules_info = (mode, binsha, '.gitmodules')

    def create_tree_contents_from_commit(self, commit):
        trees = []
        keys = []
        for entry in commit.tree.traverse():
            if not isinstance(entry, Blob):
                continue

            if not self.is_commit_target(entry):
                continue
            path = self.get_normalized_path(entry.path)
            binsha = self.add_changed_blob(entry)
            pos = bisect_left(keys, path)
            trees.insert(pos, binsha)
            keys.insert(pos, path)

        return (trees, keys)

    def write_syntax_tree(self, repo, blob):
        src = os.path.join(self.syntax_trees_dir, blob.hexsha)
        return write_tree(repo.odb, src)[1]

    def apply_change(self, commit):
        if commit.parents:
            parent = commit.parents[0]
            converted_parent_hexsha = self.old2new[parent.hexsha]
            trees, keys = self.create_tree_contents(self.top_tree_binshas[converted_parent_hexsha], parent, commit)
        else:
            trees, keys = self.create_tree_contents_from_commit(commit)

        tree_iter = self.iter_tree_contents(trees, keys)
        new_commit = self.commit(commit, tree_iter)
        self.old2new[commit.hexsha] = new_commit.hexsha
        self.top_tree_binshas[new_commit.hexsha] = trees
        self.top_tree_names[new_commit.hexsha] = keys

    def create_tree_contents(self, base_tree_contents, parent, commit):
        tree_contents = deepcopy(base_tree_contents)
        converted_parent_hexsha = self.old2new[parent.hexsha]
        keys = deepcopy(self.top_tree_names[converted_parent_hexsha])
        for diff in parent.diff(commit):
            pos = None
            if (diff.a_blob):
                if self.is_commit_target(diff.a_blob):
                    name = self.get_normalized_path(diff.a_blob.path)
                    pos = bisect_left(keys, name)
                    pos = pos if pos != len(keys) and keys[pos] == name else None
                    if not diff.b_blob:
                        del keys[pos]
                        del tree_contents[pos]

            if (diff.b_blob):
                if not self.is_commit_target(diff.b_blob):
                    continue
                path = self.get_normalized_path(diff.b_blob.path)
                binsha = self.add_changed_blob(diff.b_blob)
                if not pos:
                    pos = bisect_left(keys, path)
                    tree_contents.insert(pos, binsha)
                    keys.insert(pos, path)
                else:
                    tree_contents[pos] = binsha
                    keys[pos] = path
        return tree_contents, keys

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
