import os
from git import Repo
from exc import InvalidHistoragePathException
from subprocess import (
                            Popen,
                            PIPE,
                            check_output
                        )
import shutil
from parser import ParserExecutor

class HistorageConverter:
    parser_jar_path = "../target/kenja-0.0.1-SNAPSHOT-jar-with-dependencies.jar" 
    
    def __init__(self, org_git_repo, new_git_repo_dir_path, working_dir):
        dirname = os.path.basename(new_git_repo_dir_path)
        if(dirname == '.git'):
            raise InvalidHistoragePathException('Do not use ".git" dir for historage path')

        if os.path.exists(new_git_repo_dir_path):
            raise InvalidHistoragePathException( \
                    '%s is already exists. Historage converter will be create new directory and git repository automatically' \
                    % (new_git_repo_dir_path))

        self.historage_repo = Repo.init(new_git_repo_dir_path)
        self.org_repo = org_git_repo
        
        if not(os.path.isdir(working_dir)):
            raise Exception('%s is not a directory' % (working_dir))
        self.working_dir = working_dir

        self.syntax_trees_dir = os.path.join(self.working_dir, 'syntax_trees')
        self.parser_executor = ParserExecutor(self.syntax_trees_dir, self.parser_jar_path)

    def parse_all_java_files(self):
        for commit in self.org_repo.iter_commits(self.org_repo.head):
            for p in commit.parents:
                for diff in p.diff(commit):
                    if diff.b_blob and diff.b_blob.name.endswith(".java"):
                        self.parser_executor.parse_blob(diff.b_blob)

    def remove_files(self, index, removed_files):
        kwargs = {"r" : True}
        if len(removed_files) == 0:
            return
        index.remove(removed_files, **kwargs)
        index.write()

        for p in removed_files:
            shutil.rmtree(os.path.join(self.historage_repo.working_dir, p))

    def add_files(self, index, added_files):
        if len(added_files) == 0:
            return

        for path, hexsha in added_files.items():
            src = os.path.join(self.syntax_trees_dir, hexsha)
            dst = os.path.join(self.historage_repo.working_dir, path)
            shutil.copytree(src, dst)

        self.historage_repo.git.add(added_files.keys())
        index.update()

    def is_completed_parse(self, blob):
        path = os.path.join(self.working_dir, 'syntax_trees', blob.hexsha)
        cmd = ['find', path, '-type', 'f']
        output = check_output(cmd)
        if len(output) == 0:
            print 'Interface?:', blob.path
        return len(output) > 0

    def commit_syntax_trees(self, start, end):
        pass

    def commit_all_syntax_trees(self):
        index = self.historage_repo.index
        arg = {'reverse':True}
        for commit in self.org_repo.iter_commits(self.org_repo.head, **arg):
            print 'process commit:', commit.hexsha

            removed_files = []
            added_files = {}
            assert len(commit.parents) < 2 # Not support branched repository

            for p in commit.parents:
                for diff in p.diff(commit):

                    if(diff.a_blob):
                        if not diff.a_blob.name.endswith(".java"):
                            continue
                        if self.is_completed_parse(diff.a_blob):
                            removed_files.append(diff.a_blob.path)

                    if(diff.b_blob):
                        if not diff.b_blob.name.endswith(".java"):
                            continue
                        if self.is_completed_parse(diff.b_blob):
                            added_files[diff.b_blob.path] = diff.b_blob.hexsha

                print 'removed:', removed_files
                print 'added:', added_files 

                self.remove_files(index, removed_files)
                self.add_files(index, added_files)

            if len(index.diff(None, staged=True)):
                print 'committing...'
                index.commit(commit.hexsha)

    def parse_blob(self, blob):
        blob.data_stream.read()
        cmd = "java "
        cmd += "-cp " + self.kenja_jar
        cmd += self.kenja_parser_class
        cmd += self.kenja_outpu_dir + blob.hexsha

        p = Popen(cmd.split(' '), stdin=PIPE)
        p.stdin.write(blob.data_stream.read())
        return p

    def convert(self):
        print 'create paresr processes...'
        self.parse_all_java_files()
        
        print 'waiting parser processes'
        self.parser_executor.join()

        print 'create historage...'
        self.commit_all_syntax_trees()

if __name__ == '__main__':
    import argparse
 
    parser = argparse.ArgumentParser(description='Git Blob Parser')
    parser.add_argument('org_git_dir')
    parser.add_argument('new_git_repo_dir')
    parser.add_argument('syntax_trees_dir')

    args = parser.parse_args()
    
    git_dir = args.org_git_dir
    if not os.path.isdir(git_dir):
        print "%s is not a directory" % (git_dir)

    repo = Repo(git_dir)
    
    gbp = HistorageConverter(repo, args.new_git_repo_dir, args.syntax_trees_dir)
    gbp.convert()
