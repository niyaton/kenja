from __future__ import absolute_import
from git.repo import Repo
from collections import defaultdict
from pyrem_torq.expression import Search
from pyrem_torq.treeseq import seq_split_nodes_of_label
from pyrem_torq import script
from kenja.historage import *
from kenja.git.diff import GitDiffParser
from kenja.shingles import tokenizer, split_to_str, calculate_similarity


diff_parser = GitDiffParser()


def seq_outermost_node_iter(seq, label):
    # This function is fixed version of seq_outermost_node_iter.
    # Original version of this code is in the pyrem_torq.treeseq
    def soni_i(curPos, item):
        if item.__class__ is list:
            assert len(item) >= 1
            if item[0] == label:
                yield curPos, item
            else:
                for i in xrange(1, len(item)):
                    for v in soni_i(curPos + [i], item[i]):
                        yield v
    return soni_i([], seq)


def parsing_method_parameter_list_iter():
    # TODO Support {... , ...} and <A,B>
    simple_exp = script.compile("""
        ( block <- (null <- LP), *(req^(RP), @0), (null <- RP)) | any
    ;""")
    complex_script = script.compile("""
        ( method_invoke <- target_method, (null <- LP), *(req^(RP), @simpleExp), (null <- RP))
    ;""", replaces={'simpleExp': simple_exp})
    yield Search(complex_script)

    yield Search(script.compile("""
        ( method_invoke :: ~( target_method, +(param <- +any^(comma), ?comma)))
    ;"""))


def parsing_parameter():
    return Search(script.compile("""
        ( method_invoke :: ~( target_method, +(param <- +any^(comma), ?comma)))
    ;"""))


parsing_expressions = list(parsing_method_parameter_list_iter())


def search_method(method_name):
    return Search(script.compile("""target_method <- (id :: "%s");""" % (method_name)))


def parse_added_lines(added_lines, method_name):
    tmp = '\n'.join([line for lineno, line in added_lines])
    seq = split_to_str(tmp)
    seq = tokenizer.parse(seq)
    seq = search_method(method_name).parse(seq)
    seq = seq_split_nodes_of_label(seq, "null")[0]
    if len(list(seq_outermost_node_iter(seq, 'target_method'))) == 0:
        return []
    for expression in parsing_expressions:
        seq = expression.parse(seq)
        seq = seq_split_nodes_of_label(seq, "null")[0]

    num_args_list = set()
    for pos, invoke_seq in seq_outermost_node_iter(seq, 'method_invoke'):
        params = len(list(seq_outermost_node_iter(invoke_seq, 'param')))
        num_args_list.add(params)

    return num_args_list


def detect_extract_method(historage):
    extract_method_information = []

    for commit in historage.iter_commits(historage.head):
        for p in commit.parents:
            extract_method_information.extend(detect_extract_method_from_commit(p, commit))

    return extract_method_information


def detect_extract_method_from_commit(old_commit, new_commit):
    result = []
    extracted_method_candidates = defaultdict(set)

    diff_index = old_commit.diff(new_commit, create_patch=True)

    added_lines_dict = defaultdict(list)

    for diff in diff_index.iter_change_type('A'):
        path = diff.b_blob.path
        if is_method_body(path) or is_constructor_body(path):
            if is_method_body(path):
                method = get_method(diff.b_blob.path)
            else:
                method = get_constructor(diff.b_blob.path)
            method_name = method[:method.index(r'(')]
            args = method[method.index(r'('):].split(r',')
            num_args = len(args)
            if num_args == 1:
                num_args = 0 if args[0] == '()' else 1

            c = get_class(diff.b_blob.path)
            extracted_method_candidates[c].add(method_name)
            (deleted_lines, added_lines) = diff_parser.parse(diff.diff)
            added_lines_dict[(c, method_name, num_args)].append((method, added_lines))

    for diff in diff_index.iter_change_type('M'):
        if not (is_method_body(diff.b_blob.path) or is_constructor_body(diff.b_blob.path)):
            continue
        c = get_class(diff.b_blob.path)
        if c not in extracted_method_candidates.keys():
            continue

        (deleted_lines, added_lines) = diff_parser.parse(diff.diff)
        if not (deleted_lines and added_lines):
            continue
        a_package = get_package(diff.a_blob.path, old_commit)
        b_package = get_package(diff.b_blob.path, new_commit)
        if is_method_body(diff.b_blob.path):
            m = get_method(diff.b_blob.path)
        else:
            m = get_constructor(diff.b_blob.path)
        script = '\n'.join([l[1] for l in deleted_lines])
        for method in extracted_method_candidates[c]:
            num_args_list = parse_added_lines(added_lines, method)
            for num_args in num_args_list:
                if (c, method, num_args) not in added_lines_dict.keys():
                    continue
                for extracted_method, extracted_lines in added_lines_dict[(c, method, num_args)]:
                    extracted_lines = extracted_lines[1:-1]
                    script2 = '\n'.join([l[1] for l in extracted_lines])
                    try:
                        sim = calculate_similarity(script, script2)
                    except ZeroDivisionError:
                        sim = "N/A"
                    org_commit = get_org_commit(new_commit)

                    target_body = diff.a_blob.data_stream.read()
                    extracted_body = diff.b_blob.data_stream.read()
                    target_deleted_lines = [l[1] for l in deleted_lines]

                    refactoring_candidate = {'a_commit': old_commit.hexsha,
                                             'b_commit': new_commit.hexsha,
                                             'b_org_commit': org_commit,
                                             'a_package': a_package,
                                             'b_package': b_package,
                                             'target_class': c,
                                             'target_method': m,
                                             'extracted_method': extracted_method,
                                             'similarity': sim,
                                             'target_body': target_body,
                                             'extracted_body': extracted_body,
                                             'target_deleted_lines': target_deleted_lines,
                                             }
                    result.append(refactoring_candidate)

    return result


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
