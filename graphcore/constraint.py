# -*- coding: utf-8 -*-

import ply.lex as lex
import ply.yacc as yacc
import sys
import traceback
from graphcore.terms import *


# Global data FIXME
error_info = []
reporter = None


def reset_error_info():
    global error_info
    error_info = []


def set_reporter(rep):
    global reporter
    reporter = rep


def _print(s):
    global reporter
    if reporter is None:
        print(s)
    else:
        reporter.report(s)


# Word analysis
tokens = (
    'PROPERTYNAME',
    'ASSIGNMENT',
    'FORALL',
    'EXISTS',
    'CARD',
    'CONJ',
    'DISJ',
    'MEMBEROF',
    'IMPLICATOR',
    'QUOTE',
    'DOUBLEQUOTE',
    'NAMEDSYMBOL',
    'LPAR',
    'RPAR',
    'CLPAR',
    'CRPAR',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'PERIOD',
    'TYPEINT',
    'TYPEFLOAT',
    'TYPESTR',
    'TYPELIST',
    'TYPEBOOL',
    'FUNCDECLARESYMBOL',
    # 'FUNCTIONNAME',
    'VARIABLENAME',
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
    'EDGES'
)

def t_PROPERTYNAME(t):
    r"\'[a-zA-Z][a-zA-Z_\-]*\'"
    _print("PROPERTYNAME:[{}]".format(t.value))
    t.value = t.value
    return t
def t_ASSIGNMENT(t):
    r":="
    _print("ASSIGNMENT:[{}]".format(t.value))
    t.value = AssignmentDeclaration()
    return t
def t_FORALL(t):
    r"\\forall"
    # t.value = lambda x, y, z: forall_in_a_set(x, y, z)
    t.value = ForallEquation()
    return t
def exists_in_a_set(x, y, z):
    for a in y:
        if z.apply(x, a):
            return True
    return False
def t_EXISTS(t):
    r"\\exists"
    # t.value = lambda x, y, z: exists_in_a_set(x, y, z)
    t.value = ExistsEquation()
    return t
def t_CARD(t):
    r"card"
    t.value = lambda x: len(x)
    return t
def t_CONJ(t):
    r"and"
    t.value = lambda x, y: x and y
    return t
def t_DISJ(t):
    r"or"
    t.value = lambda x, y: x or y
    return t
def t_MEMBEROF(t):
    r"\\in"
    t.value = lambda x, y: x in y
    return t
def t_EQUALITY(t):
    r"=="
    t.value = lambda x, y: x == y
    return t
def t_INEQUALITY(t):
    r"!="
    t.value = lambda x, y: x != y
    return t
def t_LESSTHAN(t):
    r"<"
    t.value = lambda x, y: x < y
    return t
def t_LESSOREQUAL(t):
    r"<="
    t.value = lambda x, y: x <= y
    return t
def t_IMPLICATOR(t):
    r"=>"
    t.value = lambda x, y: not x or y
    return t
t_QUOTE = r"'"
t_DOUBLEQUOTE = r"\""
def t_NUMBER(t):
    r"[1-9][0-9]*\.[0-9]+|0\.[0-9]+|[0-9]+"
    _print("NUMBER:[{}]".format(t.value))
    if r"." in t.value:
        t.value = Constant(float(t.value))
    else:
        t.value = Constant(int(t.value))
    return t
def t_STRING(t):
    # r"\"[\w\W\s\S]*\""
    r"\"[a-zA-Z0-9_=/~!#$%&{}\-\[\]\(\)]*\""
    _print("STRING:[{}]".format(t.value))
    t.value = Constant(t.value)
    return t
def t_BOOLSYMBOL(t):
    r"true|false|True|False"
    if t.value in ("true", "True"):
        t.value = Constant(True)
    else:
        t.value = Constant(False)
    return t
t_NAMEDSYMBOL = r"[a-zA-Z_]+[a-zA-Z_0-9]*"
def t_LPAR(t):
    r"\("
    _print("LPAR:{}".format(t.value))
    return t
