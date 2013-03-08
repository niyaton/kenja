from git import Repo
from pygraph.classes.digraph import digraph
from pygraph.algorithms.sorting import topological_sorting
from itertools import izip
from itertools import count
from git import Commit
import tempfile

repo = Repo('/Users/kenjif/msr_repos/git/jEdit')

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

commits = get_topological_ordered_commits(repo, repo.refs)
commits.reverse()

new_repo = Repo.init('/Users/kenjif/test_git_repo')

kwargs = {}
#submodule = new_repo.create_submodule('old', 'old', url=repo.git_dir)

submodule_mode = '160000'

committed = {}
tags = {}
for tag_ref in repo.tags:
    tags[tag_ref.commit.hexsha] = tag_ref.name
for commit_hexsha, num in izip(commits, count()):
    print num, commit_hexsha
    git = new_repo.git
    commit = repo.commit(commit_hexsha)
    tree = repo.tree(commit_hexsha)

    parents = []
    for parent in commit.parents:
        parents.append(committed[parent.hexsha])

    message = '[%s] from %s' % (num, commit_hexsha)
    new_commit = Commit.create_from_tree(new_repo, tree, message, parents)
    if commit_hexsha in tags:
        new_repo.create_tag(tags[commit_hexsha], ref=new_commit)
    committed[commit_hexsha] = new_commit
