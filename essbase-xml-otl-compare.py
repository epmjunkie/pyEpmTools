__author__ = 'Keith Kikta'
__copyright__ = "Copyright 2015, EPM Junkie"
__license__ = "BSD"
__version__ = "1.0"
__maintainer__ = "Keith Kikta"
__email__ = "kkikta@gmail.com"
__status__ = "Alpha"

import sys
import io
from xml.dom.minidom import parse
from getopt import getopt, GetoptError


class Alias(object):
    def __init__(self, value, table='Default'):
        self.value = value
        self.table = table

    def __str__(self):
        return self.table + '~' + self.value

class EssMember(object):
    def __init__(self, child, index, parent='#root', consolidation='+', alias=[], delimiter='|', source='+'):
        self.parent = parent
        self.child = child
        self.consolidation = consolidation
        self.alias = alias
        self.delimiter = delimiter
        self.source = source
        self.index = index

    def __str__(self):
        alias = ','.join(str(x) for x in self.alias)
        return str(self.index) + '.\t' + self.source + self.parent + self.delimiter + self.child + self.delimiter + self.consolidation + \
            self.delimiter + alias

    def __unicode__(self):
        alias = unicode(',').join(unicode(x) for x in self.alias)
        return unicode(self.index) + '.\t' + self.source + self.parent + self.delimiter + self.child + self.delimiter + self.consolidation + \
            self.delimiter + alias

    def trim(self):
        alias = unicode(',').join(unicode(x) for x in self.alias)
        return self.parent + self.delimiter + self.child + self.delimiter + self.consolidation + self.delimiter + alias

    def __hash__(self):
        return hash((self.parent, self.child, self.consolidation))

    def __eq__(self, other):
        return (self.parent, self.child, self.consolidation, ','.join(unicode(x) for x in self.alias)) == (other.parent, other.child, other.consolidation, ','.join(unicode(x) for x in other.alias))


def main(argv):
    source = ''
    target = ''
    output = ''
    opts = None
    verbose = False
    delimeter = '|'
    try:
        opts, args = getopt(argv, "hs:t:d:v:o:", ["source=", "target=", "delim=", "verbose", "output="])
    except GetoptError:
        pass
    except Exception as e:
        display_help(True, e)
    for opt, arg in opts:
        if opt == '-h':                                     # display help
            display_help()
            sys.exit()
        elif opt in ("-p", "--print"):
            verbose = True
        elif opt in ("-s", "--source"):                      # set the name of the input file
            source = arg
        elif opt in ("-t", "--target"):                      # set the name of the output file
            target = arg
        elif opt in ('-d', '--delim'):
            delimeter = arg
        elif opt in ('-o', '--output'):
            output = arg
    if len(source) == 0 or len(target) == 0:         # check to make sure required parameters are defined (input and output file)
        display_help(True)
    compare(source, target, delimeter, verbose, output)


def compare(source, target, delimiter, verbose, output):
    doc = parse(source)
    src = doc.getElementsByTagName("application")[0]
    doc = parse(target)
    tgt = doc.getElementsByTagName("application")[0]
    a, idx = drill(src)
    b, idx = drill(tgt)
    if verbose:
        writeExport("source.txt", a, nosource=True)
        writeExport("target.txt", b, nosource=True)
    c = diff(a, b)
    if len(output):
        writeExport(output, sorted(c, key=lambda x: x.index))
    else:
        for item in sorted(c, key=lambda x: x.index):
            print str(item)


def diff(list1, list2):
    c = set(list1).union(set(list2))
    d = set(list1).intersection(set(list2))
    result = list(c - d)
    src = set(result).intersection(set(list1))
    result = markSourceRemoved(result, src)
    result.sort(key=lambda x: x.index)
    return result


def markSourceRemoved(diff, src):
    for i in range(0, len(diff)):
        if diff[i] in src:
            diff[i].source = '-'
    return diff


def writeExport(file, list, delimiter='|', nosource=False):
    with io.open(file, 'w', encoding='utf8') as f:
        for item in list:
            if not nosource:
                f.write(unicode(item) + '\n')
            else:
                f.write(item.trim() + '\n')


def drill(nodes, index=0):
    arr=[]
    for node in nodes.childNodes:
        if node.localName is not None:
            if node.localName in ('Member', 'Dimension'):
                index += 1
                obj = EssMember(child=node.attributes['name'].value, index=index, alias=getAlias(node))
                if node.parentNode.localName in ('Member', 'Dimension'):
                    obj.parent = node.parentNode.attributes['name'].value
                for key in node.attributes.keys():
                    if key == 'Consolidation':
                        obj.consolidation = node.attributes[key].value
                arr.append(obj)
            if len(node.childNodes):
                arr1, index = drill(node, index)
                if len(arr1):
                    arr.extend(arr1)
    return arr, index


def getAlias(nodes):
    alias = []
    for node in nodes.childNodes:
        if node.localName is not None:
            if node.localName == 'Alias':
                alias.append(Alias(node.childNodes[0].data, node.attributes['table'].value))
    return alias


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
    #compare(r'test-data\source-outline.xml', r'test-data\target-outline.xml', '~', True, '')
    main(sys.argv[1:])
