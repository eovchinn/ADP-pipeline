#!/usr/bin/perl

use strict;
use Data::Dumper;
use Getopt::Long;
use utf8;
use Encode;

my %conditional = ();
my %regex_conditional = ();
my %nonmerge = ();
my %merge = ();
my %id2props = ();
my %args2props = ();

my %global_token_index = ();

my $ifile = "";
my $ofile = "";
my $cfile = "";
my $sfile = "";
my $nefile = "";
my $nonmerge_opt = "";

my $cost = "1";
my $sameargs = 0;
my $modality = 0;
my $warnings = 0;
my $wholefileoutput = 0;

GetOptions ("input=s" => \$ifile,
	    "output=s" => \$ofile,
	    "conditional=s" => \$cfile,
            "cost=s" => \$cost,
            "nonmerge=s" => \$nonmerge_opt,
            "warnings=i" => \$warnings,
            "wholefileoutput=i" => \$wholefileoutput);

&setParameters();

&read_Conditional_file();

open(OUT,">:utf8","$ofile") or die "Cannot open $ofile\n";

&read_Parser_file();


if($warnings==1){print "Henry file printed.\n";}
close OUT;


###########################################################################
# SET PARAMETERS
###########################################################################

sub setParameters(){
   if(($ifile eq "")||($ofile eq "")) {print("Input or output file missing.\n"); &printUsage();}

   if(($wholefileoutput!=0)&&($wholefileoutput!=1)) {print("Wrong value of 'wholefileoutput' parameter: $wholefileoutput Only '0' and '1' accepted.\n"); exit(0);}

   if(($warnings!=0)&&($warnings!=1)) {print("Wrong value of 'warnings' parameter: $warnings. Only '0' and '1' accepted.\n"); exit(0);}

   if($cost !~ /\d+(.\d+)?/) {print("Wrong value of 'cost' parameter: $cost. Only real numbers accepted.\n"); exit(0);}

   if($nonmerge_opt ne ""){
   	my @data = split(/,/,$nonmerge_opt);
        foreach my $d (@data){
        	&setNMParameter($d);
        }
   }
}

sub setNMParameter(){
   my ($p) = @_;

   if($p eq "modality") {$modality = 1;}
   elsif($p eq "sameargs") {$sameargs = 1;}
   else{print("Wrong value of 'nonmerge' parameter: $p. Only 'modality' and 'sameargs' accepted.\n"); exit(0);}
}

###########################################################################
# PRING USAGE
###########################################################################

sub printUsage(){
    print "Usage: perl Boxer2Henry.pl\n --input <boxer file>\n --output <henry file>\n --cost <real number> (default=1)\n [--conditional <conditional unification file>]\n [--coref <standford coref file>]\n [--nedis <disambiguated named entities file>]\n [--split <split nouns concatenated by Boxer> (possible values: [0=no, 1=yes], default: 0)]\n [--nonmerge <nonmerge options> (possible values:modality,sameargs) 'modality' -- consider modality to create non-merge, 'sameargs' -- non-merge for args of the same prop] \n";
    exit(0);
}


###########################################################################
# ADD NON-MERGE CONSTRAINTS
###########################################################################

sub add_nonmerge(){
   my ($sent_id) = @_;

   if(($modality+$sameargs)==0) {return;}

   my @pids = keys %{$id2props{$sent_id}};

   my %props2pids=();
   for my $pid (@pids){
       for my $pname (keys %{$id2props{$sent_id}{$pid}}){
             for my $farg (keys %{$id2props{$sent_id}{$pid}{$pname}{'args'}}){
                   my @args =  @{$id2props{$sent_id}{$pid}{$pname}{'args'}{$farg}};
                   $props2pids{$pname}{$farg}{'args'}=[@args];
                   $props2pids{$pname}{$farg}{'pid'}{$pid}=1;
                   $props2pids{$pname}{$farg}{'pos'} = $id2props{$sent_id}{$pid}{$pname}{'pos'};
             }
       }
   }

   #CHECK CONDITIONAL AND MODALITY IN ADVANCE
   if($modality==1){
       for my $pname (keys %props2pids){
           #for my $farg (keys %{$props2pids{$pname}}){
                   #$props2pids{$pname}{$farg}{'cond'} = &check_conditional($pname);
           #}

           if($modality==1){
                foreach my $farg (keys %{$props2pids{$pname}} ){
                       if($props2pids{$pname}{$farg}{'pos'} eq 'nn'){$props2pids{$pname}{$farg}{'mod'} = "" ;}
                       else{$props2pids{$pname}{$farg}{'mod'} = &define_modality(\%props2pids,$pname,$farg);}
                }
   	   }
   	}
   }

   my @pnames = keys %props2pids;

   for (my $pi=0; $pi<(scalar @pnames);$pi++){
       my $pname1 = $pnames[$pi];

       for my $farg1 (keys %{$props2pids{$pname1}}){
           my @args1 =  @{$props2pids{$pname1}{$farg1}{'args'}};

           ## ARGUMENTS OF THE SAME PREDICATE CANNOT BE MERGED

           if($sameargs == 1){
                        my $str = "(!=";
                        foreach(my $i=0;$i<(scalar @args1);$i++){
                             $str = $str." ".$args1[$i];

	                }
                        $nonmerge{$str.")"} = 1;
           }
           ############################################

           #if($props2pids{$pname1}{$farg1}{'cond'} == 0){
                ## PREDICATES WITH DIFFERENT MODALITIES CANNOT BE MERGED
                if($modality == 1){
                     for (my $pj=$pi+1; $pj<(scalar @pnames);$pj++){
       			 my $pname2 = $pnames[$pj];
                         for my $farg2 (keys %{$props2pids{$pname2}}){
                             if(($farg1 ne $farg2)&&(!(exists $nonmerge{"(!= ".$farg2." ".$farg1.")"}))){
                                    if(&check_modality_clash(\%props2pids,$pname1,$farg1,$pname2,$farg2)==1){
                                    	$nonmerge{"(!= ".$farg1." ".$farg2.")"} = 1;
                                    }
                             }
                         }
                     }
                }
           #}
       }
   }

}

