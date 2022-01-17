# -*- coding: utf-8 -*-

import ply.lex as lex
import ply.yacc as yacc
import numpy as np
import sys
from time import sleep
import traceback
import networkx as nx
from graphcore.reporter import GraphCoreReporter
from graphcore.terms import Variable, Function, BuiltinFunction, Constant, IfStatement, WhileStatement, ForStatement, \
                             ForallEquation, ExistsEquation, GraphObject, NodesObject, EdgesObject, AssignmentStatement, \
                             PrintFunction
from networkml.network import NetworkInstance, NetworkClassInstance, NetworkMethod, NetworkCallable
from networkml.interpreter import NetworkInterpreter
from networkml.lexer import NetworkParser
from networkml.specnetwork import SpecValidator
from networkml.error import NetworkScriptInterruptionException
from PyQt5.QtCore import QObject


# Global data FIXME
_global_data = {}
error_info = []


def default_handler():  # -> GraphCoreContextHandler:
    global _global_data
    return _global_data['handler']


def default_reporter():  # -> GraphCoreReporter:
    global _global_data
    return _global_data['reporter']


def default_printer():
    global _global_data
    return _global_data['print']


def _print(s):
    if default_reporter() is None:
        print(s)
    else:
        default_reporter().report(s)


# Word analysis
tokens = (
    #'ATTRIBUTE',
    'ASSIGNMENT',
    'FOR',
    'WHILE',
    'FORALL',
    'EXISTS',
    # 'BREAK',
    'CARD',
    'CONJ',
    'DISJ',
    'MEMBEROF',
    'IMPLICATOR',
    'QUOTE',
    'DOUBLEQUOTE',
    'LPAR',
    'RPAR',
    'CLPAR',
    'CRPAR',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'PERIOD',
    'VARIABLE',
    'EQUALITY',
    'INEQUALITY',
    'LESSTHAN',
    'LESSOREQUAL',
    'NUMBER',
    'STRING',
    'BOOLSYMBOL',
    'NEGATOR',
    'SEMICOLON',
    'COMMENT',
    'GRAPH',
    'NODES',
    'EDGES',
    'ADD',
    'MULTIPLY',
    'MINUS',
    'DIVIDE',
    'MOD',
    'NUMBERINDEX',
    'ATTRIBUTEINDEX',
    'IF',
)

def t_ADD(t):
    r"\+"
    opr = lambda x, y: x + y
    t.value = Function(default_handler(), "+", operator=opr, reporter=default_reporter())
    return t
def t_MULTIPLY(t):
    r"\*"
    opr = lambda x, y: x * y
    t.value = Function(default_handler(), "*", operator=opr, reporter=default_reporter())
    return t
def t_MINUS(t):
    r"-"
    opr = lambda x, y: x - y
    t.value = Function(default_handler(), "-", operator=opr, reporter=default_reporter())
    return t
def t_DIVIDE(t):
    r"/"
    opr = lambda x, y: x / y
    t.value = Function(default_handler(), "/", operator=opr, reporter=default_reporter())
    return t
def t_MOD(t):
    r"%"
    opr = lambda x, y: x % y
    t.value = Function(default_handler(), "%", operator=opr, reporter=default_reporter())
    return t
def t_IF(t):
    r"if"
    t.value = IfStatement(default_handler())
    return t
def t_NUMBERINDEX(t):
    r"\[[0-9]+\]"
    t.value = t.value[1:len(t.value)-1]
    index = int(t.value)
    opr = lambda x: x[index]
    def assigner(x, y):
        if not isinstance(x, Variable):
            x[index] = y
        else:
            if x.reference() is None:
                z = x.reference()
            else:
                z = x
            z[index] = y
    t.value = Function(default_handler(), "index", operator=opr, assigner=assigner, arity=1, reporter=default_reporter())
    return t
def t_ATTRIBUTEINDEX(t):
    r"\[\'[a-zA-Z][a-zA-Z_\-]*\'\]"
    t.value = t.value[2:len(t.value)-2]
    index = t.value
    opr = lambda x: x[index]
    def assigner(x, y):
        if not isinstance(x, Variable):
            x[index] = y
        else:
            if x.reference() is None:
                z = x.reference()
            else:
                z = x
            z[index] = y
    t.value = Function(default_handler(), "index", operator=opr, assigner=assigner, arity=1, reporter=default_reporter())
    return t
