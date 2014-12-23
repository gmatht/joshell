if [ -z $2 ]
then
	echo Usage $0 n_colors n_vertices
else
	sed "
s/17/n_vertices/g
s/4/$1/g
s/n_vertices/$2/g
" < nonmono.c > nonmono_.c &&
	gcc -O3 nonmono_.c && ./a.out
fi
