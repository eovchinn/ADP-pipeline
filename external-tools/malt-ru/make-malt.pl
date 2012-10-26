#!/usr/bin/perl
#Serge Sharoff, April 2011
#The script converts the output of Treetagger to the CoNLL format expected by Malt
#It splits very long sentences (usually they are remainders of lists after cleaning)
#STDERR collects the sentence offsets for the text ids

$maxwordlenght=150;

$i=0;$sl=0;$start=0;
while (<>) {
    if (/^</) {
	if (/<text id="(.+?)"(.*)>/) {
	    print STDERR "$i\t$1\t$2\n";
	    print "\n";
	}
    } else {
	chomp; 
	($w,$p,$l)=split /\t/,$_;
	if (defined $l) {
	    $t=substr($p,0,1); 
	    $out="1\t$w\t$l\t$t\t$t\t$p\n";
	    print $out;
	    $sl++;
	    if (($p eq 'SENT') or (($start) and ($out=~/^1\t[;,.()-]/))) {
		#if a sentence is too long, we split by the first punctuation
		print "\n";
		$i++;
		$start=0;
	    } elsif ($start>=$maxwordlenght) {
		$start=1;
	    }
	}
    }
}
