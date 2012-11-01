use strict;
use Data::Dumper;
use Getopt::Long;

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

my $output_str = "";

my $cost = "1";
my $split = 0;
my $samepred = 1;
my $sameargs = 0;
my $modality = 0;
my $warnings = 0;
my $wholefileoutput = 0;

GetOptions ("input=s" => \$ifile,
	     "output=s" => \$ofile,
	     "conditional=s" => \$cfile,
            "coref=s" => \$sfile,
            "nedis=s" => \$nefile,
            "cost=s" => \$cost,
            "split=i" => \$split,
            "nonmerge=s" => \$nonmerge_opt,
            "warnings=i" => \$warnings,
            "wholefileoutput=i" => \$wholefileoutput);


&setParameters();

&read_Conditional_file();

if($ofile ne "") {open(OUT,">$ofile") or die "Cannot open $ofile\n";}

&read_Boxer_file();

## ADD COREF INFO FROM STANDFORD NLP
&add_coref();

## ADD NE DISAMBIGUATION INFO FROM STANDFORD NLP
&add_nedis();

## IF COREF OR NE INFO WAS ADDED THEN PRINT OUT (OTHEWISE IT HAS BEEN ALREADY PRINTED OUT)
if((($sfile ne "")||($nefile ne ""))||($wholefileoutput==1)){
        &printHenryFormat_batch();
}

if($warnings==1){print "Henry file printed.\n";}

if($ofile ne "") {close OUT;}
else{print $output_str;}


###########################################################################
# SET PARAMETERS
###########################################################################

sub setParameters(){
   if(($split!=0)&&($split!=1)) {print("Wrong value of 'split' parameter: $split. Only '0' and '1' accepted.\n"); exit(0);}

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
   elsif($p eq "samepred") {$samepred = 1;}
   elsif($p eq "sameargs") {$sameargs = 1;}
   else{print("Wrong value of 'nonmerge' parameter: $p. Only 'modality', 'samepred', and 'sameargs' accepted.\n"); exit(0);}
}

###########################################################################
# PRING USAGE
###########################################################################

sub printUsage(){
    print "Usage: perl Boxer2Henry.pl\n --input <boxer file>\n --output <henry file>\n --cost <real number> (default=1)\n [--conditional <conditional unification file>]\n [--coref <standford coref file>]\n [--nedis <disambiguated named entities file>]\n [--split <split nouns concatenated by Boxer> (possible values: [0=no, 1=yes], default: 0)]\n [--nonmerge <nonmerge options> (possible values:modality,samepred,sameargs) 'modality' -- consider modality to create non-merge, 'samepred' -- non-merge for props with the same name, 'sameargs' -- non-merge for args of the same prop] \n";
    exit(0);
}

###########################################################################
# ADD NAMED ENTITIES DISAMBIGUATION INFO
###########################################################################

my %nedis_info = ();

sub add_nedis(){
     if($nefile eq "") {return;}

     &read_nedis_file();

     my $constant_counter = 0;

    foreach my $entity (keys %nedis_info){
         $constant_counter++;
         my $new_predname = lc($entity)."-nn";
         $new_predname =~ s/_/-/g;

         my %been = ();

         foreach my $key (keys %{$nedis_info{$entity}}){
              my $start = $nedis_info{$entity}{$key}{'start'};
              my $end = $nedis_info{$entity}{$key}{'end'};

              my $sid = $nedis_info{$entity}{$key}{'sid'};
              for (my $i=$start; $i<=$end;$i++){
                   my $boxer_tid = $global_token_index{$i}{'tid'};

                   if(exists $id2props{$sid}{$boxer_tid}){
                        for my $pname (keys %{$id2props{$sid}{$boxer_tid}}){
                            for my $farg (keys %{$id2props{$sid}{$boxer_tid}{$pname}{'args'}}){
                                 my @args =  @{$id2props{$sid}{$boxer_tid}{$pname}{'args'}{$farg}};
                                 if((scalar @args)==2){
                                      #ADD NEW EQUALITY
                                      #$merge{$constant_counter."E"}{$args[0]}=1;
                                      #$merge{$constant_counter."E"}{"nee".$constant_counter}=1;

                                      $merge{$entity}{$args[1]}=1;
                                      #REPLACE OLD PREPS WITH AIDA ENTITY
                                      #$merge{$entity}{"ne".$constant_counter}=1;
	                         }
                            }
                        }
                        #REPLACE OLD PREPS WITH AIDA ENTITY
                        #delete($id2props{$sid}{$boxer_tid});
                   }
                   #REPLACE OLD PREPS WITH AIDA ENTITY
                   #$id2props{$sid}{$boxer_tid}{$new_predname}{'args'}{"nee".$constant_counter} = ["nee".$constant_counter,"ne".$constant_counter];
              }
         }
         if((scalar(keys %{$merge{$entity}}))<2){delete $merge{$entity};}
    }

    #print OUT Dumper(%merge); exit(0);
}

