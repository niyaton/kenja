# -*- coding: utf-8 -*-
from git import *
from kenja.git.util import get_reversed_topological_ordered_commits
from kenja.historage import get_org_commit

def diff(org_path,base_path,branch):
	org_repo = Repo(org_path)
	base_repo = Repo(base_path)
	commit_set = set()
	for commit in org_repo.iter_commits(branch):
		commit_set.add(str(commit))
	for item in base_repo.iter_commits(branch):
		commit = str(get_org_commit(item))
		if commit in commit_set:
			commit_set.remove(commit)
	return commit_set

def diff2(org_path,base_path):
	org_repo = Repo(org_path)
	base_repo = Repo(base_path)
	commit_set = set()
	for commit in get_reversed_topological_ordered_commits(org_repo, org_repo.refs):
		commit_set.add(commit)
	for commit in get_reversed_topological_ordered_commits(base_repo, base_repo.refs[0:-1]):
		commit=base_repo.commit(commit)
		org_commit = str(get_org_commit(commit))
		if org_commit in commit_set:
			commit_set.remove(org_commit)
	return commit_set

if __name__ == '__main__':
	name_set = diff(base_path="./historage/base_repo",org_path="./test",branch="master")
	for name in name_set:
		print name
	name_set = diff2(base_path="./historage/base_repo",org_path="./test")
	for name in name_set:
		print name





