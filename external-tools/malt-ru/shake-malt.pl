#!/usr/bin/perl
#Serge Sharoff, April 2012
#The script takes the output of the Malt Parser with information about the sentence offsets and restores information about the texts.

$ftextids=shift;
$fparsed=shift;
open(T,$ftextids) or die "Cannot read text ids from $ftextids\n";
while (<T>) {
    if (($p,$id,$rest)=/^(\d+)\t(.+?)\t(.*)/) {
	push @offsets,$p;
	push @ids,qq{<text id="$id"$rest>\n};
    }
}
close(T);
$s=0;
$/="\n\n";
open(T,$fparsed) or die "Cannot read parsed text from $fparsed\n";
$i=0;
while (<T>) {
    if ($i++ >= $offsets[0]) {
	print "</text>\n" if $i>1;
	$curid= shift @ids;
	print $curid;
	shift @offsets;
	$i--;
    }
    chomp;
    print "<s>\n";
    print $_;
    print "\n</s>\n";
}
print "</text>\n";
