__author__ = 'Keith Kikta'
__copyright__ = "Copyright 2015, EPM Junkie"
__license__ = "BSD"
__version__ = "1.0"
__maintainer__ = "Keith Kikta"
__email__ = "kkikta@gmail.com"
__status__ = "Alpha"

import sys
import re
from getopt import getopt, GetoptError

def main(argv):
    source = ''
    maps = ''
    delimiter = "\t"
    stats = False
    opts = None
    try:
        opts, args = getopt(argv, "hf:m:d:", ["file=", "map=", "delim="])
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
        elif opt in ("-m", "--map"):
            maps = arg
        elif opt in ("-d", "--delim"):
            delimiter = arg
    if source and maps:
        performreplace(source, maps, delimiter)
    else:
        display_help()


def performreplace(source, maps, delimiter="\t"):
    map = buildmap(maps, delimiter)
    rep = dict((re.escape(k), v) for k, v in map.iteritems())
    pat = re.compile("|".join(rep.keys()))
    with open(source, 'r') as f:
        text = f.read()
        text = pat.sub(lambda m: rep[re.escape(m.group(0))], text)
    print text


def buildmap(map, delimiter):
    maps = {}
    with open(map, 'r') as f:
        for item in f:
            items = item.split(delimiter)
            if not items[0] in maps:
                maps[items[0]] = items[1].strip()
            else:
                raise Exception(items[1], "Mapping already exists for " + items[0] + ":" + maps[items[0]])
    return maps


def display_help(error=False, exception=''):
    print '''Essbase Member Extract
Usage: python exportMembers.py -f <essbase extract file>
 -f, --file     Essbase extract file

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
    #performreplace(r'test-data\replace-source.txt', r'test-data\replace-maps.txt')
    main(sys.argv[1:])