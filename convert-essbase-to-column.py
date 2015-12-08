__author__ = 'Keith Kikta'
__copyright__ = "Copyright 2015, EPM Junkie"
__license__ = "BSD"
__version__ = "1.0"
__maintainer__ = "Keith Kikta"
__email__ = "kkikta@gmail.com"
__status__ = "Alpha"


import sys
import re
import shlex
from xml.dom.minidom import parse
from getopt import getopt, GetoptError


def main(argv):
    outline = ''
    source = ''
    output = ''
    opts = None
    try:
        opts, args = getopt(argv, "ho:d:f:", ["outline=", "data=", "file="])
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
        elif opt in ("-f", "--file"):
            output = arg
    if len(source) == 0 or len(outline) == 0:         # check to make sure required parameters are defined (input and output file)
        display_help(True)
    transform(outline, source, output)


def transform(outline, source, output):
    dims, members = parseoutline(outline)
    writeoutput(source, dims, members, output)


def writeoutput(data, dimension, member, output):
    mpat = re.compile(r'"(?P<member>[^"]*)"')
    dpat = re.compile(r'\s(?P<data>\-?\d*\.?\d*)')
    dimension.pop('Measure', None)
    accounts = []
    w = ''
    if len(output):
        w = open(output, 'w', 10240)
    with open(data, 'r') as f:
        for line in f:
            isAccount = False
            i = 0
            for item in shlex.split(line, posix=False):
                if item.strip() == '#Mi':
                    i += 1
                elif not isnumeric(item):
                    value = item.strip('"')
                    if value in member:
                        if member[value] == 'Measure':
                            if not isAccount:
                                isAccount = True
                                del accounts[:]
                            accounts.append(value)
                        else:
                            dimension[member[value]] = value
                else:
                    try:
                        if len(output):
                            w.write('\t'.join([''.join(value) for key, value in dimension.items()]) + '\t' + accounts[i] + '\t' + item + '\n')
                        else:
                            print '\t'.join([''.join(value) for key, value in dimension.items()]) + '\t' + accounts[i] + '\t' + item
                        i += 1
                    except:
                        print 'Error: [' + item + ']  - ' + line
                        raise
    if len(output):
        w.close()

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
    print '''Convert Essbase Extract to Column Format (ASO)
Usage: python convert-essbase-to-column.py -outline <Essbase XML Outline> -data <Data Extract>
 -o, --outline   Essbase XML Outline (required)
 -d, --data   Data Extract File (required)
Flags:
 -h             This Help
'''
    if exception:
        print exception
    if error:
        sys.exit(2)
    else:
        sys.exit()

if __name__ == '__main__':
    #transform(r'test-data\aso-essbase-outline.xml', r'test-data\aso-essbase-extract-2.txt', '')
    main(sys.argv[1:])
