__author__ = 'kiktak'


import sys
import re
import shlex
from xml.dom.minidom import parse
from getopt import getopt, GetoptError


def main(argv):
    outline = ''
    source = ''
    opts = None
    try:
        opts, args = getopt(argv, "ho:d", ["outline=", "data="])
    except GetoptError:
        pass
    except Exception as e:
        display_help(True, e)
    for opt, arg in opts:
        if opt == '-h':                                     # display help
            display_help()
            sys.exit()
        elif opt in ("-o", "--outline"):                      # set the name of the input file
            outline = arg
        elif opt in ("-d", "--data"):                      # set the name of the output file
            source = arg
    if len(source) == 0 or len(outline) == 0:         # check to make sure required parameters are defined (input and output file)
        display_help(True)
    transform(outline, source)


def transform(outline, source):
    dims, members = parseoutline(outline)
    writeoutput(source, dims, members)


def writeoutput(data, dimension, member):
    mpat = re.compile(r'"(?P<member>[^"]*)"')
    dpat = re.compile(r'\s(?P<data>\-?\d*\.?\d*)')
    dimension.pop('Measure', None)
    accounts = []
    with open(data, 'r') as f:
        for line in f:
            isAccount = False
            i = 0
            for item in shlex.split(line):
                item = item.strip('"')
                if not isnumeric(item):
                    if item in member:
                        if member[item] == 'Measure':
                            if not isAccount:
                                isAccount = True
                                del accounts[:]
                            accounts.append(item)
                        else:
                            dimension[member[item]] = item
                else:
                    print '\t'.join([''.join(value) for key, value in dimension.items()]) + '\t' + accounts[i] + '\t' + item
                    i += 1

def isnumeric(s):
    '''Returns True for all non-unicode numbers'''
    try:
        s = s.decode('utf-8')
    except:
        return False

    try:
        float(s)
        return True
    except:
        return False


def parseoutline(outline):
    members = {}
    dims = {}
    doc = parse(outline)
    otl = doc.getElementsByTagName("application")[0]
    for node in otl.childNodes:
        if node.localName is not None:
            if node.localName == 'Dimension':
                dimension = node.attributes['name'].value
                if dimension not in dims:
                    dims[dimension] = ''
                members.update(dig(node, dimension))
    return dims, members


def dig(nodes, dim):
    mydict = {}
    for node in nodes.childNodes:
        if node.localName is not None:
            if node.localName == 'Member':
                member = node.attributes['name'].value
                if not member in mydict:
                   mydict[member] = dim
                if len(node.childNodes):
                    mydict.update(dig(node, dim))
    return mydict


def display_help(error=False, exception=''):
    print '''XML Outline Compare
Usage: python essbase-xml-otl-compare.py -s <source XML file> -t <target XML file>
 -s, --source   Source XML File (required)
 -t, --target   Target XML File (required)
 -o, --output   Output File
Flags:
 -h             This Help
 -v, --verbose  Creates source.txt and target.txt files
'''
    if exception:
        print exception
    if error:
        sys.exit(2)
    else:
        sys.exit()

if __name__ == '__main__':
    #transform(r'test-data\aso-essbase-outline.xml', r'test-data\aso-essbase-extract.txt')
    main(sys.argv[1:])