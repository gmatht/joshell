#!/bin/bash
cd "$(dirname "$0")"
[ -e idx ] || find . -size +1M | tee idx
amixer set Master 100%
shuf idx 
while read -r f
do
	date +"it is %l:%M %p on %B the %dth at %l:%M %p" | 
		sed 's/1th /1st /g;s/2th /2nd /g;s/3th /3rd /g' |
		tee date.tmp | espeak -a 200
	#echo paplay "$f"
	toilet -t "`date +"%H:%M"` $(echo "$f" | sed s/.*:9000.//)" 
	ffplay -v 0  -nodisp -autoexit "$f" -af "volume=0.6"
	#read -rsn1 k
	echo "$? $f" >> log

done

#find . -size +1M | tee idx
