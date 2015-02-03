#!/bin/bash
#set -e
#export PATH=$PATH:
#if [ ! -e .svn ]
#then

#git diff --name-only HEAD

set -e
set -x

cd

DATE=`date +%F%N`
#ENDECHO_F=`mktemp ge.XXXXXXXXXXXX`
ENDECHO_F=~/ge.$DATE.tmp
endecho(){
	echo "$@" >> $ENDECHO_F
}
	

#Attempts to make sure there are no open files that would prevent a merge
safemerge(){
	#Test if a window title mentions the directory
	#problem: How do we know if there are files open in unactive tabs?
	merge_d=$1 #Relative to home directory, should also be current directory
	#WMCTRL_F=`mktemp gw.XXXXXXXXX` 
	WMCTRL_F=~/gw.$DATE.tmp
	wmctrl -l > $WMCTRL_F
	if egrep "(~|$HOME)/$merge_d/" < $WMCTRL_F >> $ENDECHO_F
	then
		endecho ^^^ so cancelling safemerge of "$d"
		return 1
	fi

	#*Some* editors store temporary files if they have the file open.
	git diff --name-only FETCH_HEAD | while read -r p
	do
		[[ "$p" == */* ]] || p="./$p"
		d="${p%/*}";
		f="${p##*/}";

		#check for a few different types of temp files (vim, LyX)
		for t in "$uni/$d/.$f.swp" "$uni/$d/#$f#" "$uni/$d/$f~" 
		do
			if [ -e "$t" ]
			then  
				endecho "$uni/$d/.$f.swp exists (open in vim?)"
				return 1
			fi
		done

		if fgrep -- " $f - " < $WMCTRL_F >> $ENDECHO_F
		then
			return 1
		fi
	done
	rm $WMCTRL_F

	#Changes to the bin/ directory could be dangerous. Ask user to confirm.
	if [ ! -z "`git diff --name_only FETCH_HEAD bin/ 2> /dev/null`" ]
	then
		git diff FETCH_HEAD bin/
		echo -n "Merge these changes to bin? " 
		read -r -c1 answer
		if [ ! "$answer" = "y" ]
		then
			echo USER REJECTED MERGE
			exit 1
			return 1
		fi
	fi

	git merge  --no-edit FETCH_HEAD || endecho FAILED: git-merge $merge_d
}
		
if [ -z "$1" ]
then
	# CHANGE THIS DIRECTORY TO BE YOUR GIT DIRECTORIES
	DIRS="gitdir1 gitdir2t "`cd ~/prj && ls -d */.git | sed 's,/.git$,,' | grep -v bak$ |sed s,^,prj/, || echo`
else
	DIRS="$*"
fi 

cached-git-push(){
	HEAD=`git rev-parse HEAD`
	if [ "`cat .g-git-pushed`" = $HEAD ]
	then
		echo repo already pushed
		return 0
	else
		if git push
		then
			echo -n "$HEAD" > .g-git-pushed
			return 0
		else
			return 1		
		fi
	fi
}

for d in $DIRS
do
(if cd ~/$d
then 
#fi
#~/bin/downvert .  
	
	#Autocommit, but not if git directory starts with prj/	
	[[ $d == prj/* ]] || [   -z "`git diff --name-only`" ] || git commit -m "Sync: $HOSTNAME" -a || endecho FAILED: git commit $d
	[[ $d == prj/* ]] && [ ! -z "`git diff --name-only`" ] && endecho "Uncommited changes: $d"

	git fetch || endecho FAILED: git fetch $d
	safemerge $d || endecho FAILED: safemerge $d
	cached-git-push || endecho FAILED: git push $d
#git commit -m "Sync: $HOSTNAME" . && git push
else
	endecho "No such directory $d"
fi
)
done

echo 
echo ----------------------------
cat $ENDECHO_F
rm $ENDECHO_F
