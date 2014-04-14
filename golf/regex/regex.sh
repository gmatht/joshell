set -e
grep -v '^#' < r2.py > r_temp.py
rm r_temp.txt
t() {
	echo -------------------------------- >> r_temp.txt
	echo "$@" >> r_temp.txt
	python r_temp.py "$@" >> r_temp.txt
}

t '.*' 1
t 'w\w+' 3
t 'w\[+' 3
t '[abx-z][^ -}][\\]' 3
t 'ab*a|c[de]*' 3
t '(foo)+(bar)?!?' 6
t '(a+|b*c)d' 4
t 'p+cg' 4
t 'a{3}' 4

diff regex_good.txt r_temp.txt && (
	echo GOOD
	wc r_temp.py
	cp r2.py regex.py
	gedit r_temp.py
)
