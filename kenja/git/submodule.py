from git.repo import Repo
from itertools import izip
from itertools import count
from git.objects import Commit
from ConfigParser import RawConfigParser
from kenja.git.util import write_blob_from_path, mktree_from_iter
from gitdb.util import (hex_to_bin,
                        bin_to_hex
                        )
from tempfile import NamedTemporaryFile


def write_submodule_config(f, name, path, url):
    config = RawConfigParser()
    section = 'submodule "%s"' % (name)
    config.add_section(section)
    config.set(section, 'path', path)
    config.set(section, 'url', url)

    config.write(f)


def store_submodule_config(odb, name, path, url):
    with NamedTemporaryFile() as f:
        write_submodule_config(f, name, path, url)
        f.flush()
        return write_blob_from_path(odb, f.name)


def get_submodule_tree_content(commit_hexsha, name):
    submodule_mode = '160000'
    return (submodule_mode, hex_to_bin(commit_hexsha), name)


def create_submodule_tree(odb, submodule_commit_hexsha):
    submodule_conf = '/Users/kenjif/test_gitmodules'
    conf_mode, conf_binsha = write_blob_from_path(odb, submodule_conf)
    tree_contents = []
    tree_contents.append((conf_mode, conf_binsha, '.gitmodules'))
    tree_contents.append(get_submodule_tree_content(submodule_commit_hexsha, 'jEdit'))

    tree_mode, binsha = mktree_from_iter(odb, tree_contents)
    return bin_to_hex(binsha)
