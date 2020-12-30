#!/usr/bin/env perl
#Usage: find ~/Mail | maildir_filter.pl
use strict;

sub open_file($)
{
    my ($filename) = @_;
    my $fd;
    open($fd, $filename)
        or die "open_file: cannot open $filename";
    return $fd;
}

#my $fh=open_file("/home/john/Mail/\[Gmail\]/Sent\ Mail/cur/1609222432.118929_1801.4kVM-VirtualBox\,U\=1801\:2\,S");
while (my $fn = <>) {
	my $fh=open_file($fn);
	while (<$fh>) {
		if (/^Date: /) {
			#my @a = split / /;
			#print "$a[4] $fn";
			use Date::Parse;
			s/^Date: //;
			 
			my  ($ss,$mm,$hh,$day,$month,$year,$zone) = strptime($_);
			$year+=1900;
			print "$year $fn";
			last;
		}
	}
}
