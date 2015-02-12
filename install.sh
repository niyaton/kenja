#!/bin/sh

# if you need to execute python setup script comment as a root, please uncomment following line.
#SUDO=sudo

# maven command
MAVEN_BIN=mvn

# python comand
PYTHON_BIN=python

# location of java-parser created by maven
JAVA_PARSER_PATH=parser/java/target/kenja-java-parser-0.4-jar-with-dependencies.jar

# root path of python-parser
PYTHON_PARSER_ROOT=parser/csharp

# update submodules for parser
git submodule init
git submodule update

# Build Java parser for kenja
cd parser/java
$MAVEN_BIN assembly:assembly
cd -
cp ${JAVA_PARSER_PATH} kenja/lib/java/java-parser.jar

# Build Python parser for kenja
if type "xbuild" > /dev/null; then
	cd ${PYTHON_PARSER_ROOT}
	xbuild /p:Configuration=Release
	cd -
	cp ${PYTHON_PARSER_ROOT}/bin/Release/* kenja/lib/csharp
else
	echo "xbuild command is not found."
	echo "csharp parser will not be installed to kenja"
	echo "Please install mono from http://www.mono-project.com if you want."
fi

# Install kenja
$SUDO $PYTHON_BIN setup.py install
