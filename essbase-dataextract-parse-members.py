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
from collections import defaultdict


def main(argv):
    source = ''
    output = ''
    stats = False
    opts = None
    try:
        opts, args = getopt(argv, "hsf:o:", ["file=", "output=", "stats"])
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
        elif opt in ("-s", "--stats"):
            stats = True
        elif opt in ("-o", "--output"):
            output = arg
    if len(source):
        extractMembers(source, output, stats)
    else:
        display_help()


def extractMembers(source, output, stats):
    pat = re.compile(r'"(?P<member>[^"]*)"')
    members = defaultdict(int)
    with open(source, 'r') as f:
        for line in f:
            grp = re.match(pat, line)
            if grp is not None:
                for item in grp.groups():
                    members[item] += 1
    if not len(output):
        for (k, v) in sorted(members.items()):
            if not stats:
                print k
            else:
                print k + '\t' + str(v)
    else:
        with open(output, 'w') as o:
            for (k, v) in sorted(members.items()):
                if not stats:
                    o.write(k + '\n')
                else:
                    o.write(k + '\t' + str(v) + '\n')


def display_help(error=False, exception=''):
    print '''Essbase Member Extract
Usage: python exportMembers.py -f <essbase extract file>
 -f, --file     Essbase extract file
 -o, --output   Output file

Flags:
 -h             This Help
 -s, --stats    Include statistics on number of occurrences in file
'''
    if exception:
        print exception
    if error:
        sys.exit(2)
    else:
        sys.exit()

if __name__ == '__main__':
    #extractMembers(r'test-data\essbase-extract-data.txt', r'test-data\essbase-extract-data-out.txt', True)
    main(sys.argv[1:])