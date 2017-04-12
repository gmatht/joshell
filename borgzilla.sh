DEST="/media/gandalf/Seagate Expansion Drive/v11.borg"

DISK=$1

if [ -z "$DISK" ]
then 
	echo Usage: $0 DISK
        ls /dev/sd?
	exit 1
fi


MNT=`mktemp -d /tmp/borgzilla.XXXXXX`
for DEVICE in $DISK?*
do
  PART=$(echo $DEVICE | sed s,^$DISK,,)
  LABEL=$PART
  eval $(blkid $DEVICE | grep -o 'LABEL="[^"]*"' | sed s/=/="$PART"_/)

  #umount $DEVICE
  umount $DEVICE
  mkdir $MNT/$LABEL
  mount $DEVICE $MNT/$LABEL
  
done

dd if=$DISK of=$MNT/0_1MB.img bs=1024 count=1024
sfdisk -d $DISK > $MNT/0.part_table

ls $MNT/*

eval $(udevadm info --query=property --name=$DISK | grep ^ID_SERIAL=)
echo PRESS ANY KEY TO BACKUP $MNT
#echo borg clone $MNT "$DEST::$ID_SERIAL-{now:%Y-%m-%dT%H:%M:%S}"
echo borg create -s -p -C auto,lzma "$DEST::$ID_SERIAL-{now:%Y-%m-%dT%H:%M:%S}" $MNT
read


rmdir $MNT
#borg clone
