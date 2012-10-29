#! /usr/bin/python
import sys,re

def to_fs(infile):
    """Change 'f' to 'fs' at the end of sentences so treetagger will know
    when a sentence stops"""
    lines = []
    new = []
    for line in infile:
        line = line.strip().split("\t")
        lines.append(line)
    for i in range(len(lines)):
        if len(lines[0]) > 2:
            if lines[0][1] == "f" and len(lines[1]) < 2:
                lines[0][1] = "fs"
        print "\t".join(lines[0])
        lines.pop(0)
    

def main():
    infile = open(sys.argv[1],"r")
    words = to_fs(infile)

if __name__ == "__main__":
    main()
