from __future__ import absolute_import
from git.repo import Repo
from git.objects import (Commit, Tree)
from git.objects.util import altz_to_utctz_str
from git.util import Actor
import io
import os
import sys
from gitdb import IStream
from gitdb.util import bin_to_hex
from StringIO import StringIO

blob_mode = '100644'
tree_mode = '040000'

def tree_item_str(mode, file_name, binsha):
    if mode[0] == 0:
        mode = mode[1:]
    return '%s %s\0%s' % (mode, file_name, binsha)

def write_blob(odb, src_path):
    assert os.path.isfile(src_path) and not os.path.islink(src_path)
    istream = IStream("blob", os.path.getsize(src_path), io.open(src_path))
    odb.store(istream)
    return (blob_mode, istream.binsha)

def write_blob_from_file(odb, f, line_size):
    if line_size == 0:
        blob_body = ''
    else:
        lines = [ f.readline() for i in range(line_size) ]
        blob_body = ''.join(lines)

    istream = IStream("blob", len(blob_body), StringIO(blob_body))
    odb.store(istream)

    return (blob_mode, istream.binsha)

def write_syntax_tree_from_file(odb, src_path):
    if not os.path.isfile(src_path):
        raise Exception

    f = open(src_path)
    line = f.readline()
    trees = [[]]
    while line:
        header, info = line[0:4], line[5:].rstrip()
        if header == '[BN]':
            # Blob entry format is following:
            # [BN] blob_name
            blob_name = info
            line = f.readline()
            header, info = line[0:4], line[5:].rstrip()
            assert header == '[BI]'
            (mode, binsha) = write_blob_from_file(odb, f, int(info))
            trees[-1].append((mode, binsha, blob_name))
        elif header == '[TS]':
            # Contents of tree start from [TS].
            # [TS] tree_name
            trees.append([])
        elif header == '[TE]':
            # Contents of tree end by [TE].
            # [TE] tree_name
            tree_name = info
            (mode, binsha) = mktree_from_iter(odb, trees.pop())
            trees[-1].append((mode, binsha, tree_name))

        line = f.readline()

    (mode, binsha) = mktree_from_iter(odb, trees.pop())
    return (mode, binsha)

def write_tree(odb, src_path):
    assert os.path.isdir(src_path) and not os.path.islink(src_path)

    items = []
    for file in sorted(os.listdir(src_path)):
        (mode, binsha) = write_path(odb, os.path.join(src_path, file))

        items.append(tree_item_str(mode, file, binsha))

    items_str = ''.join(items)
    istream = IStream("tree", len(items_str), StringIO(items_str))
    odb.store(istream)
    return (tree_mode, istream.binsha)

def write_path(odb, src_path):
    if os.path.isfile(src_path):
        return write_blob(odb, src_path)
    elif os.path.isdir(src_path):
        return write_tree(odb, src_path)

    raise Exception

def write_paths(odb, paths, names):
    items = []
    for (path, name) in zip(paths, names):
        (mode, binsha) = write_path(odb, path)

        items.append(tree_item_str(mode, name, binsha))

    items_str = ''.join(items)
    istream = IStream("tree", len(items_str), StringIO(items_str))
    odb.store(istream)
    return (tree_mode, istream.binsha)

def mktree(odb, modes, binshas, names):
    items = [tree_item_str(mode, name, binsha) for mode, binsha, name in zip(modes, binshas, names)]
    items_str = ''.join(items)

    istream = IStream("tree", len(items_str), StringIO(items_str))
    odb.store(istream)
    return (tree_mode, istream.binsha)

def mktree_from_iter(odb, object_info_iter):
    items = [tree_item_str(mode, name, binsha) for mode, binsha, name in object_info_iter]
    items_str = ''.join(items)

    istream = IStream("tree", len(items_str), StringIO(items_str))
    odb.store(istream)
    return (tree_mode, istream.binsha)

def commit_from_binsha(repo, binsha, org_commit, parents=None):
    env = os.environ

    author_date = "%d %s" % (org_commit.authored_date, altz_to_utctz_str(org_commit.author_tz_offset))
    env[Commit.env_author_date] = author_date

    committer_date = "%d %s" % (org_commit.committed_date, altz_to_utctz_str(org_commit.committer_tz_offset))
    env[Commit.env_committer_date] = committer_date

    env[Actor.env_author_name] = org_commit.author.name.encode(org_commit.encoding)
    if org_commit.author.email is None:
        env[Actor.env_author_email] = ""
    else:
        env[Actor.env_author_email] = org_commit.author.email

    env[Actor.env_committer_name] = org_commit.committer.name.encode(org_commit.encoding)
    if org_commit.committer.email is None:
        env[Actor.env_committer_email] = ""
    else:
        env[Actor.env_committer_email] = org_commit.committer.email

    message = org_commit.message.encode(org_commit.encoding)

    tree = Tree.new(repo, bin_to_hex(binsha))

    return Commit.create_from_tree(repo, tree, message, parents, True)

def create_note(repo, message):
    kwargs = ['add', '-f', '-m', message]
    repo.git.notes(kwargs)

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

if __name__ == '__main__':
    repo = Repo.init('test_git')
    #(mode, binsha) = write_tree(repo.odb, 'temp')

    #(mode, binsha) = write_tree(repo.odb, 'temp/00')
    #(mode, binsha) = write_tree(repo.odb, 'temp/01')

    paths = ['temp/00', 'temp/01']
    names = ['a', 'b']

    (mode, binsha) = write_paths(repo.odb, paths, names)

    tree = Tree.new(repo, bin_to_hex(binsha))
    c = Commit.create_from_tree(repo, tree, 'test commit', None, True)
