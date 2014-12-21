from __future__ import absolute_import
import os


def get_refs(historage):
    for ref in historage.refs:
        if not ref.path.startswith('refs/notes/'):
            yield ref


def is_method_body(path):
    if os.path.basename(path) != 'body':
        return False
    dirname = os.path.basename(os.path.dirname(os.path.dirname(path)))
    return dirname == '[MT]'


def is_constructor_body(path):
    if os.path.basename(path) != 'body':
        return False
    dirname = os.path.basename(os.path.dirname(os.path.dirname(path)))
    return dirname == '[CS]'


def is_method_parameters(path):
    if os.path.basename(path) != 'parameters':
        return False
    dirname = os.path.basename(os.path.dirname(os.path.dirname(path)))
    return dirname == '[MT]'


def is_constructor_parameters(path):
    if os.path.basename(path) != 'parameters':
        return False
    dirname = os.path.basename(os.path.dirname(os.path.dirname(path)))
    return dirname == '[CS]'


def get_class(path):
    split_path = path.split('/')
    split_path.reverse()
    cn_index = split_path.index('[CN]')
    assert cn_index - 1 <= len(split_path)
    return split_path[cn_index - 1]


def get_method(path):
    split_path = path.split('/')
    mt_index = split_path.index('[MT]')
    assert mt_index + 1 <= len(split_path)
    return split_path[mt_index + 1]


def get_constructor(path):
    split_path = path.split('/')
    mt_index = split_path.index('[CS]')
    assert mt_index + 1 <= len(split_path)
    return split_path[mt_index + 1]


def get_org_commit(commit):
    return commit.repo.git.notes(['show', commit.hexsha])


def get_package(path, commit):
    split_path = path.split('/')
    path = os.path.join(split_path[0], 'package')
    try:
        package_blob = commit.tree / path
    except KeyError:
        return None
    return package_blob.data_stream.read()
