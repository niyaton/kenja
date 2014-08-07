from __future__ import absolute_import
import os
from itertools import count, izip
from git.repo import Repo
from git.objects import Blob
from kenja.parser import ParserExecutor
from kenja.git.util import get_reversed_topological_ordered_commits
from kenja.committer import SyntaxTreesCommitter


class HistorageConverter:
    parser_jar_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'java-parser.jar')

    def __init__(self, org_git_repo_dir, historage_dir, syntax_trees_dir):
        if org_git_repo_dir:
            self.org_repo = Repo(org_git_repo_dir)

        if os.path.isdir(historage_dir):
            if os.listdir(historage_dir):
                raise Exception('%s is not a empty directory' % (historage_dir))
        else:
            try:
                os.mkdir(historage_dir)
            except OSError:
                print '%s has not a parent directory' % (historage_dir)
                raise

        self.historage_dir = historage_dir

        if os.path.isdir(syntax_trees_dir):
            if os.listdir(syntax_trees_dir):
                raise Exception('%s is not a empty directory' % (syntax_trees_dir))
        else:
            try:
                os.mkdir(syntax_trees_dir)
            except OSError:
                print '%s has not a parent directory' % (syntax_trees_dir)
                raise

        self.syntax_trees_dir = syntax_trees_dir

        self.num_commits = 0

        self.is_bare_repo = False

    def is_target_blob(self, blob, ext):
        return blob and blob.name.endswith(ext)

    def parse_all_java_files(self):
        print 'create paresr processes...'
        parser_executor = ParserExecutor(self.syntax_trees_dir, self.parser_jar_path)
        parsed_blob = set()
        for commit in get_reversed_topological_ordered_commits(self.org_repo, self.org_repo.refs):
            self.num_commits = self.num_commits + 1
            commit = self.org_repo.commit(commit)
            if commit.parents:
                for p in commit.parents:
                    for diff in p.diff(commit):
                        if self.is_target_blob(diff.b_blob, '.java'):
                            if diff.b_blob.hexsha not in parsed_blob:
                                parser_executor.parse_blob(diff.b_blob)
                                parsed_blob.add(diff.b_blob.hexsha)
            else:
                for entry in commit.tree.traverse():
                    if isinstance(entry, Blob) and self.is_target_blob(entry, '.java'):
                        if entry.hexsha not in parsed_blob:
                            parser_executor.parse_blob(entry)
                            parsed_blob.add(entry.hexsha)
        print 'waiting parser processes'
        parser_executor.join()

    def prepare_base_repo(self):
        base_repo = Repo.init(self.historage_dir, bare=self.is_bare_repo)
        return base_repo

    def convert(self):
        self.parse_all_java_files()
        self.construct_historage()

    def construct_historage(self):
        print 'create historage...'

        base_repo = self.prepare_base_repo()
        committer = SyntaxTreesCommitter(Repo(self.org_repo.git_dir), base_repo, self.syntax_trees_dir)
        num_commits = self.num_commits if self.num_commits != 0 else '???'
        for num, commit in izip(count(), get_reversed_topological_ordered_commits(self.org_repo, self.org_repo.refs)):
            commit = self.org_repo.commit(commit)
            print '[%d/%s] convert %s to: %s' % (num, num_commits, commit.hexsha, base_repo.git_dir)
            committer.apply_change(commit)
        committer.create_heads()
        committer.create_tags()
        if not self.is_bare_repo:
            base_repo.head.reset(working_tree=True)
