#!/bin/bash
#read -r L
#LAST_WORD="`echo $L | sed s/\ *$// | sed s/.*\ //`"
WORD="$1"
case $WORD in
==|eq|\!=|ne|\<|lt|\>|gt|\<=|le|\>=|ge) cat <<EOF
Numeric    String         Meaning
==            eq           equal
!=            ne           not equal
<             lt           less than
>             gt           greater than
<=            le           less than or equal
>=            ge           greater then or equal
EOF
	;;
	*) (echo -- "$WORD" --- ; perldoc -v "$WORD" || perldoc -f "$WORD") 2>&1 | more
	;;
esac



