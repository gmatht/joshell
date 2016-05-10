#!/usr/bin/env perl
# USAGE: perl bits/memoize.pl nl_bctl3.ml > nl_bctl3memo.ml ; ocamlopt.opt nl_bctl3memo.ml -o memo
use strict;
our $ml;
our $signatures;

if (exists $ARGV[0]) {
	$ml=`cat $ARGV[0]`;
	$signatures=`ocaml < $ARGV[0]`;
} else {
	print STDERR "-------------------
Script to memoize modules in a OCaml file.

Usage $0 memoize_sample_input.ml > newfile.ml

file.ml should have '(* MEMOIZE MODULE Foo *)' after the module Foo if you want to memoize it.

The resulting file should be equivalent to the original, but faster and use more memory.



Note:
	Foo.t becomes int after memoization for efficient '='
	Foo must define equals, hash and compare
	Void functions are not memoized since you probably want the side-effect
Limitations:
	Limited to functions with 2 inputs
	Limited support for functions with complex";
	die
}


# sig
#    type t = string
#    val empty : string
#    val beep : string -> string
#    val boop : string -> string
#    val len : string -> int
#  end
#

print "(* ADDED BY memoize.pl *)
let int_compare = compare
let memo f =
  let m = Hashtbl.create 9 in
    fun x ->
      try Hashtbl.find m x
      with Not_found ->
        let y = f x in
          Hashtbl.add m x y; y
let memo2 f =
  let m = Hashtbl.create 9 in
    fun x x2 ->
      try Hashtbl.find m (x, x2)
      with Not_found ->
        let y = f x x2 in
          Hashtbl.add m (x, x2) y; y

";


my $Boilerplate_sample="(* Boilerplate *)
  type t = int
  let to_id_h  = HashtblDroid.create 9
  let from_id_a = ref [| Droid.empty |] (*or use array*)
  let last_id = ref (-1)
  let from_id i = (!from_id_a).(i)
  let to_id (x :Droid.t) : int = 
    if   HashtblDroid.mem  to_id_h x 
    then HashtblDroid.find to_id_h x
    else (
      last_id := (!last_id)+1;
      HashtblDroid.add  to_id_h x (!last_id);
      let resize a siz = if (Array.length a) < siz then Array.append a a else a in
      from_id_a:=(resize (!from_id_a) (1+(!last_id)));
      (!from_id_a).(!last_id) <- x;
      !last_id
    )
";

sub wrappers {
	my $module =$_[0];
	my @signature = split '\n', $_[1];
	my $output = "(* Wrappers *)\n";
	my $t;
	my $r="[[:alnum:]. ]+|[(][^()\n]*[)]";
	foreach(@signature) {
		my $fun;	
		if (/type t = (\w+)/	){
			$t=$1;
		} elsif (/val (\w+) : ($r)$/){
			$fun = "$module.$1";
			if ($2 eq $t or $2 eq "t") { $fun = "to_id $fun" }
			print STDERR "2= |$2|\n";
			{if ($2 =~ /^($t|t) (\w+)$/) { 
				$fun = (ucfirst $2).".map to_id $fun"
			}}
			$output .= "  let $1 = $fun\n"; 
		} elsif (/val (\w+) : ($r) -> ($r)$/){
			my $x = "x"; if ($2 eq $t or $2 eq "t") {$x="(from_id $x)"}
			$fun="($module.$1 $x)";
			if ($3 eq $t or $3 eq "t") {$fun="(to_id $fun)"}
			$fun="(fun x -> $fun)";
			if ($3 ne "unit") {$fun="(memo $fun)"}
			$output .= "  let $1 = $fun\n"; 
    #val for_all : (elt -> bool) -> t -> bool
		} elsif (/val (\w+) : ($r) -> ($r) -> ($r)$/){
			my $x = "x"; if ($2 eq $t or $2 eq "t") {$x="(from_id $x)"}
			my $y = "y"; if ($3 eq $t or $3 eq "t") {$y="(from_id $y)"}
			$fun="($module.$1 $x $y)";
			if ($4 ne "unit" and (index("$2$3", "->") == -1)) {
				if ($4 eq $t or $4 eq "t") {$fun="(to_id $fun)"}
				$fun="(memo2 (fun x y -> $fun))";
				#$fun="(fun x y -> $fun (x,y))";
			} else {
				$fun="(fun x y -> $fun)";
			}
			
			$output .= "  let $1 = $fun\n"; 
		} else {
			#print STDERR "FAILED: $_\n";
		}
	}
	$output .= "
  let equal = (=)
  let hash  = fun x -> x
  let compare = int_compare
";
	return $output;
}


# fun x y -> fun x, y -> memo ( fun (x,y) -> D.f x y ) x y 

sub memoize {
	my $module =$_[0];
	my $remainder =$_[1];
	$remainder =~ s/\b$module\b/Memo$module/g;

	if ($signatures =~ /module $module :\s*sig\s*((?:.|\n)*?)end/m) {
		my $wrapper = wrappers($module, $1);
		my $Boilerplate = $Boilerplate_sample;
		$Boilerplate =~ s/Droid/$module/g;
		return "
module Hashtbl$module = Hashtbl.Make($module)
module Memo$module = struct
$Boilerplate
$wrapper
end
$remainder
";
	} else {
		die;
	}
}
 

$ml=~s/\(\* MEMOIZE MODULE (\w+) \*\)(.*)/memoize $1,$2/egs;
$ml=~s/\(\* MEMOIZE MODULE (\w+) \*\)(.*)/memoize $1,$2/egs;
$ml=~s/\(\* IF MEMOIZE (.*?) \*\)/$1/g;
print "$ml";

exit;

our $t;

