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

processes=0
while read line 
do
	git show $line | java -cp ../kenja-0.0.1-SNAPSHOT-jar-with-dependencies.jar jp.naist.sd.kenja.factextractor.ASTGitTreeCreator ./syntax-trees/$line &
	echo $processes
	if [ $processes -ge 16 ]; then
		wait
		processes=0
	fi
	processes=$(($processes + 1))
done < blobs
