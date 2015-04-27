my %filereps = ();
my %sparse_used =();
my $lastpath="";

our $cache_out_file='';

foreach $a (@ARGV) {
	if ( $a =~ /-c(.*)/ ) {
		$cache_out_file="$1.ofmC1.gz";
		print STDERR "Outputing cache file $cache_out_file\n";
		#open(our $cache_out_fh, ">", "$cache_out_file.new") or die ("Cannot open '$cache_out_file' for writing");
		open(my $cache_out_fh, "|-" , "gzip > $cache_out_file.new") or die "Cannot open Cache pipe :(";
;
}



#use integer;
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
			$path=uc($path); # Ignore Case

# Names of vob files are meaningless, consider parent directory instead:
# Maybe should ensure this doesn't result in fname's longer than 256 bytes
# In the output cache files?
# That could cause problems with Pipes on some OS's?
			$path=~s,/VIDEO_TS/,v,g;

			my $fname=$path;

			$fname=~ s/.*\///;
			# Simplify names down to MS-DOS allowed chars
			# and '+', and '?' for anything not understood.
			$fname=~s/[^[:alnum:]!#%&'()-@^_`{}~\+ ]/?/g;

			my $used=int($size);
			if ($size =~ /([0-9]*)b([0-9]*)/) {
				$size=$1;
				my $blocks=$2;
				$used=$blocks*512;
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

			if ($cache_out_file) {
				printf ($cache_out_fh "%16x%s\0%16x\n", $size, $fname, $used);
			}
			#Sort with ... | LC_ALL=C sort

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
		print (int($extension{$_}/1000000000)."G\t$_\n");
	}
}	
undef %extension;

foreach my $m (0,0.0001,0.001,1,10) {
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

if ($cache_out_file) {
	rename ("$cache_out_file.new", $cache_out_file);
}
}}
