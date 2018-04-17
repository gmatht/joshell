#Unzip stellaris 2.0 savegame. run as 
#   perl stellaris_terraforming_candidate.pl < gamestate
#Finds terraforming candidates

use strict;

=for
Looks for worlds like the following

      751={
                name="Despad VI"
                planet_class="pc_barren_cold"
                coordinate={
                        x=-141.405
                        y=-85.140
                        origin=24
                }
                orbit=165.000
                planet_size=22
                bombardment_damage=0.000
                last_bombardment="1.01.01"
                timed_modifier={
                        modifier="terraforming_candidate"
                        days=-1
                }

=cut

our $key;
our $val;
our $L;

our $name="";
our $val;
our $size;

our %dispatch = (
	name => sub { $name=$val; $name=~s/[",]//g },
	planet_size => sub { $size=$val },
	modifier => sub { if ($val =~ /terraforming.candidate/) { print "$size, $name\n" } },
	tech_status => sub { # Once we reach this tag we have finished parsing planets and stars
		exit;
	}

);

my $line;
while(<>){
	chomp;
	if (/^	*([0-9a-z_]*)=(.*)/){
		$key=$1;
		$val=$2;
		my $f=$dispatch{$key};
		if (defined $f){$f->()}
	}
}
