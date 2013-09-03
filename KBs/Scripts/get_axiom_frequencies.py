#! /usr/bin/python

import argparse
import sys
import re

def convert_tag(tag):
    tagmap = {"a":"adj","n":"nn","adv":"rb","v":"vb"}
    return tagmap[tag]

def build_key(pos,word):
    return word+"-"+pos
    
def build_freq_dict(ffile):
    content_tags = set(["a","adv","n","v"])
    freq_dict = {}
    with open(ffile,"r") as openfile:
        for line in openfile:
            items = line.strip().split(",")
            rank = items[0]
            freq = items[1]
            word = items[2]
            pos = items[3]
            if pos in content_tags:
                pos = convert_tag(items[3])
                combo = build_key(pos,word)
                #freq_dict[word] = [freq,pos,rank]
                freq_dict[combo] = [freq,rank]
    openfile.close()
    return freq_dict

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

def output_axiom_freq(input,freqs):
    with open(input,"r") as openfile:
        lines = filter(lambda l: l.startswith("("), (line.rstrip() for line in openfile))
        for line in lines:
            rs = find_right_side(line)
            #the following if loop processes only single-token axioms
            #could add a second conditional for > 2 right side split
            #to handle colocations, if necessary
            if rs and len(rs.split("(")) == 2:
                ax_combo = rs.split("(")[1].split()[0]
                #print ax_combo
                if freqs.has_key(ax_combo):
                    print ax_combo,",".join(freqs[ax_combo])

def main():
    parser = argparse.ArgumentParser(
        description="Gather frequencies for axioms.")
    parser.add_argument(
        "-i",
        "--input",
        help="Input file of axioms.",
        required=True,
        default=None)  
    parser.add_argument(
        "-f",
        "--frequencies",
        help="File containing frequencies. Default is English frequency file in this directory.",
        default="word.freq.en.csv")  
    parser.add_argument(
        "--output",
        help="Output file. Default is stdout.",
        default=None)  
    pa = parser.parse_args()

    freq_file = pa.frequencies
    freq_dict = build_freq_dict(freq_file)
    infile = pa.input
    output_axiom_freq(infile,freq_dict)
    
if __name__ == "__main__":
    main()
