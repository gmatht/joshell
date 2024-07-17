[ `date +"%Y"` -gt 2023 ] || ntpdate pool.ntp.org
tput setaf 3
setfont sun12x22
clear
while true
do
	D1=`date +"%H:%M %Y"`
	D2=`date +"%a %b %d"`
	S=`date +"%S"`
      	#echo "$D"
	#tput reset
	#T1=`toilet -f bigmono12 -t "$D1"`
	T2=`toilet -f bigmono12 -t "$D1 $D2" | tr '\n' 'n' | sed 's/^[n ]n*//;s/n[n ]*$//;s/n[n ]*n/nnn/g' | tr 'n' '\n' | tee t` #" | grep '[^ ]'`
	#clear
	tput cup 0 0
	#echo "$T1"
	#toilet -f bigmono12 -t "$D1"
	#tput cup 15 0
	echo "$T2"
	tput cup 15 50
	echo "$S"
	#toilet -f bigmono12 -t "$D2"
	#date +"%s"
	if echo $D | grep ' 07:4'
	then
		./m.sh
	fi
	sleep 1
done