###########################################################################
# ADD NAMED ENTITIES DISAMBIGUATION INFO
###########################################################################

sub read_nedis_file(){
    open(FILE,$nefile) or die "Cannot open $nefile\n";

    my $nedis_counter = 0;

    while(my $line=<FILE>){
         if($line =~ /^(.+) ([^\s]+):(\d+)-(\d+) -> ([^\s\n]+)/){
                my $mention = $1;
                my $sid = $2;
                my $start_id = $3;
                my $end_id = $4;
                my $entity = $5;

                #REPLACE UNICORE
                #002d -
    		#002c ,
    		#002e .
    		#0028 (
    		#0029 )
    		#0027 '

                $entity =~ s/\\u002d/-/g;
                $entity =~ s/\\u002c//g;
                $entity =~ s/\\u002e/\./g;
                $entity =~ s/\\u0028//g;
                $entity =~ s/\\u0029//g;
                $entity =~ s/\\u0027/'/g;

                if($entity ne "--NME--"){
                	$nedis_counter++;
                        #$nedis_info{$entity}{$nedis_counter}{'mention'} = $mention;
                        #$nedis_info{$entity}{$nedis_counter}{'sid'} = $sid;

                        #MATCH AIDA TOKENIZAZION WITH BOXER TOKENIZATION
                        my @tokens = split(/ /,$mention);
                        my $first_token = $tokens[0];
                        my $found=0;
                        my $real_start=-1;
                        my $real_end=-1;

                        my $iteration=0;
                        my $i=$start_id;
                        while($iteration < 50){
                            if($first_token eq $global_token_index{$i}{'word'}){
                            	$found=1;
                                $real_start=$i;
                                $real_end=$end_id-$iteration;
                                last;
                            }
                            else{
                            	$i--;
                                if(!(exists $global_token_index{$i})){last;}
                            }
                            $iteration++;
                        }

                        if($found==0){
                        	my $iteration=0;
	                        my $i=$start_id;
	                        while($iteration < 50){
                                    if($first_token eq $global_token_index{$i}{'word'}){
	                                $found=1;
	                                $real_start=$i;
                                        $real_end=$end_id+$iteration;
                                        last;
	                            }
	                            else{
	                                $i++;
                                        if(!(exists $global_token_index{$i})){last;}
	                            }
                                    $iteration++;
	                        }
                        }
                        if($found==1){
                                $nedis_info{$entity}{$nedis_counter}{'start'} = $real_start;
                                $nedis_info{$entity}{$nedis_counter}{'end'} = $real_end;
                                $nedis_info{$entity}{$nedis_counter}{'sid'} = $global_token_index{$real_start}{'sid'};
                        }
                }
         }
         else{
                if($warnings==1){
                	print "Strange NE line: $line";
                }
         }
    }

    close FILE;

    #print Dumper(%nedis_info);
    #exit(0);
}

###########################################################################
# ADD COREF INFO
###########################################################################

