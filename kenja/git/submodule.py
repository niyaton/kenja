from git.repo import Repo
from itertools import izip
from itertools import count
from git.objects import Commit
from ConfigParser import RawConfigParser
from kenja.git.util import write_blob, mktree_from_iter
from gitdb.util import (hex_to_bin,
                        bin_to_hex
                        )
from tempfile import NamedTemporaryFile


def write_submodule_config(f, name, path, url):
    config = RawConfigParser()
    section = 'submodule "%s"' % (name)
    config.add_section(section)
    config.set(section, 'path', path)
    config.set(section, 'url', url)

    config.write(f)


def store_submodule_config(odb, name, path, url):
    with NamedTemporaryFile() as f:
        write_submodule_config(f, name, path, url)
        f.flush()
        return write_blob(odb, f.name)


def get_submodule_tree_content(commit_hexsha, name):
    submodule_mode = '160000'
    return (submodule_mode, hex_to_bin(commit_hexsha), name)


def create_submodule_tree(odb, submodule_commit_hexsha):
    submodule_conf = '/Users/kenjif/test_gitmodules'
    conf_mode, conf_binsha = write_blob(odb, submodule_conf)
    tree_contents = []
    tree_contents.append((conf_mode, conf_binsha, '.gitmodules'))
    tree_contents.append(get_submodule_tree_content(submodule_commit_hexsha, 'jEdit'))

    tree_mode, binsha = mktree_from_iter(odb, tree_contents)
    return bin_to_hex(binsha)

if __name__ == '__main__':
    from kenja.git.util import get_reversed_topological_ordered_commits
    repo = Repo('/Users/kenjif/msr_repos/git/jEdit')

    commits = get_reversed_topological_ordered_commits(repo, repo.refs)

    new_repo = Repo.init('/Users/kenjif/test_git_repo')

    with open('/Users/kenjif/test_gitmodules', 'wb') as f:
        name = 'jEdit'
        path = 'jEdit'
        url = '/Users/kenjif/msr_repos/git/jEdit'
        write_submodule_config(f, name, path, url)

    committed = {}
    tags = {}
    heads = {}
    for tag_ref in repo.tags:
        tags[tag_ref.commit.hexsha] = tag_ref.name

    for head in repo.heads:
        heads[head.commit.hexsha] = head.name

    for commit_hexsha, num in izip(commits, count()):
        print num, commit_hexsha
        git = new_repo.git
        commit = repo.commit(commit_hexsha)

        parents = []
        for parent in commit.parents:
            parents.append(committed[parent.hexsha])

        message = '[%s] from %s' % (num, commit_hexsha)
        new_tree = create_submodule_tree(new_repo.odb, commit_hexsha)
        new_commit = Commit.create_from_tree(new_repo, new_tree, message, parents)
        if commit_hexsha in tags:
            new_repo.create_tag(tags[commit_hexsha], ref=new_commit)
        if commit_hexsha in heads:
            new_repo.create_head(heads[commit_hexsha], commit=new_commit)
        committed[commit_hexsha] = new_commit
