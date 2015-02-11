from __future__ import absolute_import
import os
from tempfile import mkdtemp
from shutil import rmtree
from itertools import count, izip
from git.repo import Repo
from git.objects import Blob
from kenja.git.util import memdb
from gitdb.db.pack import PackedDB
from kenja.parser import BlobParser
from kenja.language import is_target_blob, extension_dict
from kenja.git.util import get_reversed_topological_ordered_commits
from kenja.committer import SyntaxTreesCommitter
from logging import getLogger

logger = getLogger(__name__)


class HistorageConverter:
    def __init__(self, org_git_repo_dir, historage_dir, syntax_trees_dir=None):
        if org_git_repo_dir:
            self.org_repo = Repo(org_git_repo_dir)

        self.check_and_make_working_dir(historage_dir)
        self.historage_dir = historage_dir

        self.use_tempdir = syntax_trees_dir is None
        if self.use_tempdir:
            self.syntax_trees_dir = mkdtemp()
            logger.info(self.syntax_trees_dir)
        else:
            self.check_and_make_working_dir(syntax_trees_dir)
            self.syntax_trees_dir = syntax_trees_dir

        self.num_commits = 0

        self.is_bare_repo = False

    def check_and_make_working_dir(self, path):
        if os.path.isdir(path):
            if os.listdir(path):
                raise Exception('{0} is not an empty directory'.format(path))
        else:
            try:
                os.mkdir(path)
            except OSError:
                logger.error('Kenja cannot make a directory: {0}'.format(path))
                raise

    def parse_all_target_files(self):
        logger.info('create parser processes...')
        blob_parser = BlobParser(extension_dict, self.syntax_trees_dir, self.org_repo.git_dir)
        parsed_blob = set()
        for commit in get_reversed_topological_ordered_commits(self.org_repo, self.org_repo.refs):
            self.num_commits = self.num_commits + 1
            if commit.parents:
                for p in commit.parents:
                    for diff in p.diff(commit):
                        if is_target_blob(diff.b_blob):
                            if diff.b_blob.hexsha not in parsed_blob:
                                blob_parser.parse_blob(diff.b_blob)
                                parsed_blob.add(diff.b_blob.hexsha)
            else:
                for entry in commit.tree.traverse():
                    if isinstance(entry, Blob) and is_target_blob(entry):
                        if entry.hexsha not in parsed_blob:
                            blob_parser.parse_blob(entry)
                            parsed_blob.add(entry.hexsha)
        logger.info('waiting parser processes')
        blob_parser.join()

    def prepare_historage_repo(self):
        historage_repo = Repo.init(self.historage_dir, bare=self.is_bare_repo)
        self.set_git_config(historage_repo)
        return historage_repo

    def set_git_config(self, repo):
        reader = repo.config_reader()  # global config
        writer = repo.config_writer()  # local config
        user_key = 'user'
        if not reader.has_option(user_key, 'name'):
            if not writer.has_section(user_key):
                writer.add_section(user_key)
            writer.set(user_key, 'name', 'Kenja Converter')
        if not reader.has_option(user_key, 'email'):
            if not writer.has_section(user_key):
                writer.add_section(user_key)
            writer.set(user_key, 'email', 'default@example.com')

    def convert(self):
        self.parse_all_target_files()
        self.construct_historage()

    def construct_historage(self):
        logger.info('convert a git repository to a  historage...')

        historage_repo = self.prepare_historage_repo()
        committer = SyntaxTreesCommitter(Repo(self.org_repo.git_dir), historage_repo, self.syntax_trees_dir)
        num_commits = self.num_commits if self.num_commits != 0 else '???'
        for num, commit in izip(count(), get_reversed_topological_ordered_commits(self.org_repo, self.org_repo.refs)):
            logger.info('[%d/%s] convert %s to: %s' % (num, num_commits, commit.hexsha, historage_repo.git_dir))
            committer.apply_change(commit)
        committer.create_heads()
        committer.create_tags()

        memdb.stream_copy(memdb.sha_iter(), historage_repo.odb)
        #packeddb = PackedDB(os.path.join(historage_repo.git_dir, 'objects', 'pack'))
        #memdb.stream_copy(memdb.sha_iter(), historage_repo.odb)
        #memdb.stream_copy(memdb.sha_iter(), packeddb)

        if not self.is_bare_repo:
            historage_repo.head.reset(working_tree=True)
        logger.info('completed!')

    def __del__(self):
        if self.use_tempdir and os.path.exists(self.syntax_trees_dir):
            rmtree(self.syntax_trees_dir)
