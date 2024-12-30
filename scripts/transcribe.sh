#!/bin/bash
# To install dependancies:
# sudo apt install ffmpeg
# sudo pip install --break-system-packages openai-whisper
# Tested under Mint 22, does not work under WSL

function clean_up {
	kill $RECORD_PID
	#pkill pw-record
	exit
}

trap clean_up SIGHUP SIGINT SIGTERM

(
mkdir -p tmp
while true
do
        F=`date +%Y%m%d_%H%M%S`.wav
        timeout 15 pw-record -P '{ stream.capture.sink=true }' tmp/$F
        mv tmp/$F .
done
)&
RECORD_PID=$!

mkdir -p bak
while true
do
        ls -rt *.wav 2>/dev/null | while read L
        do
                echo "$L: "
                nice whisper --model tiny.en "$L" 2> /dev/null | tee "$L".txt && rm "$L"
                mv "$L" bak 2> /dev/null
        done 
        echo -n '.'
        sleep 1
done 
wait $RECORD_PID
