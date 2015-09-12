set -e
set -x
echo begin
mkdir -p /mnt/Benchmarks
umount /mnt/Benchmarks || true
echo 0 > /proc/sys/kernel/randomize_va_space
#for fs in ext4 xfs btrfs nilfs2
#for fs in xfs btrfs nilfs2
for fs in nilfs2
do
for vol in SMR Toshiba
do
	mkfs.$fs -f /dev/vg0/Benchmark$vol # -F for ext4 to force overwrite
	mount /dev/vg0/Benchmark$vol /mnt/Benchmarks
	echo mounted $vol $fs
	sleep 4
	for i in `seq 0 2`
	do
		name=$vol.$fs.$i.out
		cd ~john/benchmarks
		echo "TEST	$vol $fs $i"
		filebench -f my_fileserver.f | tee $name
		df | tee $name.df
		time sync 2>&1 | tee -a  $name
	done
	echo unmounting
	sleep 60
	umount /mnt/Benchmarks
	echo unmounted
	sleep 60
done
done
