from setuptools import setup, find_packages

setup(name='kenja',
    version='0.4',
    description='A Refactoring Detection tool powered by Historage',
    author='Kenji Fujiwara',
    author_email='kenji-f@is.naist.jp',
    url='https://github.com/niyaton/kenja',
    packages=find_packages(),
    data_files=[("kenja/lib", ["kenja/lib/java-parser.jar"])],
    entry_points = {
        'console_scripts': [ 
            'kenja.convert = kenja.convert:main',
            'kenja.detection = kenja.refactoring_detection:main'
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
