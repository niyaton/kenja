from __future__ import absolute_import
from git.objects import (Commit, Tree)
import io
import os
import git.refs
from gitdb import IStream
from gitdb.util import bin_to_hex
from git.objects.util import altz_to_utctz_str
from StringIO import StringIO
from collections import deque

blob_mode = '100644'
tree_mode = '40000'


def tree_item_str(mode, file_name, binsha):
    if mode[0] == 0:
        mode = mode[1:]
    return '{} {}\0{}'.format(mode, file_name, binsha)


def write_blob_from_path(odb, src_path):
    assert os.path.isfile(src_path) and not os.path.islink(src_path)
    istream = IStream("blob", os.path.getsize(src_path), io.open(src_path))
    odb.store(istream)
    return (blob_mode, istream.binsha)


def write_blob_from_file(odb, f, line_size):
    if line_size == 0:
        blob_body = ''
    else:
        lines = [f.readline() for i in range(line_size)]
        blob_body = ''.join(lines)

    istream = IStream("blob", len(blob_body), StringIO(blob_body))
    odb.store(istream)

    return (blob_mode, istream.binsha)


def write_syntax_tree_from_file(odb, src_path):
    if not os.path.isfile(src_path):
        raise Exception('{} is not a file'.format(src_path))

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
        return write_blob_from_path(odb, src_path)
    elif os.path.isdir(src_path):
        return write_tree(odb, src_path)

    raise Exception('{} is not a valid file or directory'.format(src_path))


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
    tree = Tree.new(repo, bin_to_hex(binsha))

    env = os.environ

    offset = altz_to_utctz_str(org_commit.author_tz_offset)
    date = org_commit.authored_date
    env[Commit.env_author_date] = '{} {}'.format(date, offset)

    offset = altz_to_utctz_str(org_commit.committer_tz_offset)
    date = org_commit.committed_date
    env[Commit.env_committer_date] = '{} {}'.format(date, offset)

    return Commit.create_from_tree(repo, tree, org_commit.message, parents,
                                   head=True,
                                   author=org_commit.author,
                                   committer=org_commit.committer)


def create_note(repo, message):
    kwargs = ['add', '-f', '-m', message]
    repo.git.notes(kwargs)


def get_reversed_topological_ordered_commits(repo, refs):
    revs = [repo.commit(ref) for ref in refs]
    nodes = deque(revs)
    visited_hexsha = set()
    visited_commits = []
    while nodes:
        node = nodes.pop()
        if node.hexsha in visited_hexsha:
            continue

        children = [parent for parent in node.parents if parent.hexsha not in visited_hexsha]

        if children:
            nodes.append(node)
            nodes.extend(children)
        else:
            visited_hexsha.add(node.hexsha)
            visited_commits.append(node)

    return visited_commits
