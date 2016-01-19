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

use_minidom = False
try:
   from lxml import etree
except ImportError:
  from xml.dom.minidom import parse
  use_minidom = True


class Member:
    def __init__(self, dimension, name, parent):
        self.name = name
        self.dimension = dimension
        self.parent = parent


def main(argv):
    source = ''
    output = ''
    try:
        opts, args = getopt(argv, "hf:o:", ["file=", "output="])
    except GetoptError:
        pass
    except Exception as e:
        display_help(True, e)
    for opt, arg in opts:
        if opt == '-h':                                     # display help
            display_help()
            sys.exit()
        elif opt in ("-f", "--file"):
            source = arg
        elif opt in ("-o", "--output"):
            output = arg
    if len(source):
        extractOutline(source, output)
    else:
        display_help()


def loadxml(file):
    if not use_minidom:
        return etree.parse(file).getroot()
    else:
        return parse(file).getElementsByTagName("application")[0]


def extractOutline(source, output):
    src = loadxml(source)
    a, idx = drill(src)
    f = None
    if output:
        f = open(output, "w")
    for item in a:
        if not output:
            print(item.dimension + '|' + item.parent + '|' + item.name)
        else:
            f.write(item.dimension + '|' + item.parent + '|' + item.name + '\r\n')
    if output:
        f.close()


def drill(nodes, index=0):
    if not use_minidom:
        arr, index = drillx(nodes, index)
    else:
        arr, index = drillm(nodes, index)
    return arr, index


def isnull(value, default):
    if value is not None:
        return value
    else:
        return default

def drillx(nodes, dimension=None, index=0):
    arr=[]
    for node in nodes.iterchildren():
        if node.tag == 'Member':
            index += 1
            obj = Member(name=node.attrib['name'],
                         parent=node.getparent().attrib['name'],
                         dimension=dimension
                         )
            arr.append(obj)
        elif node.tag == 'Dimension':
            dimension = node.attrib['name']
        arr1, index = drillx(node, dimension, index)
        if len(arr1):
            arr.extend(arr1)
    return arr, index


def drillm(nodes, dimension=None, index=0):
    arr=[]
    for node in nodes.childNodes:
        if node.localName is not None:
            if node.localName == 'Member':
                index += 1
                if node.parentNode.localName in ('Member', 'Dimension'):
                    parent = node.parentNode.attributes['name'].value
                obj = Member(name=node.attributes['name'].value, parent=parent, dimension=dimension)
                arr.append(obj)
            elif node.localName == 'Dimension':
                dimension = node.attributes['name'].value
            if len(node.childNodes):
                arr1, index = drillm(node, dimension, index)
                if len(arr1):
                    arr.extend(arr1)
    return arr, index

def display_help(error=False, exception=''):
    print('''Parse Essbase Outline Members
Usage: python essbase-xml-outline-members.py -f <essbase extract file>
 -f, --file     Essbase extract file (required)
 -o, --output   Output file

Flags:
 -h             This Help
''')
    if exception:
        print(exception)
    if error:
        sys.exit(2)
    else:
        sys.exit()

if __name__ == '__main__':
    #extractOutline(r'test-data\aso-essbase-outline.xml', "")
    main(sys.argv[1:])
