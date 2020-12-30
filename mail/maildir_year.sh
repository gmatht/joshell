
#src=~/"Mail/[Gmail]"
#dest=/mnt/Mail/Other
src=~/"Mail/Inbox"
dest=/mnt/Mail/Inbox
cd "$src"
echo STARTING
find . | maildir_year.pl | tee .byyear
cut -f 1 .byyear -d\ | sort -u | while read year
do
	echo processing year $year
	grep "^$year" .byyear | sed s/^.....// | tar -z -c -f $dest$year.tgz -T -
done

