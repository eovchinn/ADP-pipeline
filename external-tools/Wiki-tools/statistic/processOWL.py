#!/usr/bin/python
# -*- coding: utf-8 -*-

import xml.etree.cElementTree as xml

class Node:
    def __init__(self):
        self.name = ''
        self.children = []
        self.equNodes = []
        self.parent = None
    
def buildHTree(owlTree):
    '''
    build a tree which reflect the subclassof relation from the owl file
    This function return another xml tree as result
'''
    #pdb.set_trace()
    # some namespace
    rdf = '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}'
    owl = '{http://www.w3.org/2002/07/owl#}'
    rdfs = '{http://www.w3.org/2000/01/rdf-schema#}'
    
    root = Node()
    root.name = '__root__'
    nodeMap={}
    rootMap={}
    owlRoot = owlTree.getroot()
    for owlClass in owlRoot.findall(owl +'Class'):
        parentXML = owlClass.find(rdfs+"subClassOf")
        if parentXML != None:

            parentName = parentXML.get(rdf+"resource")
            #print parentName
            if not parentName in nodeMap:
                parentNode = Node()
                parentNode.name = parentName
                nodeMap[parentName]=parentNode
                rootMap[parentName]=parentNode
            
            name = owlClass.get(rdf+'about')
            if not name in nodeMap:
                node = Node()
                node.name = name
                nodeMap[name]=node
            
            node = nodeMap[name]
            parentNode = nodeMap[parentName]
            
            parentNode.children.append(node)
            node.parent = parentNode
            
            if name in rootMap:
                del rootMap[name]

            
        else:
            # add self in nodeMap and rootMap
            name = owlClass.get(rdf+'about')
            if not name in nodeMap:
                node = Node()
                node.name = name 
                nodeMap[name]=node
                rootMap[name]=node
        # equivant class
        name = owlClass.get(rdf+'about')
        node = nodeMap[name]
        for equClass in owlClass.findall(owl+"equivalentClass"):
            equName = equClass.get(rdf+'resource')
            if not equName in nodeMap:
                equNode= Node()
                equNode.name= equName
                nodeMap[equName]=equNode
            equNode = nodeMap[equName]
            node.equNodes.append(equNode)
            
    for rname in rootMap:
        n = rootMap[rname]
        root.children.append(n)
    
    return root


def convert2XML(root):
    queue=[]
    xmlqueue=[]
    queue.append(root)
    xmlroot = xml.Element('Type')
    xmlroot.attrib['name']=root.name
    xmlqueue.append(xmlroot)
    while len(queue)>0:
        current = queue[0]
        del queue[0]
        currentXML = xmlqueue[0]
        del xmlqueue[0]
        for child in current.children:
            childXML = xml.Element('Type')
            childXML.attrib['name']= child.name
            currentXML.append(childXML)
            queue.append(child)
            xmlqueue.append(childXML)
        
    return xmlroot

        
def main():
    from optparse import OptionParser
    #option
    usage = "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-f","--file", dest="filePath",help="the *.owl files dir path")
    parser.add_option("-o","--outputfile", dest="outPath",help="the hierachical files dir path")
    (options,args) = parser.parse_args()
    filePath = options.filePath
    outPth = options.outPath

    tree = xml.parse(filePath)
    root = buildHTree(tree)
    rootXML = convert2XML(root)
    xmlStr = xml.tostring(rootXML)
    file = open(outPath,'w')
    file.write(xmlStr)
    file.close()

if __name__ == '__main__':
    main()
