from git import Repo
from pygraph.classes.digraph import digraph
from pygraph.algorithms.sorting import topological_sorting
from itertools import izip
from itertools import count
from git import Commit
import tempfile
from ConfigParser import RawConfigParser
import gittools
from gitdb.util import (hex_to_bin,
                        bin_to_hex
                        )

def write_submodule_config(f, name, path ,url):
    config = RawConfigParser()
    section = 'submodule "%s"' % (name)
    config.add_section(section)
    config.set(section, 'path', path)
    config.set(section, 'url', url)

    config.write(f)

def get_topological_ordered_commits(repo, revs):
    dag = digraph()
    checked_nodes = set()
    for rev in revs:
        for commit in repo.iter_commits(rev):
            hexsha = commit.hexsha
            if not dag.has_node(hexsha):
                dag.add_node(hexsha)
            finished = True
            for parent in commit.parents:
                p_hexsha = parent.hexsha
                if not dag.has_node(p_hexsha):
                    dag.add_node(p_hexsha)
                edge = (hexsha, p_hexsha)
                if not dag.has_edge(edge):
                    dag.add_edge(edge)
                if not hexsha in checked_nodes:
                    finished = False
            checked_nodes.add(commit.hexsha)
            if finished:
                break
    return topological_sorting(dag)

def get_reversed_topological_ordered_commits(repo, revs):
    revs = [repo.commit(rev).hexsha for rev in revs]
    nodes = list(revs)
    visited = set()
    post = []
    while nodes:
        node = nodes[-1]
        if node in visited:
            nodes.pop()
            continue
        commit = repo.commit(node)

        children = []
        for parent in commit.parents:
            if not parent.hexsha in visited:
                children.append(parent.hexsha)

        if children:
            nodes.extend(children)
        else:
            nodes.pop()
            visited.add(node)
            post.append(node)

    return post

def create_submodule_tree(odb, submodule_commit_hexsha):
    submodule_mode = '160000'
    submodule_conf = '/Users/kenjif/test_gitmodules'
    conf_mode, conf_binsha = gittools.write_blob(odb, submodule_conf)
    tree_contents = []
    tree_contents.append((conf_mode, conf_binsha, '.gitmodules'))
    tree_contents.append((submodule_mode, hex_to_bin(submodule_commit_hexsha), 'jEdit'))

    tree_mode, binsha = gittools.mktree_from_iter(odb, tree_contents)
    return bin_to_hex(binsha)

if __name__ == '__main__':
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
