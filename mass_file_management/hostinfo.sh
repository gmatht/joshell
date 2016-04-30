echo $HOSTNAME; ifconfig | perl -e 'while(<>){if (/inet addr:([0-9.]*)/){print "$1\n";exit}}'; cat /proc/cpuinfo | grep model.name | head -n1 | sed s/.*:.//
