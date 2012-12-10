import os
from git import Repo
from git import Commit
from exc import InvalidHistoragePathException
from parser import ParserExecutor
from committer import SyntaxTreesParallelCommitter

class HistorageConverter:
    parser_jar_path = "../target/kenja-0.0.1-SNAPSHOT-jar-with-dependencies.jar" 
    
    def __init__(self, org_git_repo_dir, working_dir):
        if org_git_repo_dir:
            self.org_repo = Repo(org_git_repo_dir)
        
        if not(os.path.isdir(working_dir)):
            raise Exception('%s is not a directory' % (working_dir))

        self.working_dir = working_dir

        self.syntax_trees_dir = os.path.join(self.working_dir, 'syntax_trees')

        self.num_commit_process = 8
        self.parallel = True

        self.changed_commits = None

    def disable_parallel(self):
        self.parallel = False

    def get_changed_commits(self):
        changed_commits = []
        for commit in self.org_repo.iter_commits(self.org_repo.head):
            assert len(commit.parents) < 2
            for p in commit.parents:
                for diff in p.diff(commit):
                    if self.is_target_blob(diff.a_blob, ".java") \
                        or self.is_target_blob(diff.b_blob, ".java"):
                            changed_commits.append(commit.hexsha)
                            break

        return changed_commits

    def is_target_blob(self, blob, ext):
        if not blob:
            return False
        return blob.name.endswith(ext)

    def parse_all_java_files(self):
        print 'create paresr processes...'
        parser_executor = ParserExecutor(self.syntax_trees_dir, self.parser_jar_path)
        self.changed_commits = []
        for commit in self.org_repo.iter_commits(self.org_repo.head):
            for p in commit.parents:
                changed = False
                for diff in p.diff(commit):
                    if diff.a_blob and diff.a_blob.name.endswith(".java"):
                        changed = True
                    if diff.b_blob and diff.b_blob.name.endswith(".java"):
                        parser_executor.parse_blob(diff.b_blob)
                        changed = True
                if changed:
                    self.changed_commits.append(commit.hexsha)
        print 'waiting parser processes'
        parser_executor.join()

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

    def prepare_repositories(self, num_working_repos):
        base_repo = self.prepare_base_repo()
        self.clone_working_repos(base_repo, num_working_repos)

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

    def convert(self):
        self.parse_all_java_files()
        self.construct_historage_repositories()
        self.merge_work_repos()

    def construct_historage_repositories(self):
        print 'create historage...'
        self.prepare_repositories(self.num_commit_process)

        divided_commits = self.divide_commits(self.num_commit_process)
        parallel_committer = SyntaxTreesParallelCommitter(self.syntax_trees_dir, self.org_repo.git_dir)
        for (commits, working_repo_dir) in zip(divided_commits, self.working_repo_dirs):
            parallel_committer.commit_syntax_trees_parallel(working_repo_dir, commits)

        print 'waiting commit processes...'
        parallel_committer.join()

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
                parent = Commit.create_from_tree(repo, commit.tree, commit.message,
                        parent_commits = [parent], head=True)

if __name__ == '__main__':
    import argparse
    class ConvertorCommandParser:
        def __init__(self):
            self.parser = argparse.ArgumentParser(description='Git convert to Historage')
            self.subparsers = self.parser.add_subparsers()

            self.add_convert_command()
            self.add_parse_command()
            self.add_construct_command()
            self.add_merge_command()

        def parse_and_execute_command(self):
            args = self.parser.parse_args()
            args.func(args)
    
        def add_convert_command(self):
            sub_parser = self.subparsers.add_parser('convert', 
            help='convert git repository to historage')
            sub_parser.add_argument('org_git_dir', 
                    help='path of original git repository')
            sub_parser.add_argument('working_dir', 
                    help='path of working directory')
            sub_parser.add_argument('--non-parallel',
                    action='store_true'
                    )
            sub_parser.add_argument('--parser-processes',
                    type=int,
                    help='set parser processes (default value is number of processers of your machine)',
                    )
            sub_parser.add_argument('--working-repositories',
                    type=int,
                    help='set number of working repositories (default value is 2)',
                    )
            sub_parser.set_defaults(func=self.convert)

        def convert(self, args):
            print args
            hc = HistorageConverter(args.org_git_dir, args.working_dir)

            if args.non_parallel:
                hc.disable_parallel()
                
            if args.parser_processes:
                hc.parser_processes = args.parser_processes

            if args.working_repositories:
                hc.num_commit_process = args.working_repositories

            hc.convert()

        def add_parse_command(self):
            sub_parser = self.subparsers.add_parser('parse', 
                    help='parse all java files from orginal git repository')
            sub_parser.add_argument('org_git_dir', 
                    help='path of original git repository')
            sub_parser.add_argument('working_dir', 
                    help='"syntax_treses" dir will be created in this dir')
            sub_parser.add_argument('--non-parallel',
                    action='store_true'
                    )
            sub_parser.set_defaults(func=self.parse)

        def parse(self, args):
            hc = HistorageConverter(args.org_git_dir, args.working_dir)

            if args.non_parallel:
                hc.disable_parallel()

            hc.parse_all_java_files()
            pass

        def add_construct_command(self):
            sub_parser = self.subparsers.add_parser('construct', 
                    help='construct historage by using syntax trees')
            sub_parser.add_argument('org_git_dir', 
                    help='path of original git repository')
            sub_parser.add_argument('working_dir', 
                    help='path of working dir')
            sub_parser.add_argument('--syntax-trees-dir',
                    help='path of syntax treses dir')
            sub_parser.add_argument('--without-merge', 
                    action='store_true',
                    help='Convertor will not merge working repos to base repo'
                    )
            sub_parser.add_argument('--non-parallel',
                    action='store_true'
                    )
            sub_parser.set_defaults(func=self.construct)

        def construct(self, args):
            hc = HistorageConverter(args.org_git_dir, args.working_dir)
            hc.construct_historage_repositories()

        def add_merge_command(self):
            sub_parser = self.subparsers.add_parser('merge', 
                    help='merge working repositorie to base repo')
            sub_parser.add_argument('working_dir', 
                    help='path of working repositories dir')
            sub_parser.set_defaults(func=self.merge)

        def merge(self, args):
            hc = HistorageConverter(None, args.working_dir)
            hc.merge_work_repos()
    
    parser = ConvertorCommandParser()
    parser.parse_and_execute_command()
