import os
import sys
import hashlib
import urllib
from setuptools import setup, find_packages

parser_path = 'kenja/lib/java-parser.jar'
parser_location = 'https://github.com/niyaton/kenja-java-parser/releases/download/0.1/kenja-java-parser-0.1-jar-with-dependencies.jar'
parser_digest = 'efeaf203579b4cf7264873ccfe4abcda'

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


setup(name='kenja',
    version='0.4',
    description='A Refactoring Detection tool powered by Historage',
    author='Kenji Fujiwara',
    author_email='kenji-f@is.naist.jp',
    url='https://github.com/niyaton/kenja',
    packages=find_packages(),
    data_files=[("kenja/lib", ["kenja/lib/java-parser.jar"]),
                ("kenja", ["kenja/readme_for_historage.txt"])],
    entry_points = {
        'console_scripts': [
            'kenja.historage.convert = kenja.convert:convert',
            'kenja.historage.parse = kenja.convert:parse',
            'kenja.historage.construct = kenja.convert:construct',
            'kenja.detection.extract_method = kenja.refactoring_detection:main',
            'kenja.detection.pull_up_method = kenja.pull_up_method:main'
        ]
    },
    install_requires = [
        "pyrem_torq",
        "GitPython"
    ],
    dependency_links = [
            'https://github.com/tos-kamiya/pyrem_torq/tarball/master#egg=pyrem_torq',
            'https://github.com/gitpython-developers/GitPython/tarball/0.3#egg=GitPython'
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
        'Topic :: Software Development :: Libraries'
        'Topic :: Utilities',
    ],
)
