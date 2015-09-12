mkdir -p /tmp/out
cp * /tmp/out
for f in */*
do 
	cp $f /tmp/out/`echo $f|sed s,/,_,`
done

