from git import Repo

class GitDistiller:
    def __init__(self, git_dir):
        pass
        self.org_repo = Repo(git_dir)

    def clone_repo(self, new_repo_path):
        self.new_repo = self.org_repo.clone(new_repo_path)

    def distille(self, new_repo_path, extensions):
        self.clone_repo(new_repo_path)
        git = self.new_repo.git
        cmd = ['tree-filter', ','.join(self.create_remove_command(extensions))]
        git.filter_branch(cmd)

    def create_remove_command(self, extensions):
        assert len(extensions) > 0
        cmd = ['find']
        first_extension = extensions.pop(0)
        cmd.extend(['-name', '*.%s' % (first_extension)])
        for extension in extensions:
            cmd.extend(['-name', '*.%s' % (extension)])
        cmd.extend(['-type', 'd'])
        print cmd
        return cmd
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

