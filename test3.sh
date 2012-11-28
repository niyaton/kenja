previous=""
cd ./historage
git --git-dir=../.git rev-list --topo-order --reverse HEAD | while read line 
do 
	echo $line
	if [ -n "$previous" ]; then
		git --git-dir=../.git diff-tree -r ${previous}..${line} | while read line2;
		do
			fpath=`echo $line2 | cut -d ' ' -f 6`
			ext="${fpath##*.}"
			if [ $ext = "java" ]; then
				old_id=`echo $line2 | cut -d ' ' -f 3`
				new_id=`echo $line2 | cut -d ' ' -f 4`
				change=`echo $line2 | cut -d ' ' -f 5`

				dirname=`dirname ${fpath}`

				#echo $change
				if [ $change = "D" -o $change = "M" ]; then
					rm -rf ${fpath}
					git rm -rf ${fpath}
					#echo git rm -r ${fpath} 
				fi

				if [ $change = "D" ]; then
					continue
				fi

				#echo mkdir ${dirname}
				mkdir -p ${dirname}

				#echo cp -R ../syntax-trees/${new_id} ${fpath}
				cp -R ../syntax-trees/${new_id} ${fpath}
				git add -N $fpath 

				#echo git add $fpath
				#echo git add "$fpath"
				#git add "$fpath"
			fi
		done

		wait

		#echo git add .
		#echo git commit -a -m $line

		#echo git commit -m $line

		#git add .
		#git commit -a -m $line

		echo git commit -m $line
		git commit -a -m $line --quiet
	fi
	previous=$line
done

