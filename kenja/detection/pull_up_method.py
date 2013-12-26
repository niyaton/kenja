from __future__ import absolute_import
from itertools import product, combinations
from git.objects import Blob
from collections import defaultdict
from kenja.historage import *

def get_extends(commit, org_file_name, class_name):
    extends_path = '/'.join([org_file_name, '[CN]', class_name, 'extend'])
    try:
        extend = commit.tree / extends_path
        assert isinstance(extend, Blob)
    except KeyError:
        return None

    return extend.data_stream.read().rstrip()

def detect_pull_up_method(historage):
    pull_up_method_information = []

    for commit in historage.iter_commits(historage.head):
        for p in commit.parents:
            #pull_up_method_information.extend(detect_pullup_method_from_commit(p, commit))
            pull_up_method_information.extend(detect_shingle_pullup_method(p, commit))

    return pull_up_method_information

class Method(object):
    def __init__(self, blob, commit):
        self.blob = blob

        self.package_name = get_package(blob.path, commit)
        self.class_name = get_class(blob.path)
        self.method_name = get_method(blob.path)

    def get_full_name(self):
        if self.package_name:
            return '.'.join([self.package_name, self.class_name, self.method_name])
        else:
            return '.'.join([self.class_name, self.method_name])

    @classmethod
    def create_from_blob(cls, blob, commit):
        if is_method_body(blob.path):
            return cls(blob, commit)
        else:
            return None

    def __str__(self):
        return self.get_full_name()



def detect_shingle_pullup_method(old_commit, new_commit):
    result = []
    #pullup_method_candidates = default

    diff_index = old_commit.diff(new_commit, create_patch=False)

    #method_added_classes =
    added_methods = defaultdict(list)
    delted_methods = defaultdict(lambda : defaultdict(list))
    for diff in diff_index.iter_change_type('A'):
        new_blob_path = diff.b_blob.path
        new_method = Method.create_from_blob(diff.b_blob, new_commit)
        if new_method:
            added_methods[new_method.class_name].append(new_method)

    for diff in diff_index.iter_change_type('D'):
        deleted_blob_path = diff.a_blob.path
        if is_method_body(deleted_blob_path):
            c = get_class(deleted_blob_path)
            split_path =deleted_blob_path.split('/')
            extend = get_extends(new_commit, split_path[0], c)
            if not extend:
                continue

            extend = extend.rstrip()
            if extend in added_methods.keys():
                #print extend
                delted_methods[extend][c].append(get_method(deleted_blob_path))

    for super_class, v in delted_methods.iteritems():
        if super_class not in added_methods:
            print '%s does\'nt have a deleted method' % (super_class)
            continue
        for dst_method in added_methods[super_class]:
            for src_class in v.keys():
                for src_method in v[src_class]:
                    print '[from] %s [to] %s' % (src_method, dst_method)
    return result

def detect_pullup_method_from_commit(old_commit, new_commit):
    result = []
    #pullup_method_candidates = default

    diff_index = old_commit.diff(new_commit, create_patch=False)

    #method_added_classes =
    added_methods = defaultdict(list)
    delted_methods = defaultdict(lambda : defaultdict(list))
    for diff in diff_index.iter_change_type('A'):
        if is_method_body(diff.b_blob.path):
            c = get_class(diff.b_blob.path)
            added_methods[c].append(get_method(diff.b_blob.path))

    for diff in diff_index.iter_change_type('D'):
        if is_method_body(diff.a_blob.path):
            c = get_class(diff.a_blob.path)
            split_path =diff.a_blob.path.split('/')
            extend = get_extends(new_commit, split_path[0], c)
            if not extend:
                continue

            extend = extend.rstrip()
            if extend in added_methods.keys():
                #print extend
                delted_methods[extend][c].append(get_method(diff.a_blob.path))

    for k, v in delted_methods.items():
        pull_up_target = k
        #method_deleted_classes = set()
        #for c, m in v.items():
        #    method_deleted_classes.add(c)
        if len(v.keys()) > 2:
            print old_commit, new_commit, pull_up_target, v
            print '[keys]:', v.keys()
            for p in combinations(v.keys(), 2):
                print p
                for p2 in product(v[p[0]], v[p[1]]):
                    print p, p2




    return result