###########################################################################
# CHECL MODALITY CLASH
###########################################################################

sub check_modality_clash(){
    my ($tmp,$pname1,$farg1,$pname2,$farg2) = @_;

    my %props2pids = %{$tmp};

    my $pos1 = $props2pids{$pname1}{'pos'};
    my $pos2 = $props2pids{$pname2}{'pos'};

    if(($pos1 eq "n")||($pos2 eq "n")){
    	return 0;
    }

    if($pos1 ne $pos2){
    	return 0;
    }

    my $mod1 = $props2pids{$pname1}{$farg1}{'mod'};
    my $mod2 = $props2pids{$pname2}{$farg2}{'mod'};

    if($mod1 ne $mod2) {return 1;}

    return 0;
}

###########################################################################
# DEFINE MODALITY
###########################################################################

sub define_modality(){
   my ($tmp,$pname,$farg) = @_;

   my %props2pids = %{$tmp};

   my $arg1 = $props2pids{$pname}{$farg}{'args'}[0];

   for my $pname2 (keys %props2pids){
      if(((($pname2=~/-vb$/)||($pname2 eq "not"))||($pname2 eq "pos"))||($pname2 eq "nec")){
        for my $farg2 (keys %{$props2pids{$pname2}}){
              my @args2 = @{$props2pids{$pname}{$farg}{'args'}};
              foreach(my $i=1;$i<(scalar @args2);$i++){
	      	if($args2[$i] eq $arg1){
	           return $farg2.$pname2;
	        }
	      }
        }
      }
   }

   return "";
}
###########################################################################
# CREATE FINAL OUTPUT BATCH
###########################################################################

sub printHenryFormat_batch(){

   foreach my $sent_id(keys %id2props){
        &add_nonmerge($sent_id);
        printHenryFormat($sent_id,0);
        %nonmerge = ();
   }

   print OUT "\n(O (name 0) (^";

   foreach my $sent_id(keys %id2props){
        &add_nonmerge($sent_id);
        printHenryFormat($sent_id,1);
        %nonmerge = ();
   }

   my $str = "";
   foreach my $key (keys %merge){
	   $str = $str . " (=";
	   foreach my $arg (keys %{$merge{$key}}){
                $str = $str . " ".$arg;
	   }
	   $str = $str . ")";
   }

   print OUT $str . "))\n";
}

###########################################################################
# CREATE FINAL OUTPUT
###########################################################################

sub printHenryFormat(){
    my ($sent_id,$bash) = @_;

    my $str = "";

    if($bash==0) {$str = "(O (name $sent_id) (^";}

    my $id_counter = 1;

    my %out_str = ();

    foreach my $pid (keys %{$id2props{$sent_id}}){
         foreach my $pname (keys %{$id2props{$sent_id}{$pid}}){
              foreach my $farg (keys %{$id2props{$sent_id}{$pid}{$pname}{'args'}}){
                       my @args = @{$id2props{$sent_id}{$pid}{$pname}{'args'}{$farg}};
                       my $key = $pname.",".$args[0];
                       if(!(exists $out_str{$key})){
                            my $pred_str = "(".$pname;
                            foreach my $arg (@args){
	                        $pred_str = $pred_str ." ".$arg;
	               	    }
                            $id_counter++;
                            $pred_str = " ".$pred_str . " :$cost:$sent_id-$id_counter";

                            $out_str{$key}{'pred'} = $pred_str;
                       }
                       push(@{$out_str{$key}{'pids'}},$pid);
              }
    	}
    }


    foreach my $key (keys %out_str){
        $str = $str . $out_str{$key}{'pred'} . ":[";
        foreach my $pid (@{$out_str{$key}{'pids'}}){
           $str = $str . $pid . ",";
        }
        chop($str);
        $str = $str . "])";
    }

    foreach my $nm (keys %nonmerge){
    	$str = $str . " " . $nm;
    }


    if($bash==0) {
	$str = $str  . "))\n";
    }
    else{$str = $str  . "\n";}

    print OUT $str;
    %out_str = ();
}

