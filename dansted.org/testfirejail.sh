rm good.txt
rm bad.txt
OPT="--net=none"
#gCMD=""
ls / | sed 's,^,--blacklist=/,' | while read -r r
do
	echo $r
	CMD="firejail $OPT $r jpegtran-static -progressive"
	echo "$CMD"
	$CMD < /usr/share/doc/php-tcpdf/examples/images/image_demo.jpg > t.tmp
	if file t.tmp | grep JPEG 
	then
		OPT="$OPT $r"
		echo "OPT=$OPT"
		echo "$r" >> good.txt
		gCMD="$CMD"
		echo gCMD $gCMD
	else
		echo "$r" >> bad.txt
	fi
done | tee log
grep gCMD log | tail -n1
#echo "OPT=$OPT"
#echo -- "$gCMD" | tee gCMD.sh
