from __future__ import absolute_import
from git.repo import Repo
from git.objects import (Commit, Tree)
#from git import Tree
import io
import os
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
            trees[-1].append(mode, binsha, blob_name)
        elif header == '[TN]':
            # Tree entry format is following:
            # [TN] tree_name
            pass
        elif header == '[TS]':
            # Contents of tree start from [TS].
            # [TS] tree_name
            trees.append([])
        elif header == '[TE]':
            # Contents of tree end by [TE].
            # [TE] tree_name
            tree = trees.pop()
            tree_name = info
            (mode, binsha) = mktree_from_iter(odb, tree)
            trees[-1].append(mode, binsha, tree_name)

        line = f.readline()

    tree = trees.pop()
    (mode, binsha) = mktree_from_iter(odb, tree)
    return (mode, binsha)

def write_blob_from_file(odb, f, line_size):
    lines = []

    for i in range(line_size):
        lines.append(f.readline())

    blob_body = ''.join(lines) if line_size != 0 else ''
    istream = IStream("blob", len(blob_body), StringIO(blob_body))
    odb.store(istream)

    return (blob_mode, istream.binsha)

def write_path(odb, src_path):
    if os.path.isfile(src_path):
        return write_blob(odb, src_path)
    elif os.path.isdir(src_path):
        return write_tree(odb, src_path)

    raise Exception

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
    items = []
    for (mode, binsha, name) in zip(modes, binshas, names):
        items.append(tree_item_str(mode, name, binsha))


    items_str = ''.join(items)
    istream = IStream("tree", len(items_str), StringIO(items_str))
    odb.store(istream)
    return (tree_mode, istream.binsha)

def commit_from_binsha(repo, binsha, message, parents=None):
    tree = Tree.new(repo, bin_to_hex(binsha))
    return Commit.create_from_tree(repo, tree, message, parents, True)

def mktree_from_iter(odb, object_info_iter):
    items = []
    for (mode, binsha, name) in object_info_iter:
        items.append('%s %s\0%s' % (mode, name, binsha))

    items_str = ''.join(items)
    istream = IStream("tree", len(items_str), StringIO(items_str))
    odb.store(istream)
    return (tree_mode, istream.binsha)

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
