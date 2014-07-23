from __future__ import absolute_import
import os
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
    parser_class = "jp.naist.sd.kenja.factextractor.GitTreeCreator"

    def __init__(self, output_dir, parser_path, processes=None):
        self.output_dir = output_dir
        self.parser_path = parser_path
        self.processes = processes if processes else cpu_count()
        self.pool = Pool(self.processes)
        self.closed = False

    def parse_blob(self, blob):
        # src = blob.data_stream.read()
        src = blob.hexsha
        cmd = self.make_cmd(blob.hexsha)

        if(self.closed):
            self.pool = Pool(self.processes)
            self.closed = False

        self.pool.apply_async(execute_parser, args=[cmd, src])

    def parse_blobs(self, blobs):
        src = '\n'.join([b.hexsha for b in blobs])
        cmd = self.make_cmd("")

        if(self.closed):
            self.pool = Pool(self.processes)
            self.closed = False

        self.pool.apply_async(execute_parser, args=[cmd, src])

    def make_cmd(self, hexsha):
        cmd = ["java",
               "-cp",
               self.parser_path,
               self.parser_class,
               self.output_dir
               ]
        return cmd

    def join(self):
        self.pool.close()
        self.closed = True
        self.pool.join()
        self.pool = None
