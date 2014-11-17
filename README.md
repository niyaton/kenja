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
$kenja.convert convert <your_repository_path> <path of working directory>
```

The direcotry ``base_repo`` is a historage converted by kenja.

## Detect extract method from your historage
```
$kenja.detection all <historage_path>
```

# Development
## Install latest version of kenja
use install.sh

```
sh install.sh
```

### Requirements
Apache Maven 2 or 3

# Notes
- The Historage which converted by kenja is case sensitive, because Git is case sensitive too.
- Your local file system should use case sensitive file system when you construct Historage by kenja.
