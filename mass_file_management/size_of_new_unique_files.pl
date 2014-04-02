#!/usr/bin/perl
# A Perl script to filter out directories from the output of `du -ab'
# and optionally find how many many MB would be used by the new files
our $last_Dfiname="";
our $new_files=0;
our $total_new_bytes=0;

our %existing_files=();
sub get_id {
	$siz=$1;
	$name=$4;
	$name=~s/.*\///;
	$name=uc($name);
	return "$siz $name\n";
}

sub commify {
   my $input = shift;
   $input = reverse $input;
   $input =~ s/(\d\d\d)(?=\d)(?!\d*\.)/$1,/g;
   return reverse $input;
}	

sub testf {
	$id=get_id $_;
	if (!exists $existing_files{$id}) {
		$existing_files{$id}=();
		if ($new_files) {
			print "$1\t$4\n";
			our $total_new_bytes+=int($1);
		}

	} else {
	}
		
}


sub process_file {
open (FILE, "<", $_[0]) or die "Cannot open $_[0].";
while (<FILE>) {
	if ( $_ =~ /([0-9]*).*(....-..-..)([^\t]*)\t(.*)/) {
		$Dfname = $4;
		$Dfnames = "$4/";
		if (substr($last_Dfname,0,length($Dfnames)) eq $Dfnames) {
			#print "\n$1,$4/";
		} else {
			testf $_;
			#print "\n$1,$4";
		}
		$last_Dfname=$Dfname;
	} else {
		print ".";
	}
}
close FILE;
}

if ($#ARGV<1) {
print "
A Perl script to figure out how any MB would be used if we import
all new unique files

Usage: $0 oldlist0 oldlist1 ... -n newlist1 newlist2 ...

The '-n' option is used to seperate the old list from the new lists.
The lists are lists of file generated by the command:
	du -ab
"

$last_Dfiname="";

foreach (@ARGV) {
	print "Processing Argument $_\n";
	if ($_ eq "-n") {
		$new_files=1;
	} else {
		process_file ($_);
	}
	#print STDERR "TOTAL: " + commify ($total_new_bytes);
}
$mb=int($total_new_bytes/1024/1024);
$mb=commify($mb);
print "\nTOTAL: $mb MB\n";