def t_STRING(t):
    # r"\"[\w\W\s\S]*\""
    r"\"[a-zA-Z0-9_=/~!#$%&{}\-\[\]\(\)\.\*]*\""
    # r"\"((\\[\\\'\"])|(^[\\\'\"]))*\""
    # _print("STRING:[{}]".format(t.value))
    t.value = t.value[1:len(t.value)-1]
    # t.value = t.value.replace(r"\\\\", r"\\")
    # t.value = t.value.replace(r"\\\'", r"\'")
    # t.value = t.value.replace(r'\\\"', r'\"')
    t.value = Constant(default_handler(), t.value)
    return t
def t_ATTRIBUTE(t):
    r"\'[a-zA-Z][a-zA-Z_\-]*\'"
    # _print("ATTRIBUTE:[{}]".format(t.value))
    t.value = t.value
    return t
def t_ASSIGNMENT(t):
    r":="
    # _print("ASSIGNMENT:[{}]".format(t.value))
    t.value = AssignmentStatement(default_handler(), reporter=default_reporter())
    return t
def t_FOR(t):
    r"for"
    t.value = ForStatement(default_handler(), reporter=default_reporter())
    return t
def t_WHILE(t):
    r"while"
    t.value = WhileStatement(default_handler(), reporter=default_reporter())
    return t
def t_BREAK(t):
    r"\\break"
    t.value = t.value
    return t
def t_FORALL(t):
    r"forall"
    t.value = ForallEquation(default_handler(), reporter=default_reporter())
    return t
def t_EXISTS(t):
    r"exists"
    t.value = ExistsEquation(default_handler(), reporter=default_reporter())
    return t
def t_CARD(t):
    r"card"
    opr = lambda x: len(x)
    t.value = Function(default_handler(), t.value, operator=opr, arity=1, reporter=default_reporter())
    return t
def t_CONJ(t):
    r"and"
    opr = lambda x, y: x and y
    t.value = Function(default_handler(), t.value, operator=opr, arity=2, reporter=default_reporter())
    return t
def t_DISJ(t):
    r"or"
    opr = lambda x, y: x or y
    t.value = Function(default_handler(), t.value, operator=opr, arity=2, reporter=default_reporter())
    return t
def t_MEMBEROF(t):
    r"in"
    opr = lambda x, y: x in y
    t.value = Function(default_handler(), t.value, operator=opr, arity=2, reporter=default_reporter())
    return t
def t_EQUALITY(t):
    r"=="
    opr = lambda x, y: x == y
    t.value = Function(default_handler(), t.value, operator=opr, arity=2, reporter=default_reporter())
    return t
def t_INEQUALITY(t):
    r"!="
    opr = lambda x, y: x != y
    t.value = Function(default_handler(), t.value, operator=opr, arity=2, reporter=default_reporter())
    return t
def t_LESSTHAN(t):
    r"<"
    opr = lambda x, y: x < y
    t.value = Function(default_handler(), t.value, operator=opr, arity=2, reporter=default_reporter())
    return t
def t_LESSOREQUAL(t):
    r"<="
    opr = lambda x, y: x <= y
    t.value = Function(default_handler(), t.value, operator=opr, arity=2, reporter=default_reporter())
    return t
def t_IMPLICATOR(t):
    r"=>"
    opr = lambda x, y: not x or y
    t.value = Function(default_handler(), t.value, operator=opr, arity=2, reporter=default_reporter())
    return t
def t_QUOTE(t):
    r"'"
    t.value = t.value
    return t
def t_DOUBLEQUOTE(t):
    r"\""
    t.value = t.value
    return t
def t_NUMBER(t):
    r"[1-9][0-9]*\.[0-9]+|0\.[0-9]+|[0-9]+"
    # _print("NUMBER:[{}]".format(t.value))
    if r"." in t.value:
        t.value = Constant(default_handler(), float(t.value))
    else:
        t.value = Constant(default_handler(), int(t.value))
    return t
def t_BOOLSYMBOL(t):
    r"true|false|True|False"
    if t.value in ("true", "True"):
        t.value = Constant(default_handler(), True)
    else:
        t.value = Constant(default_handler(), False)
    return t
def t_LPAR(t):
    r"\("
    # _print("LPAR:{}".format(t.value))
    return t
