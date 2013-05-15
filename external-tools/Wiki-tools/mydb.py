#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import sys

def get_CONN():
    return "host='localhost' dbname='wiki' user='wiki' password='wiki'"

def getCon(CONN_STRING):
    try:
        con = psycopg2.connect(CONN_STRING)
        con.set_client_encoding('UTF8')
        return con
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(-1)
    
def closeCon(con):
    if con:
        con.close()
     
def executeManyQuery(con,querys,debug):
    try:
        cur = con.cursor()
        for query in querys:
            if debug:
                print query
            cur.execute(query)
            con.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(-1)

def executeQuery(con,query,debug):
    try:
        cur = con.cursor()
        if debug:
            print query
        cur.execute(query)
        con.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(-1)

def executeQueryRecords(con,query,records,debug):
    try:
        cur = con.cursor()
        if debug:
            print query
        cur.executemany(query,records)
        con.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(-1)

def executeQueryResult(con,query,debug):
    try:
        cur = con.cursor()
        if debug:
            print query
        cur.execute(query)
        rows=cur.fetchall()
        return rows
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        sys.exit(-1)
