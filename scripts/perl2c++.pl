#!/usr/bin/perl
# A horrible prototype of a Perl to C++ compiler.
#
# Not a Joke (unfortunately?)
# 	e.g. doesn't output a one-line "C++" program like: system("your-perl.pl")
# 
# If it works (it probably won't) the code emitted may theoretically
# 	1) Pass code review in orgs that don't like perl
# 	2) Avoid the need to bundle perl with your application
# 	3) Be faster than Perl bytecode.
#
# No attempt will ever be made to handle all valid Perl inputs.
# But still, surely someone could do something less horrible than this?
#
# Compare:
# 	perl perl2c++.pl < LCG.pl | tee out.c && g++ out.c -O3 && time ./a.out
# 		OUTPUT: x[ 10000000 ] = 1282874041, amigo! ( in 0.02s )
# 	perl LCG.pl
# 		OUTPUT: x[ 10000000 ] = 1282874041, amigo! ( in 1.04s )


print "
#include <iostream>

int main(){\
";
$NUM_TYPE="double";

$INT_OP="[+-=/%]";

$INT="[0-9]+";
for ($count=1; $count<3; $count++){
	$MATCH_PAREN="\((?:[^()]|$MATCH_PAREN)+\)";
	$INT_or_VAR="(?:\\\$[[:alnum:]]+|$INT)";
	#$INT="(?:\\($INT\\)|$INT *$INT_OP *$INT|$INT_or_VAR *$INT_OP *$INT_or_VAR";
	$INT="(?:$INT|\\($INT\\)|$INT *$INT_OP *$INT|$INT_or_VAR *$INT_OP *$INT_or_VAR|int$MATCH_PAREN)";
	$DQ_STR='"(?:[^"]|\\")*"';
	$SQ_STR="'(?:[^']|\\')*'";
	$STR="(?:$DQ_STR|$SQ_STR|str *$MATCH_PAREN)";
}

print STDERR "$INT\n";
#print "XXX $DQ_STR\n";
#exit(1);

sub print_dq_string{
	$s=$_[0];
	$s=~ s/\$([[:alnum:]]+)/" << $1 << "/g; 
	#$s=~ s/\\n/" << std::endl << "/; 
	return "std::cout << $s";
}

while(my $L = <>) {
	if ($L =~ s/^ *use  *integer *; *//) { $NUM_TYPE="int"; }
	#if ($L =~ s/^ *use  *integer *; *//) { $NUM_TYPE="long long"; }
	if ($L =~ s/^ *no  *integer *; *//) { $NUM_TYPE="double"; }
	if ($L =~ s/^ *use  *[[:alnum:]]+ *; *//) { }

	#$L =~ s/my [$]([[:alnum:]])/int ${1}/g;
	#$L =~ s/my \$([[:alnum:]]) *= *([0-9]+)/int ${1}=${2}/g;
	$L =~ s/my \$([[:alnum:]]+) *= *($INT)/$NUM_TYPE ${1}=${2}/g;
	$L =~ s/my \$([[:alnum:]]+) *= *($STR)/std::string ${1}(${2})/g;
	$L =~ s/print *\$([[:alnum:]]+)/std::cout << ${1}/g;
	#$L =~ s/print *($DQ_STR)/print_dq_string(${1})/eg;
	$L =~ s/print *(\".*\")/print_dq_string($1)/eg;
	#$L =~ s/print *($DQ_STR)/print_dq_string($1)/eg;
	$L =~ s,( *)#,$1//,g;
	#$L =~ s,($INT) *[%] *($INT),((unsigned)$1) % $2,g;
	$L =~ s,(\($INT\)) *[%] *($INT),((unsigned)$1) % $2,g;

	#Kludges follow. There seems to be a bug in my INT regex
	$L =~ s,(\(.*?$INT_OP *$INT_or_VAR\)) *\% *($INT_or_VAR),((unsigned)$1) % $2$3,g;
	#$L =~ s,(\(.*?\)) *[%] *($INT),((unsigned)$1) % $2,g; # Kludge
	$L =~ s,\b2 *\*\* *($INT),(1<<$1),g;

	#Do some final clean ups...
	$L =~ s/\$([[:alnum:]]+)/${1}/g;
	print $L;
	#s/[$]//;
}
print "return 0;\n";
print "}";