def t_RPAR(t):
    r"\)"
    # _print("RPAR:{}".format(t.value))
    return t
t_CLPAR = r"\["
t_CRPAR = r"\]"
t_LBRACKET = r"{"
t_RBRACKET = r"}"
t_COMMA = r","
t_PERIOD = r"."
def t_TYPEINT(t):
    r"int"
    t.value = int
    return t
def t_TYPEFLOAT(t):
    r"float"
    t.value = float
    return t
def t_TYPESTR(t):
    r"str"
    t.value = str
    return t
def t_TYPELIST(t):
    r"list"
    t.value = list
    return t
def t_TYPEBOOL(t):
    r"bool"
    t.value = bool
    return t
def t_SEMICOLON(t):
    r";"
    # _print("SEMICORON: {}".format(t.value))
    t.value = r";"
    return t
def t_VARIABLE(t):
    r"[a-zA-Z]+[a-zA-Z_0-9]*"
    # _print("VARIABLE:[{}]".format(t.value))
    _handler = default_handler()
    if t.value == "print":
        t.value = default_printer()
    elif _handler.context.has_function(t.value):
        f = _handler.context.function(t.value)
        arity = _handler.context.arity(t.value)
        t.value = BuiltinFunction(default_handler(), t.value, function=f, arity=arity, reporter=default_reporter())
    elif _handler.context.has_variable(t.value):
        v = _handler.context.variable(t.value)
        t.value = Variable(default_handler(), t.value, reference=v, reporter=default_reporter())
    else:
        t.value = Variable(default_handler(), t.value, reporter=default_reporter())
    return t
def t_NEGATOR(t):
    r"\\neg"
    opr = lambda x: not x
    t.value = Function(default_handler(), t.value, operator=opr, arity=1, reporter=default_reporter())
    return t
def t_GRAPH(t):
    r"\\Graph"
    t.value = GraphObject(default_handler(), reporter=default_reporter())
    return t
def t_NODES(t):
    r"\\Nodes"
    t.value = NodesObject(default_handler(), reporter=default_reporter())
    return t
def t_EDGES(t):
    r"\\Edges"
    t.value = EdgesObject(default_handler(), reporter=default_reporter())
    return t
t_ignore_COMMENT = r"/\*\[\s\S]*\*/|//.*"
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    # _print("Illegal character {}".format(t.value[0]))
    t.lexer.skip(1)


# Lexer
lexer = lex.lex()
# lex.lex()


# GraphCoreTerm class
def parse_term(term):
    return


# Syntax analysis

# general term
def p_terms(p):
    """
    terms :
    terms : execution_steps
    """
    if len(p) == 1:
        p[0] = []
    elif len(p) == 2:
        p[0] = p[1]


def p_execution_steps(p):
    # """
    # execution_steps : single_execution
    #                 | execution_steps single_execution
    #                 | IF boolean_expression single_execution
    #                 | IF boolean_expression LBRACKET execution_steps RBRACKET
    #                 | FOR variable MEMBEROF collection single_execution
    #                 | FOR variable MEMBEROF collection LBRACKET execution_steps RBRACKET
    #                 | WHILE boolean_expression single_execution
    #                 | WHILE boolean_expression LBRACKET execution_steps RBRACKET
    # """
    """
    execution_steps : single_execution
                    | LBRACKET execution_steps RBRACKET
                    | execution_steps single_execution
                    | execution_steps execution_steps
                    | IF boolean_expression LBRACKET execution_steps RBRACKET
                    | FOR variable MEMBEROF collection LBRACKET execution_steps RBRACKET
                    | WHILE boolean_expression LBRACKET execution_steps RBRACKET
    """
    if len(p) == 2:  # single_execution
        p[0] = [p[1]]
    elif len(p) == 3:
        if type(p[2]) == list:
            # execution_steps execusion_steps
            p[0] = p[1]
            p[0].extend(p[2])
        else:
            # execution_steps single_execution
            p[0] = p[1]
            p[0].append(p[2])
    elif len(p) == 4:
        p[0] = p[2]
    # elif len(p) == 4:  # WHILE boolean_expression single_execution
    #                    # IF boolean_expression single_execution
    #     p[0] = p[1]
    #     p[0].set_condition(p[2])
    #     p[0].set_execution([p[3]])
    #     p[0] = [p[0]]
    #     pass
                       # FOR variable MEMBEROF collection single_execution
    elif len(p) == 6:  # WHILE boolean_expression LBRACKET execution_steps RBRACKET
                       # IF boolean_expression LBRACKET execution_steps RBRACKET
        if type(p[1]) is ForStatement:
            p[0] = p[1]
            p[0].variable = p[2]
            p[0].collection = p[4]
            p[0].execution = [p[5]]
            p[0] = [p[0]]
        elif type(p[1]) in (IfStatement, WhileStatement):
            p[0] = p[1]
            p[0].condition = p[2]
            p[0].execution = p[4]
            p[0] = [p[0]]
        pass
    elif len(p) == 8:  # FOR variable MEMBEROF collection LBRACKET executon_steps RBRACKET
        p[0] = p[1]
        p[0].variable = p[2]
        p[0].collection = p[4]
        p[0].execution = p[6]
        p[0] = [p[0]]
        pass


