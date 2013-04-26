from __future__ import absolute_import
from git.repo import Repo
import kenja.singles as singles
from kenja.historage import *
from kenja.git.diff import GitDiffParser
from kenja.singles import tokenize
from kenja.singles import tokenizing_expr
from collections import defaultdict
from itertools import count, izip

tokenizer = tokenizing_expr()

def parse_added_lines(added_lines, method_name):
    tmp = '\n'.join([line for lineno, line in added_lines])
    tokens = tokenize(tokenizer, tmp)
    num_args_list = set()

    i = 1 # tokens[0] contains 'code'
    while i + 2 < len(tokens):
        type, num, str = tokens[i]
        if type != 'id':
            i = i + 1
            continue
        if str == method_name:
            i = i + 1
            type, num, str = tokens[i]
            if type != 'LP':
                continue
            i = i + 1
            type, num, str = tokens[i]
            if type == 'RP':
                num_args_list.add(0)
                continue
            lp = 1
            num_args = 1
            while i < len(tokens):
                type, num, str = tokens[i]
                if type == 'LP':
                    lp = lp + 1
                elif type == 'RP':
                    lp = lp - 1
                    if lp == 0:
                        break
                elif type == 'comma' and lp == 1:
                    num_args = num_args + 1
                elif type == 'op_lt' or type == 'LB':
                    # TODO Support {... , ...} and <A,B>
                    # However it's rarely case.
                    pass
            num_args_list.add(num_args)

    return num_args_list

def detect_extract_method(historage):
    extract_method_information = []

    parser = GitDiffParser()
    for commit in historage.iter_commits(historage.head):
        for p in commit.parents:
            extracted_method_candidates = defaultdict(set)

            diff_index = p.diff(commit, create_patch=True)

            added_lines_dict = defaultdict(list)

            for diff in diff_index.iter_change_type('A'):
                if is_method_body(diff.b_blob.path):
                    method = get_method(diff.b_blob.path)
                    method_name = method[:method.index(r'(')]
                    args = method[method.index(r'('):].split(r',')
                    num_args = len(args)
                    if num_args == 1:
                        num_args = 0 if args[0] == '()' else 1

                    c = get_class(diff.b_blob.path)
                    extracted_method_candidates[c].add(method_name)
                    (deleted_lines, added_lines) = parser.parse(diff.diff)
                    added_lines_dict[(c, method_name, num_args)].append((method, added_lines))

            for diff in diff_index.iter_change_type('M'):
                if not is_method_body(diff.b_blob.path):
                    continue
                c = get_class(diff.b_blob.path)
                if c not in extracted_method_candidates.keys():
                    continue

                (deleted_lines, added_lines) = parser.parse(diff.diff)
                if not(deleted_lines and added_lines):
                    continue
                a_package = get_package(diff.a_blob.path, p)
                b_package = get_package(diff.b_blob.path, commit)
                m = get_method(diff.b_blob.path)
                script = '\n'.join([l[1] for l in deleted_lines])
                for method in extracted_method_candidates[c]:
                    num_args_list = parse_added_lines(added_lines, method)
                    for num_args in num_args_list:
                        if (c, method, num_args) not in added_lines_dict.keys():
                            continue
                        for extracted_method, extracted_lines in added_lines_dict[(c, method, num_args)]:
                            extracted_lines = extracted_lines[1:-1]
                            script2 = '\n'.join([l[1] for l in extracted_lines])
                            sim = singles.calculate_similarity(script, script2)
                            org_commit = get_org_commit(commit)
                            extract_method_information.append((commit.hexsha, org_commit, a_package, b_package, c, m, extracted_method, sim))
                            #print deleted_lines, added_lines_dict[(c, method, num_args)]

    return extract_method_information

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Extract Method Detector')
    parser.add_argument('historage_dir',
            help='path of historage repository dir')
    args = parser.parse_args()

    historage = Repo(args.historage_dir)
    extract_method_information = detect_extract_method(historage)

    candidate_revisions = set()
    for info in extract_method_information:
        candidate_revisions.add(info[0])
        print '"%s","%s","%s","%s","%s","%s","%s","%s"' % info

    print 'candidates:', len(extract_method_information)
    print 'candidate revisions:', len(candidate_revisions)