my %coref_info = ();

sub add_coref(){

    if($sfile eq "") {return;}

    &read_coref_file();

    my $constant_counter = 0;

    foreach my $key (keys %coref_info){
        $constant_counter++;
        my %been = ();
        foreach my $sid (keys %{$coref_info{$key}}){
             foreach my $tid (keys %{$coref_info{$key}{$sid}}){
                  my $boxer_tid = $sid * 1000 + $tid;
                  if(exists $id2props{$sid}{$boxer_tid}){
                        for my $pname (keys %{$id2props{$sid}{$boxer_tid}}){
                           for my $farg (keys %{$id2props{$sid}{$boxer_tid}{$pname}{'args'}}){
                                my @args =  @{$id2props{$sid}{$boxer_tid}{$pname}{'args'}{$farg}};

	                        my $arg = "";

	                        if((scalar @args)==2){
	                              $arg = $args[1];
	                        }
	                        elsif($pname =~ /^of-in/){
	                              $arg = $args[2];
	                        }
	                        else{
                                        if($warnings==1){
                                        	print "Another coref element ($sid, $boxer_tid): $pname\n";
                                        }
	                        }

                                $merge{$constant_counter}{$arg}=1;
                           }
                        }
                  }
             }
        }

        if((scalar(keys %{$merge{$constant_counter}}))<2){delete $merge{$constant_counter};}
    }

    if($warnings==1){print "Coreference information added.\n";}
    #print OUT Dumper(%merge); exit(0);
}

###########################################################################
# REPLACE ARGS
###########################################################################

sub replace_args(){
    my ($arg,$newarg,$sid) = @_;

    if($sid ne ""){
    	foreach my $aid (keys %{$args2props{$sid}{$arg}}){
	            foreach my $ap (keys %{$args2props{$sid}{$arg}{$aid}}){
	                    foreach my $aind (keys %{$args2props{$sid}{$arg}{$aid}{$ap}}){
                                       if(exists $id2props{$sid}{$aid}{$ap}){
                                       		$id2props{$sid}{$aid}{$ap}{'args'}[$aind] = $newarg;
                                       }
	                    }
	            }
	}
	$args2props{$sid}{$newarg} = delete $args2props{$sid}{$arg};

    }
    else{
       foreach my $s (keys %args2props){
          &replace_args($arg,$newarg,$s);
       }
    }
}

###########################################################################
# READ COREF FILE
###########################################################################

sub read_coref_file(){
    open(FILE,$sfile) or die "Cannot open $sfile\n";

    my $sid = "";
    my $tid = "";
    my %id2word = ();
    my $coref_counter = -1;
    my $coref_flag = 0;

    my $coref_sid;
    my $coref_head;

    while(my $line=<FILE>){
         if($line =~ /<sentence id="(\d+)">/){
         	$sid = $1;
         }
         elsif($line =~ /<token id="(\d+)">/){
                $tid = $1;
         }
         elsif($line =~ /<word>(.+)<\/word>/){
         	my $word = $1;
                $id2word{$sid}{$tid} = $word;
         }
         elsif($line =~ /<coreference>/){
                $coref_counter++;
                $coref_flag = 1;
         }
         elsif(($coref_flag==1)&&($line =~ /<sentence>(\d+)<\/sentence>/)){
                $coref_sid = $1;
         }
         elsif(($coref_flag==1)&&($line =~ /<head>(\d+)<\/head>/)){
                my $coref_tid = $1;
                $coref_info{$coref_counter}{$coref_sid}{$coref_tid} = $id2word{$coref_sid}{$coref_tid};
         }
    }

    close FILE;
    %id2word = ();

    if($warnings==1){print "Coference file read.\n"; }
}


###########################################################################
# ADD NON-MERGE CONSTRAINTS
###########################################################################