def p_single_execution(p):
    """
    single_execution : variable ASSIGNMENT expression SEMICOLON
                     | variable ATTRIBUTEINDEX ASSIGNMENT expression SEMICOLON
                     | function_call SEMICOLON
    """
    if len(p) == 3:  # function_call SEMICOLON
        p[0] = p[1]
    elif len(p) == 5:  # variable ASSIGNMENT expression SEMICOLON
        p[0] = p[2]
        p[0].variable = p[1]
        p[0].value = p[3]
    elif len(p) == 6:  # variable ATTRIBUTEINDEX ASSIGNMENT expression SEMICOLON
        p[0] = p[3]
        p[0].variable = p[1]
        p[0].assigner = p[2].assigner
        p[0].value = p[4]


def p_expression(p):
    """
    expression : constant
               | attribute
               | variable
               | function_call
               | binary_computation
               | LPAR expression RPAR
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = p[2]


def p_binary_computation(p):
    """
    binary_computation : binary_operand binary_operator binary_operand
    """
    p[0] = p[2]
    p[0].args = [p[1], p[3]]


def p_binary_operator(p):
    """
    binary_operator : ADD
                    | MULTIPLY
                    | MINUS
                    | DIVIDE
                    | MOD
    """
    p[0] = p[1]


def p_binary_operand(p):
    """
    binary_operand : constant
                   | variable
                   | attribute
                   | LPAR binary_operand RPAR
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 4:
        p[0] = p[2]


def p_function_call(p):
    """
    function_call : variable LPAR RPAR
                  | variable LPAR args RPAR
    """
    if len(p) == 4:
        p[0] = p[1]
        p[0].args = []
    elif len(p) == 5:
        p[0] = p[1]
        p[0].args = p[3]


# def p_function(p):
#     """
#     function : variable
#     """
#     p[0] = p[1]


def p_args(p):
    """
    args : arg
         | args COMMA arg
    """
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = p[1]
        p[0].append(p[3])


def p_arg(p):
    """
    arg : constant
        | attribute
        | variable
        | boolean_expression
    """
    p[0] = p[1]


def p_constant(p):
    """
    constant : BOOLSYMBOL
             | NUMBER
             | STRING
    """
    p[0] = p[1]


