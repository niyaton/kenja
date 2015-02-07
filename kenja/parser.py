from __future__ import absolute_import
import os
from kenja_parser.gittree import parse_and_write_gittree
from subprocess import (
    Popen,
    PIPE,
    )
from multiprocessing import (
    Pool,
    cpu_count
    )


def execute_parser(cmd, src):
    p = Popen(cmd, stdin=PIPE)
    p.stdin.write(src)
    p.communicate()
    return True


class ParserExecutor:
    def __init__(self, output_dir, processes=None):
        self.output_dir = output_dir
        self.processes = processes if processes else cpu_count()
        self.pool = Pool(self.processes)
        self.closed = False

    def parse_blob(self, blob):
        src = blob.data_stream.read()
        cmd = self.make_cmd(blob.hexsha)

        if(self.closed):
            self.pool = Pool(self.processes)
            self.closed = False

        self.pool.apply_async(execute_parser, args=[cmd, src])

    def make_cmd(self, hexsha):
        cmd = ["true"]
        return cmd

    def join(self):
        if self.closed:
            return
        self.pool.close()
        self.closed = True
        self.pool.join()
        self.pool = None


class JavaParserExecutor(ParserExecutor):
    parser_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'java/java-parser.jar')

    def make_cmd(self, hexsha):
        cmd = ["java",
               "-jar",
               self.parser_path,
               os.path.join(self.output_dir, hexsha)
               ]
        return cmd


class PythonParserExecutor(ParserExecutor):
    def parse_blob(self, blob):
        src = blob.data_stream.read()

        if(self.closed):
            self.pool = Pool(self.processes)
            self.closed = False

        output_path = os.path.join(self.output_dir, blob.hexsha)
        self.pool.apply_async(parse_and_write_gittree, args=[src, output_path])


blob_parsers = {'java': JavaParserExecutor, 'python': PythonParserExecutor}


class BlobParser:
    def __init__(self, supported_language, output_dir):
        self.initialize_parsers(supported_language, output_dir)

    def initialize_parsers(self, supported_language, output_dir):
        self.parsers = {}
        for language, extensions in supported_language.items():
            parser = blob_parsers[language](output_dir)
            for extension in extensions:
                self.parsers[extension] = parser

    def parse_blob(self, blob):
        root, ext = os.path.splitext(blob.name)
        self.parsers[ext].parse_blob(blob)

    def join(self):
        for parser in self.parsers.values():
            parser.join()
