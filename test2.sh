#!/bin/bash - 
#===============================================================================
#
#          FILE:  test2.sh
# 
#         USAGE:  ./test2.sh 
# 
#   DESCRIPTION:  
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR: Kenji Fujiwara (), kenji-f@is.naist.jp
#       COMPANY: NAIST
#       CREATED: 10/05/12 12:37:35 JST
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

KENJA_PARSER="./kenja-0.0.1-SNAPSHOT-jar-with-dependencies.jar"
KENJA_EXEC="${KENJA_PARSER} jp.naist.sd.kenja.factextractor.ASTGitTreeCreator"
GITDIR=$1

processes=0
while read line 
do
	git --git-dir=$GITDIR show $line | java -cp ${KENJA_EXEC} ./syntax-trees/$line &
	echo $processes
	if [ $processes -ge 10 ]; then
		wait
		processes=0
	fi
	processes=$(($processes + 1))
done < blobs
