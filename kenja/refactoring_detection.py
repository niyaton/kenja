from __future__ import absolute_import
from git.repo import Repo
from gitdb.exc import BadObject
from kenja.detection.extract_method import detect_extract_method
from kenja.detection.extract_method import detect_extract_method_from_commit
import argparse
import csv
import sys
import json


class RefactoringDetectionCommandParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Kenja a refactoring detection tool')
        self.parser.add_argument('--format', help='output format', default='csv')
        self.subparsers = self.parser.add_subparsers()

        self.add_all_command()
        self.add_commits_command()

    def parse_and_execute_command(self):
        args = self.parser.parse_args()
        args.func(args)

    def add_all_command(self):
        help_str = 'detect refactoring from all commits in the Historage'
        subparser = self.subparsers.add_parser('all', help=help_str)

        help_str = 'path of Historage dir'
        subparser.add_argument('historage_dir', help=help_str)

        subparser.set_defaults(func=self.detect_all)

    def detect_all(self, args):
        historage = Repo(args.historage_dir)
        extract_method_candidates = detect_extract_method(historage)
        self.print_candidates(extract_method_candidates, args.format)

    def print_candidates(self, candidates, format):
        if format == 'csv':
            self.print_csv(candidates)
        elif format == 'umldiff':
            self.print_umldiff(candidates)
        elif format == 'json':
            self.print_json(candidates)

    def print_csv(self, candidates):
        fieldnames = ('a_commit',
                      'b_commit',
                      'b_org_commit',
                      'a_package',
                      'target_class',
                      'target_method',
                      'b_package',
                      'extracted_method',
                      'similarity',
                      'extracted_body',
                      'target_before_body',
                      'target_after_body',
                      'target_deleted_lines',
                      'target_method_path',
                      'extracted_method_path'
                      )
        for candidate in candidates:
            candidate['target_deleted_lines'] = '\n'.join(candidate['target_deleted_lines'])

        writer = csv.DictWriter(sys.stdout, fieldnames)
        writer.writeheader()
        writer.writerows(candidates)

    def print_umldiff(self, candidates):
        candidate_revisions = set()
        writer = csv.writer(sys.stdout)
        for candidate in candidates:
            candidate_revisions.add(candidate['b_commit'])
            writer.writerow(self.format_for_umldiff(candidate, 'jedit'))

        print 'candidates:', len(candidates)
        print 'candidate revisions:', len(candidate_revisions)

    def print_json(self, candidates):
        print json.dumps(candidates, encoding='utf_8', indent=4)

    def format_for_umldiff(self, extract_method_information, package_prefix=None):
        target_method_path = extract_method_information['target_method_path']
        extracted_method_path = extract_method_information['extracted_method_path']
        target_method = self.get_method_full_name(package_prefix,
                                                  extract_method_information['a_package'],
                                                  target_method_path
                                                  )
        extracted_method = self.get_method_full_name(package_prefix,
                                                     extract_method_information['b_package'],
                                                     extracted_method_path
                                                     )

        split_path = target_method_path.split('/')
        target_method_is_inner = split_path.count('[CN]') > 1
        target_method_is_constructor = '[CS]' in split_path

        split_path = extracted_method_path.split('/')
        extracted_method_is_inner = split_path.count('[CN]') > 1
        extracted_method_is_constructor = '[CS]' in split_path

        a_commit = extract_method_information['a_commit']
        b_commit = extract_method_information['b_commit']
        org_commit = extract_method_information['b_org_commit']
        sim = extract_method_information['similarity']
        return [a_commit, b_commit, org_commit,
                target_method, target_method_is_inner, target_method_is_constructor,
                extracted_method, extracted_method_is_inner, extracted_method_is_constructor,
                sim]

    def get_method_full_name(self, prefix, package, path_of_method):
        info = [prefix, package]

        split_path = path_of_method.split('/')

        target_path = ['[CN]', '[MT]', '[CS]']
        for i, p in enumerate(split_path):
            if p in target_path:
                info.append(split_path[i+1])

        return '.'.join([s for s in info if s is not None])

    def join_method_name(self, prefix, package, class_name, method):
        info = [prefix, package, class_name, method]
        return '.'.join([s for s in info if s is not None])

    def add_commits_command(self):
        help_str = 'detect refactoring from commits in the csv'
        subparser = self.subparsers.add_parser('commits', help=help_str)

        help_str = 'path of Historage dir'
        subparser.add_argument('historage_dir', help=help_str)

        help_str = 'comma separated commits list. please write a_commit hash and b_commit hash per line'
        subparser.add_argument('commits_list', help=help_str)

        subparser.set_defaults(func=self.detect_from_commits_list)

    def detect_from_commits_list(self, args):
        historage = Repo(args.historage_dir)
        extract_method_information = []
        try:
            for a_commit_hash, b_commit_hash in csv.reader(open(args.commits_list)):
                a_commit = historage.commit(a_commit_hash)
                b_commit = historage.commit(b_commit_hash)
                extract_method_information.extend(detect_extract_method_from_commit(a_commit, b_commit))
        except ValueError:
            print "Invalid input."
            return
        except BadObject, name:
            print "Invalid hash of the commit:", name.message

        self.print_candidates(extract_method_information, args.format)


def main():
    parser = RefactoringDetectionCommandParser()
    parser.parse_and_execute_command()


if __name__ == '__main__':
    main()
