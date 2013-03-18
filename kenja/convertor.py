from __future__ import absolute_import
import os
from itertools import count, izip
from git.repo import Repo
from git.objects import Commit
from kenja.parser import ParserExecutor
from kenja.git.util import get_reversed_topological_ordered_commits
from kenja.committer import SyntaxTreesParallelCommitter
from kenja.committer import FastSyntaxTreesCommitter

class HistorageConverter:
    parser_jar_path = "../target/kenja-0.0.1-SNAPSHOT-jar-with-dependencies.jar"

    def __init__(self, org_git_repo_dir, working_dir):
        if org_git_repo_dir:
            self.org_repo = Repo(org_git_repo_dir)
        
        if not(os.path.isdir(working_dir)):
            raise Exception('%s is not a directory' % (working_dir))

        self.working_dir = working_dir

        self.syntax_trees_dir = os.path.join(self.working_dir, 'syntax_trees')

        self.num_commits = 0

    def is_target_blob(self, blob, ext):
        return blob and blob.name.endswith(ext)

    def parse_all_java_files(self):
        print 'create paresr processes...'
        parser_executor = ParserExecutor(self.syntax_trees_dir, self.parser_jar_path)
        parsed_blob = set()
        for commit in get_reversed_topological_ordered_commits(self.org_repo, self.org_repo.refs):
            self.num_commits = self.num_commits + 1
            commit = self.org_repo.commit(commit)
            for p in commit.parents:
                for diff in p.diff(commit):
                    if self.is_target_blob(diff.b_blob, '.java'):
                        if not diff.b_blob.hexsha in parsed_blob:
                            parser_executor.parse_blob(diff.b_blob)
                            parsed_blob.add(diff.b_blob.hexsha)

        print 'waiting parser processes'
        parser_executor.join()

    def prepare_base_repo(self):
        base_repo_dir = os.path.join(self.working_dir, 'base_repo')
        base_repo = Repo.init(base_repo_dir)
        return base_repo
    
    def clone_working_repos(self, base_repo, num_working_repos):
        self.working_repo_dirs = []
        for i in range(num_working_repos):
            working_repo_dir = os.path.join(self.working_dir, 'work_repo%d' % (i))
            self.working_repo_dirs.append(working_repo_dir)
            base_repo.clone(working_repo_dir)

    def convert(self):
        self.parse_all_java_files()
        self.construct_historage()

    def construct_historage(self):
        print 'create historage...'

        base_repo = self.prepare_base_repo()
        committer = FastSyntaxTreesCommitter(Repo(self.org_repo.git_dir), base_repo, self.syntax_trees_dir)
        num_commits = self.num_commits if self.num_commits != 0 else '???'
        for num, commit in izip(count(), get_reversed_topological_ordered_commits(self.org_repo, self.org_repo.refs)):
            print '[%d/%s] commit to: %s' % (num, num_commits, base_repo.git_dir)
            commit = self.org_repo.commit(commit)
            committer.apply_change(commit)
        committer.create_heads()
        committer.create_tags()

class ParallelHistorageConverter(HistorageConverter):
    def __init__(self, org_git_repo_dir, working_dir):
        HistorageConverter.__init__(self, org_git_repo_dir, working_dir)

        self.num_commit_process = 8

    def construct_historage(self):
        print 'create historage...'
        self.prepare_repositories(self.num_commit_process)

        divided_commits = self.divide_commits(self.num_commit_process)
        parallel_committer = SyntaxTreesParallelCommitter(self.syntax_trees_dir, self.org_repo.git_dir, FastSyntaxTreesCommitter)

        for (commits, working_repo_dir) in zip(divided_commits, self.working_repo_dirs):
            parallel_committer.commit_syntax_trees_parallel(working_repo_dir, commits)

        print 'waiting commit processes...'
        parallel_committer.join()

        self.merge_work_repos()

    def divide_commits(self, num):
        if not self.changed_commits:
            self.changed_commits = self.get_changed_commits()

        self.changed_commits.reverse()
        num_commits = len(self.changed_commits)
        step = num_commits // num
        first = step + num_commits % step
        result = []
        result.append(self.changed_commits[0:first])
        result.extend( [self.changed_commits[i:i+step] for i in range(first, num_commits, step)])
        return result

    def prepare_base_repo(self):
        base_repo_dir = os.path.join(self.working_dir, 'base_repo')
        base_repo = Repo.init(base_repo_dir)
        open(os.path.join(base_repo_dir, 'historage_dummy'), 'w').close()
        base_repo.index.add(['historage_dummy'])
        base_repo.index.commit('Initail dummy commit')
        return base_repo

    def clone_working_repos(self, base_repo, num_working_repos):
        self.working_repo_dirs = []
        for i in range(num_working_repos):
            working_repo_dir = os.path.join(self.working_dir, 'work_repo%d' % (i))
            self.working_repo_dirs.append(working_repo_dir)
            base_repo.clone(working_repo_dir)

    def prepare_repositories(self, num_working_repos):
        base_repo = self.prepare_base_repo()
        self.clone_working_repos(base_repo, num_working_repos)

    def merge_work_repos(self):
        print 'merge working repos...'
        parent = None
        new_remotes = []
        base_repo_dir = os.path.join(self.working_dir, 'base_repo')
        repo = Repo(base_repo_dir)

        for i in range(self.num_commit_process):
            work_repo = Repo(os.path.join(self.working_dir, 'work_repo' + str(i)))
            abspath = os.path.abspath(work_repo.git_dir)
            new_remote = repo.create_remote('work_repo' + str(i), abspath)
            print 'fetch %d th repo' % (i)
            new_remote.fetch()
            new_remotes.append(new_remote)

        for remote in new_remotes:
            arg = {"reverse":True}
            commits = repo.iter_commits(remote.refs.master, **arg)
            if not parent:
                parent = commits.next()
            else:
                commits.next()
            for commit in commits:
                print 'process remote commit: %s' % (commit.hexsha)
                print 'parent is: %s' % (parent.hexsha)
                print 'tree is: %s' % (commit.tree.hexsha)
                message = commit.message.encode(commit.encoding)
                parent = Commit.create_from_tree(repo, commit.tree, message,
                        parent_commits = [parent], head=True)
