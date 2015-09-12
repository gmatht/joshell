    use Fcntl 'SEEK_SET';
    open(my $fh,"<", "/proc/sys/kernel/random/entropy_avail");
    while (1) { print <$fh>; sleep(1); seek($fh,0,SEEK_SET); }

