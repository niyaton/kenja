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

repo = Repo('/Users/kenjif/msr_repos/git/jEdit')

def write_submodule_config(f):
    config = RawConfigParser()
    section = 'submodule "%s"' % ('jEdit')
    config.add_section(section)
    config.set(section, 'path', 'jEdit')
    config.set(section, 'url', '/Users/kenjif/msr_repos/git/jEdit')

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

if __name__ == '__main__':
    commits = get_topological_ordered_commits(repo, repo.refs)
    commits.reverse()

    new_repo = Repo.init('/Users/kenjif/test_git_repo')

    submodule_mode = '160000'
    with open('/Users/kenjif/test_gitmodules', 'wb') as f:
        write_submodule_config(f)

    def create_submodule_tree(odb, submodule_commit_hexsha):
        submodule_conf = '/Users/kenjif/test_gitmodules'
        conf_mode, conf_binsha = gittools.write_blob(odb, submodule_conf)
        tree_contents = []
        tree_contents.append((conf_mode, conf_binsha, '.gitmodules'))
        tree_contents.append((submodule_mode, hex_to_bin(submodule_commit_hexsha), 'jEdit'))

        tree_mode, binsha = gittools.mktree_from_iter(odb, tree_contents)
        return bin_to_hex(binsha)

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
        #new_commit = Commit.create_from_tree(new_repo, tree, message, parents)
        new_commit = Commit.create_from_tree(new_repo, new_tree, message, parents)
        if commit_hexsha in tags:
            new_repo.create_tag(tags[commit_hexsha], ref=new_commit)
        if commit_hexsha in heads:
            new_repo.create_head(heads[commit_hexsha], commit=new_commit)
        committed[commit_hexsha] = new_commit
