%sizes=();


sub human {
  $n = @_[0];
  $i=0;
  while ($n>1024) {$n/=1024; $i++;};
  $f = $i==0 ? "d" : ".2f"; 
  return sprintf("%$f%s", $n, qw(b K M G T P E Z Y)[$i])
}

sub display {
	my $union=@_[0];
	my $a=@_[1];
	my $b=@_[2];
	my $intersect=$sizes{$a}+$sizes{$b}-$union;
	my $b_only=$sizes{$b}-$intersect;
	my $a_only=$sizes{$a}-$intersect;
	if ($sizes{$b}<1) {exit 1;}
	my $a_human=human($sizes{$a});
	my $b_human=human($sizes{$b});
	use integer;
	my $b_percent=(100*$b_only)/$sizes{$b};
	my $a_percent=(100*$a_only)/$sizes{$a};
	print "$a_percent%\t$b_percent\t$a_human\t$b_human\t$a\t$b\t$union\t$sizes{$a}::$sizes{$b}\n";
}

while (<>) {
	my $L=$_;
	$L=~s/,//g;
	if ($L=~/DEDUP (?<files>.*) (?<bytes>.*) (?<a>.*) (?<b>.*)/) {
		#`print "$+{a} -- $+{b}\n";
		display($+{bytes},$+{a},$+{b});
	} elsif ($L=~/DEDUP (?<files>.*) (?<bytes>.*) (?<a>.*)/) {
		$sizes{$+{a}}=$+{bytes};
		#print "$L XXX\n";
	} else {
	}
}
		
