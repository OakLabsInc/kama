#!/usr/bin/env python
from kama.client import connect
import IPython.terminal.embed
import sys


def main():
    kama = connect()
    return IPython.terminal.embed.embed(banner1='\n\tThis is the kama shell.\n\tType help(kama) to get started\n')


if __name__ == '__main__':
    sys.exit(main())
