#!/bin/bash

# These are needed for sounds
command -v ogg123                            || sudo apt-get install vorbis-tools
[ -e /usr/share/aisleriot/sounds/click.ogg ] || sudo apt-get install aisleriot

score=0;
order=""

display_colour () {
	tput reset
	grey='\E[30;37m' ; r=$grey ; g=$grey ; y=$grey ; b=$grey
	e="\033[0m"
	case "$1" in
		r) r='\E[30;41m' ;;
		g) g='\E[30;42m' ;;
		y) y='\E[30;43m' ;;
		b) b='\E[30;44m' ;;
	esac

	for x in `seq 0 9`; do echo -e "$r|RRRRRRRRRRRRRRR|$e|$g|GGGGGGGGGGGGGGG|$e"; done		
	for x in `seq 0 9`; do echo -e "$y|YYYYYYYYYYYYYYY|$e|$b|BBBBBBBBBBBBBBB|$e"; done
	echo
	echo -e "Score: \E[37;44m$score$e"
}

blink_colour () {
	display_colour $1
	(case "$1" in
		r) ogg123 -K1 /usr/share/aisleriot/sounds/click.ogg ;;
		g) ogg123 -K1 /usr/share/aisleriot/sounds/slide.ogg ;;
		y) ogg123 -K1 /usr/share/aisleriot/sounds/splat.ogg ;;
		b) ogg123 -k2 -K3 /usr/share/aisleriot/sounds/victory.ogg ;;
	esac) 2> /dev/null
        sleep 0.2 ; display_colour "null"
}

while true
do
	order="$order `< /dev/urandom tr -dc yrgb | dd bs=1 count=1 2> /dev/null`"
	sleep 0.5
	for c in $order; do blink_colour $c ; sleep 0.5 ; done
	for c in $order
	do
		read -n 1 i > /dev/null 2> /dev/null
		if [ "$c" != "$i" ]
		then
			echo ; echo
			echo "You entered $i, but should have entered $c! Game Over!"
			exit
		fi
		score=$((score+1))
		blink_colour $c
	done
done
