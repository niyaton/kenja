from __future__ import absolute_import
from itertools import product, combinations
from git.objects import Blob
from collections import defaultdict
from kenja.historage import *
from kenja.shingles import calculate_similarity


def get_extends(commit, org_file_name, classes):
    classes_path = '/[CN]/'.join(classes)
    extends_path = '/'.join([org_file_name, '[CN]', classes_path, 'extend'])
    try:
        extend = commit.tree / extends_path
        assert isinstance(extend, Blob)
    except KeyError:
        return None

    return extend.data_stream.read().rstrip()


def exist_class(blob, commit):
    split_path = blob.path.split('/')
    while split_path[-2] != '[CN]':
        split_path.pop()
    class_path = '/'.join(split_path)

    try:
        commit.tree / class_path
    except KeyError:
        return False
    return True


def detect_pull_up_method(historage):
    pull_up_method_information = []

    checked_commit = set()
    detection_stack = []
    for ref in get_refs(historage):
        ref_commit = historage.commit(ref)
        detection_stack.append(ref_commit)
        while detection_stack:
            commit = detection_stack.pop()
            if commit.hexsha in checked_commit:
                continue
            for p in commit.parents:
                pull_up_method_information.extend(detect_shingle_pullup_method(p, commit))
                detection_stack.append(p)
            checked_commit.add(commit.hexsha)

    return pull_up_method_information


class Method(object):
    def __init__(self, blob, commit):
        self.blob = blob

        self.package_name = get_package(blob.path, commit)
        self.classes = self.get_classes(blob.path)
        self.method_name = get_method(blob.path)
        self.body_cache = None

    def get_classes(self, path):
        classes = []
        split_path = path.split('/')
        for i, v in enumerate(split_path):
            if v == '[CN]':
                classes.append(split_path[i+1])
        return classes

    def get_class_name(self):
        return self.classes[-1]

    def get_full_name(self):
        class_name = '.'.join(self.classes)
        if self.package_name:
            return '.'.join([self.package_name, class_name, self.method_name])
        else:
            return '.'.join([class_name, self.method_name])

    def get_full_class_name(self):
        class_name = '.'.join(self.classes)
        if self.package_name:
            return '.'.join([self.package_name, class_name])
        else:
            return '.'.join([class_name])

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
        if self.body_cache is None:
            self.body_cache = self.blob.data_stream.read()
        return self.body_cache

    def __str__(self):
        return self.get_full_name()


class SubclassMethod(Method):
    def __init__(self, blob, commit):
        super(SubclassMethod, self).__init__(blob, commit)

        split_path = blob.path.split('/')
        self.extend = get_extends(commit, split_path[0], self.classes)


def match_type(a_method, b_method):
    a_types = a_method.get_parameter_types()
    b_types = b_method.get_parameter_types()
    return a_types == b_types


def detect_shingle_pullup_method(old_commit, new_commit):
    diff_index = old_commit.diff(new_commit, create_patch=False)

    added_methods = defaultdict(list)
    deleted_methods = defaultdict(list)
    for diff in diff_index.iter_change_type('A'):
        new_method = Method.create_from_blob(diff.b_blob, new_commit)
        if new_method:
            added_methods[new_method.get_class_name()].append(new_method)

    deleted_classes = set()
    for diff in diff_index.iter_change_type('D'):
        # NOTE change following old_commit to new_commit to detect
        # pull_up_method by same condtion of UMLDiff
        subclass_method = SubclassMethod.create_from_blob(diff.a_blob, old_commit)

        if subclass_method:
            if not subclass_method.extend:
                continue

            if subclass_method.get_full_class_name() in deleted_classes:
                continue

            if not exist_class(diff.a_blob, new_commit):
                deleted_classes.add(subclass_method.get_full_class_name())
                continue

            if subclass_method.extend in added_methods.keys():
                deleted_methods[subclass_method.extend].append(subclass_method)

    pull_up_method_candidates = []

    old_org_commit = get_org_commit(old_commit)
    new_org_commit = get_org_commit(new_commit)

    for super_class, v in deleted_methods.iteritems():
        if super_class not in added_methods:
            print('%s does\'nt have a deleted method' % (super_class))
            continue
        for dst_method in added_methods[super_class]:
            dst_body = dst_method.get_body()
            if not dst_body:
                continue
            dst_body = '\n'.join(dst_body.split('\n')[1:-2])
            for src_method in v:
                src_body = src_method.get_body()

                is_same_parameters = match_type(src_method, dst_method)
                if src_body:
                    src_body = '\n'.join(src_body.split('\n')[1:-2])

                if src_body or dst_body:
                    try:
                        sim = calculate_similarity(src_body, dst_body)
                    except ZeroDivisionError:
                        sim = "N/A"
                else:
                    sim = 0
                pull_up_method_candidates.append((old_commit.hexsha,
                                                  new_commit.hexsha,
                                                  old_org_commit,
                                                  new_org_commit,
                                                  str(src_method),
                                                  str(dst_method),
                                                  sim,
                                                  is_same_parameters))

    return pull_up_method_candidates
