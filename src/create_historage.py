import os
from git import Repo
#from git.repo.fun import is_git_dir
from exc import InvalidHistoragePathException
from subprocess import (
                            Popen,
                            PIPE
                        )
from multiprocessing import Pool
import multiprocessing
import shutil

def func_star(a_b):
    return work(*a_b)

kenja_jar = "../target/kenja-0.0.1-SNAPSHOT-jar-with-dependencies.jar" 
kenja_outpu_dir = " ./syntax_trees/"
kenja_parser_class = " jp.naist.sd.kenja.factextractor.ASTGitTreeCreator"

def work(blob, hexsha):
    cmd = "java "
    cmd += "-cp " + kenja_jar
    cmd += kenja_parser_class
    #cmd += kenja_outpu_dir + blob.hexsha
    cmd += kenja_outpu_dir + hexsha
    
    p = Popen(cmd.split(' '), stdin=PIPE)
    #p.stdin.write(blob.data_stream.read())
    p.stdin.write(blob)
    p.communicate()
    return True

class HistorageConverter:
    kenja_jar = "../target/kenja-0.0.1-SNAPSHOT-jar-with-dependencies.jar" 
    kenja_outpu_dir = " ./syntax_trees/"
    kenja_parser_class = " jp.naist.sd.kenja.factextractor.ASTGitTreeCreator"
    
    def __init__(self, org_git_repo, new_git_repo_dir_path, working_dir):
        dirname = os.path.basename(new_git_repo_dir_path)
        if(dirname == '.git'):
            raise InvalidHistoragePathException('Do not use ".git" dir for historage path')

        if os.path.exists(new_git_repo_dir_path):
            raise InvalidHistoragePathException('%s is already exists. Historage converter will be create new directory and git repository automatically' % (new_git_repo_dir_path))

        #    abspath = os.path.abspath(new_git_repo_dir_path)
        #    
        #    if not(os.path.isdir(new_git_repo_dir_path)):
        #        raise InvalidHistoragePathException('%s is not a directory' % (new_git_repo_dir_path))

        #    git_dir = os.path.join(new_git_repo_dir_path + '.git')
        #    if is_git_dir(git_dir):
        #        raise InvalidHistoragePathException('You already have git repository in %s' % (abspath))
        #    elif os.path.exists(git_dir):
        #        raise InvalidHistoragePathException('%s is already exists but not a git repository' % (git_dir))

        self.historage_repo = Repo.init(new_git_repo_dir_path)
        self.org_repo = org_git_repo

        if not(os.path.isdir(working_dir)):
            raise Exception('%s is not a directory' % (working_dir))
        self.working_dir = working_dir

    def get_all_blob_hashes(self):
        #blob_hashes = set()
        #blobs = set()
        blobs = list()
        for commit in self.org_repo.iter_commits(self.org_repo.head):
            for p in commit.parents:
                diff = p.diff(commit)
                for change in diff.iter_change_type("M"):
                    if change.b_blob.name.endswith(".java"):
                        #blob_hashes.add(change.b_blob.hexsha)
                        #blobs.add([change.b_blob.data_stream.read(), change.b_blob.hexsha])
                        blobs.append([change.b_blob.data_stream.read(), change.b_blob.hexsha])
                        #blobs.add(change.b_blob)
                for change in diff.iter_change_type("A"):
                    if change.b_blob.name.endswith(".java"):
                        #blob_hashes.add(change.b_blob.hexsha)
                        blobs.append([change.b_blob.data_stream.read(), change.b_blob.hexsha])
                        #blobs.add(change.b_blob)

        #return blob_hashes
        return blobs

    def commit_all_syntax_trees(self):
        index = self.historage_repo.index
        working_dir_abspath = self.historage_repo.working_dir
        syntax_trees_path = os.path.join(self.working_dir, 'syntax_trees')
        arg = {'reverse':True}
        for commit in self.org_repo.iter_commits(self.org_repo.head, **arg):
            print 'process commit:', commit.hexsha
            for p in commit.parents:
                diff = p.diff(commit)
                for change in diff.iter_change_type("D"):
                    if change.a_blob.name.endswith(".java"):
                        #hexsha = change.a_blob.hexsha
                        print 'remove', change.a_blob.path
                        #dirname = os.path.dirname(change.a_blob.path)
                        dirname = change.a_blob.path
                        kwargs = {"r":True}
                        index.remove([change.a_blob.path], **kwargs)
                        index.write()
                        shutil.rmtree(os.path.join(working_dir_abspath, dirname))
                for change in diff.iter_change_type("M"):
                    if change.b_blob.name.endswith(".java"):
                        print 'remove changed', change.a_blob.path
                        #dirname = os.path.dirname(change.a_blob.path)
                        dirname = change.a_blob.path
                        kwargs = {"r":True}
                        index.remove([change.a_blob.path], **kwargs)
                        index.write()
                        shutil.rmtree(os.path.join(working_dir_abspath, dirname))

                        print 'add change', change.b_blob.path
                        dirname = os.path.dirname(change.b_blob.path)

                        new_dir = os.path.join(working_dir_abspath, dirname)
                        if not os.path.exists(new_dir):
                            os.makedirs(os.path.join(working_dir_abspath, dirname))
                            
                        hexsha = change.b_blob.hexsha
                        src = os.path.join(syntax_trees_path, hexsha)
                        #dst = os.path.join(working_dir_abspath, dirname)
                        dst = os.path.join(working_dir_abspath, change.b_blob.path)
                        print 'copy from %s to %s' % (src, dst)
                        shutil.copytree(src, dst)

                        self.historage_repo.git.add([change.b_blob.path])
                        index.update()

                for change in diff.iter_change_type("A"):
                    if change.b_blob.name.endswith(".java"):
                        print 'add new', change.b_blob.path
                        dirname = os.path.dirname(change.b_blob.path)

                        new_dir = os.path.join(working_dir_abspath, dirname)
                        if not os.path.exists(new_dir):
                            os.makedirs(os.path.join(working_dir_abspath, dirname))

                        hexsha = change.b_blob.hexsha
                        src = os.path.join(syntax_trees_path, hexsha)
                        dst = os.path.join(working_dir_abspath, change.b_blob.path)
                        print 'copy from %s to %s' % (src, dst)
                        shutil.copytree(src, dst)
                        
                        self.historage_repo.git.add([change.b_blob.path])
                        index.update()
            #if self.historage_repo.is_dirty():
            #    index.commit(commit.hexsha)
            if len(index.diff(None, staged=True)):
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
        print 'get all blobs...'
        self.blobs = self.get_all_blob_hashes()
        
        print 'parse all blobs...'
        #pool = Pool(multiprocessing.cpu_count())
        #pool.map(func_star, self.blobs)

        print 'commiting...'
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
