#! /usr/bin/python

import argparse
import sys
import re

def find_right_side(line):
    """Returns the right side of lexical axioms. 
    Returns false if the axiom is for mapping. """
    re.split("\(\^",line)
    if len(re.split("\(\^",line)) == 1:
        return False 
    if len(re.split("\(\^",line)) == 2:
        return "("+line.split("(")[-1]       
    if len(re.split("\(\^",line)) == 3:
        return re.split("\(\^",line)[-1] 

def collect_lexemes(infile):
    lexemes = []
    with open(infile,"r") as openfile:
        lines = filter(lambda l: l.startswith("("), (line.rstrip() for line in openfile))
        for line in lines:
            rs = find_right_side(line)  
            rs = find_right_side(line)
            #the following if loop processes only single-token axioms
            #could add a second conditional for > 2 right side split
            #to handle colocations, if necessary
            if rs and len(rs.split("(")) == 2:
                ax_combo = rs.split("(")[1].split()[0]
                lexemes.append(ax_combo)
    openfile.close()
    return lexemes

def combine_target_source(targets,sources):
    for t in targets:
        for s in sources:
            print t,s

def main():
    parser = argparse.ArgumentParser(
        description="Gather frequencies for axioms.")
    parser.add_argument(
        "-t",
        "--targets",
        help="Input file of target axioms.",
        required=True,
        default=None)  
    parser.add_argument(
        "-s",
        "--sources",
        help="Input file of source axioms.",
        required=True,
        default=None)  
    parser.add_argument(
        "--output",
        help="Output file. Default is stdout.",
        default=None)  
    pa = parser.parse_args()

    targetfile = pa.targets
    sourcefile = pa.sources
    target_words = collect_lexemes(targetfile)
    source_words = collect_lexemes(sourcefile)    
    combine_target_source(target_words,source_words)
    
if __name__ == "__main__":
    main()
