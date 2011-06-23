#!/usr/bin/env python

import argparse
import sys

def parse_args():
    def positive(string):
        try:
            r = int(string)
            if r > 0:
                return r
        except ValueError:
            pass
        raise argparse.ArgumentTypeError('%s is not a positive integer' % string)

    def to_int(string):
        return int(string)

    def to_float(string):
        return float(string)

    def sort_spec(string):
        s = set(string.lower())
        if len(string) > 2 or len(string) != len(s) or \
          not s.issubset(set('rnf')) or ('n' in s and 'f' in s):
            raise argparse.ArgumentTypeError('%s is not a sort specification' % string)
        conversion = None
        if 'n' in s:
            conversion = to_int
        elif 'f' in s:
            conversion = to_float
        return (conversion, 'r' in s)

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delimiter', dest='delimiter',
                        default=' ')
    parser.add_argument('-f', '--field', dest='field', type=positive,
                        required=True)
    parser.add_argument('-v', '--value', dest='value')
    parser.add_argument('-s', '--sort', dest='sort', type=sort_spec, nargs='?', action='append')
    parser.add_argument('file', nargs='?', default=None)
    args = parser.parse_args()
    if args.value and args.sort:
        raise argparse.ArgumentTypeError('Cannot specify both -v and -s.')
    if not args.value and not args.sort:
        raise argparse.ArgumentTypeError('Must specify -v or -s.')
    if args.sort == [None]:
        args.sort = (None, False)
    else:
        args.sort = args.sort[0]
    return args

def sort(file, delimiter, field, sort):
    lines = file.readlines()
    for idx, line in enumerate(lines):
        line = line.rstrip('\n')
        cols = line.split(delimiter)
        if len(cols) <= field:
            continue;
        lines[idx] = (line, cols[field])
    for line in sorted(lines, key=(lambda r: sort[0](r[1])),
                       reverse = sort[1]):
        print line[0]

def filter(file, delimiter, field, value):
    for line in file:
        line = line.rstrip('\n')
        cols = line.split(delimiter)
        if len(cols) <= field or cols[field] != value:
            continue
        print line

if __name__ == '__main__':
    args = parse_args()
    f = open(args.file) if args.file else sys.stdin
    print args
    if args.value:
        filter(f, args.delimiter, args.field - 1, args.value)
    else:
        sort(f, args.delimiter, args.field - 1, args.sort)
    f.close()
