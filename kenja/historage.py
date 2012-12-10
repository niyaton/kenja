from git import Repo

if __name__ == '__main__':
    historage = Repo('~/kenja_test/columba/command_test/1212101432/base_repo')
    for commit in historage.iter_commits(historage.head):
        for p in commit.parents:
            method_added = False
            for diff in p.diff(commit):
                #if diff.a_blob and diff.a_blob.path.find('[MT]'):
                #    print diff.a_blob.path
                if diff.b_blob and diff.b_blob.path.find('[MT]'):
                    method_added = True

            if method_added:
                print commit.hexsha
