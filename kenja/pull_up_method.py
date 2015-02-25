from __future__ import absolute_import
from git.repo import Repo
from gitdb.exc import BadObject
from kenja.detection.pull_up_method import detect_shingle_pullup_method
from kenja.detection.pull_up_method import detect_pull_up_method
import argparse
import csv


class RefactoringDetectionCommandParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Kenja a refactoring detection tool')
        self.subparsers = self.parser.add_subparsers()

        self.add_all_command()
        self.add_commits_command()

    def parse_and_execute_command(self):
        args = self.parser.parse_args()
        args.func(args)

    def add_all_command(self):
        help_str = 'detect Pull Up Method refactoring from all commits in the Historage'
        subparser = self.subparsers.add_parser('all', help=help_str)

        help_str = 'path of Historage dir'
        subparser.add_argument('historage_dir', help=help_str)
        subparser.set_defaults(func=self.detect_all)

    def detect_all(self, args):
        historage = Repo(args.historage_dir)
        pull_up_method_candidates = detect_pull_up_method(historage)
        print('"old_commit","new_commit","old_org_commit","new_org_commit",' +
              '"src_method","dst_method","similarity","isSamePrameters"')
        for info in pull_up_method_candidates:
            print(','.join(['"' + str(s) + '"' for s in info]))

    def format_for_umldiff(self, package_prefix, a_commit, b_commit, org_commit, a_package, b_package, c, m, method,
                           sim):
        target_method_info = [package_prefix]
        if a_package:
            target_method_info.append(a_package)
        target_method_info.extend((c, m))
        target_method = '.'.join(target_method_info)
        extracted_method_info = [package_prefix]
        if b_package:
            extracted_method_info.append(b_package)
        extracted_method_info.extend((c, method))
        extracted_method = '.'.join(extracted_method_info)
        return '"%s","%s","%s","%s","%s","%s"' % (a_commit, b_commit, org_commit, target_method, extracted_method, sim)

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
        results = []
        try:
            for a_commit_hash, b_commit_hash in csv.reader(open(args.commits_list)):
                a_commit = historage.commit(a_commit_hash)
                b_commit = historage.commit(b_commit_hash)
                results.extend(detect_shingle_pullup_method(a_commit, b_commit))
        except ValueError:
            print("Invalid input.")
            return
        except BadObject, name:
            print("Invalid hash of the commit:", name.message)

        for result in results:
            # result[6] = sim
            result[6] = str(result[6])
            print(','.join(['"' + s + '"' for s in result]))


def main():
    parser = RefactoringDetectionCommandParser()
    parser.parse_and_execute_command()

if __name__ == '__main__':
    main()
