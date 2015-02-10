import os
import sys
import hashlib
import urllib
import subprocess
import glob
from setuptools import setup, find_packages

kenja_version = '0.6-122-gbd1964f'

def copy_java_parser():
    parser_path = 'kenja/lib/java/java-parser.jar'
    parser_location = 'https://github.com/niyaton/kenja-java-parser/releases/download/0.3/kenja-java-parser-0.3-jar-with-dependencies.jar'
    parser_digest = '9e45f37dd7f52f5cf5c817026159db3b'

    confirm_text = None
    exit_when_no = True
    if not os.path.exists(parser_path):
        confirm_text = "{0} does not exist. Do you want to download it?[y/n]".format(parser_path)
    elif hashlib.md5(open(parser_path).read()).hexdigest() != parser_digest:
        confirm_text = "{0} is different from designated parser script. Do you want to overwrite it?[y/n]".format(parser_path)
        exit_when_no = False

    if confirm_text is not None:
        print(confirm_text)
        choice = raw_input().lower()
        yes = set(['yes', 'y', 'ye'])
        no = set(['no', 'n'])
        if choice in yes:
            urllib.urlretrieve(parser_location, parser_path)
            digest = hashlib.md5(open(parser_path).read()).hexdigest()
            if parser_digest != digest:
                print("md5 hash of {0} is incorrect! remove it and try again.".format(parser_path))
                sys.exit(1)
        elif exit_when_no:
            sys.exit(1)

copy_java_parser()

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
      data_files=[("kenja/lib/java", ["kenja/lib/java/java-parser.jar"]),
                  ("kenja/lib/csharp", glob.glob("kenja/lib/csharp/*")),
                  ("kenja", ["kenja/readme_for_historage.txt"])],
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
          "GitPython",
          "kenja-python-parser"
      ],
      dependency_links=[
          'https://github.com/tos-kamiya/pyrem_torq/tarball/master#egg=pyrem_torq',
          'https://github.com/gitpython-developers/GitPython/tarball/0.3.2#egg=GitPython',
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