###########################################################################
# READ CONDITIONAL FILE INTO A STRUCTURE
###########################################################################
sub read_Conditional_file(){
    if($cfile eq "") {return;}

   open(CFILE,$cfile) or die "Cannot open $cfile \n";
   while(my $line=<CFILE>){
     if($line =~ /set_condition\(\/(.+)\/(\d+):/){
     	my $regexp_name = $1;
        my $arity = $2;

        $regex_conditional{$regexp_name} = $arity;
     }
     elsif($line =~ /set_condition\((.+)\/(\d+):/){
        my $name = $1;
        my $arity = $2;

        $conditional{$name} = $arity;
     }
   }
   close(CFILE);

   print "Conditional unification predicates file read\n";
}

###########################################################################
# CHECK IF CONDITIONAL
###########################################################################

sub check_conditional(){
	my ($pred) = @_;

        if(exists $conditional{$pred}){
        	return 1;
        }

        foreach my $regex (keys %regex_conditional){
            if($pred =~ /$regex/){
               return 1;
            }
        }

        return 0;
}

###########################################################################
# READ BOXER FILE INTO A STRUCTURE, ADD NONMERGE CONSTRAINTS, OUTPUT
###########################################################################
sub read_Parser_file(){
    my $ne_count = 0;
    my $new_id = 0;
    my $sent_id = "";
    my $word_counter = 0;

    open IN, "<:utf8", $ifile or die "Can't open '$ifile' for reading: $!";

    while(my $line=<IN>){
       chomp($line);
       if($line =~ /^%/){

       }
       elsif($line =~ /^id\((.+)\)\./){
           if(($sent_id ne "")&&((scalar keys %id2props)==0)){
                if($warnings==1){
                	print "No props for sent: $sent_id \n";
                }
    	   }

           if(((($sfile eq "")&&($nefile eq ""))&&($sent_id ne ""))&&($wholefileoutput==0)){
                if($warnings==1){
                	print "Processing sentence $sent_id.\n";
                }
	    	&add_nonmerge($sent_id);
	   	&printHenryFormat($sent_id,0);
                %id2props = ();
                %nonmerge = ();
           }

           $sent_id = $1;
           $sent_id =~ s/ //g;
           $sent_id =~ s/'//g;
       }
       elsif($line ne ""){
           my @prop_str = split(" & ", $line);
           foreach my $p (@prop_str){
                my $name;
                my @args;
                my $id_str="";
                my @ids = ();

                if($p =~ /\[(.*)\]:([^\(]+)\(([^\)]+)\)/){
                        $id_str = $1;
                        $name = lc($2);
                	@args = split(/,/,$3);
                }
                else{
                        if($warnings==1){
                        	print "Strange propositions: $p\n";
                        }
                }

                if($id_str eq ""){
                	$new_id++;
                        push(@ids,"$sent_id-ID$new_id");
                }
                else{
                    @ids = $id_str =~ /(\d+)/g;
                }

                for (my $i=0;$i<(scalar @args);$i++){
                	$args[$i]=$sent_id.$args[$i];
                }

                $name =~ s/ /-/g;
                $name =~ s/_/-/g;
                $name =~ s/:/-/g;
                #$name =~ s/\./-/g;
                $name =~ s/\//-/g;

                if($name =~ /(.+)-([vniar][nbd][j]?)$/){  ## THERE IS A PREFIX
                  my $prefix = $1;
                  my $postfix = $2;

                  if ($prefix =~ /[\w\d]/){ ## IT IS A NORMAL PREDICATE, NOT JUST SOME SYMBOLS
                       foreach my $id (@ids){
                               $id2props{$sent_id}{$id}{$name}{'args'}{$args[0]} = [@args];
                               $id2props{$sent_id}{$id}{$name}{'pos'} = $postfix;

                       }
                  }
           	}
                else{	##THERE IS NO POSTFIX
                   if ($name =~ /[\w\d]/){  ## IT IS A NORMAL PREDICATE, NOT JUST SOME SYMBOLS
                        foreach my $id (@ids){
                                    	$id2props{$sent_id}{$id}{$name}{'args'}{$args[0]} = [@args];
                                    	$id2props{$sent_id}{$id}{$name}{'pos'} = "";
                        }
                   }
                }
           }
       }
    }
    close IN;

    if(($sent_id ne "")&&((scalar keys %id2props)==0)){
                if($warnings==1){
                	print "No props for sent: $sent_id \n";
                }
    }

    if(($sfile eq "")&&($wholefileoutput==0)){
        if($warnings==1){
        	print "Processing sentence $sent_id.\n";
        }
	&add_nonmerge($sent_id);
	&printHenryFormat($sent_id,0);
        %id2props = ();
        %nonmerge = ();
    }

    if($warnings==1){print "Malt file read.\n";}
}