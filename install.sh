#!/bin/sh

# if you need to execute python setup script comment as a root, please uncomment following line.
#SUDO=sudo

# maven command
MAVEN_BIN=mvn

# python comand
PYTHON_BIN=python

# location of java-parser created by maven
PARSER_PATH=parser/java/target/kenja-java-parser-0.1-jar-with-dependencies.jar

# Build Java parser for kenja
git submodule init
git submodule update
cd parser/java
$MAVEN_BIN assembly:assembly
cd -
cp $PARSER_PATH kenja/lib/java-parser.jar
$SUDO $PYTHON_BIN setup.py install
