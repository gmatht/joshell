if [ -z $2 ]
then
	echo Usage $0 n_colors n_edges
else
	sed "s/17/$2/g
s/4/$1/g" < nonmono.c > nonmono_.c &&
	gcc nonmono_.c && ./a.out
fi
