cat <<"EOF"|sed s/E/`echo -e '\E'`/>simon_golf.sh;bash simon_golf.sh;wc simon_golf.sh
d(){ echo 'Ecx1r09mRx2g10mG
x3y11mYx4b14mBx0m'$s|sed s/.$1"//
s/[rgyb]..//g
s/x/E[48;5;/g";};x(){ d $c;espeak $c;d j;};l(){
for c in $o;{ eval $1;x;};};f(){ o=$o\ `tr -dc yrgb</dev/urandom|head -c1`
l;l 'read -n1 i;[ $c = $i ]||exit;let s++';sleep 1;f;};f
EOF

cat <<"EOF" > win10_simon_golf.sh
espeak(){
        /mnt/c/Windows/SysWOW64/WindowsPowerShell/v1.0/PowerShell.exe -Command "Add-Type –AssemblyName System.Speech; (New-Object System.Speech.Synthesis.SpeechSynthesizer).Speak('$1');"
}
EOF
cat simon_golf.sh >> win10_simon_golf.sh
