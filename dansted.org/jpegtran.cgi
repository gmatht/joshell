#!/bin/sh
read -r _
read -r L2
read -r _
read -r _
FNAME=$(printf '%s' "$L2" | sed 's/.*filename="//;s/".*//;s/.jpg$//;s/.jpeg$//i' | tr -cd '[:alnum:]_')_lossless.jpg
printf 'Content-Type:application/octet-stream; name="%s"\n' "$FNAME"
printf 'Content-Disposition: attachment; filename="%s"\n\n' "$FNAME"
firejail --quiet --net=none --blacklist=/boot --blacklist=/chroot --blacklist=/chroot24.04 --blacklist=/dev --blacklist=/etc --blacklist=/home --blacklist=/install --blacklist=/lost+found --blacklist=/media --blacklist=/mnt --blacklist=/opt --blacklist=/proc --blacklist=/root --blacklist=/run --blacklist=/sbin --blacklist=/snap --blacklist=/srv --blacklist=/sys --blacklist=/tmp --blacklist=/var jpegtran -progressive 2> /dev/null
