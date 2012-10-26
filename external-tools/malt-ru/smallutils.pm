#a set of small utilities for corpus processing, use perldoc to get usage info

@EXPORT = qw/create_fq_list cyr2lat lat2cyr getremotehost initnum2str num2str str2num intersect min max minstring maxstring openfile signint ln llscore/;

use utf8;
use strict;
use Carp;


sub create_fq_list { #parameters: word list file, [from, to]; 
    my ($fname,$fromwords,$towords)=@_;
    my $fh=openfile($fname);
    my $curcount=0;
    undef my %wl;
    my $totalfq=0;
    my ($fq,$w);
    while (<$fh>) {
	if ((($fq,$w)=/^\d+\s([\d.]+)\s(.+)/) or
	    ((($fq,$w)=/^\s*(\d+)\s(.+)/) and ($w=~/\w/))) { # for plain fq lists from uniq -c
	    $curcount++;
	    next if (defined $fromwords) and ($curcount<=$fromwords);
	    $wl{$w}+=$fq;
	    $totalfq+=$fq;
	    last if (defined $towords) and ($curcount==$towords);
	}
    }
    close($fh);
    return($totalfq,\%wl);
}

my %cyr2lat=(
'а' => 'a',
'б' => 'b',
'в' => 'v',
'г' => 'g',
'д' => 'd',
'е' => 'e',
'ё' => 'e',
'ж' => 'zh',
'з' => 'z',
'и' => 'i',
'й' => 'j',
'к' => 'k',
'л' => 'l',
'м' => 'm',
'н' => 'n',
'о' => 'o',
'п' => 'p',
'р' => 'r',
'с' => 's',
'т' => 't',
'у' => 'u',
'ф' => 'f',
'х' => 'x',
'ц' => 'c',
'ч' => 'ch',
'ш' => 'sh',
'щ' => 'w',
'ъ' => 'qh',
'ы' => 'y',
'ь' => 'q',
'э' => 'eh',
'ю' => 'ju',
'я' => 'ja',

'А' => 'A',
'Б' => 'B',
'В' => 'V',
'Г' => 'G',
'Д' => 'D',
'Е' => 'E',
'Ё' => 'E',
'Ж' => 'ZH',
'З' => 'Z',
'И' => 'I',
'Й' => 'J',
'К' => 'K',
'Л' => 'L',
'М' => 'M',
'Н' => 'N',
'О' => 'O',
'П' => 'P',
'Р' => 'R',
'С' => 'S',
'Т' => 'T',
'У' => 'U',
'Ф' => 'F',
'Х' => 'X',
'Ц' => 'C',
'Ч' => 'CH',
'Ш' => 'SH',
'Щ' => 'W',
'Ъ' => 'QH',
'Ы' => 'Y',
'Ь' => 'Q',
'Э' => 'EH',
'Ю' => 'JU',
'Я' => 'JA'
);

my %lat2cyr=(
'a' => 'а',
'b' => 'б',
'v' => 'в',
'g' => 'г',
'd' => 'д',
'e' => 'е',
'z' => 'з',
'i' => 'и',
'j' => 'й',
'k' => 'к',
'l' => 'л',
'm' => 'м',
'n' => 'н',
'o' => 'о',
'p' => 'п',
'r' => 'р',
's' => 'с',
't' => 'т',
'u' => 'у',
'f' => 'ф',
'x' => 'х',
'c' => 'ц',
'w' => 'щ',
'y' => 'ы',
'q' => 'ь',

'A' => 'А',
'B' => 'Б',
'V' => 'В',
'G' => 'Г',
'D' => 'Д',
'E' => 'Е',
'Z' => 'З',
'I' => 'И',
'J' => 'Й',
'K' => 'К',
'L' => 'Л',
'M' => 'М',
'N' => 'Н',
'O' => 'О',
'P' => 'П',
'R' => 'Р',
'S' => 'С',
'T' => 'Т',
'U' => 'У',
'F' => 'Ф',
'X' => 'Х',
'C' => 'Ц',
'W' => 'Щ',
'Y' => 'Ы',
'Q' => 'Ь'
);


