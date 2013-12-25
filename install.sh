#!/bin/sh

# if you need to execute python setup script comment as a root, please uncomment following line.
#SUDO=sudo

# maven command
MAVEN_BIN=mvn

# python comand
PYTHON_BIN=python

# location of java-parser created by maven
PARSER_PATH=target/kenja-0.0.1-SNAPSHOT-jar-with-dependencies.jar 

# Build Java parser for kenja
$MAVEN_BIN assembly:assembly
cp $PARSER_PATH kenja/lib/java-parser.jar
$SUDO $PYTHON_BIN setup.py install
