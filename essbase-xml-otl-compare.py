__author__ = 'Keith Kikta'
__copyright__ = "Copyright 2015, EPM Junkie"
__license__ = "BSD"
__version__ = "1.0"
__maintainer__ = "Keith Kikta"
__email__ = "kkikta@gmail.com"
__status__ = "Alpha"

import sys
import io
from getopt import getopt, GetoptError
from difflib import SequenceMatcher

use_minidom = False
try:
   from lxml import etree
except ImportError:
  from xml.dom.minidom import parse
  use_minidom = True


class Alias(object):
    def __init__(self, value, table='Default'):
        self.value = value
        self.table = table

    def __str__(self):
        return self.table + '~' + self.value

class EssMember(object):
    def __init__(self, child, index, flags, parent='#root', consolidation='+', alias=[], delimiter='|', source='+', formula=None):
        self.parent = parent
        self.child = child
        self.consolidation = consolidation
        self.alias = alias
        self.delimiter = delimiter
        self.source = source
        self.index = index
        self.flags = flags
        self.formula = formula

    def __str__(self):
        alias = ','.join(str(x) for x in self.alias)
        return str(self.index) + '.\t' + self.source + self.parent + self.delimiter + self.child + \
               self.delimiter + self.consolidation + self.delimiter + alias

    def __unicode__(self):
        alias = unicode(',').join(unicode(x) for x in self.alias)
        return unicode(self.index) + '.\t' + self.source + self.parent + self.delimiter + self.child + \
               self.delimiter + self.consolidation + self.delimiter + alias

    def trim(self):
        alias = unicode(',').join(unicode(x) for x in self.alias)
        return self.parent + self.delimiter + self.child + self.delimiter + self.consolidation + self.delimiter + alias

    def __hash__(self):
        return hash((self.parent, self.child, self.consolidation))

    def __eq__(self, other):
        aopts = ""
        bopts = ""
        for x in self.flags.lower():
            if x == "c":  # Consolidation
                aopts += ','.join([aopts, self.consolidation])
                bopts += ','.join([bopts, other.consolidation])
            if x == "a":  # Aliases
                aopts += ','.join([aopts, ','.join(unicode(x) for x in self.alias)])
                bopts += ','.join([bopts, ','.join(unicode(x) for x in other.alias)])
            if x == "f":  # Formula
                aopts += ','.join([aopts, self.formula])
                bopts += ','.join([bopts, other.formula])
        return (self.parent, self.child, aopts) == (other.parent, other.child, bopts)


def main(argv):
    source = ''
    target = ''
    output = ''
    opts = None
    verbose = False
    delimeter = '|'
    flags = ''
    diffreport = False
    checkPyVersion()
    try:
        opts, args = getopt(argv, "hs:t:d:v:o:f:d:", ["source=", "target=", "delim=", "verbose", "output=", "flags=", "diff"])
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
        elif opt in ('-f', '--flags'):
            flags = arg
        elif opt in ('-d', '--diff'):
            diffreport = True
    if len(source) == 0 or len(target) == 0:         # check to make sure required parameters are defined (input and output file)
        display_help(True)
    compare(source, target, delimeter, verbose, output, flags, diffreport)

def loadxml(file):
    if not use_minidom:
        return etree.parse(file).getroot()
    else:
        return parse(file).getElementsByTagName("application")[0]

def compare(source, target, delimiter, verbose, output, flags, diffreport):
    src = loadxml(source)
    tgt = loadxml(target)
    a, idx = drill(src, flags)
    b, idx = drill(tgt, flags)
    if verbose:
        writeExport("source.txt", a, nosource=True)
        writeExport("target.txt", b, nosource=True)
    if diffreport:
        sm = SequenceMatcher(None, a, b)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != 'equal':
                    diffprint(tag, a, b, i1, i2, j1, j2)
    else:
        c = diff(a, b)
        if len(output):
            writeExport(output, sorted(c, key=lambda x: x.index))
        else:
            for item in sorted(c, key=lambda x: x.index):
                print(unicode(item))

def diffprint(tag, src, tgt, i, j, x, y):
    if tag != 'replace':
        for a in range(i, j):
            print(unicode(tag) + '\t' + unicode(src[a]))
        for a in range(x, y):
            print(unicode(tag) + '\t' + unicode(tgt[a]))
    else:
        z = j - i
        for a in range(0,z):
            print(unicode(tag) + '\t' + unicode(src[i + a]) + '\n\t' + unicode(tgt[x + a]))

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


def drill(nodes, flags, index=0):
    if not use_minidom:
        arr, index = drillx(nodes, flags, index)
    else:
        arr, index = drillm(nodes, flags, index)
    return arr, index


def isnull(value, default):
    if value is not None:
        return value
    else:
        return default

def drillx(nodes, flags, index=0):
    arr=[]
    for node in nodes.iterchildren():
        if node.tag in ('Member', 'Dimension'):
            index += 1
            obj = EssMember(child=node.attrib['name'],
                            parent=node.getparent().attrib['name'],
                            consolidation=isnull(node.get('Consolidation'), '+'),
                            flags=flags,
                            index=index,
                            alias=getAliasx(node))
            arr.append(obj)
        arr1, index = drillx(node, flags, index)
        if len(arr1):
            arr.extend(arr1)
    return arr, index


def drillm(nodes, flags, index=0):
    arr=[]
    for node in nodes.childNodes:
        if node.localName is not None:
            if node.localName in ('Member', 'Dimension'):
                index += 1
                obj = EssMember(child=node.attributes['name'].value,
                                flags=flags,
                                index=index,
                                alias=getAliasm(node))
                if node.parentNode.localName in ('Member', 'Dimension'):
                    obj.parent = node.parentNode.attributes['name'].value
                for key in node.attributes.keys():
                    if key == 'Consolidation':
                        obj.consolidation = node.attributes[key].value
                arr.append(obj)
            if len(node.childNodes):
                arr1, index = drillm(node, flags, index)
                if len(arr1):
                    arr.extend(arr1)
    return arr, index


def getAliasx(nodes):
    alias = []
    for node in nodes.iterchildren():
        if node.tag == 'Alias':
            alias.append(Alias(node.text, node.attrib['table']))
    return alias


def getAliasm(nodes):
    alias = []
    for node in nodes.childNodes:
        if node.localName is not None:
            if node.localName == 'Alias':
                alias.append(Alias(node.childNodes[0].data, node.attributes['table'].value))
    return alias


def display_help(error=False, exception=''):
    print('''XML Outline Compare
Usage: python essbase-xml-otl-compare.py -s <source XML file> -t <target XML file> [-f[ca]]
 -s, --source   Source XML File (required)
 -t, --target   Target XML File (required)
 -o, --output   Output File
 -f, --flags    a - Aliases
                c - Consolidation
                f - Formuals

Flags:
 -h             This Help
 -v, --verbose  Creates source.txt and target.txt files
 -d, --diff     Creates a diff style report
''')
    if exception:
        print(exception)
    if error:
        sys.exit(2)
    else:
        sys.exit()

def checkPyVersion():
    if sys.version_info[0] > 2:
        print('Requires Python or Jython 2.x')
        sys.exit()

if __name__ == '__main__':
    #compare(r'test-data\sourceP.xml', r'test-data\targetP.xml', '~', True, '', 'c')
    main(sys.argv[1:])