def t_RPAR(t):
    r"\)"
    _print("RPAR:{}".format(t.value))
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
    _print("SEMICORON: {}".format(t.value))
    t.value = r";"
    return t
def t_FUNCDECLARESYMBOL(t):
    r"function"
    _print("function declaration")
    t.value = t.value
    return t
def t_VARIABLENAME(t):
    r"[a-zA-Z]+[a-zA-Z_0-9]*"
    _print("VARIABLENAME:[{}]".format(t.value))
    t.value = NamedSymbol(t.value)
    return t
def t_NEGATOR(t):
    r"\\neg"
    t.value = lambda x: not x
    return t
t_GRAPH = r"\\Graph"
t_NODES = r"\\Nodes"
t_EDGES = r"\\Edges"
t_ignore_COMMENT = r"/\*\[\s\S]*\*/|//.*"
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    _print("Illegal character {}".format(t.value[0]))
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
    # """
    # TERM :
    # TERM : STRINGTERM
    # TERM : NUMBERTERM
    # TERM : BOOLTERM
    # TERM : FUNCTIONTERM
    # """
    """
    terms :
    terms : declaration_list
    """
    for i, a in enumerate(p):
        _print("[f{}] {}".format(i, a))
    if len(p) == 1:
        p[0] = []
    else:
        # print("term, ", p[1])
        p[0] = p[1]


def p_declaration_list(p):
    """
    declaration_list : declaration
                     | declaration_list declaration
    """
    for i, a in enumerate(p):
        _print("[e{}] {}".format(i, a))
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[2])


# def p_declarations(p):
#     """
#     declaration_list : declarations
#     """
#     for i, a in enumerate(p):
#         print("[d{}] {}".format(i, a))
#     p[0] = [p[1]]

def p_variablename(p):
    """
    variable_name : VARIABLENAME
    """
    p[0] = p[1]


def p_constant(p):
    """
    constant : NUMBER
             | STRING
             | BOOLSYMBOL
    """
    p[0] = p[1]


def p_assignment(p):
    """
    assignment : ASSIGNMENT
    """
    p[0] = p[1]


def p_declaration(p):
    """
    declaration : type_symbol variable_name LPAR type_list RPAR SEMICOLON
                | type_symbol variable_name LPAR RPAR SEMICOLON
                | type_symbol variable_name SEMICOLON
                | boolean_equation SEMICOLON
    """
    # | variable_name
    # assignment
    # NUMBER
    # SEMICOLON
    # | variable_name
    # assignment
    # STRING
    # SEMICOLON
    # | variable_name
    # assignment
    # boolean_equation
    # SEMICOLON
    # | variable
    # SEMICOLON
    # | attribute
    # SEMICOLON
    for i, a in enumerate(p):
        _print("[{}] {}".format(i, a))
    # boolean_equation ;
    if len(p) == 3:
        p[0] = p[1]
    elif len(p) == 4:
        # type_symbol variable_name ;
        if p[1] in (int, float, str, list, bool):
            p[0] = VariableDeclaration(p[1], p[2])
        # type_symbol variable_name ;
        else:
            p[0] = BasicEquation(p[1], p[2])
    # variable_name assignment NUMBER|STRING|boolean_equation ;
    elif len(p) == 5:
        p[0] = p[2]
        p[0].set_named_symbol(p[1])
        p[0].set_value(p[3])
    # type_symbol variable_name() ;
    elif len(p) == 6:
        p[0] = FunctionDeclaration(p[1], p[2])
    # type_symbol variable_name(type_list) ;
    elif len(p) == 7:
        p[0] = FunctionDeclaration(p[1], p[2], p[4])


