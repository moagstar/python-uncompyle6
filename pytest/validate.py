# future
from __future__ import print_function
# std
import dis
import difflib
import subprocess
# compatability
import six
# 3rd party
import astdump
# uncompyle6 / xdis
from uncompyle6 import PYTHON_VERSION, deparse_code


def _dis_to_text(co):
    return dis.Bytecode(co).dis()


def html_diff(original, uncompyled):
    """
    Display a pretty html line difference between the original and
    uncompyled code and bytecode.

    :param original: Text describing the original code object.
    :param uncompyled: Text describing the uncompyled code object.
    """
    original_lines = original.split('\n')
    uncompyled_lines = uncompyled.split('\n')
    args = original_lines, uncompyled_lines, 'original', 'uncompyled'
    diff = difflib.HtmlDiff().make_file(*args)
    with open('diff.html', 'w') as f:
        # TODO : Better way of removing legend
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(diff, "lxml")
        soup.select_one('table[summary="Legends"]').extract()
        f.write(str(soup))
        # TODO : tempfile, maybe use stdin?
        print()
        # TODO : EAFP for elinks not installed
        print(subprocess.check_output([
            'elinks',
            '-dump',
            '-no-references',
            '-dump-color-mode',
            '1',
            'diff.html',
        ]).decode('utf-8'))


def are_instructions_equal(i1, i2):
    """
    Determine if two instructions are approximately equal,
    ignoring certain fields which we allow to differ, namely:

    * code objects are ignore (should probaby be checked) due to address
    * line numbers

    :param i1: left instruction to compare
    :param i2: right instruction to compare

    :return: True if the two instructions are approximately equal, otherwise False.
    """
    result = (1==1
        and i1.opname == i2.opname
        and i1.opcode == i2.opcode
        and i1.arg == i2.arg
        # ignore differences due to code objects
        # TODO : Better way of ignoring address
        and (i1.argval == i2.argval or '<code object' in str(i1.argval))
        # TODO : Should probably recurse to check code objects
        and (i1.argrepr == i2.argrepr or '<code object' in i1.argrepr)
        and i1.offset == i2.offset
        # ignore differences in line numbers
        #and i1.starts_line
        and i1.is_jump_target == i2.is_jump_target
    )
    return result


def code_objects_equal(co1, co2):
    """
    Determine if two code objects are approximately equal,
    see are_instructions_equal for more information.

    :param i1: left code object to compare
    :param i2: right code object to compare

    :return: True if the two code objects are approximately equal, otherwise False.
    """
    # TODO : Use xdis for python2 compatability
    instructions1 = dis.Bytecode(co1)
    instructions2 = dis.Bytecode(co2)
    for opcode1, opcode2 in zip(instructions1, instructions2):
        if not are_instructions_equal(opcode1, opcode2):
            return False
    return True


def run_test(text, mode='exec'):
    """
    Validate decompilation of the given source code.

    :param text: Source to validate decompilation of.
    """
    original_code = compile(text, '<string>', mode)
    original_dis = _dis_to_text(original_code)
    original_text = text
    original_ast = astdump.indented(original_text, False)

    deparsed = deparse_code(PYTHON_VERSION, original_code,
                            compile_mode=mode, out=six.StringIO())
    uncompyled_text = deparsed.text
    uncompyled_code = compile(uncompyled_text, '<string>', 'exec')

    if not code_objects_equal(uncompyled_code, original_code):

        uncompyled_dis = _dis_to_text(uncompyled_text)
        uncompyled_ast = astdump.indented(uncompyled_text, False)

        def output(text, ast, dis):
            width = 60
            return '\n\n'.join([
                ' SOURCE CODE '.center(width, '#'),
                text.strip(),
                ' ABSTRACT SYNTAX TREE '.center(width, '#'),
                ast,
                ' BYTECODE '.center(width, '#'),
                dis
            ])

        original = output(original_text, original_ast, original_dis)
        uncompyled = output(uncompyled_text, uncompyled_ast, uncompyled_dis)
        html_diff(original, uncompyled)

        assert False
