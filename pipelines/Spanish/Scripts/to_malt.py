#! bash/bin/env python
import sys,re
arg_list = sys.argv
file = arg_list[1]


def malter(LINE_OBJECT):
    """formats lines for maltparser in conll format"""
    #Lemma
    Token = LINE_OBJECT[0].strip()
    #Use twice: POS and CPOS
    POS = replace_tag(LINE_OBJECT[1].strip())
    Lemma = LINE_OBJECT[2].strip()
    malt_line = "0"+"\t"+Token+"\t"+Lemma+"\t"+POS+"\t"+POS+"\t"+"0"+"\t"+"0"+"\t"+"ROOT"+"\t"+"-"+"\t"+"-"
    return malt_line

def reform(File):
    file_object = open(File,'r')
    malt_lines = []
    for line in file_object:
        line = line.rstrip()
        listed = line.split()
        #print line
        try:
            if re.search ("%%",line):
                pass
            else:
                #print line
                #print listed
                malt = malter(listed)
                #print malt
                malt_lines.append(malt)
                #print malt_lines
        except IndexError:
            malt_lines.append(line)
            #pass
    return malt_lines
    file_object.close()

def replace_tag(tag):
    if treeAdj.match(tag):
        return "a"
    elif treeConj.match(tag):
        return "c"
    elif treeDet.match(tag):
        return "d"
    elif treePunct.match(tag):
        return "f"
    elif treeInter.match(tag):
        return "i"
    elif treeNoun.match(tag):
        return "n"
    elif treePro.match(tag):
        return "p"
    elif treeAdv.match(tag):
        return "r"    
    elif treePrep.match(tag):
        return "s"
    elif treeVerb.match(tag):
        return "v"
    # elif treeDate.match(tag):
    #     return "w"
    elif treeNum.match(tag):
        return "z"
    else:
        return tag
    
treeAdj = re.compile("ADJ")
treeConj = re.compile("CC.*|CQUE|CSUBX")
treeDet = re.compile("ART|DM|QU")
treePunct = re.compile("BACKSLASH|CM|COLON|DASH|DOTS|LP|PERCT|QT|RP|SEMICOLON|SLASH|SYM|UMMX")
#^also FS for full stop - but need this to sepatate sents
treeInter = re.compile("ITJN|PNC")
treeNoun = re.compile("NMEA|NMON|NC|NP|ALF*|ACRNM|CODE|PE")
treePro = re.compile("INT|PPC|PPO|PPX|REL|SE")
treeAdv = re.compile("CSUBF|ADV|NEG")
treePrep = re.compile("PREP|CSUBI|PAL|PDAL|PREP/DEL")
treeVerb = re.compile("^V.*")
#treeDate = re.compile("")
treeNum = re.compile("CARD|FO|ORD")

def main():
    printable = reform(file)
    for line in printable:
        line_list = line.split('\t')
        try:
            pos = line_list[3]
            if pos == 'fs' or pos == 'FS':
                line_list[3] = "f"
                line_list[4] = "f"
                print "\t".join(line_list),'\n'
            else:
                print "\t".join(line_list)
        except IndexError:
            print line

if __name__ == "__main__":
    main()
