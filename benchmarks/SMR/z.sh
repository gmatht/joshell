for f in `ls | sort` `ls */attic_stats.txt | sort` `ls */attic_time1` `*/attic_time2`
do
	[ -d $f ] || (
		echo
		echo [[[[[ $f ]]]]]
		cat $f
	)
done | tee ~/all_benchmarks.txt
