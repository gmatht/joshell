#use File::MountPoint qw( is_mountpoint );
use Time::Local 'timegm';
use File::Spec;
use Fcntl ':mode';
use POSIX qw(strftime);
use integer;

my $output_file="tmp_out";

$|=1;

use strict;
use warnings;

open (my $out_fh, "| /bin/gzip -c > $output_file.gz") or die "error starting gzip $!";

(our $d_dev,my $d_ino,my $d_mode,my $d_nlink,my $d_uid,my $d_gid,my $d_rdev,my $d_size, my $d_atime,my $d_mtime,my $d_ctime,my $d_blksize,my $d_blocks) = lstat(".");
our $count=0;
our $total_du=0;
sub parse_dir{
	my $prefix=$_[0];
	#my $d_dev=-1;
	#my $d_dev=$_[1];
	opendir(my $dh, ".") or die "cannot open directory $prefix";

	my $file;
	while(defined($file = readdir($dh))) {
		(my $dev,my $ino,my $mode,my $nlink,my $uid,my $gid,my $rdev,my $size, my $atime,my $mtime,my $ctime,my $blksize,my $blocks) = lstat($file);

		if (not defined $mode) {
			print "NOT DEFINED: $prefix$file\n";
			next;
		}

		if (not S_ISLNK($mode)) {
		#if (not -l $file) {
			$count++;
			my $clean_fname=$file;
			#$clean_fname=~tr/[\x20-x7e]/!/c; #Replace weird characters with !
			$clean_fname=~tr/[ -~]/!/c; #Replace weird characters with !
		
#			if ($count>255) {
#				print substr( $prefix."                 ", 0, 70 )."\r";
#				$count=0;
#				#printf "%70s\r", $prefix;
#			}
			#my $fname="$prefix$file";
			if (S_ISREG($mode)) {
				my $du=$blocks*512;
				$total_du+=$du;
				#print "FILE: $prefix$file size=$size du=$du blocks=$blocks blksize=$blksize mtime=$mtime\n"
				#my $time=strftime("%Y-%m-%d %M:%S", gmtime($mtime));
				#my $time=strftime("%Y-%m-%d %H:%M:%S", gmtime($mtime));
				#my $time=strftime("%Y%m%d %H%M%S", localtime($ctime));
				my $time=$mtime;
				if ($du<$size){
					print $out_fh $size."u$du	$time	$prefix$clean_fname\n";
				} else {
					print $out_fh "$size	$time	$prefix$clean_fname\n";
				}
					
			} elsif (S_ISDIR($mode)) {
				if ( -l $file ) { die "????"; }
				next if $file eq '.';
				next if $file eq '..';
				if ($count>1023) {
					#print "\r".substr( $prefix."_________________________________________", 0, 70 )."\r";
					#print "\r".substr( $prefix."_________________________________________", 0, 70 );
					print "\r".substr( ($total_du/1000000)." $prefix                                         ", 0, 70 );
					$count=0;
				}
				#if ($d_dev==-1) {
				#        ($d_dev,my $d_ino,my $d_mode,my $d_nlink,my $d_uid,my $d_gid,my $d_rdev,my $d_size, my $d_atime,my $d_mtime,my $d_ctime,my $d_blksize,my $d_blocks) = stat(".");
				#}
	 			if ($dev == $d_dev) {
			  		#not a mountpoint
					chdir $file || die "couldn't change the directory to $prefix$clean_fname/";;
					parse_dir("$prefix$clean_fname/",$dev);
					chdir ".."  || die "couldn't change the directory to $prefix$clean_fname/..";
				}
			}
		}
	}
	close $dh;
}

parse_dir("");
