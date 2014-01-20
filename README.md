# Requirements

python 2.7+ (kenja doesn't support python 3 because GitPython does'nt support python 3)
Java


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
$kenja.convert convert <your_repository_path> <name of converted repository>
```

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
