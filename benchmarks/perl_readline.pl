$i=0;
while (my $line = <>) {
	$i=$i+1;
	if ($i>1000000) {
		exit();
	}
}