sub cyr2lat {
   my $s=shift;
   utf8::upgrade($_) unless (utf8::is_utf8($s)); 
   my $res='';
   for (my $i=0; $i<length($s); $i++) {
       my $char=substr($s, $i, 1);
       my $charnum=ord($char);
       $res.=$cyr2lat{$char} || $char;
   }
   return($res);
}

sub lat2cyr {
   my $s=shift;
   utf8::upgrade($_) unless (utf8::is_utf8($s)); 
   my $res='';
    $s=~s/zh/ж/g;
    $s=~s/ch/ч/g;
    $s=~s/sh/ш/g;
    $s=~s/qh/ъ/g;
    $s=~s/eh/э/g;
    $s=~s/ju/ю/g;
    $s=~s/ja/я/g;
    $s=~s/ZH/Ж/g;
    $s=~s/CH/Ч/g;
    $s=~s/SH/Ш/g;
    $s=~s/QH/Ъ/g;
    $s=~s/EH/Э/g;
    $s=~s/JU/Ю/g;
    $s=~s/JA/Я/g;
#    $s=~s/JO/Ё/g;
#    $s=~s/jo/ё/g;
    for (my $i=0; $i<length($s); $i++) {
    	my $char=substr($s, $i, 1);
	if ($char eq "\\") { $res.=substr($s, ++$i, 1); } # save occasional latin chars if protected by \
	elsif (exists $lat2cyr{$char}) {
	    $res.= $lat2cyr{$char};
	} else {
	    $res.=$char;
	};
    };
   return($res);
}

sub getremotehost {
    my $cgiquery=shift;
    if ($cgiquery) {
	my $remote_host=$cgiquery->remote_host;
	chomp(my $dnsname=`host $remote_host`);
	unless ($dnsname=~/ not found:/) {
	    ($remote_host)=$dnsname=~/(\S+)$/;
	};
	if ($ENV{'HTTP_VIA'}) {$remote_host.=" via ".$ENV{'HTTP_VIA'}}
	return $remote_host
    };
}


#simple procedures for converting numbers to strings and back
my %base;
my @base;

sub initnum2str {
    my $base=shift;
    @base=split //,$base;
    undef %base;
    my $next=0;
    foreach (@base) {
	$base{$_}=$next++;
    }
};

sub num2str {
    use integer;
    my $i=shift;
    my $s='';
    while ($i>$#base) {
	my $lastn=$i % scalar(@base);
	$s=$base[$lastn].$s;
	$i=$i/scalar(@base)
	};
    return "$base[$i]$s";
}

sub str2num {
    my $i=0;
    my $s=shift;
    my @s=reverse split //,$s;
    foreach my $p (0..$#s) {
	$i+=scalar(@base)**$p*$base{$s[$p]}
    };
    return $i;
}

sub intersect { #words for references to hashes as well as to arrays
    my $aref=shift;
    my $bref=shift;
    my %result;
    if (ref $aref eq 'ARRAY') {
	my %a;
	@a{@{$aref}}=();
	$aref=\%a;
    };
    if (ref $bref eq 'ARRAY') {
	my %b;
	@b{@{$bref}}=();
	$bref=\%b;
    };
    if (scalar(keys %{$aref})>scalar(keys %{$bref})) {
	($aref,$bref)=($bref,$aref);
    }
    foreach (keys %{$aref}) {
	$result{$_}=1 if exists ${$bref}{$_};
    }
    return \%result;
}

# strange: I was unable to find the standard functions for min and max in perl5
sub min {
    return (($_[0] < $_[1]) ? $_[0] : $_[1])
}
sub max {
    return (($_[0] > $_[1]) ? $_[0] : $_[1])
}
sub minstring {
    return (($_[0] lt $_[1]) ? $_[0] : $_[1])
}
sub maxstring {
    return (($_[0] gt $_[1]) ? $_[0] : $_[1])
}
sub signint {
    return ($_[0] <=> 0)
}

