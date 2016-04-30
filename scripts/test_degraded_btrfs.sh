set -xe
if [ ! `whoami` = root ]
then
	echo run as: "sudo bash $0"
	exit 1
fi 

for raid in single raid1 raid0
do
	mountpoint /mnt/btrfs && umount /mnt/btrfs
		
	[ -e 1.btrfs ] && rm ?.btrfs
	truncate -s 2G 1.btrfs; truncate -s 2G 2.btrfs
	(losetup -d /dev/loop1; losetup -d /dev/loop2) || true
	sleep 0.3
	mkfs.btrfs -m raid1 -d $raid 1.btrfs 2.btrfs 
	(losetup -d /dev/loop1; losetup -d /dev/loop2) || true
	sleep 0.3
	(losetup -d /dev/loop1; losetup -d /dev/loop2) || true
	losetup /dev/loop2 2.btrfs; losetup /dev/loop1 1.btrfs; mount /dev/loop1 /mnt/btrfs/
	for i in `seq 10 15` 20 26
	do
		siz=$((2**i))
		dd if=/dev/zero bs=$siz count=1 of=/mnt/btrfs/$i.$raid.zero
		#dd if=/dev/zero bs=$((siz-1)) count=1 of=/mnt/btrfs/$i.-1.$raid.zero
		#dd if=/dev/zero bs=$((siz-8)) count=1 of=/mnt/btrfs/$i.-8.$raid.zero
		dd if=/dev/zero bs=$((siz-64)) count=1 of=/mnt/btrfs/$i.-64.$raid.zero
		siz=$((siz*2))
	done
	(
		ls /mnt/btrfs -l
		echo ----- Drive 1: $raid ----
		sync; umount /mnt/btrfs; sleep 0.1; losetup -d  /dev/loop1; sleep 0.1; sudo mount -o degraded,ro /dev/loop2 /mnt/btrfs/; md5sum /mnt/btrfs/* || true
		echo ----- Drive 2: $raid  ----
		sync; umount /mnt/btrfs; sleep 0.1; losetup /dev/loop1 1.btrfs; losetup -d  /dev/loop2; sleep 0.1; sudo mount -o degraded,ro /dev/loop1 /mnt/btrfs/; md5sum /mnt/btrfs/* || true
	) 2>&1 | tee out.$raid.txt
	sleep 0.3
done
