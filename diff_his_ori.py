# -*- coding: utf-8 -*-
from git import *
from kenja.historage import get_org_commit
from collections import deque

def get_all_commits(repo):
	note_rev = 'refs/notes/commits'
	commit_set = set([c.commit for c in repo.refs if c.path != note_rev])
	queue = deque([c.commit for c in repo.refs if c.path != note_rev])
	while queue:
		commit = queue.pop()
		for parent in commit.parents:
			if parent not in commit_set:
				queue.append(parent)
				commit_set.add(parent)
	return commit_set

def get_diff_commits(org_repo,base_repo):
	commit_set = [str(c) for c in get_all_commits(org_repo)]
	for commit in get_all_commits(base_repo):
		commit = str(commit.repo.git.notes(['show', commit.hexsha]))
		if commit in commit_set:
			commit_set.remove(commit)
	return commit_set

if __name__ == '__main__':
	org_repo = Repo("~/Desktop/test")
	base_repo = Repo("~/Desktop/historage/base_repo")
#	get_all_commits(org_repo)
#	get_all_commits(base_repo)
	print get_diff_commits(org_repo,base_repo)
#	commits = get_diff_commits(org_repo,base_repo)
#	commits = diff2(org_repo,base_repo)
#	print commits





