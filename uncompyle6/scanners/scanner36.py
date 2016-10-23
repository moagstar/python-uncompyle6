#  Copyright (c) 2016 by Rocky Bernstein
"""
Python 3.5 bytecode scanner/deparser

This sets up opcodes Python's 3.5 and calls a generalized
scanner routine for Python 3.
"""

from __future__ import print_function

import sys

from uncompyle6.scanners.scanner3 import Scanner3

# bytecode verification, verify(), uses JUMP_OPs from here
from xdis.opcodes import opcode_36 as opc
JUMP_OPs = map(lambda op: opc.opname[op], opc.hasjrel + opc.hasjabs)


class Scanner36(Scanner3):

    def __init__(self, show_asm=None):
        Scanner3.__init__(self, 3.6, show_asm)

    def ingest(self, co, classname=None, code_objects=None, show_asm=None):
        """
        Ignore SETUP_ANNOTATIONS which has no useful meaning for decompilation.
        """
        code_objects = {} if code_objects is None else code_objects
        tokens, customize = Scanner3.ingest(self, co, classname, code_objects, show_asm)
        tokens = [t for t in tokens if t.type != 'SETUP_ANNOTATIONS']
        return tokens, customize


if __name__ == "__main__":
    from uncompyle6 import PYTHON_VERSION
    if PYTHON_VERSION == 3.6:
        import inspect
        co = inspect.currentframe().f_code
        tokens, customize = Scanner36().ingest(co)
        for t in tokens:
            print(t.format())
        pass
    else:
        print("Need to be Python 3.6 to demo; I am %s." %
              PYTHON_VERSION)
