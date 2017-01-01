# future
from __future__ import print_function
# test
import hypothesis
from hypothesis import strategies as st
# uncompyle / xdis
from validate import run_test


@st.composite
def ranges(draw, min_value, max_value):
    return range(draw(st.integers(min_value, max_value)))


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
    r = draw(ranges(min_arg_count, max_arg_count))
    args = ['arg' + str(x) for x in r]

    r = draw(ranges(min_named_arg_count, max_named_arg_count))
    named_args = ['name' + str(x) + '=value' + str(x) for x in r]

    def maybe_value(maybe_boolean, value):
        if maybe_boolean is None:
            maybe_boolean = draw(st.booleans())
        return [value] if maybe_boolean else []

    return name + '(' + ','.join(
        args +
        maybe_value(has_star_arg, '*args') +
        named_args +
        maybe_value(has_double_star_arg, '**kwargs')
    ) + ')'


def simple_function_calls(**kwargs):
    """
    Simple function calls strategy which can be used to isolate
    certain types of function calls.

    The default parameters passed to function_calls is to have
    all features turned off, which will result in a function call
    like this::

        func()

    Features can be turned on using kwargs, for example::

        simple_function_calls(max_arg_count=8)

    Will produce function calls with up to 8 positional arguments,
    for example::

        func(arg1, arg2)

    :param kwargs: Customize the default function_calls parameters,
                   see function_calls for the available parameters.

    :return: Hypothesis strategy for generating function calls.
    """
    return function_calls(
        **dict(
            dict(
                has_star_arg=False,
                max_arg_count=0,
                max_named_arg_count=0,
                has_double_star_arg=False
            ),
            **kwargs
        )
    )


@hypothesis.given(simple_function_calls(max_arg_count=8))
def test_function_calls_only_positional(function_call):
    run_test(function_call)


@hypothesis.given(simple_function_calls(max_named_arg_count=8))
@hypothesis.example('func(name0=value0, name1=value1)')
def test_function_calls_only_named(function_call):
    run_test(function_call)


@hypothesis.given(simple_function_calls(has_star_arg=True))
def test_function_calls_only_star(function_call):
    run_test(function_call)


@hypothesis.given(simple_function_calls(has_double_star_arg=True))
def test_function_calls_only_double_star(function_call):
    run_test(function_call)


@hypothesis.given(function_calls())
def test_function_calls(function_call):
    run_test(function_call)
