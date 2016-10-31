# std
import dis
# 3rd party
import hypothesis
from hypothesis import strategies as st
# uncompyle6
from uncompyle6 import PYTHON_VERSION, deparse_code


@st.composite
def function_calls(draw, name='func', min_arg_count=0, max_arg_count=8, has_star_arg=None,
                   min_named_arg_count=0, max_named_arg_count=8, has_double_star_arg=None):
    """
    Generate a function call.

    :param draw: Let hypothesis draw from other strategies.
    :param name: The name of the function being called.
    :param min_arg_count: The minimum number of positional arguments to generate.
    :param max_arg_count: The maximum number of positional arguments to generate.
    :param has_star_arg: True to generate with *arg, False for no *arg or None to draw
                         a boolean to determine if *arg is generated.
    :param min_named_arg_count: The minimum number of named arguments to generate.
    :param max_named_arg_count: The minimum number of named arguments to generate.
    :param has_double_star_arg: True to generate with **kwarg, False for no *kwarg or None
                                to draw a boolean to determine if **kwarg is generated.

    :return: String with the code for the generated function call.
    """
    arg_count = draw(st.integers(min_value=min_arg_count, max_value=max_arg_count))
    args = ['arg' + str(x) for x in range(arg_count)]

    if has_star_arg is None:
        has_star_arg = draw(st.booleans())
    star_arg = ['*args'] if has_star_arg else []

    named_arg_count = draw(st.integers(min_value=min_named_arg_count, max_value=max_named_arg_count))
    named_args = ['name' + str(x) + '=value' + str(x) for x in range(named_arg_count)]

    if has_double_star_arg is None:
        has_double_star_arg = draw(st.booleans())
    double_star_arg = ['**kwargs'] if has_double_star_arg else []

    all_args = ','.join(args + star_arg + named_args + double_star_arg)

    return name + '(' + all_args + ')'


def run_test(text):

    expr = text + '\n'
    code = compile(expr, '<string>', 'single')

    try:
        deparsed = deparse_code(PYTHON_VERSION, code, compile_mode='single')
    except:
        dis.dis(expr)
        raise

    recompiled = compile(deparsed.text, '<string>', 'single')
    if recompiled != code:
        assert 'dis(' + deparsed.text.strip('\n') + ')' == 'dis(' + expr.strip('\n') + ')'


@hypothesis.given(function_calls())
def test_function_calls(function_call):
    run_test(function_call)