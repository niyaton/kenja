#!/bin/bash - 
#===============================================================================
#
#          FILE:  setup_historage.sh
# 
#         USAGE:  ./setup_historage.sh 
# 
#   DESCRIPTION:  
# 
#       OPTIONS:  ---
#  REQUIREMENTS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR: Kenji Fujiwara (), kenji-f@is.naist.jp
#       COMPANY: NAIST
#       CREATED: 10/08/12 07:26:34 JST
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error

rm -rf historage
mkdir historage
cd historage
git init