sub add_nonmerge(){
   my ($sent_id) = @_;

   if(($modality+$samepred+$sameargs)==0) {return;}

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
   if(($samepred==1)||($modality==1)){
       for my $pname (keys %props2pids){
           if($samepred==1){
                for my $farg (keys %{$props2pids{$pname}}){
                	$props2pids{$pname}{$farg}{'cond'} = &check_conditional($pname);
                }
           }

           if($modality==1){
                foreach my $farg (keys %{$props2pids{$pname}} ){
                       if($props2pids{$pname}{$farg}{'pos'} eq 'n'){$props2pids{$pname}{$farg}{'mod'} = "" ;}
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

           if($props2pids{$pname1}{$farg1}{'cond'} == 0){
                if($samepred == 1){
                     for my $farg2 (keys %{$props2pids{$pname1}}){
                           if(($farg1 ne $farg2)&&(!(exists $nonmerge{"(!= ".$farg2." ".$farg1.")"}))){
                            ## FIRST ARGUMENTS OF PREDICATES HAVING THE SAME NAME AND THE SAME PID
           			## CANNOT BE MERGED (EXCLUDING CONDITIONAL UNIFICATION PREDICATES)
                           	for my $pid (keys %{$props2pids{$pname1}{$farg1}{'pid'}}){
                                     if(exists $props2pids{$pname1}{$farg2}{'pid'}{$pid}){
                                         $nonmerge{"(!= ".$farg1." ".$farg2.")"} = 1;
                                         last;
                                     }
                                }
                                ############################################
                           }
                     }
                }
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
           }
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

   if($ofile ne ""){print OUT "\n(O (name 0) (^";}
   else{$output_str = $output_str . "\n(O (name 0) (^";}

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

   if($ofile ne ""){print OUT $str . "))\n";}
   else{$output_str = $output_str . $str . "))\n";}
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

    if($ofile ne ""){print OUT $str;}
    else{$output_str = $output_str . $str;}
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
sub read_Boxer_file(){
    my $ne_count = 0;
    my $new_id = 0;
    my $sent_id = "";
    my $word_counter = 0;
    my @lines = ();

    if($ifile ne ""){
	open(IN,$ifile) or die "Cannot open $ifile\n";
    	@lines = <IN>;
    }
    else{@lines = <STDIN>;}
    
    foreach my $line(@lines){
       chomp($line);
       if($line =~ /^%%%/){

       }
       elsif($line =~ /^id\((.+),\d+\)\./){
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
           $ne_count = 0;

           #$count_words_before{$sent_id} = $word_counter;
       }
       elsif($line =~ /^(\d+) ([^\s]+) [^\s]+ [^\s]+ [^\s]+/){
           $word_counter++;
           if(($sfile ne "")||($nefile ne "")){
                  my $id = $1;
	          my $word = $2;
	          $global_token_index{$word_counter}{'tid'} = $id;
                  $global_token_index{$word_counter}{'sid'} = $sent_id;
                  $global_token_index{$word_counter}{'word'} = $word;
           }
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

                if($name =~ /(.+)-([a-z])$/){  ## THERE IS A PREFIX
                  my $prefix = $1;
                  my $postfix = $2;

                  my $newpostfix;

                  if($postfix eq "n"){
                      $newpostfix = "nn";
                  }
                  elsif($postfix eq "v"){
                      $newpostfix = "vb";
                  }
                  elsif($postfix eq "a"){
                      $newpostfix = "adj";
                  }
                  elsif($postfix eq "r"){
                      $newpostfix = "rb";
                  }
                  elsif($postfix eq "p"){
                      $newpostfix = "in";
                  }
                  else{
                        if($warnings==1){
                        	print "Strange postfix: $prefix-$postfix in sent $sent_id \n";
                        }
                        $newpostfix = $postfix;
                  }

                  if ($prefix =~ /[\w\d]/){ ## IT IS A NORMAL PREDICATE, NOT JUST SOME SYMBOLS
                       if(($split==1)&&(($postfix eq "n")&&($prefix =~ /-/))){ ## A NOUN NEEDS TO BE SPLIT
                           my @nns = split("-",$prefix);
                           for (my $i=0; $i<(scalar @nns);$i++){
                        	if($i==(scalar @nns)-1){
                                    my $lname = $nns[$i]."-nn";

                                    foreach my $id (@ids){
                                    	$id2props{$sent_id}{$id}{$lname}{'args'}{$args[0]} = [@args];
                                    	$id2props{$sent_id}{$id}{$lname}{'pos'} = "n";

                                    }
                                }
                                else{
                                    my $ne_count++;
                                    my $lname = $nns[$i]."-".$newpostfix;

                                    foreach my $id (@ids){
                                    	$id2props{$sent_id}{$id}{$lname}{'args'}{$sent_id."ne".$ne_count} = [$sent_id."ne".$ne_count,$args[1]];
                                    	$id2props{$sent_id}{$id}{$lname}{'pos'} = "n";
                                    }
                                }
                           }
                       }
                       else{  ## NO NEED TO SPLIT
                                my $lname = $prefix."-".$newpostfix;

                                foreach my $id (@ids){
                                    	$id2props{$sent_id}{$id}{$lname}{'args'}{$args[0]} = [@args];
                                    	$id2props{$sent_id}{$id}{$lname}{'pos'} = $postfix;

                                }
                       }
                  }
           	}
                else{	##THERE IS NO POSTFIX
                   if ($name =~ /[\w\d]/){  ## IT IS A NORMAL PREDICATE, NOT JUST SOME SYMBOLS
                        $name = &check_prep($name);  ## CHECK IF IT IS A PROPOSITION
                        my $lname = $name;

                        foreach my $id (@ids){
                                    	$id2props{$sent_id}{$id}{$lname}{'args'}{$args[0]} = [@args];
                                    	$id2props{$sent_id}{$id}{$lname}{'pos'} = "";
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

    if((($sfile eq "")&&($nefile eq ""))&&($wholefileoutput==0)){
        if($warnings==1){
        	print "Processing sentence $sent_id.\n";
        }
	&add_nonmerge($sent_id);
	&printHenryFormat($sent_id,0);
        %id2props = ();
        %nonmerge = ();
    }

    if($warnings==1){print "Boxer file read.\n";}
}
################################################################################
# CHECK IF BOXER DID NOT RECOGNIZE SOME PREPOSITIONS AS SUCH
################################################################################
sub check_prep()
{
  my ($predname) = @_;

  my @prepositions = (
	"abaft",
	"aboard",
	"about",
	"above",
	"absent",
	"across",
	"afore",
	"after",
	"against",
	"along",
	"alongside",
	"amid",
	"amidst",
	"among",
	"amongst",
	"around",
	"as",
	"aside",
	"astride",
	"at",
	"athwart",
	"atop",
	"barring",
	"before",
	"behind",
	"below",
	"beneath",
	"beside",
	"besides",
	"between",
	"betwixt",
	"beyond",
	"but",
	"by",
	"concerning",
	"despite",
	"during",
	"except",
	"excluding",
	"failing",
	"following",
	"for",
	"from",
	"given",
	"in",
	"including",
	"inside",
	"into",
	"lest",
	"like",
	"minus",
	"modulo",
	"near",
	"next",
	"of",
	"off",
	"on",
	"onto",
	"opposite",
	"out",
	"outside",
	"over",
	"pace",
	"past",
	"plus",
	"pro",
	"qua",
	"regarding",
	"round",
	"sans",
	"save",
	"since",
	"than",
	"through",
	"throughout",
	"till",
	"times",
	"to",
	"toward",
	"towards",
	"under",
	"underneath",
	"unlike",
	"until",
	"up",
	"upon",
	"versus",
	"via",
	"vice",
	"with",
	"within",
	"without",
	"worth",
	);

  foreach my $preposition (@prepositions){
       if($predname eq $preposition){
                #print $predname . "\n";
       		return $predname."-in";
       }
  }

   return $predname;
}
