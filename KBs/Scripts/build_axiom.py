#! /usr/bin/python

import argparse
import sys


class Template(object):
    """
    Class representing axiom templates
    """
    def __init__(self,pos,name,domain,subdomain,r1,r2,r3,r4,weight):
        self.pos = pos
        self.name = name
        self.domain = domain
        self.subdomain = subdomain if subdomain else None
        self.r1 = r1 if r1 else None
        self.r2 = r2 if r2 else None
        self.r3 = r3 if r3 else None
        self.r4 = r4 if r4 else None
        self.weight = str(weight)
        
    def build_name(self):
        return "(name "+self.name+")"

    def build_domain(self):
        #if self.pos == "noun":
        arg = "x"
        return "(S#"+self.domain.upper()+" "+arg+" :"+self.weight+")"

    def build_subdomain(self):
        if self.pos == "noun":
            arg = "x"
        else:
            arg = "e0"
        return "(SS#"+self.subdomain.upper()+" "+arg+" :"+self.weight+")"

    def build_role(self,role):
        if role:
            #if self.pos == "noun":
            arg = "y e0"
            return "(R#"+role.upper()+" "+arg+" :"+self.weight+")"
        else:
            return ""

    def define_weight(self):
        elements = 0

    def build_left_side(self):
        roles = ""
        lsdomain = self.build_domain()        
        lssubdomain = self.build_subdomain()
        for role in [self.r1,self.r2,self.r3,self.r4]:
            roles += self.build_role(role)
        return "(^"+lsdomain+lssubdomain+roles+")"


    def assign_posTag(self,text):
        if text.lower() == "noun":
            return "nn"
        if text.lower() == "verb":
            return "vb"

    def build_right_side(self):
        tag = self.assign_posTag(self.pos)
        if tag == "nn":
            return "("+self.name+"-"+tag+" e0 x)"
        if tag == "vb":
            return "("+self.name+"-"+tag+" e0 x y u)"

    def build_full_axiom(self):
        outname = self.build_name()
        ls = self.build_left_side()
        rs = self.build_right_side()
        return "(B "+outname+"(=>"+ls+" "+rs+"))"

def determine_weight(d,sd,r1,r2,r3,r4):
    elements = 0
    for v in locals().values():
        if v is not None:
            if type(v) == str:
                elements +=1
    weight = round(0.9/elements,2)
    return weight
        
def main():
    parser = argparse.ArgumentParser(
        description="Axiom builder for lexical axioms.")
    parser.add_argument(
        "-n",
        "--name",
        help="The name of the word to be axiomatized. Should be the lemma of the word. Required to build an axiom.",
        required=True,        
        )    
    parser.add_argument(
        "-p",
        "--pos",
        help="Part of speech for the lexical entry. Must be one of:"
        "Noun, verb-intransitive, verb-transitive. "
        "Required to build an axiom.",
        required=True,
        )
    parser.add_argument(
        "-d",
        "--domain",
        help="The domain of the lexical entry. Required to build an axiom.",
        required=True,
        )
    parser.add_argument(
        "-s",
        "--subdomain",
        help="The subdomain of the lexical entry. If none is provided, the output will have only a domain.",
        required=True,
        )    
    parser.add_argument(
        "--role",
        help="Role that the word being axiomatized expects to be filled."
        )
    parser.add_argument(
        "--role2",
        help=" Second role that the word being axiomatized expects to be filled."
        )
    parser.add_argument(
        "--role3",
        help="Third role that the word being axiomatized expects to be filled."
        )
    parser.add_argument(
        "--role4",
        help="Fourth role that the word being axiomatized expects to be filled."
        )
    parser.add_argument(
        "--output",
        help="Output file. Default is stdout.",
        default=None)    
    pa = parser.parse_args()


    axName = str(pa.name).lower()
    axPOS = str(pa.pos).lower()
    axDomain = str(pa.domain)
    axSubdomain = str(pa.subdomain) 
    axRole = str(pa.role) if pa.role else None
    axRole2 = str(pa.role2) if pa.role2 else None
    axRole3 = str(pa.role3) if pa.role3 else None
    axRole4 = str(pa.role4) if pa.role4 else None 
    weight = determine_weight(axDomain,axSubdomain,axRole,axRole2,axRole3,axRole4)
    template = Template(axPOS,axName,axDomain,axSubdomain,axRole,axRole2,axRole3,axRole4,weight)
    #print template.build_name()
    #print template.build_domain()
    #print template.build_subdomain()    
    #print template.build_left_side()
    #print template.build_right_side()
    print template.build_full_axiom()
    
if __name__ == "__main__":
    main()