def p_boolean_expression(p):
    """
    boolean_expression : BOOLSYMBOL
                       | NEGATOR boolean_expression
                       | LPAR boolean_expression RPAR
                       | boolean_expression CONJ boolean_expression
                       | boolean_expression DISJ boolean_expression
                       | boolean_expression EQUALITY boolean_expression
                       | boolean_expression INEQUALITY boolean_expression
                       | boolean_expression IMPLICATOR boolean_expression
                       | variable EQUALITY NUMBER
                       | variable INEQUALITY NUMBER
                       | variable LESSTHAN NUMBER
                       | variable LESSOREQUAL NUMBER
                       | variable EQUALITY variable
                       | variable INEQUALITY variable
                       | variable LESSTHAN variable
                       | variable LESSOREQUAL variable
                       | NUMBER EQUALITY variable
                       | NUMBER INEQUALITY variable
                       | NUMBER LESSTHAN variable
                       | NUMBER LESSOREQUAL variable
                       | variable EQUALITY attribute
                       | variable INEQUALITY attribute
                       | variable LESSTHAN attribute
                       | variable LESSOREQUAL attribute
                       | attribute EQUALITY variable
                       | attribute INEQUALITY variable
                       | attribute LESSTHAN variable
                       | attribute LESSOREQUAL variable
                       | STRING EQUALITY STRING
                       | STRING INEQUALITY STRING
                       | NUMBER EQUALITY NUMBER
                       | NUMBER INEQUALITY NUMBER
                       | NUMBER LESSTHAN NUMBER
                       | NUMBER LESSOREQUAL NUMBER
                       | attribute EQUALITY STRING
                       | attribute INEQUALITY STRING
                       | attribute EQUALITY NUMBER
                       | attribute INEQUALITY NUMBER
                       | attribute LESSTHAN NUMBER
                       | attribute LESSOREQUAL NUMBER
                       | STRING EQUALITY attribute
                       | STRING INEQUALITY attribute
                       | NUMBER EQUALITY attribute
                       | NUMBER INEQUALITY attribute
                       | NUMBER LESSTHAN attribute
                       | NUMBER LESSOREQUAL attribute
                       | attribute EQUALITY attribute
                       | attribute INEQUALITY attribute
                       | attribute LESSTHAN attribute
                       | attribute LESSOREQUAL attribute
                       | FORALL variable MEMBEROF nodes_or_edges boolean_expression
                       | EXISTS variable MEMBEROF nodes_or_edges boolean_expression
    """
    if len(p) == 2:  # BOOLSYMBOL
        p[0] = p[1]
    elif len(p) == 3:  # NEGATOR boolean_expression
        p[0] = p[1]
        p[0].args = [p[2]]
    elif len(p) == 4:
        if type(p[1]) == str:  # LPAR boolean_expression RPAR
            p[0] = p[2]
        else:  # left-operand comparator right-operand
            p[0] = p[2]
            p[0].args = [p[1], p[3]]
    elif len(p) == 6:  # forall | exists variable MEMBEROF nodes_or_edges boolean_expression
        p[0] = p[1]
        p[0].variable_name = p[2]
        p[0].collection = p[4]
        p[0].equation = p[5]


def p_comparable(p):
    """
    comparable : variable
               | attribute
               | constant
    """
    p[0] = p[1]


def p_attribute(p):
    """
    attribute : variable ATTRIBUTEINDEX
    """
    p[0] = p[2]
    p[0].args = [p[1]]


def p_variable(p):
    """
    variable : VARIABLE
    """
    p[0] = p[1]


def p_nodes_or_edges(p):
    """
    nodes_or_edges : NODES
                   | EDGES
    """
    p[0] = p[1]


def p_collection(p):
    """
    collection : variable
               | GRAPH
               | NODES
               | EDGES
    """
    p[0] = p[1]


# if error occurred
def p_error(p):
    # _print('Syntax error: %d: %d: %r' % (p.lineno, p.lexpos, p.value))
    error_info.append('Syntax error: %d: %d: %r' % (p.lineno, p.lexpos, p.value))


# parse GraphCore constraint language
# def graphcore_parse_script(handler: GraphCoreContextHandler, text, reporter=None):
def graphcore_parse_script(handler, text, reporter):
    global _global_data
    global error_info
    error_info = []
    _global_data['context'] = handler.context
    _global_data['handler'] = handler
    _global_data['reporter'] = reporter
    _global_data['print'] = PrintFunction(handler, reporter=reporter)
    parser = yacc.yacc()
    result = parser.parse(text, lexer=lexer)
    return result, error_info


