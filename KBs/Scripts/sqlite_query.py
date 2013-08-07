#!/usr/bin/python
# -*- coding: utf-8 -*-
import build_axiom as ba
import sqlite3
import sys
import argparse
        
def fetch_candidates(cursor,query,arg):
    candidates = []
    cursor.execute(query)
    while True:
        row = cursor.fetchone()
        if row == None:
            break
        candidates.append(row[arg])
    return candidates

def collect_word_info(word):
    name = word
    pos = raw_input("What is the POS? ")
    roles = raw_input("Enter any roles separated by commas ").split(",")
    if roles[0] == '':
        roles[0] = None
    while len(roles) < 4:
        roles.append(None)
    return pos,roles

def determine_utility(word):
    if type(word) == int:
        word = unicode(word)
    answer = raw_input("Do you want to build an axiom for "+word.encode("utf-8")+"? ")
    if answer == "yes" or answer == "y":
        return True
    return False
       

def build_axiom(word,pos,roles,domain,subdomain):
    axDomain = domain
    axSubdomain = subdomain
    axRole = roles[0]
    axRole2 = roles[1]
    axRole3 = roles[2]
    axRole4 = roles[3]
    weight = ba.determine_weight(domain,subdomain,axRole,axRole2,axRole3,axRole4)
    template = ba.Template(pos,word,axDomain,axSubdomain,axRole,axRole2,axRole3,axRole4,weight)        
    print template.build_full_axiom()
    
def main():
    parser = argparse.ArgumentParser(
        description="Axiom builder for lexical axioms.")
    parser.add_argument(
        "-w",
        "--word",
        help="The word to search . Should be the lemma of the word. Required to build an axiom.",
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
        help="The subdomain of the lexical entry.",
        required=True,
        )    
    parser.add_argument(
        "-c",
        "--conceptnet",
        help="conceptnet database (sql) to use",
        default="concept_net.db",
        )
    pa = parser.parse_args()
    axDomain = str(pa.domain)
    axSubdomain = str(pa.subdomain)
    #sqlite will look for a database with three columns (relation, arg1, arg2)
    con = sqlite3.connect(pa.conceptnet)
    to_find = "'"+pa.word.lower()+"'"
    query1 = "SELECT * FROM concepts where arg1="+to_find+";"
    query2 = "SELECT * FROM concepts where arg2="+to_find+";"

    with con:
      cur = con.cursor()
      candidates1 = fetch_candidates(cur,query1,2)
      candidates2 = fetch_candidates(cur,query2,1)        
      all_candidates = candidates1+candidates2
      no_dupes = sorted(list(set(all_candidates)))
      for c in no_dupes:
          if determine_utility(c):
              pos,roles = collect_word_info(c)
              build_axiom(c,pos,roles,axDomain,axSubdomain)
if __name__ == "__main__":
    main()
