#This is a perl script to clean up a transcription log, such as one generated with the Windows native Bash command:
#
#while true; do f=`date +'%Y-%m-%d_%H-%M-%S'`.wav ; echo -e "\n" -- READING $f 1>&2 ; timeout 10 D:/bin/fmedia/fmedia --dev-loopback 2 --record -o $f > /dev/null ; echo $f ; done | while read f; do echo -- TRANSCRIBING $f | tee -a transcript ; time whisper.exe --model small.en --language en $f | tee -a transcript ; rm $f ; done

open(FH,'<',"GConTranscript.txt") or die $!;

while(<FH>){
	chomp;
	s/^.00:...... --> ..:.........//;
	s/^\s*//;s/\s*$//;
	s/[.]wav$//;
	s/[.].\n/.\n/;
	s/[.].$/./;
	if(/^you.?.?$/i){next}
	if(/^Thank you.?.?.?$/i){next} 
	if(not /.../){next}
	if(/^ *$/){next}
	$L=$_;
	if ($L=~/^--/) {$ll="\n$L\n"} else {print "$ll$L\n";$ll=""}
}
