from __future__ import absolute_import
import os
from gitdb.util import bin_to_hex
from git.objects.fun import tree_entries_from_data


def is_method_body(path):
    if os.path.basename(path) != 'body':
        return False
    dirname = os.path.basename(os.path.dirname(os.path.dirname(path)))
    return dirname == '[MT]'


def is_method_parameters(path):
    if os.path.basename(path) != 'parameters':
        return False
    dirname = os.path.basename(os.path.dirname(os.path.dirname(path)))
    return dirname == '[MT]'


def get_class(path):
    split_path = path.split('/')
    cn_index = split_path.index('[CN]')
    assert cn_index + 1 <= len(split_path)
    return split_path[cn_index + 1]


def get_method(path):
    split_path = path.split('/')
    mt_index = split_path.index('[MT]')
    assert mt_index + 1 <= len(split_path)
    return split_path[mt_index + 1]


def get_org_commit(commit):
    tree_entries = tree_entries_from_data(commit.tree.data_stream.read())
    for binsha, mode, name in tree_entries:
        if name == 'org_repo':
            return bin_to_hex(binsha)
    return None


def get_package(path, commit):
    split_path = path.split('/')
    path = os.path.join(split_path[0], 'package')
    try:
        package_blob = commit.tree / path
    except KeyError:
        return None
    return package_blob.data_stream.read()
