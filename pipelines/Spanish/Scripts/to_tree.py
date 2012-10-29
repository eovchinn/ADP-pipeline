#! bash/bin/env python
import sys,re

def make_treeish(infile):
    trees = []
    for line in infile:
        line = line.strip().split("\t")
        if len(line) > 1:
            text = line[1]
            lemma = line[2]
            tag = line[3]
            treeline = [text,tag,lemma]
            trees.append(treeline)
        else:
            trees.append(line)
    infile.close()
    return trees


def main():
    infile = open(sys.argv[1],"r")
    treeLines = make_treeish(infile)
    for line in treeLines:
        print "\t".join(line)

if __name__ == "__main__":
    main()
