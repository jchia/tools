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

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delimiter', dest='delimiter',
                        default=' ')
    parser.add_argument('-f', '--field', dest='field', type=positive,
                        required=True)
    parser.add_argument('-v', '--value', dest='value', required=True)
    parser.add_argument('file', nargs='?', default=None)
    args = parser.parse_args()
    return args

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
    filter(f, args.delimiter, args.field - 1, args.value)
    f.close()
