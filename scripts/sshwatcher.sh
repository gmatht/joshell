#!/bin/sh
SECS_PER_CYCLE=9
NET_WAIT_COUNT_MAX=3
####################
NET_WAIT_COUNT=0


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
ip route get 8.8.8.8 2> /dev/null | head -1 | cut -d' ' -f8
}

PREV_IP=`getip`
while true
do
	NEW_IP=`getip`
	if [ "$PREV_IP" != "$NEW_IP" ]
	then
		if [ -z "$NEW_IP" -a "$NET_WAIT_COUNT" -lt "$NET_WAIT_COUNT_MAX" ]
		then
			echo "Waiting for network to come up ($NET_WAIT_COUNT/$NET_WAIT_COUNT_MAX)"
			NET_WAIT_COUNT=$((NET_WAIT_COUNT+1))
		else
			if [ -z "$PREV_IP" ]
			then
				echo Connected to Network "IP=$NEW_IP".
			else
				echo IP address changed "($PREV_IP->$NEW_IP)", killing SSH sessions.
				pkill -x ssh
				sleep 1 
				pkill -9 -x ssh
			fi
			PREV_IP="$NEW_IP"
		fi
	else
		NET_WAIT_COUNT=0
		#echo no change "($PREV_IP->$NEW_IP)".
	fi
	sleep 9
done
