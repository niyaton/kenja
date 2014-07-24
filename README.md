# Requirements

- python 2.7+ (kenja doesn't support python 3 because GitPython does'nt support python 3)
- Java

# Dependencies
Kenja needs following libraries.

- [pyrem_torq](https://github.com/tos-kamiya/pyrem_torq)
- [GitPython](https://github.com/gitpython-developers/GitPython/)
- [kenja-java-parser](https://github.com/niyaton/kenja-java-parser/)

# Installation

```
python setup.py
```

## Manual Installation

```
git submodule init
git submodule update
cd parser/java
mvn assembly:assembly
cd -
cp parser/java/target/kenja-java-parser-0.1-jar-with-dependencies.jar kenja/lib/java-parser.jar
python setup.py install
```

# How to use

## Convert your git repository to historage
```
$kenja.historage.convert <your_repository_path> <path_of_working_directory> <path_of_syntax_tree_directory>
```

The direcotry ``base_repo`` is a historage converted by kenja.

## Detect extract method from your historage
```
$kenja.detection.extract_method all <historage_path>
```
## Detect pull up method from your historage
```
$kenja.detection.pull_up_method all <historage_path>
```

# Development
## Install latest version of kenja
use install.sh

```
sh install.sh
```

### Requirements
Apache Maven 2 or 3
