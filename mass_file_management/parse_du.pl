my %filereps = ();
my %sparse_used =();
my $lastpath="";
use integer;
$|=1;
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

			if ($size =~ /([0-9]*)b([0-9]*)/) {
				$size=$1;
				my $blocks=$2;
				my $used=$blocks*512;
				my $id="$size\t$fname";
				#print "$id -> Sparse Size: $used ($blocks 512 byte blocks) $path\n";
				#print "$size -> Sparse Size: $used ($blocks 512 byte blocks) $path\n";
				if (defined $sparse_used{$id}) {
					if ($used < $sparse_used{$id}) {
						$sparse_used{$id}=$used;
					}
				} else {
					$sparse_used{$id}=$used;
				}	
			}


			my $id="$size\t$fname";
			if (not $fname =~ /.*[.].*/){
				#print "$id '$path'\n";
				#print "$id '$path'\r";
			}
			#print "$id\n";
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
	
sub commify {
	my $input = shift;
	$input = reverse $input;
	$input =~ s/(\d\d\d)(?=\d)(?!\d*\.)/$1,/g;
	return reverse $input;
}

my %extension = ();
for (keys %filereps) {
	if (/([0-9]*)\t.*[.]([[:alnum:]]*)/) {
		$extension{uc($2)}+=$1;
	}
}
for (keys %extension) {
	if ($extension{$_} > 1000000000) {
		print (($extension{$_}/1000000000)."G\t$_\n");
	}
}	
undef %extension;

foreach my $m (0,1,10) {
foreach my $u (0..1) {

my $bytes_raw=0; my $bytes_dedup=0;
my $files_raw=0; my $file_dedup=0;
for (keys %filereps) {
	my $bytes = $_;
	if ($bytes < 1000000000*$m or (not $m)) {
		if (defined $sparse_used{$_} and $u) {
			$bytes = $sparse_used{$_};
			#print "$_ -> $bytes\n";
		}
		#print "$_ $filereps{$_}\n"
		$files_raw   += $filereps{$_};
		$files_dedup += 1;
		$bytes_dedup  += $bytes;  
		$bytes_raw += $filereps{$_}*$bytes;  
		#print "$filereps{$_}\n";
	}
}

$files_raw=commify($files_raw); $bytes_raw=commify($bytes_raw);
$files_dedup=commify($files_dedup); $bytes_dedup=commify($bytes_dedup);


my $fmt="%8s%15s%25s\n";
printf "\n-- USED_SIZE: $u\t LIMIT_TO_GB: $m -- \n";
printf ($fmt, "",      "FILES",      "BYTES");
printf ($fmt, "RAW",   $files_raw,   $bytes_raw);
printf ($fmt, "DEDUP", $files_dedup, $bytes_dedup);

}}
