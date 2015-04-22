use integer;
# Use figures based on gcc LCG
my $a = 1103515245; my $c = 12345; my $m = 2**31;
my $steps = 10000000;

my $friendstr = "amigo";
# Now set the random seed
my $x = 1337;
for (my $i=0; $i < $steps; $i++) {
	# See http://en.wikipedia.org/wiki/Linear_congruential_generator
	$x = (($a * $x + $c) % $m );
}
print "x[ $steps ] = $x, $friendstr!\n";
