my %filereps = ();
my $lastpath="";
while (my $line = <>) {
	if ($line =~ /([^\t]*)\t([^\t]*)\t([^\n\r]*)/) {
		my $size=$1; my $date=$2; my $path=$3;
		my $isdir=0;
		if ((substr $path, -1) eq "/") {
			print "$path ENDS IN SLASH\n";
			$isdir=$1;
		} elsif (length($path) < length($lastpath) or $path =~ /.*[\/]$/ ) {
			if (substr($lastpath,0,length($3)+1) eq  "$path/") {
				$isdir=1;
			}
		}
		#print "$1\t$2\t$e 
		#print "$3";
		if (not $isdir) {
			my $fname=$path;
			$fname=~ s/.*\///;
			my $id="$size\t$fname";
			if (not $fname =~ /.*[.].*/){
				print "$id '$path'\n";
			}
			print "$id\n";
			$filereps{$id}++;

			#print "/";
		}
		#print "\n";
		#print("$isdir:$3, $lastpath <- $3\n");
		$lastpath=$path;
	} else {
		print "ERROR: $line\n";
	}
	
}
	

my $bytes_raw=0; my $bytes_dedup=0;
my $files_raw=0; my $file_dedup=0;
for (keys %filereps) {
	#print "$_ $filereps{$_}\n"
	$files_raw   += $filereps{$_};
	$files_dedup += 1;
	$bytes_dedup  += $_;  
	$bytes_raw += $filereps{$_}*$_;  
	#print "$filereps{$_}\n";
}

printf "$files_raw\t$bytes_raw\n";
printf "$files_dedup\t$bytes_dedup\n";

