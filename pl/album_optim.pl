#Optimize photo album created by 'album'                                                                                                                                                                                                                    #usage: for f in *.html; perl album_optim.pl < $f > new/$f ; done

my @arr;

while(<>){
        if(/href='([^']*.JPG.html)'/){
                push (@arr, $1)
        }
        if(/^<.html>/){
                print "<link rel='prefetch' href='$arr[1]'>";
                $j = $arr[1] =~ s/.JPG.html$/.med.JPG/r;
                print "<link rel='prefetch' href='$j'>";
                print "<link rel='prefetch' href='$arr[2]'>";
                $j = $arr[2] =~ s/.JPG.html$/.med.JPG/r;
                print "<link rel='prefetch' href='$j'>";
                #print "$arr[1] $arr[2] $_";
        }
        print $_;
}
