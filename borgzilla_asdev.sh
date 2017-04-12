DEST="/media/gandalf/Seagate Expansion Drive/v11.borg"
DEST="/media/sf_v11.borg"

DISK=$1
DIR=`pwd`

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

	TYPE=""
	eval $(sudo blkid $DEVICE | grep -o 'TYPE="[^"]*"')
	mkfifo $MNT/$LABEL.img
	if command -v partclone.$TYPE 
	then
		C="echo $DEVICE; partclone.$TYPE -D -s $DEVICE -L /tmp/junk -o - | 
			grep ^0x.*0x |
			$DIR/unrescue 3< $DEVICE | pv > $MNT/$LABEL.img"
		echo "$C"
		xterm -e "$C; sleep 5" &
	elif [ "$TYPE" = swap ]
	then
		echo FIXME: Ignoring swap partition
		rm $MNT/$LABEL.img
	elif [ "$TYPE" = dos ]
	then
		echo Ignoring extended partition.
		rm $MNT/$LABEL.img
        else 
		xterm -e "dd if=$DEVICE | pv >  $MNT/$LABEL.img" &
	fi
done

dd if=$DISK of=$MNT/0_1MB.img bs=1024 count=1024
sfdisk -d $DISK > $MNT/0.part_table

ls $MNT/*

eval $(udevadm info --query=property --name=$DISK | grep ^ID_SERIAL=)
echo PRESS ANY KEY TO BACKUP $MNT
#echo borg clone $MNT "$DEST::$ID_SERIAL-{now:%Y-%m-%dT%H:%M:%S}"
read
borg create --read-special -s -p -C auto,zlib "$DEST::$ID_SERIAL-dev-{now:%Y-%m-%dT%H:%M:%S}" $MNT
wait


rmdir $MNT
#borg clone
