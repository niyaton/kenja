from __future__ import absolute_import
import os
import re
import pkg_resources
from copy import deepcopy
from tempfile import NamedTemporaryFile
from string import Template
from git.objects import Blob
from kenja.language import is_target_blob
from kenja.git.tree_contents import SortedTreeContents
from kenja.git.util import (
    commit_from_binsha,
    mktree_from_iter,
    write_syntax_tree_from_file,
    tree_mode,
    create_note,
    write_blob_from_path
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
        return os.path.isfile(path)

    def is_convert_target(self, blob):
        if not is_target_blob(blob):
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
        (_, binsha) = mktree_from_iter(self.new_repo.odb, tree_contents)

        parents = [self.new_repo.commit(self.old2new[parent.hexsha]) for parent in org_commit.parents]

        result = commit_from_binsha(self.new_repo, binsha, org_commit, parents)

        note_message = str(org_commit.hexsha)
        create_note(self.new_repo, note_message)
        return result

    def apply_change(self, commit):
        if commit.parents:
            tree_contents = self.create_tree_contents(commit.parents[0], commit)
        else:
            tree_contents = self.create_tree_contents_from_commit(commit)
            tree_contents = self.create_readme(tree_contents)

        new_commit = self.commit(commit, tree_contents)
        self.old2new[commit.hexsha] = new_commit.hexsha
        self.sorted_tree_contents[new_commit.hexsha] = tree_contents

    def create_tree_contents_from_commit(self, commit):
        tree_contents = SortedTreeContents()

        for entry in commit.tree.traverse():
            if isinstance(entry, Blob) and self.is_convert_target(entry):
                path = self.get_normalized_path(entry.path)
                binsha = self.add_changed_blob(entry)
                tree_contents.insert(tree_mode, binsha, path)

        return tree_contents

    def create_readme(self, tree_contents):
        with NamedTemporaryFile() as f:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            with open(dir_path + '/readme_for_historage.txt', 'r') as readme:
                text = readme.read()
            try:
                url = self.org_repo.remotes.origin.url
                repo_name = re.search('/(.*)$', url).group(1).replace('.git', '')
            except AttributeError:
                url = 'unknown url'
                repo_name = 'unknown repository'
            version = pkg_resources.require("kenja")[0].version
            text = Template(text).substitute(
                name=repo_name,
                url=url,
                version=version
            )
            f.write(text)
            f.flush()
            mode, binsha = write_blob_from_path(self.new_repo.odb, f.name)
            tree_contents.insert(mode, binsha, 'README.md')
            return tree_contents

    def create_tree_contents(self, parent, commit):
        converted_parent_hexsha = self.old2new[parent.hexsha]
        # TODO This deepcopy have a potential of performance bug.
        # I think there is more clever algorithm for this situation.
        tree_contents = deepcopy(self.sorted_tree_contents[converted_parent_hexsha])

        for diff in parent.diff(commit):
            is_a_target = self.is_convert_target(diff.a_blob)
            is_b_target = self.is_convert_target(diff.b_blob)
            if is_a_target and (not is_b_target or diff.renamed):
                # Blob was removed
                name = self.get_normalized_path(diff.a_blob.path)
                tree_contents.remove(name)
                if is_b_target and diff.renamed:
                    # Blob was created
                    name = self.get_normalized_path(diff.b_blob.path)
                    binsha = self.add_changed_blob(diff.b_blob)
                    tree_contents.insert(tree_mode, binsha, name)
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
