#!/usr/bin/perl
# Usage: du.pl OUTPUT_FILE DIRECTORY PREFIX

#use File::MountPoint qw( is_mountpoint );
use Time::Local 'timegm';
use File::Spec;
use Fcntl ':mode';
use POSIX qw(strftime);
use Cwd;
use File::Copy;
use strict;
use warnings;
use integer;

our $d_dev;

my $output_file="tmp_out";

$|=1; #Buffering does not play well with "\r"

my $orig_cwd = getcwd;
my $base_prefix="";

if ($#ARGV>=0) {
	$output_file=$ARGV[0];
}

open (my $out_fh, "| /bin/gzip -c > $output_file.tmp.gz") or die "error starting gzip $!";

my @SCAN_DIRS;
if ($#ARGV>=1) {
	@SCAN_DIRS=@ARGV;
	shift @SCAN_DIRS;
} else { 
	@SCAN_DIRS='.'
}

#if ($#ARGV>=1) {
#	chdir $ARGV[1] || die "Cannot enter starting directory $ARGV[1]";
#	print "Entered directory $ARGV[1]";
#	if ($#ARGV>=2) {
#		if ($#ARGV>=3) {
#			print "Too many arguments\n";
#			exit 1;
#		}
#		$base_prefix=$ARGV[2];
#	} else {
#		$base_prefix=$ARGV[1];
#	}
#}

our $count=0;
our $total_du=0;
sub parse_dir{
	my $prefix=$_[0];
	#print "$prefix\n";
	#my $d_dev=-1;
	#my $d_dev=$_[1];
	opendir(my $dh, ".") or die "cannot open directory $prefix";

	my $file;
	while(defined($file = readdir($dh))) {
		#print "$file\n";
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
				if ($blocks>0){
					my $du=$blocks*512;
					$total_du+=$du;
					#print "FILE: $prefix$file size=$size du=$du blocks=$blocks blksize=$blksize mtime=$mtime\n"
					#my $time=strftime("%Y-%m-%d %M:%S", gmtime($mtime));
					#my $time=strftime("%Y-%m-%d %H:%M:%S", gmtime($mtime));
					#my $time=strftime("%Y%m%d %H%M%S", localtime($ctime));
					my $time=$mtime;
					#print ".";
					if ($du<$size){
						print $out_fh $size."b$blocks	$time	$prefix$clean_fname\n";
					} else {
						print $out_fh "$size	$time	$prefix$clean_fname\n";
					}
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
	 			if ($dev == $d_dev or $file =~ /^@/ or 1) {
			  		#not a mountpoint
					#If file starts with "@", probably a btrfs subvolume
					#chdir is about 2x as fast as referencing long paths
					if (chdir $file) {
						parse_dir("$prefix$clean_fname/",$dev);
						chdir ".."  || die "couldn't change the directory to $prefix$clean_fname/..";
					} else {
						print "Couldn't change the directory to $prefix$clean_fname/ !!!\n";
						#|| die "couldn't change the directory to $prefix$clean_fname/";;
					}
				} else {
					#print "Avoiding mountpoint $prefix$clean_fname/\n";;
				}
			}
		}
	}
	close $dh;
}

# foreach loop execution
# foreach $a (@list){
#     print "value of a: $a\n";
#     }
foreach my $D (@SCAN_DIRS){
	if ($D eq "" or $D eq ".") {
		$base_prefix="";
	} else {
		chdir $D || die "Cannot enter starting directory $D";
		$base_prefix=$D;
		$base_prefix=~s!/*$!/!; #Add trailing slash;
	}
	($d_dev,my $d_ino,my $d_mode,my $d_nlink,my $d_uid,my $d_gid,my $d_rdev,my $d_size, my $d_atime,my $d_mtime,my $d_ctime,my $d_blksize,my $d_blocks) = lstat(".");
	print "du: $D $base_prefix\n";
	parse_dir($base_prefix);
	chdir $orig_cwd || die "Cannot return to original directory: $orig_cwd";
}
close $out_fh;
move("$output_file.tmp.gz", "$output_file.gz");
