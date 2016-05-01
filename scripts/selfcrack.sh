#!/bin/sh
PURPOSE="Generate passphrases that can be cracked iff you remember part of it"

words_per_phrase=4
[ -e ~/.cache/wordlist.html ] || wget https://en.wiktionary.org/wiki/Wiktionary:Frequency_lists/PG/2006/04/1-10000 -O  ~/.cache/wordlist.html

wordlist=`perl -e 'while(<>){if(/">(.*)<.a><.td>/){print "$1\n"}}' < ~/.cache/wordlist.html | tr -dc '[:alpha:]\n' | tr '[:upper:]' '[:lower:]' |grep -v refwiki| sort | uniq`

randword(){
	#perl -e 'while(<>){if(/">(.*)<.a><.td>/){print "$1\n"}}' < 1-10000 | tr -dc '[:alpha:]\n' | tr '[:upper:]' '[:lower:]' | sort | uniq
	echo "$wordlist" | shuf -n1
}

allmatch(){
(
	base="$1"
	match="$2"
	shift; shift
	if [ -z "$1" ]
	then
		echo "$wordlist" | grep "$match" | while read w
		do
			echo "$base$w"
		done
	else 
		echo "$wordlist" | grep "$match" | while read w
		do	
			allmatch "$base$w-" "$@"
		done
	fi
)
}


case $1 in
g*) #get passphrases
	for i in `seq 1 10`
	do
		for j in `seq 2 $words_per_phrase`
		do
			echo -n `randword`-
		done
		echo    `randword`
	done
	nwords=`echo "$wordlist"|wc -l`
	echo "----\n#words: $nwords	Passphrase Entropy in bits: "`echo "l($nwords)/l(2)*$words_per_phrase" | bc -l | grep -o ^.....`
	
;;

w*) #wordlist
	echo "$wordlist"
;;

a*) #allmatch
	shift
	allmatch '' "$@"
;;

*)
	echo === Self Crack v0.01 ===
	echo Tend to forget your passphrases?
	echo $PURPOSE.
	echo
	echo usage:  
	echo g: get 10 random passphrases
	echo w: get wordlist
	echo a REGEX1 R2 R3 R4: get all passphrases matching REGEX1-R2-R3-R3
;;
esac
