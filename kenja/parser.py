from __future__ import absolute_import
import os
from kenja_parser.gittree import parse_and_write_gittree
from subprocess import (
    Popen,
    PIPE,
    )
from multiprocessing import (
    Pool,
    cpu_count,
    Process,
    JoinableQueue
    )
from logging import getLogger
from functools import partial

logger = getLogger(__name__)


def execute_parser(cmd, src):
    p = Popen(cmd, stdin=PIPE)
    p.stdin.write(src)
    p.communicate()
    return p.returncode == 0


def callback_main(blob_hash, result):
    if not result:
        logger.error("parsing {} was not completed correctly.".format(blob_hash))


class ParserExecutor:
    def __init__(self, output_dir, repo_path, processes=None):
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

        callback = partial(callback_main, blob.hexsha)
        self.pool.apply_async(execute_parser, args=[cmd, src], callback=callback)

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


class JavaConsumer(Process):
    parser_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', 'java/java-parser.jar')

    def __init__(self, blobs_queue, repo_path, output_dir):
        Process.__init__(self)
        self.blobs_queue = blobs_queue
        self.output_dir = output_dir
        self.repo_path = repo_path

    def run(self):
        parser_process = Popen(self.make_cmd(), stdin=PIPE)
        while True:
            blob_hexsha = self.blobs_queue.get()
            if blob_hexsha is None:
                break
            parser_process.stdin.write(blob_hexsha + '\n')
            self.blobs_queue.task_done()

        parser_process.communicate()
        self.blobs_queue.task_done()

    def make_cmd(self):
        cmd = ["java",
               "-jar",
               self.parser_path,
               self.repo_path,
               self.output_dir
               ]
        return cmd


class JavaMultipleParserExecutor:
    def __init__(self, output_dir, repo_path, processes=None):
        self.target_blobs = JoinableQueue()

        self.num_consumers = processes if processes else cpu_count()
        self.consumers = [JavaConsumer(self.target_blobs, repo_path, output_dir)
                          for i in range(self.num_consumers)]

        for consumer in self.consumers:
            consumer.start()

        self.closed = False

    def parse_blob(self, blob):
        if self.closed:
            return
        self.target_blobs.put(blob.hexsha)

    def join(self):
        if self.closed:
            return
        for i in range(self.num_consumers):
            self.target_blobs.put(None)

        self.target_blobs.join()
        self.closed = True


class PythonParserExecutor(ParserExecutor):
    def parse_blob(self, blob):
        src = blob.data_stream.read()

        if(self.closed):
            self.pool = Pool(self.processes)
            self.closed = False

        output_path = os.path.join(self.output_dir, blob.hexsha)
        self.pool.apply_async(parse_and_write_gittree, args=[src, output_path])


class CSharpParserExecutor(ParserExecutor):
    file_path = 'csharp/kenja-csharp-parser.exe'
    parser_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib', file_path)

    def make_cmd(self, hexsha):
        cmd = ["mono",
               self.parser_path,
               os.path.join(self.output_dir, hexsha)
               ]
        return cmd


class RubyParserExecutor(ParserExecutor):

    def make_cmd(self, hexsha):
        cmd = ["parse_ruby",
               os.path.join(self.output_dir, hexsha)
               ]
        return cmd


blob_parsers = {'java': JavaMultipleParserExecutor,
                'python': PythonParserExecutor,
                'csharp': CSharpParserExecutor,
                'ruby': RubyParserExecutor}


class BlobParser:
    def __init__(self, supported_language, output_dir, repo_path):
        self.initialize_parsers(supported_language, output_dir, repo_path)

    def initialize_parsers(self, supported_language, output_dir, repo_path):
        self.parsers = {}
        for language, extensions in supported_language.items():
            parser = blob_parsers[language](output_dir, repo_path)
            for extension in extensions:
                self.parsers[extension] = parser

    def parse_blob(self, blob):
        root, ext = os.path.splitext(blob.name)
        self.parsers[ext].parse_blob(blob)

    def join(self):
        for parser in self.parsers.values():
            parser.join()
