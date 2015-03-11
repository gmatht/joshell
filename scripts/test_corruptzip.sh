for i in `seq 0 9`; do cp /usr/share/common-licenses/GPL-2 $i.txt; done
zip a.zip *.txt
cp a.zip b.zip; dd if=/dev/urandom of=b.zip bs=512 count=1 seek=100 conv=notrunc; ls *zip -l
mkdir -p out
cd out
unzip ../b.zip
md5sum *.txt
