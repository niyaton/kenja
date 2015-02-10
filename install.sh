#!/bin/sh

# if you need to execute python setup script comment as a root, please uncomment following line.
#SUDO=sudo

# maven command
MAVEN_BIN=mvn

# python comand
PYTHON_BIN=python

# location of java-parser created by maven
JAVA_PARSER_PATH=parser/java/target/kenja-java-parser-0.3-jar-with-dependencies.jar

# update submodules for parser
git submodule init
git submodule update

# Build Java parser for kenja
cd parser/java
$MAVEN_BIN assembly:assembly
cd -
cp ${JAVA_PARSER_PATH} kenja/lib/java-parser.jar

# Install kenja
$SUDO $PYTHON_BIN setup.py install
