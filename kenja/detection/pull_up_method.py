from __future__ import absolute_import
from itertools import product, combinations
from git.objects import Blob
from collections import defaultdict
from kenja.historage import *
from kenja.shingles import calculate_similarity

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

    def get_parameter_types(self):
        index = self.method_name.index('(')
        return self.method_name[index:-1].split(',')

    @classmethod
    def create_from_blob(cls, blob, commit):
        if is_method_body(blob.path):
            return cls(blob, commit)
        else:
            return None

    def get_body(self):
        return self.blob.data_stream.read()

    def __str__(self):
        return self.get_full_name()


class SubclassMethod(Method):
    def __init__(self, blob, commit):
        super(SubclassMethod, self).__init__(blob, commit)

        split_path = blob.path.split('/')
        self.extend = get_extends(commit, split_path[0], self.class_name)

def match_type(a_method, b_method):
    a_types = a_method.get_parameter_types()
    b_types = b_method.get_parameter_types()
    return a_types == b_types

def detect_shingle_pullup_method(old_commit, new_commit):
    diff_index = old_commit.diff(new_commit, create_patch=False)

    added_methods = defaultdict(list)
    delted_methods = defaultdict(lambda : defaultdict(list))
    for diff in diff_index.iter_change_type('A'):
        new_blob_path = diff.b_blob.path
        new_method = Method.create_from_blob(diff.b_blob, new_commit)
        if new_method:
            added_methods[new_method.class_name].append(new_method)

    for diff in diff_index.iter_change_type('D'):
        subclass_method = SubclassMethod.create_from_blob(diff.a_blob, old_commit)

        if subclass_method:
            if not subclass_method.extend:
                continue

            if subclass_method.extend in added_methods.keys():
                delted_methods[subclass_method.extend][subclass_method.class_name].append(subclass_method)

    pull_up_method_candidates = []
    for super_class, v in delted_methods.iteritems():
        if super_class not in added_methods:
            print '%s does\'nt have a deleted method' % (super_class)
            continue
        for dst_method in added_methods[super_class]:
            for src_class in v.keys():
                for src_method in v[src_class]:
                    src_body = src_method.get_body()
                    dst_body = dst_method.get_body()

                    is_same_parameters = match_type(src_method, dst_method)
                    if dst_body:
                        dst_body = '\n'.join(dst_body.split('\n')[1:-2])
                        if src_body:
                            src_body = '\n'.join(src_body.split('\n')[1:-2])

                        if src_body or dst_body:
                            sim = calculate_similarity(src_body, dst_body)
                        else:
                            sim = 0
                        pull_up_method_candidates.append((old_commit.hexsha, new_commit.hexsha, str(src_method), str(dst_method), sim, is_same_parameters))

    return pull_up_method_candidates

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



