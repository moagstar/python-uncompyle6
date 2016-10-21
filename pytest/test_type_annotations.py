import dis
import hypothesis
from hypothesis import strategies as st


@st.composite
def type_names_and_strategies(draw):
    return draw(st.sampled_from((
        ('int', st.integers()),
        ('float', st.floats()),
        ('str', st.text()),
        #('List', st.text()),           # TODO : generics
        #('[t1, t2]', st.text()),       # TODO : type union
    )))


variable_names = st.text(st.characters(
    min_codepoint=65, max_codepoint=90), min_size=1)


@st.composite
def typed_variables(draw):
    variable_name = draw(variable_names)
    type_name, strategy = draw(type_names_and_strategies())
    with_value = draw(st.booleans())
    value = (' = ' + repr(draw(strategy))) if with_value else ''
    return '{variable_name}: {type_name}{value}'.format(**locals())


@st.composite
def untyped_variables(draw):
    variable_name = draw(variable_names)
    _, strategy = draw(type_names_and_strategies())
    value = repr(draw(strategy))
    return '{variable_name} = {value}'.format(**locals())


@st.composite
def class_methods(draw):
    # TODO
    return """\
    @classmethod
    def method(): pass
"""


@st.composite
def instance_methods(draw):
    # TODO
    return """\
    @classmethod
    def method(self): pass
"""

@st.composite
def class_definitions(draw):

    class_name = draw(variable_names)

    class_members = '\n'.join(draw(st.lists(st.one_of(
        typed_variables(), untyped_variables()), min_size=1)))

    init_args = ', '.join(draw(st.lists(st.one_of(
        typed_variables(), untyped_variables()), min_size=1)))
    init_args = (', ' + init_args) if len(init_args) else ''
    init = 'def __init__(self{init_args}): pass'.format(**locals())

    class_methods_ = '\n'.join(draw(st.lists(class_methods())))

    instance_methods_ = '\n'.join(draw(st.lists(instance_methods())))

    return """\
class {class_name}:
    {class_members}
    {init}
    {class_methods_}
    {instance_methods_}
""".format(**locals())


@hypothesis.given(typed_variables())
def test_typed_variables(expr):
    code = compile(expr, '<string>', 'single')
    dis.dis(code)


@hypothesis.given(class_definitions())
def test_class_defintions(statement):
    code = compile(statement, '<string>', 'exec')
    dis.dis(code)
    assert not statement
