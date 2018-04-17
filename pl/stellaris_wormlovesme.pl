#Unzip stellaris savegame. run as 
#   stellaris_wormlovesme < gamestate
#Finds habitiable systems with lots of worlds of size 10..25 for the worm to love
#Note: doesn't exclude gas giants

use strict;

our @p2s=[]; #Planet to system
our @nplanets=[];
our @system_name=[];
our $key;
our $val;
our $star=0;
our $id;
our @hashab=[];
our $L;
our $star;
our %ishab= (
	pc_a_star => 0,
	pc_alpine => 1,
	pc_arctic => 1,
	pc_arid => 1,
	pc_asteroid => 0,
	pc_b_star => 0,
	pc_barren => 0,
	pc_barren_cold => 0,
	pc_black_hole => 0,
	pc_broken => 0,
	pc_continental => 1,
	pc_desert => 1,
	pc_f_star => 0,
	pc_frozen => 0,
	pc_g_star => 0,
	pc_gaia => 1,
	pc_gas_giant => 0,
	pc_k_star => 0,
	pc_m_star => 0,
	pc_molten => 0,
	pc_neutron_star => 0,
	pc_nuked => 1,
	pc_ocean => 1,
	pc_pulsar => 0,
	pc_savannah => 1,
	pc_toxic => 0,
	pc_tropical => 1,
	pc_tundra => 1,
);


our %dispatch = (
	planet => sub { $p2s[$val]=$id; },
	planet_size => sub{if($val>=10 and $val<=25){$nplanets[$p2s[$id]]++}},
	type => sub { if ($val == "star") { $star=1; } },
	name => sub { if ($star) { $system_name[$id] = $val; } },
	planet_class => sub { $val =~ s/[",]//g; if (%ishab{$val}) {$hashab[$p2s[$id]]=1}},
	tech_status => sub { # Once we reach this tag we have finished parsing planets and stars
		for my $np (1..99) { 
			for my $i (0..$#system_name) {
				if ($nplanets[$i] == $np and $hashab[$i]) {
					print "$nplanets[$i],	$system_name[$i]\n"
				
				}
			}
		}
		exit;
	}

);

my $line;
print STDERR "Processing Line\n";
while(<>){
	chomp;
	$L=$_;
	(++$line % 10000) or print STDERR "$line\r";
	#if (length($_) > 1000) {next}
	if (/^	*([0-9a-z_]*)=(.*)/){
		$key=$1;
		$val=$2;
		if ($key =~ /^[0-9]+$/) {
			$id=$key;
			$star=0;
		} 
		else
		{
#		print "$key, $val, $id\n";
			my $f=$dispatch{$key};
			if (defined $f){$f->()}
		}
	}
}
