from src.parse_changed_files import GitBlobParser
from git import Repo
from git import Blob
from gitdb.util import hex_to_bin

class TestGitBlobParser:

    test_git_dir = "~/historage_recover_test/columba_all"

    def setup(self):
       self.repo = Repo(self.test_git_dir) 
       self.git_blob_parser = GitBlobParser(self.repo)
        
    def test_parse_blob(self):
        test_blobs = [
        "fa173dfa25f834639c9152f3152f14fc84a49bc5",
        "96d714ae0dfafa57467a9d5e2744b669f6064a46",
        "cf7519027e88b9904a737249b8195920c08ed1e4",
        "42a29b61a0428eb350ea4df66a5a46070fb5e280",
        "3d42a14c99e60cc6ae722a750ecdcc5c93336cdd",
        "b09c51d14c3a22956d755072dbe4fe9f47e16d34",
        "757d720728b4894cd1f8e7c1e671432f2eb14522",
        "4748b802f24a31522f86bd6a7b1145e079196d12",
        "0355c34ba84707dc20846a3ced35b0acb01e351e",
        "c1656c40dd4943183fdc05d5c928e7ece24adb71",
        "1cce03cda27628ae2f89e17d20bb0f5a4cd667f4",
        "e178905382f32b7b0173d0fd09d892fdae4b9af7",
        "dfa80e406664d6548ff00139eb572103dd549aba",
        "17a078a19860bc1747a903cb7b10d633b5100cbb",
        "28a825c550ba681cdc23686a8e315fc509d86cff",
        "3d0a72d557bfe3f054f2423ebde57ce4628d9b8c",
        "66e592822381b507365e7dc7e535c95307ec9477",
        "1ef57130fcb52ae2f13b4af2258cfa3891ec5b17",
        "8f0bb1aa6490e35f46bc894748def17b0b9b7d7c",
        "2613a1e581e22088a157985ee1bbda40db19ebab"
        ]
        for blob_hexsha in test_blobs:
            blob = self.get_blob_from_hexsha(blob_hexsha)
            self.git_blob_parser.parse_blob(blob)

    def get_blob_from_hexsha(self, hexsha):
        return Blob.new_from_sha(self.repo ,hex_to_bin(hexsha))

        
