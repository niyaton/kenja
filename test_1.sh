processes=0
previous=""
git rev-list --topo-order --reverse HEAD | while read line 
do 
	if [ -n "$previous" ]; then
		git diff-tree -r ${previous}..${line} | while read line2;
		do
			fpath=`echo $line2 | cut -d ' ' -f 6`
			ext="${fpath##*.}"
			if [ $ext = "java" ]; then
				echo $line2 | cut -d ' ' -f 4
			fi
		done &
	fi
	if [ $processes -ge 500 ]; then
		wait
		processes=0
	fi
	processes=$(($processes + 1))
	previous=$line
done | sort | uniq
