from __future__ import absolute_import
import argparse
import kenja.language
from kenja.converter import HistorageConverter
from logging import basicConfig


class CommandParser(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser(description=self.get_description())

        self.add_main_argument()
        self.add_option_argument()
        self.parser.set_defaults(func=self.set_function)

    def parse_and_execute_command(self):
        args = self.parser.parse_args()
        basicConfig(level=args.logging_level)
        args.func(args)

    def add_main_argument(self):
        self.parser.add_argument('org_git_dir', help='path of original git repository')
        self.parser.add_argument('historage_dir', help='path of historage directory')
        self.parser.add_argument('--logging-level', help='debug level for python logger', default='WARNING')
        for extention in kenja.language.extension_dict.keys():
            self.parser.add_argument(
                '--disable-' + extention,
                action='store_true',
                help='disable parsing {0} files'.format(extention)
            )

    def add_option_argument(self):
        self.parser.add_argument('--syntax-trees-dir', help='path of syntax trees dir')

    def set_function(self, args):
        pass

    def get_description(self):
        pass


class ConvertCommandParser(CommandParser):
    def add_option_argument(self):
        super(ConvertCommandParser, self).add_option_argument()
        self.parser.add_argument(
            '--parser-processes',
            type=int,
            help='set parser processes (default value is number of processers of your machine)'
        )
        self.parser.add_argument(
            '--bare',
            action='store_true',
            help='create a bare repository for historage'
        )

    def set_function(self, args):
        hc = HistorageConverter(args.org_git_dir, args.historage_dir, args.syntax_trees_dir)

        if args.parser_processes:
            hc.parser_processes = args.parser_processes

        hc.is_bare_repo = args.bare

        disable_arg = 'disable_'
        args_dict = args.__dict__
        for arg in filter(lambda arg: disable_arg in arg, args_dict):
            if args_dict[arg]:
                disable_extention = arg.replace(disable_arg, '')
                kenja.language.extension_dict.pop(disable_extention)

        hc.convert()

    def get_description(self):
        return 'convert git repository to historage'


class ParseCommandParser(CommandParser):
    def set_function(self, args):
        hc = HistorageConverter(args.org_git_dir, args.historage_dir, args.syntax_trees_dir)
        hc.parse_all_target_files()
        pass

    def get_description(self):
        return 'parse all java files from orginal git repository (for debug)'


class ConstructCommandParser(CommandParser):
    def add_option_argument(self):
        super(ConstructCommandParser, self).add_option_argument()
        self.parser.add_argument(
            '--bare',
            action='store_true',
            help='create a bare repository for historage'
        )

    def set_function(self, args):
        hc = HistorageConverter(args.org_git_dir, args.historage_dir, args.syntax_trees_dir)

        hc.is_bare_repo = args.bare

        hc.construct_historage()

    def get_description(self):
        return 'construct historage by using syntax trees (for debug)'


def convert():
    parser = ConvertCommandParser()
    parser.parse_and_execute_command()


def parse():
    parser = ParseCommandParser()
    parser.parse_and_execute_command()


def construct():
    parser = ConstructCommandParser()
    parser.parse_and_execute_command()
