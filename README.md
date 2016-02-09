# Requirements

## for General
- python 2.7+ (kenja doesn't support python 3 yet)
- git (confirmed versions)
    - 1.7.10
    - 1.8.5.2
    - 2.0.1
    - 2.2.2

## for Java 
- Java

## for CSharp
### Windows
- .NET Framework

### Mac or Linux
- Mono

# Dependencies
Kenja needs following libraries.

- [pyrem_torq](https://github.com/tos-kamiya/pyrem_torq)
- [GitPython](https://github.com/gitpython-developers/GitPython/)
- [kenja-python-parser](https://github.com/sdlab-naist/kenja-python-parser/)
- [kenja-java-parser](https://github.com/niyaton/kenja-java-parser/)

# Installation

```sh
python setup.py install
```

## Installation (for developers)

```sh
sh install.sh
```

If you cannot 

# How to use

## Convert your git repository to historage
```sh
kenja.historage.convert <your_repository_path> <path_of_historage_directory>
```

- Use path of empty directory for \<path_of_historage_directory\>
    - Historage (a Git repository) will be created here.
    - Kenja will make this directory automatically if you give non-existing directory.
    - use `--disable-python`, `--disable-ruby`, `--disable-csharp` or `--disable-java` option to avoid handling `.py`, `.rb`, `.cs` or `.java` files.

### Store syntax trees infromation [for DEBUG]
```sh
kenja.historage.convert --syntax-trees-dir=<path_of_syntax_tree_directory> <your_repository_path> <path_of_historage_directory> 
```

- Information of syntax trees will be stored in the \<path_of_syntax_tree_directory\>
- We recommend you to provide path of empty dir for \<path_of_syntax_tree_directory\>
    - Kenja will make a lot of files which contains syntax information to construct a historage.
    - Kenja will make this directory automatically if you give non-existing directory.


## Detect extract method from your historage

### Output as CSV format
```sh
kenja.detection.extract_method all <historage_path>
```

### Output as JSON format
```sh
kenja.detection.extract_method --format json all <historage_path>
```

## Detect pull up method from your historage
```sh
kenja.detection.pull_up_method all <historage_path>
```

# Development
## Install latest version of kenja
use install.sh

```sh
sh install.sh
```

### Requirements
Apache Maven 2 or 3

# Notes
- The Historage which converted by kenja is case sensitive, because Git is case sensitive too.
- Your local file system should use case sensitive file system when you construct Historage by kenja.
