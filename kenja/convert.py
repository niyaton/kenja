from __future__ import absolute_import
import argparse
from kenja.convertor import HistorageConverter


class ConvertorCommandParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Git convert to Historage')
        self.subparsers = self.parser.add_subparsers()

        self.add_convert_command()
        self.add_parse_command()
        self.add_construct_command()

    def parse_and_execute_command(self):
        args = self.parser.parse_args()
        args.func(args)

    def add_convert_command(self):
        help_str = 'convert git repository to historage'
        sub_parser = self.subparsers.add_parser('convert', help=help_str)

        help_str = 'path of original git repository'
        sub_parser.add_argument('org_git_dir', help=help_str)

        help_str = 'path of working directory'
        sub_parser.add_argument('working_dir', help=help_str)

        help_str = 'set parser processes (default value is number of processers of your machine)'
        sub_parser.add_argument('--parser-processes', type=int, help=help_str)

        help_str = 'set number of working repositories (default value is 2)'
        sub_parser.add_argument('--working-repositories', type=int, help=help_str)
        sub_parser.set_defaults(func=self.convert)

    def convert(self, args):
        print args

        hc = HistorageConverter(args.org_git_dir, args.working_dir)

        if args.parser_processes:
            hc.parser_processes = args.parser_processes

        if args.working_repositories:
            hc.num_commit_process = args.working_repositories

        hc.convert()

    def add_parse_command(self):
        help_str = 'parse all java files from orginal git repository'
        sub_parser = self.subparsers.add_parser('parse', help=help_str)

        help_str = 'path of original git repository'
        sub_parser.add_argument('org_git_dir', help=help_str)

        help_str = '"syntax_treses" dir will be created in this dir'
        sub_parser.add_argument('working_dir', help=help_str)
        sub_parser.set_defaults(func=self.parse)

    def parse(self, args):
        hc = HistorageConverter(args.org_git_dir, args.working_dir)
        hc.parse_all_java_files()
        pass

    def add_construct_command(self):
        help_str = 'construct historage by using syntax trees'
        sub_parser = self.subparsers.add_parser('construct', help=help_str)

        help_str = 'path of original git repository'
        sub_parser.add_argument('org_git_dir', help=help_str)

        help_str = 'path of working dir'
        sub_parser.add_argument('working_dir', help=help_str)

        help_str = 'path of syntax treses dir'
        sub_parser.add_argument('--syntax-trees-dir', help=help_str)
        sub_parser.set_defaults(func=self.construct)

    def construct(self, args):
        hc = HistorageConverter(args.org_git_dir, args.working_dir)

        if args.syntax_trees_dir:
            hc.syntax_trees_dir = args.syntax_trees_dir

        hc.construct_historage()


def main():
    parser = ConvertorCommandParser()
    parser.parse_and_execute_command()


if __name__ == '__main__':
    main()