class GraphCoreScript(QObject):
    def __init__(self, handler, reporter: GraphCoreReporter):
        super().__init__()
        from graphcore.shell import GraphCoreThreadSignal
        from graphcore.script_worker import get_script_worker
        self._handler = handler
        self._reporter = reporter
        from networkml.network import NetworkClass, NetworkInstance
        meta = NetworkClass(None, "GCScriptClass")
        clazz_sig = "{}[{}]".format("GCScriptClass", 1)
        embedded = ()
        args = ()
        meta.set_running(True)
        clazz = meta(meta, (clazz_sig, embedded, args))
        meta.set_running(False)
        sig = "{}.{}".format(clazz.signature, clazz.next_instance_id)
        initializer_args = ()
        clazz.set_running(True)
        self._toplevel: NetworkInstance = clazz(clazz, (sig, (), initializer_args))
        clazz.set_running(False)
        self._toplevel.set_stack_enable(True)
        # validator/evaluator
        validator = SpecValidator(owner=self._toplevel)
        self._toplevel.set_validator(validator)
        # parse
        self._parser = NetworkParser(self._toplevel)
        #
        self._interpreter = NetworkInterpreter(self._toplevel)
        self._toplevel.declare_method(self._interpreter, globally=True)

        # methods
        self.install_builtin_methods()

    @property
    def toplevel(self) -> NetworkInstance:
        return self._toplevel

    @property
    def handler(self):
        return self._handler

    @handler.setter
    def handler(self, handler):
        self._handler = handler

    @property
    def reporter(self) -> GraphCoreReporter:
        return self._reporter

    @reporter.setter
    def reporter(self, reporter: GraphCoreReporter):
        self._reporter = reporter

    def execute_script(self, script: str) -> bool:
        try:
            # parse
            parser = self._parser
            self._toplevel.set_running(True)
            ret = parser.parse_script(script)
            for r in ret:
                if isinstance(r, NetworkClassInstance):
                    self._toplevel.declare_class(r, globally=True)
                    self.reporter.report('class {} declared.'.format(r))
                elif isinstance(r, NetworkMethod):
                    self._toplevel.declare_method(r, globally=True)
                    self.reporter.report('method {} declared.'.format(r.signature))
                elif isinstance(r, NetworkCallable):
                    # rtn = r(toplevel)
                    # self.reporter.report(str(rtn))
                    r(self._toplevel)
                else:
                    pass
            self._toplevel.set_running(False)
        except NetworkScriptInterruptionException as ex:
            self._toplevel.set_running(False)
        except Exception as ex:
            self.reporter.report(traceback.format_exc())
            self._toplevel.set_running(False)

    def cancel_script(self):
        self._toplevel.set_running(False)

    def run_user_scripts(self, *args):
        scripts = self.handler.context.graph['scripts']
        for sid in args:
            sid = str(sid)
            if sid not in scripts.keys():
                continue
            enabled = scripts[sid]['enabled']
            if enabled:
                script = scripts[sid]['script']
                interpret = self.toplevel.get_method(self.toplevel, "interpret")
                interpret(self.toplevel, (script, "--safe=False"))

    def run_system_scripts(self, *args):
        scripts = self.main_window.settings.setting('system-scripts')
        for sid in args:
            sid = str(sid)
            if sid not in scripts.keys():
                continue
            enabled = scripts[sid]['enabled']
            if enabled:
                script = scripts[sid]['script']
                interpret = self.toplevel.get_method(self.toplevel, "interpret")
                interpret(self.toplevel, (script, "--safe=False"))

    def read(self, filename):
        with open(filename, "r") as f:
            return f.read()

    def write(self, filename, text):
        with open(filename, "w") as f:
            f.write(text)

    def install_builtin_methods(self):
        from networkml.network import ExtensibleWrappedAccessor
        # system
        m = ExtensibleWrappedAccessor(self._toplevel, "sleep", None,
                                      lambda ao, c, eo, ca, ea: sleep(ca[0]), globally=True)
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "print", self.toplevel,
                                      lambda ao, c, eo, ca, ea: eo.print(" ".join([str(_) for _ in ca])),
                                      globally=True)
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "append", None,
                                      lambda ao, c, eo, ca, ea: ca[0].append(ca[1]),
                                      globally=True)
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "len", None,
                                      lambda ao, c, eo, ca, ea: len(ca[0]),
                                      globally=True)
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "keys", None,
                                      lambda ao, c, eo, ca, ea: ca[0].keys())
        self._toplevel.declare_method(m, globally=True)
        # graphcore
        m = ExtensibleWrappedAccessor(self._toplevel, "nodes", None,
                                      lambda ao, c, eo, ca, ea: [_ for _ in self.handler.context.G.nodes],
                                      globally=True)
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "new_node", None,
                                      lambda ao,c,eo,ca,ea: self.handler.new_node())
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "remove_node", None,
                                      lambda ao,c,eo,ca,ea: self.handler.remove_node(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "node_attr_keys", None,
                                      lambda ao, c, eo, ca, ea: [_ for _ in self.handler.context.G.nodes[ca[0]].keys()],
                                      globally=True)
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "get_node_value", None,
                                      lambda ao, c, eo, ca, ea: self.handler.node_attr(ca[0], ca[1]),
                                      globally=True)
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "set_node_value", None,
                                      lambda ao, c, eo, ca, ea: self.handler.change_node_attr(ca[0], *ca[1:]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "edges", None,
                                      lambda ao, c, eo, ca, ea: [_ for _ in self.handler.context.G.edges],
                                      globally=True)
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "add_edge", None,
                                      lambda ao,c,eo,ca,ea: self.handler.add_edge(ca[0], ca[1]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "remove_edge", None,
                                      lambda ao,c,eo,ca,ea: self.handler.remove_edge(a[0], a[1]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "edge_attr_keys", None,
                                      lambda ao, c, eo, ca, ea: [_ for _ in
                                                                 self.handler.context.G.edges[ca[0], ca[1]].keys()],
                                      globally=True)
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "get_edge_value", None,
                                      lambda ao, c, eo, ca, ea: self.handler.edge_attr(ca[0], ca[1], ca[2]),
                                      globally=True)
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "set_edge_value", None,
                                      lambda ao, c, eo, ca, ea: self.handler.change_edge_attr(ca[0], ca[1], *ca[2:]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "run_user_script", None,
                                      lambda ao, c, eo, ca, ea: self.handler.run_user_script(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "run_system_script", None,
                                      lambda ao, c, eo, ca, ea: self.handler.run_system_script(ca[0]))
        self._toplevel.declare_method(m, globally=True)

        # networkx
        successors = ExtensibleWrappedAccessor(self._toplevel, "successors", None,
                                               lambda ao, c, eo, ca, ea: [_ for _ in
                                                                          self.handler.context.G.successors(ca[0])],
                                               globally=True)
        self._toplevel.declare_method(successors, globally=True)
        predecessors = ExtensibleWrappedAccessor(self._toplevel, "predecessors", None,
                                                 lambda ao, c, eo, ca, ea: [_ for _ in
                                                                            self.handler.context.G.predecessors(ca[0])],
                                                 globally=True)
        self._toplevel.declare_method(predecessors, globally=True)

        # numpy
        m = ExtensibleWrappedAccessor(self._toplevel, "sin", None,
                                      lambda ao, c, eo, ca, ea: np.sin(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "cos", None,
                                      lambda ao, c, eo, ca, ea: np.cos(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "tan", None,
                                      lambda ao, c, eo, ca, ea: np.tan(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "acos", None,
                                      lambda ao, c, eo, ca, ea: np.arccos(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "asin", None,
                                      lambda ao, c, eo, ca, ea: np.arcsin(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "exp", None,
                                      lambda ao, c, eo, ca, ea: np.exp(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "sqrt", None,
                                      lambda ao, c, eo, ca, ea: np.sqrt(ca[0]))
        self._toplevel.declare_method(m)
        m = ExtensibleWrappedAccessor(self._toplevel, "log", None,
                                      lambda ao, c, eo, ca, ea: np.log(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "log2", None,
                                      lambda ao, c, eo, ca, ea: np.log2(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "log10", None,
                                      lambda ao, c, eo, ca, ea: np.log10(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "uniform", None,
                                      lambda ao, c, eo, ca, ea: np.random.uniform(ca[0], ca[1]))
        self._toplevel.declare_method(m, globally=True)
        # custom
        m = ExtensibleWrappedAccessor(self._toplevel, "run_user_scripts", None,
                                      lambda ao,c,eo,ca,ea: self.run_user_scripts(*ca))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "run_system_scripts", None,
                                      lambda ao, c, eo, ca, ea: self.run_system_scripts(*ca))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "read_file", None,
                                      lambda ao, c, eo, ca, ea: self.read(ca[0]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "write_file", None,
                                      lambda ao, c, eo, ca, ea: self.write(ca[0], ca[1]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "concat", None,
                                      lambda ao, c, eo, ca, ea: "".join([str(_) for _ in ca]))
        self._toplevel.declare_method(m, globally=True)
        m = ExtensibleWrappedAccessor(self._toplevel, "replace", None,
                                      lambda ao, c, eo, ca, ea: ca[0].replace(ca[1], ca[2]))
        self._toplevel.declare_method(m, globally=True)
