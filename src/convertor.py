import os
from git import Repo
from git import Commit
from exc import InvalidHistoragePathException
from parser import ParserExecutor
from committer import SyntaxTreesParallelCommitter

class HistorageConverter:
    parser_jar_path = "../target/kenja-0.0.1-SNAPSHOT-jar-with-dependencies.jar" 
    
    def __init__(self, org_git_repo, working_dir):
        self.org_repo = org_git_repo
        
        if not(os.path.isdir(working_dir)):
            raise Exception('%s is not a directory' % (working_dir))

        self.working_dir = working_dir

        self.syntax_trees_dir = os.path.join(self.working_dir, 'syntax_trees')
        self.parser_executor = ParserExecutor(self.syntax_trees_dir, self.parser_jar_path)

        self.num_commit_process = 8

    def parse_all_java_files(self):
        self.changed_commits = []
        for commit in self.org_repo.iter_commits(self.org_repo.head):
            for p in commit.parents:
                changed = False
                for diff in p.diff(commit):
                    if diff.a_blob and diff.a_blob.name.endswith(".java"):
                        changed = True
                    if diff.b_blob and diff.b_blob.name.endswith(".java"):
                        self.parser_executor.parse_blob(diff.b_blob)
                        changed = True
                if changed:
                    self.changed_commits.append(commit.hexsha)

    def divide_commits(self, num):
        self.changed_commits.reverse()
        num_commits = len(self.changed_commits)
        step = num_commits // num
        starts = range(0, num_commits, step)
        ends = range(0 + step - 1, num_commits, step) 
        ends[-1] = num_commits - 1
        if(starts > num):
            starts.pop()
        
        return(starts, ends)

    def prepare_base_repo(self):
        base_repo_dir = os.path.join(self.working_dir, 'base_repo')
        self.base_repo = Repo.init(base_repo_dir)
        open(os.path.join(base_repo_dir, 'historage_dummy'), 'w').close()
        self.base_repo.index.add(['historage_dummy'])
        self.base_repo.index.commit('Initail dummy commit')

    def clone_working_repos(self, num):
        self.working_repos = []
        for i in range(num):
            working_repo_dir = os.path.join(self.working_dir, 'work_repo%d' % (i))
            self.working_repos.append(self.base_repo.clone(working_repo_dir))

    def convert(self):
        print 'create paresr processes...'
        self.parse_all_java_files()
        
        print 'waiting parser processes'
        self.parser_executor.join()

        print 'create historage...'
        print len(self.changed_commits)
        
        self.prepare_base_repo()
        self.clone_working_repos(self.num_commit_process)

        (starts, ends) = self.divide_commits(self.num_commit_process)

        parallel_committer = SyntaxTreesParallelCommitter(self.syntax_trees_dir, self.changed_commits, self.org_repo.git_dir)
        for i in range(len(starts)):
            print 'process %d th repo...' % (i)
            parallel_committer.commit_syntax_trees_parallel(self.working_repos[i].git_dir, starts[i], ends[i])

        print 'waiting commit processes...'
        parallel_committer.join()

        print 'merge working repos...'
        self.merge_work_repos()

    def merge_work_repos(self):
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
 
    parser = argparse.ArgumentParser(description='Git convert to Historage')
    parser.add_argument('org_git_dir')
    parser.add_argument('working_dir')

    args = parser.parse_args()
    
    git_dir = args.org_git_dir
    if not os.path.isdir(git_dir):
        print "%s is not a directory" % (git_dir)

    repo = Repo(git_dir)
    
    gbp = HistorageConverter(repo, args.working_dir)
    gbp.convert()
