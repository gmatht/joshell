#!/bin/bash
#Script to manage your Fractured Space settings files.
#It should load the correct players settings (and crew) 
#before starting Fractured Space.
#
#Players are identified by first letter of email address
#(It assumes these are distinct)
#
#To automatically login, you will need to create a file c.login
#where c is the first letter of the players email address
#the file should have a singe line of format:
#USERNAME PASSWORD
#
#Ideally git should be installed. You may want to set up a remote.
#
#To run it easily, you will want to setup a shortcut with a target like:
#   C:\cygwin64\bin\bash.exe /home/Al/FracturedSpace/fsloader.sh
#
#At a minimum you will need to modify the following two lines:
CONFIG=/cygdrive/c/Users/Al/AppData/Local/spacegame/Saved/Config/WindowsNoEditor/GameUserSettings.ini
BACKUP_DIR=/home/Al/FracturedSpace 
#HOME=/home/Al

PATH=/usr/bin:/bin
PATH="/cygdrive/c/Users/Al/bin/sysinternals:${HOME}/bin:${PATH}"

cd "$BACKUP_DIR"

set -x

owner=unknown
owner_str=$(grep ^Email= $CONFIG | sed s/^Email=// | tr -d \\r\\n )
owner=$(echo $owner_str | grep -o ^.)
echo "Current Owner is $owner_str ($owner)"

BACKUP=$owner.ini

if [ $CONFIG -nt $BACKUP -o ! -e $BACKUP ]
then	
	if grep Name $CONFIG | grep -qv "The Starter Crew"
	then 
		echo found crews
		echo backing up
		cp -p $CONFIG $BACKUP
	
		# Use version control, so we can bring back old crew
		if [ ! -e .git ]
		then
			echo git not initialised, press any key to initalise
			echo if you want remote backup, you will have to set that up yourself
			echo in the repository at $BACKUP_DIR/.git
			read -n 1 c
			git init
		fi
		git add $BACKUP backup.sh
		git commit -a -m "Sync $owner"
		git pull
		git push
	else
		echo Only Starter Crew?
		echo Corrupted or nothing to back up.
	fi 
fi

echo -n "Who will next play [ng]: "

read -n 1 c
cp -p $c.ini  $CONFIG || (
	echo restore of $c.ini failed
	read
)

if pslist steam; then
  cat <<PROMPT

  Press k to kill running games and start Fractured Space

  Press any other key to start Fractured Space
  (Logout of steam first!)
PROMPT
  read -n 1 d

  case "$d" in
	k|K)	pslist TimeClickers && pskill TimeClickers
	  	pslist itrtg && pskill itrtg
	  	pslist steam && pskill steam
		;;
	*)	pslist steam && echo "$0: Steam running, trying anyway?" 1>&2
  esac
fi

cd '/cygdrive/c/Program Files (x86)/Steam/' || echo "$0: Could not change to Steam executable dir" 1>&2

LOGIN=$BACKUP_DIR/$c.login

if [ -e $LOGIN ]
then
	./Steam.exe -login $(cat $LOGIN)  -applaunch 310380
	# Properties -> General -> Set launch options -> "-autostart"
else
	echo "'$LOGIN'" does not exist
	echo It should contain one line like:
	echo "username password"
	echo
	read
fi

# If a crew called Battle has gone missing, restore with something like:
# First find the revisions it was in with:
# git reflog |  awk '{ print $1 }' | while read f; do git show $f g.ini | grep Battle > /dev/null && echo $f; done
# then
#  git show 66acbc8 g.ini > g.ini
# git reflog |  awk '{ print $1 }' | while read f; do git show $f:g.ini | grep Battle > /dev/null && echo $f; done | head -n 1 | (read r; git show $r:g.ini > g.ini)
