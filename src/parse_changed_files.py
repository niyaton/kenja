from git import Repo
import os
from subprocess import Popen
from subprocess import PIPE

class GitBlobParser:
    kenja_jar = "../target/kenja-0.0.1-SNAPSHOT-jar-with-dependencies.jar" 
    kenja_outpu_dir = " ./syntax_trees/"
    kenja_parser_class = " jp.naist.sd.kenja.factextractor.ASTGitTreeCreator"

    def __init__(self, repo):
        self.repo = repo
        self.subprocesses = {}

    def parse_blob(self, blob):
        blob.data_stream.read()
        cmd = "java "
        cmd += "-cp " + self.kenja_jar
        cmd += self.kenja_parser_class
        cmd += self.kenja_outpu_dir + blob.hexsha

        p = Popen(cmd.split(' '), stdin=PIPE)
        p.stdin.write(blob.data_stream.read())


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Git Blob Parser')
    parser.add_argument('org_git_dir')

    args = parser.parse_args()
    
    git_dir = args.org_git_dir
    if not os.path.isdir(git_dir):
        print "%s is not a directory" % (git_dir)

    repo = Repo(git_dir)
    
    gbp = GitBlobParser(repo)
    gbp.print_all_blob_hashes()
