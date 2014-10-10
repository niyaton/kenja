from git import Repo


def check_duplicate_entry(path):
    repo = Repo(path)

    visited_commit = set()
    visited_tree = set()
    for ref in repo.refs:
        for commit in repo.iter_commits(ref):
            if commit.hexsha in visited_commit:
                continue
            trees = [commit.tree]
            while trees:
                current_tree = trees.pop(0)
                if current_tree.hexsha in visited_tree:
                    continue
                trees.extend(current_tree.trees)

                blob_names = set()
                for blob in current_tree.blobs:
                    blob_names.add(blob.name)

                s = set()
                duplicated_blobs = [b.name for b in current_tree.blobs if b.name in s or s.add(b.name)]

                assert len(blob_names) == len(current_tree.blobs), duplicated_blobs

                tree_names = set()
                for tree in current_tree.trees:
                    tree_names.add(tree.name)

                s = set()
                duplicated_trees = [t.name for t in current_tree.trees if t.name in s or s.add(t.name)]

                assert len(tree_names) == len(current_tree.trees), duplicated_trees

                visited_tree.add(current_tree.hexsha)

            visited_commit.add(commit.hexsha)
    print("OK!")


def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: {0} path_of_git_repo".format(sys.argv[0]))
        exit()

    check_duplicate_entry(sys.argv[1])


if __name__ == '__main__':
    main()