def p_boolean_equation(p):
    """
    boolean_equation : BOOLSYMBOL
                     | LPAR boolean_equation RPAR
                     | NEGATOR boolean_equation
                     | boolean_equation CONJ boolean_equation
                     | boolean_equation DISJ boolean_equation
                     | boolean_equation EQUALITY boolean_equation
                     | boolean_equation INEQUALITY boolean_equation
                     | boolean_equation IMPLICATOR boolean_equation
                     | variable EQUALITY variable
                     | variable INEQUALITY variable
                     | STRING EQUALITY STRING
                     | STRING INEQUALITY STRING
                     | NUMBER EQUALITY NUMBER
                     | NUMBER INEQUALITY NUMBER
                     | NUMBER LESSTHAN NUMBER
                     | NUMBER LESSOREQUAL NUMBER
                     | attribute EQUALITY attribute
                     | attribute INEQUALITY attribute
                     | attribute LESSTHAN attribute
                     | attribute LESSOREQUAL attribute
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
                     | FORALL VARIABLENAME MEMBEROF nodes_or_edges boolean_equation
                     | EXISTS VARIABLENAME MEMBEROF nodes_or_edges boolean_equation
    """
    for i, a in enumerate(p):
        _print("[b{}] {}".format(i, a))
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = BasicEquation(p[1], p[2])
    elif len(p) == 4:
        if type(p[1]) == str:
            p[0] = p[2]
        else:
            p[0] = BasicEquation(p[2], p[1], p[3])
    elif len(p) == 6:
        p[0] = p[1]
        p[0].set_variable_name(p[2])
        p[0].set_collection(p[4])
        p[0].set_equation(p[5])
    elif len(p) == 7:
        p[0] = NamedSymbol(p[1], attr=p[4])


def p_attribute(p):
    """
    attribute : VARIABLENAME CLPAR PROPERTYNAME CRPAR
    """
    p[0] = p[1]
    p[0].set_attr(p[3][1:len(p[3])-1])


def p_variable(p):
    """
    variable : VARIABLENAME
    """
    p[0] = p[1]


def p_nodes_or_edges(p):
    """
    nodes_or_edges : NODES
                   | EDGES
    """
    p[0] = p[1]


def p_type_symbol(p):
    """
    type_symbol : TYPEINT
                | TYPEFLOAT
                | TYPESTR
                | TYPELIST
                | TYPEBOOL
    """
    for i, a in enumerate(p):
        _print("[c{}] {}".format(i, a))
    p[0] = p[1]  # MyType(p[1])


def p_variable_symbol(p):
    """
    variable_symbol : VARIABLENAME
    """
    _print("variable_symbol({})".format(p[1]))
    p[0] = p[1]  # MyVariable(p[1])


def p_type_list(p):
    """
    type_list : type_symbol
              | type_list COMMA type_symbol
    """
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1]
        p[0].append(p[3])


# if error occurred
def p_error(p):
    _print('Syntax error: %d: %d: %r' % (p.lineno, p.lexpos, p.value))
    error_info.append('Syntax error: %d: %d: %r' % (p.lineno, p.lexpos, p.value))


parser = yacc.yacc()


# parse GraphCore constraint language
def graphcore_parse_constraint(text, rep=None):
    reset_error_info()
    set_reporter(rep)
    result = parser.parse(text, lexer=lexer)
    return result, error_info


def yacc_test(text, rep=None):
    data = text
    set_reporter(rep)

    result = parser.parse(data)
    _print('result: ', result)
    for r in result:
        _print("eval({})={}".format(r, r.evaluate()))


# def lex_test():
#     while True:
#         print("input")
#         line = sys.stdin.readline()
#         if line == "exit\n" or line == "quit\n":
#             break
#         lexer.input(line)
#         while True:
#             token = lexer.token()
#             if not token:
#                 break
#             print(token)
#     print("program quit")


if __name__ == "__main__":
    # lex_test()
    while True:
        try:
            print("input>")
            line = sys.stdin.readline()
            if line == "exit\n" or line == "quit\n":
                break
            yacc_test(line)
        except Exception as ex:
            print(traceback.format_exc(ex))
    print("program quit")

