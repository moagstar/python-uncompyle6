import dis
import hypothesis
from hypothesis import strategies as st
# uncompyle6
from uncompyle6 import PYTHON_VERSION, deparse_code


@st.composite
def type_names_and_strategies(draw):
    # TODO : More extensive list of types
    return draw(st.sampled_from((
        ('int', st.integers()),
        ('float', st.floats()),
        ('str', st.text()),
        #('List', st.text()),           # TODO : generics
        #('[t1, t2]', st.text()),       # TODO : type union
    )))


names = st.text(st.characters(min_codepoint=65, max_codepoint=90), min_size=1)


@st.composite
def statements(draw):
    # TODO : Larger corpus (or hypothesis generated)
    return draw(st.sampled_from(
        'pass',
    ))

@st.composite
def typed_variables(draw):
    variable_name = draw(names)
    type_name, strategy = draw(type_names_and_strategies())
    with_value = draw(st.booleans())
    value = (' = ' + repr(draw(strategy))) if with_value else ''
    return '{variable_name}: {type_name}{value}'.format(**locals())


@st.composite
def untyped_variables(draw):
    variable_name = draw(names)
    _, strategy = draw(type_names_and_strategies())
    value = repr(draw(strategy))
    return '{variable_name} = {value}'.format(**locals())


@st.composite
def lists_of_variables(draw):
    variables = st.one_of(typed_variables(), untyped_variables())
    return draw(st.lists(variables, min_size=1))


@st.composite
def function_arguments(draw):
    args = ', '.join(draw(lists_of_variables()))
    return (', ' + args) if len(args) else ''


@st.composite
def function_definitions(draw, name=None, args=''):
    name = draw(names) if name is None else name
    extra_args = draw(function_arguments())
    return 'def {name}({args}{extra_args}):'.format(**locals())


@st.composite
def functions(draw, name=None, args='', indent=0):
    function_definition = draw(function_definitions(name, args))
    lists_of_statements = st.lists(statements(), min_size=1)
    function_body = '\n'.join(draw(lists_of_statements))
    body_indent = (indent + 1) * '    '
    indent *= '    '
    return """
{indent}{function_definition}
{body_indent}{function_body}
""".format(**locals())


@st.composite
def class_methods(draw, name=None, indent=0):
    function_definition = draw(functions(name, 'cls', indent))
    return """\
@classmethod
{function_definition}
""".format(**locals())


@st.composite
def instance_methods(draw, name=None, indent=0):
    function_definition = draw(functions(name, 'self', indent))
    return '{function_definition}'.format(**locals())


@st.composite
def class_definitions(draw):
    class_name = draw(names)
    class_members = '\n'.join(draw(lists_of_variables()))
    indent = 1
    init = draw(instance_methods('__init__', indent=indent))
    class_methods_ = '\n'.join(draw(st.lists(class_methods(indent=indent))))
    instance_methods_ = '\n'.join(draw(st.lists(instance_methods(indent=indent))))
    return """\
class {class_name}:
    {class_members}
    {init}
    {class_methods_}
    {instance_methods_}
""".format(**locals())


@hypothesis.given(typed_variables())
def test_typed_variables(statement):
    code = compile(statement, '<string>', 'exec')
    deparsed = deparse_code(PYTHON_VERSION, code, compile_mode='single')
    recompiled = compile(deparsed.text, '<string>', 'single')


@hypothesis.given(class_definitions())
def test_class_defintions(statement):
    code = compile(statement, '<string>', 'exec')
    deparsed = deparse_code(PYTHON_VERSION, code, compile_mode='single')
    recompiled = compile(deparsed.text, '<string>', 'single')
