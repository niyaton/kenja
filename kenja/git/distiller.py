from __future__ import absolute_import
from git import Repo
import os


class GitDistiller:
    def __init__(self, git_dir):
        pass
        self.org_repo = Repo(git_dir)

    def clone_repo(self, new_repo_path):
        self.new_repo = self.org_repo.clone(new_repo_path)

    def distille(self, new_repo_path, extensions):
        new_repo_path = os.path.abspath(new_repo_path)
        self.clone_repo(new_repo_path)
        git = self.new_repo.git
        execcmd = self.create_remove_command_find(extensions)
        # execcmd = self.create_remove_command_xargs(extensions)
        cmd = ['--tree-filter', execcmd]

        git.filter_branch(cmd)

    def prune_empty(self):
        git = self.new_repo.git
        kwargs = {'f': True, 'prune-empty': True}
        git.filter_branch(**kwargs)

    def create_remove_command_find(self, extensions):
        assert len(extensions) > 0
        cmd = ['find', '.', '\\!', '\\(']
        first_extension = extensions.pop(0)
        cmd.extend(['-name', '\'*.%s\'' % (first_extension)])
        for extension in extensions:
            cmd.extend(['-o', '-name', '\'*.%s\'' % (extension)])
        cmd.extend(['-o', '-type', 'd'])
        cmd.append('\\)')
        cmd.extend(['-exec', 'rm', '{}', '\;'])

        return ' '.join(cmd)

    def create_remove_command_xargs(self, extensions):
        assert len(extensions) > 0
        cmd = ['find', '.', '\\!', '\\(']
        first_extension = extensions.pop(0)
        cmd.extend(['-name', '\'*.%s\'' % (first_extension)])
        for extension in extensions:
            cmd.extend(['-o', '-name', '\'*.%s\'' % (extension)])
        cmd.extend(['-o', '-type', 'd'])
        cmd.append('\\)')
        cmd.extend(['-print0', '|', 'xargs', '-0', 'rm'])
        print(cmd)
        return ' '.join(cmd)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Git Distiller')
    parser.add_argument('repo_dir',
                        help='path of repository dir')
    parser.add_argument('new_repo',
                        help='path of new repository')
    parser.add_argument('extension', nargs='*')
    parser.add_argument('--delete-no-extension')
    args = parser.parse_args()

    distiller = GitDistiller(args.repo_dir)
    distiller.distille(args.new_repo, args.extension)
