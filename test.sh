GITDIR=$1
previous=""

git --git-dir=${GITDIR} rev-list --topo-order --reverse HEAD | while read line 
do 
	if [ -n "$previous" ]; then
		git --git-dir=${GITDIR} diff-tree -r ${previous}..${line} | while read line;
		do
			fpath=`echo $line | cut -d ' ' -f 6`
			ext="${fpath##*.}"
			if [ $ext = "java" ]; then
				echo $line | cut -d ' ' -f 4
			fi
		done
	fi
	previous=$line
done | sort | uniq

