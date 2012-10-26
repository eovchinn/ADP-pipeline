#!/usr/bin/perl -w
# 
# version: 0.2
# Serge Sharoff # 2009-2011, University of Leeds, 
# The script does lemmatisation of the output of Treetagger or TnT using cstlemmatiser for unknow words

use lib('/corpora/tools');
use smallutils;
use Getopt::Long;
use File::Temp qw/ tempfile tempdir /;

$usage='Lemmatiser of the output of TnT (uses cstlemma by default). Usage: 
lemmatiser.pl <incorpus >outcorpus
--accepttags pattern (POS values to be passed on to the lemmatiser).
--goodchars crange (chars to be passed on to the lemmatiser).
--from encoding (cst recognises only iso encodings)
--lex fname known lemmas (in the Treetagger format)
--patterns fname cstlemma patterns
--to encoding (cst recognises only iso encodings)';

#$fromencoding='iso-8859-5';
#$toencoding='utf8';
$cstlemma='cstlemma';
$maxlength=1024; # to fight problems with tokenisation
binmode(STDIN,":utf8");
binmode(STDOUT,":utf8");
binmode(STDERR,":utf8");

$goodchars='[а-яА-Я]'; #only Russian words to lemmatise automatically by default
utf8::decode($goodchars);
$goodpos='[ANV]'; #only postags starting from goodpos
$cstfool='Afp'; # a known pos that can do no harm (cst lemmatises everything and
		# dies on unknown tags)

GetOptions (
	    "accepttags=s" => \$goodpos,
	    "cstlemma=s" => \$cstlemma,
#	    "fromencoding=s" => \$fromencoding,
	    "fool=s" => \$cstfool,
	    "goodchars=s" => \$goodchars,
	    "help" => \$opt_help,
	    "lex=s" => \$lexfile,
	    "patterns=s" => \$patterns,
#	    "toencoding=s" => \$toencoding,
	    );

my @flist=@ARGV;
die "$usage\n" if $opt_help;

die "The lexicon file $lexfile doesn't exist\n" if ((defined $lexfile) and (!-f $lexfile));

die "The patterns file $patterns does not exist\n" if ((defined $patterns) and (! -f $patterns));

#read the lexicon

$opentool=($lexfile=~/\.gz$/) ? 'gzip -cd' :
    ($lexfile=~/\.bz2?$/) ? 'bzip2 -cd' : 'cat';
open($fh,"$opentool $lexfile|") or die "error in opening $opentool $lexfile: $!\n";
binmode($fh,":utf8");

while (<$fh>) {
    next unless /^$goodchars/;
    $tabpos=index($_,"\t");
    unless ($tabpos == -1) {
	$w=substr($_,0,$tabpos);
	foreach (split /\t/,substr($_,$tabpos)) {
	    if (($posgr,$l)=/^([A-Z0-9-]+?) (.+)/i) { 
		$l=lc($l);
		if (exists $lex{$w}{$posgr}) {
		    $oldlex=$lex{$w}{$posgr};
		    unless ($oldlex eq $l) {
			if (length($l)>length($oldlex)) { #when merging two form-pos pairs, we keep the longer lemma
			    $lex{$w}{$posgr}=$l;
			}
		    }
		} else {
		    $lex{$w}{$posgr}=$l;
		};
	    };
	};
    }
}
close($fh);

my ($corpusfh, $corpusfile) = tempfile(); # for storing the corpus
binmode($corpusfh,":utf8");

my ($lemmafh, $lemmafile) = tempfile(); #for storing unknown lemmas
binmode($lemmafh,":utf8");

unless (defined $patterns) {
    close($corpusfh);
    $corpusfh=*STDOUT;
};

$i=1;
while (<STDIN>) {
    if (length($_)>$maxlength) {
	$_=substr($_,0,$maxlength);
	$_.= qq{\">\n} if (/^</);
    };
    utf8::decode($_);
    if (($word,$pos)=/^($goodchars+?)\s+(\S+)/) {
#	if (exists $lex{$word}{$pos}) {
	if ($lex{$word}{$pos}) {
	    $lemma=$lex{$word}{$pos};
	} elsif (exists $lex{lc($word)}{$pos}) {
	    $lemma=$lex{lc($word)}{$pos};
	} else {
	    if (($word=~/$goodchars$/) and ($pos=~/^$goodpos/)) {
		print $lemmafh "$i/$cstfool\n",lc($word),"/$pos\n";
		$lemma="<unknown>";
	    } else {
		$lemma=lc($word); #."\t<unknown>"; #no need to signal for non-inflected forms
		$pos='-' unless $word=~/$goodchars/;
	    };
	};
	$_="$word\t$pos\t$lemma\n";
    } elsif (substr($_,0,1) ne '<') { # a non-Russian word
	($word,$pos)=split(/\s+/,$_); #tnt often leaves useless extra tab chars
	$lemma=lc($word);
	$_="$word\t$pos\t$lemma\n";
    };
    print $corpusfh $_;
    $i++;
}
undef %lex;
close($corpusfh);
close($lemmafh);

if (defined $patterns) {
print STDERR "Guessing unknown lemmas in $lemmafile\n";
#`recode -f $toencoding..$fromencoding $lemmafile`;
#open($lemmafh,"$cstlemma -t -f $patterns <$lemmafile | recode -f $fromencoding..$toencoding |");
open($lemmafh,"$cstlemma -eU -t -f $patterns <$lemmafile |");
binmode($lemmafh,":utf8");

$corpusfh=openfile($corpusfile);
$i=1;
($lempos,$lemval)=getnextlemposval($lemmafh);
while (<$corpusfh>) {
    if ($lempos == $i) {
	$l=$lemval;
	s/\t<unknown>/\t$l\t<guessed>/;
	($lempos,$lemval)=getnextlemposval($lemmafh);
    }
    if (/<unknown>/) {
	print STDERR "$i; $lempos; $lemval; $_"
    }
    print ;
    $i++;
}
}

close($corpusfh);
close($lemmafh);
unlink($corpusfile);
unlink($lemmafile);

sub getnextlemposval {
    my $fh=shift;
    my ($pos, $l);
    do {
	$posline=<$fh>;
    } until (! defined $posline) or ($posline=~/^(\d+)\s+/);
    $pos=$1||0;
    if ($lline=<$fh>) { #read the next line for the lemma
	$l=$2  if ($lline=~/^(.+?)\t(.+?)\t/);
    };
    return ($pos,$l);
}
