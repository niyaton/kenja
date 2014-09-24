# -*- coding: utf-8 -*-
from git import *
from kenja.historage import get_org_commit
from collections import deque

def get_reversed_topological_ordered_commits(repo, refs):
    revs = [ref.commit.hexsha for ref in refs]
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
            if parent.hexsha not in visited:
                children.append(parent.hexsha)

        if children:
            nodes.extend(children)
        else:
            nodes.pop()
            visited.add(node)
            post.append(node)

    return post

def get_all_commits(repo):
	note_rev = 'refs/notes/commits'
	visited = set([c.commit for c in repo.refs if c.path != note_rev])
	queue = deque([c.commit for c in repo.refs if c.path != note_rev])
	while queue:
		commit = queue.pop()
		for parent in commit.parents:
			if parent not in visited:
				queue.append(parent)
				visited.add(parent)
	return visited

def diff_commits(org_repo,base_repo):
	org_commit = get_reversed_topological_ordered_commits(org_repo,org_repo.refs)
	base_commit = get_all_commits(base_repo)
	org_id = set([str(c) for c in org_commit])
	base_id = set([str(c.repo.git.notes(['show',c.hexsha]))for c in base_commit])
	diff_id = org_id.difference(base_id)
	ret = []
	for c in org_commit:
		if str(c) in diff_id:
			ret.append(str(c))
	return ret

if __name__ == '__main__':
	org_repo = Repo("~/Desktop/test")
	base_repo = Repo("~/Desktop/historage/base_repo")
	print diff_commits(org_repo,base_repo)
#	commits = get_diff_commits(org_repo,base_repo)
#	commits = diff2(org_repo,base_repo)
#	print commits





