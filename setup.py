import os
import sys
import hashlib
import urllib
import subprocess
import glob
from tarfile import open as tarfile_open
from setuptools import setup, find_packages

kenja_version = '0.6-122-gbd1964f'
data_files = [("kenja", ["kenja/readme_for_historage.txt"])]


def validate_md5sum(digest, path):
    return digest == hashlib.md5(open(path).read()).hexdigest()


class JavaParserInstaller:
    parser_path = 'kenja/lib/java/java-parser.jar'
    parser_location = 'https://github.com/niyaton/kenja-java-parser/releases/download/0.5/kenja-java-parser-0.5-jar-with-dependencies.jar'
    parser_digest = '3686529db9d36d5ef5d7425692d95aea'

    def validate_parser(self):
        if not os.path.exists(self.parser_path):
            return 'not installed'

        if not validate_md5sum(self.parser_digest, self.parser_path):
            return 'invalid parser'
        return 'installed'

    def get_confirm_text(self, status):
        if status == 'not installed':
            return "{0} does not exist. Do you want to download it?[y/n]".format(self.parser_path)
        elif status == 'invalid parser':
            return "{0} is different from designated parser script. Do you want to overwrite it?[y/n]".format(self.parser_path)
        else:
            return ""

    def ask_yesno(self, confirm_text):
        print(confirm_text)
        choice = raw_input().lower()
        yes = set(['yes', 'y', 'ye'])
        return choice in yes

    def install_parser(self):
        install_status = self.validate_parser()
        if install_status == 'installed':
            return True

        if not self.ask_yesno(self.get_confirm_text(install_status)):
            return install_status != 'not installed'

        self.download_parser()
        install_status = self.validate_parser()

        if self.validate_parser() != 'installed':
            print("md5 hash of {0} is incorrect! remove it and tryagain.".format(self.parser_path))
            sys.exit(1)
        return True

    def download_parser(self):
        urllib.urlretrieve(self.parser_location, self.parser_path)


class CSharpParserInstaller(JavaParserInstaller):
    parser_path = os.path.join('kenja', 'lib', 'csharp')
    parser_location = 'https://github.com/sdlab-naist/kenja-csharp-parser/releases/download/0.3/kenja-csharp-parser-0.3.tar.gz'
    md5sum_location = 'https://github.com/sdlab-naist/kenja-csharp-parser/releases/download/0.3/kenja-csharp-parser-0.3.md5sum'
    parser_tar_digest = '0f5db497559f68ec884d6699057777d9'

    def __init__(self):
        (filename, _) = urllib.urlretrieve(self.md5sum_location)
        with open(filename) as f:
            self.hash_table = [line.strip().split(' ') for line in f.readlines()]

    def validate_parser(self):
        for h, f in self.hash_table:
            path = os.path.join(self.parser_path, f)
            if not os.path.exists(path):
                return 'not installed'

            if not validate_md5sum(h, path):
                return 'invalid parser'

        return 'installed'

    def download_parser(self):
        (filename, _) = urllib.urlretrieve(self.parser_location)
        if not validate_md5sum(self.parser_tar_digest, filename):
            print("md5 hash of downloaded file is incorrect! try again.")
            sys.exit(1)

        tarfile = tarfile_open(filename, 'r')
        tarfile.extractall('kenja/lib/csharp')


def copy_java_parser():
    installer = JavaParserInstaller()
    if installer.install_parser():
        data_files.append(("kenja/lib/java", ["kenja/lib/java/java-parser.jar"]))
    else:
        print("java parser will not be installed.")
        print("You should disable java parser when you run kenja")


def copy_csharp_parser():
    installer = CSharpParserInstaller()
    if installer.install_parser():
        data_files.append(("kenja/lib/csharp", glob.glob("kenja/lib/csharp/*")))
    else:
        print("C# parser will not be installed.")
        print("You should disable C# parser when you run kenja")

copy_java_parser()
copy_csharp_parser()

try:
    kenja_version = subprocess.check_output(["git", "describe"]).rstrip()
except subprocess.CalledProcessError, e:
    pass

setup(name='kenja',
      version=kenja_version,
      description='A Refactoring Detection tool powered by Historage',
      author='Kenji Fujiwara',
      author_email='kenji-f@is.naist.jp',
      url='https://github.com/niyaton/kenja',
      packages=find_packages(),
      data_files=data_files,
      entry_points={
          'console_scripts': [
              'kenja.historage.convert = kenja.convert:convert',
              'kenja.historage.parse = kenja.convert:parse',
              'kenja.historage.construct = kenja.convert:construct',
              'kenja.detection.extract_method = kenja.refactoring_detection:main',
              'kenja.detection.pull_up_method = kenja.pull_up_method:main',
              'kenja.debug.check_duplicate_entry = kenja.git.detect_duplicate_entry:main',
              'kenja.debug.check_historage_equivalence = kenja.git.diff:main'
          ]
      },
      install_requires=[
          "pyrem_torq",
          "GitPython==0.3.6",
          "kenja-python-parser"
      ],
      dependency_links=[
          'https://github.com/tos-kamiya/pyrem_torq/tarball/master#egg=pyrem_torq',
          'https://github.com/sdlab-naist/kenja-python-parser/tarball/master#egg=kenja-python-parser'
      ],
      license="MIT license",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Science/Resarch',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Programming Language :: Java',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'Topic :: Software Development :: Libraries',
          'Topic :: Utilities'
      ]
      )