sub ln {
    return(($_[0]>0) ? log($_[0]) : 0)
}
sub llscore {
    my ($a, $b,$c,$d)=@_;
    return 0 unless $a and $b and $c and $d;
    my $cd=$c+$d;
    my $E1 = $c*($a+$b)/($cd);
    my $E2 = $d*($a+$b)/($cd);
    my $g2= ($a/$c>$b/$d) ?  
	 #if the feature overused in the test corpus
	(2*(($a*ln($a/$E1))+ ($b*ln($b/$E2)))) : 0;
    return $g2
};

sub openfile {
    open(my $fh, "<:utf8", "$_[0]") or croak "Cannot open $_[0]: $!";
    return $fh;
}


1;

=head1 NAME

I<smallutils>: a set of small utilities for corpus processing, use B<perldoc -t smallutils> to get usage info

=head1 FUNCTION create_fq_list

=head2 SYNOPSIS

($totalq,$fqref)=create_fq_list('bnc.lst',0,100) 

This takes the top hundred words from 'bnc.lst'

=head2 DESCRIPTION create_fq_list(file,[from,[to]]) 

Reads a frequency list from BNC-like lists (format: rank frequency word) or from frequency lists produced by uniq -c (sort|uniq -c |sort -nr -k 1).  Can skip first B<from> words and words after first B<to>.

=head1 FUNCTION cyr2lat
 
=head2 SYNOPSIS

$latstr=cyr2lat('Ваш')

The output should be 'Vash'

=head2 DESCRIPTION cyr2lat(cyrillic string)

A function for Latin transliteration using a reversible transliteration scheme (see http://corpus.leeds.ac.uk/tools/translit.html).  Opposite to B<lat2cyr>

=head1 FUNCTION getremotehost

=head2 SYNOPSIS

print getremotehost($CGI)

=head2 DESCRIPTION  getremotehost(cgi_object)

prints a human-readable host name from a cgi object

=head1 FUNCTION initnum2str 

=head2 SYNOPSIS

initnum2str('abcdef')

=head2 DESCRIPTION initnum2str(str)

Takes a string and initialises the generator

=head1 FUNCTION num2str 

=head2 SYNOPSIS

print num2str(25)

=head2 DESCRIPTION num2str(str)

Generates a string using chars from the init string (e.g. 'eb' for 25 if initialised as above)

=head1 FUNCTION str2num 

=head2 SYNOPSIS

print str2num('eb')

=head2 DESCRIPTION str2num

Generates the numerical value from a string using the init string (e.g. 25 from 'eb' if initialised as above)

=head1 FUNCTION intersect

=head2 SYNOPSIS

@x=qw/a b c d/;
@y=qw/c d e f/;
$hashref=intersect(\@x,\@y)

=head2 DESCRIPTION intersect(ref1,ref2)

Returns the reference to a hash containing the intersection of two references to hashes or arrays provided in the parameters

=head1 FUNCTION lat2cyr

=head2 SYNOPSIS

$cyrstr=lat2str('Vash')

The output should be 'Ваш'

=head2 DESCRIPTION lat2cyr(latin string)

A function for making a Cyrillic string using a reversible transliteration scheme (see http://corpus.leeds.ac.uk/tools/translit.html).  Opposite to B<cyr2lat>


=head FUNCTION llscore

=head2 SYNOPSIS

$llscore=llscore(10,100,$testsize,$refsize)

=head2 DESCRIPTION llscore(a,b,c,d)

Computes the LL-score (following Paul Rayson's calculator) for scoring the frequency in a test corpus against a reference corpus (only items more frequent in the test corpus are scored).

=head1 FUNCTION openfile

=head2 DESCRIPTION openfile(fname)

Opens a UTF8 file, croaks if it cannot be opened

=head1 DEPENDENCIES

utf8 processing works best with perl 5.8 or higher; Carp

=head1 AUTHOR

Serge Sharoff, University of Leeds

=head1 BUGS

Probably many: if you find one, please let me know.

=head1 COPYRIGHT

Copyright 2007, Serge Sharoff

This module is free software. You may copy or redistribute it under
the same terms as Perl itself.

=cut
