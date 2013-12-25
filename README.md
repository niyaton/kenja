# Requirements

python 2.7+ (kenja doesn't support python 3 because GitPython does'nt support python 3)
Java


# Installation
## Requirements
Apache Maven 2 or 3

## Use install.sh

```
sh install.sh
```

## Manual Installation

```
mvn assembly:assembly
cp target/kenja-0.0.1-SNAPSHOT-jar-with-dependencies.jar kenja/lib/java-parser.jar
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
## Create eclipse project
```
$mvn eclipse:eclipse
```

