NUM_RUNNING=`ps x | grep '/bin/sh.*sshwatcher.sh' | fgrep -v "D+" | wc -l`
#NUM_RUNNING=`ps x | grep '/bin/sh.*sshwatcher.sh' | fgrep -v "D+" |tee swlog.tmp | wc -l`
ps x | grep sshwatcher.sh
echo $NUM_RUNNING

# 3, 1 for this one, 2 for grep, 3 to work around nohup related bug 
if [ "$NUM_RUNNING" -gt 3 ]
then
	echo Another Watcher is running, exiting.
	exit
fi

echo running

getip(){
ip route get 8.8.8.8 | head -1 | cut -d' ' -f8
}

PREV_IP=`getip`
while true
do
	NEW_IP=`getip`
	if [ "$PREV_IP" != "$NEW_IP" ]
	then
		echo IP address changed "($PREV_IP->$NEW_IP)", killing SSH sessions.
		pkill ssh
		sleep 1 
		pkill -9 ssh
		PREV_IP="$NEW_IP"
	#else
		#echo no change "($PREV_IP->$NEW_IP)".
	fi
	sleep 9
done
