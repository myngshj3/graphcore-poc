# -*- coding: utf-8 -*-

import ply.lex as lex
import ply.yacc as yacc
import sys
import traceback

# Word analysis
tokens = (
    'BOOLNEGATOR',
    'NUMBERNEGATOR',
    'FORALL',
    'EXISTS',
    'FUNCTIONNAME',
    'CARD',
    'CONJ',
    'DISJ',
    'MEMBEROF',
    'COMPARATOR',
    'BOOLCOMPARATOR',
    'IMPLICATOR',
    'QUOTE',
    'DOUBLEQUOTE',
    'ALPHABET',
    'ALPHABETS',
    'CHAR',
    'UNDERSCORE',
    'BOOLSYMBOL',
    'NATURALNUMBER',
    'POSITIVEFLOAT',
    'NUMBERREVERSER',
    'NAMEDSYMBOL',
    'NUMBEROPERATOR',
    'LITERAL',
    'LPAR',
    'RPAR',
    'CLPAR',
    'CRPAR',
    'LBRACKET',
    'RBRACKET',
    'COMMA',
    'PERIOD',
    'COMMENT'
)

t_BOOLNEGATOR = r"!|neg"
t_NUMBERNEGATOR = r"-"
t_FORALL = r"forall"
t_EXISTS = r"exists"
t_FUNCTIONNAME = r"card|strcat"
t_CARD = r"card"
t_CONJ = r"and"
t_DISJ = r"or"
t_MEMBEROF = r"in"
t_COMPARATOR = r"==|<=|<|!="
t_BOOLCOMPARATOR = r"==|!="
t_IMPLICATOR = r"=>"
t_QUOTE = r"'"
t_DOUBLEQUOTE = r"\""
t_ALPHABET = r"[a-zA-Z]"
t_ALPHABETS = r"[a-zA-Z]+"
t_CHAR = r"^[\"]"
t_UNDERSCORE = r"_"
t_BOOLSYMBOL = r"true|false|True|False"
t_NATURALNUMBER = r"[1-9][0-9]*|0"
t_POSITIVEFLOAT = r"0\.[0-9]+|[1-9][0-9]*\.[0-9]+"
t_NUMBERREVERSER = r"-"
t_NAMEDSYMBOL = r"[a-zA-Z_]+[a-zA-Z_0-9]*"
t_NUMBEROPERATOR = r"\+|\*|/|%"
t_LITERAL = r"\"[\\\"'-\?\*_/<>!#$%&\(\)=~|{}a-zA-Z0-9]*\""
t_LPAR = r"\("
t_RPAR = r"\)"
t_CLPAR = r"\["
t_CRPAR = r"\]"
t_LBRACKET = r"{"
t_RBRACKET = r"}"
t_COMMA = ","
t_PERIOD = "."
t_ignore_COMMENT = r"/\*\[\s\S]*\*/|//.*"
t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character {}".format(t.value[0]))
    t.lexer.skip(1)


# Lexer
# lexer = lex.lex()
lex.lex(debug=0)


# GraphCoreTerm class
def parse_term(term):
    return


# Syntax analysis

# general term
def p_term(p):
    # """
    # TERM :
    # TERM : STRINGTERM
    # TERM : NUMBERTERM
    # TERM : BOOLTERM
    # TERM : FUNCTIONTERM
    # """
    """
    TERM :
    TERM : BOOLTERM
    """
    print("term, ", p)
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]


# term is number
def p_numberterm(p):
    """
    NUMBERTERM : NATURALNUMBER
               | POSITIVEFLOAT
               | NUMBERREVERSER NUMBERTERM
               | LPAR NUMBERTERM RPAR
               | NUMBERTERM NUMBEROPERATOR NUMBERTERM
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 4:
        p[0] = p[1] + p[2] + p[3]
    else:
        print("numberterm Bug!!!, ", p)


# term is string
def p_stringterm(p):
    """
    STRINGTERM : DOUBLEQUOTE CHARSEQUENCE DOUBLEQUOTE
               | DOUBLEQUOTE DOUBLEQUOTE
    """
    if len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 4:
        p[0] = p[1] + p[2] + p[3]
    else:
        print("stringterm Bug!!!, ", p)


# term is char sequence
def p_charsequence(p):
    """
    CHARSEQUENCE : CHAR
                 | CHAR CHARSEQUENCE
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + p[2]
    else:
        print("charsequence Bug!!!, ", p)


# term is bool
def p_boolterm(p):
    # """
    # BOOLTERM : BOOLSYMBOL
    #          | LPAR BOOLTERM RPAR
    #          | BOOLTERM BOOLCOMPARATOR BOOLTERM
    #          | BOOLNEGATOR BOOLTERM
    # """
    """
    BOOLTERM : BOOLSYMBOL
    """
    if len(p) == 1:
        p[0] = p[1]
    elif len(p) == 2:
        p[0] = p[1] + p[2]
    elif len(p) == 3:
        p[0] = p[1] + p[2] + p[3]
    else:
        print("boolterm Bug!!!, ", p)


# term is function call
def p_functionterm(p):
    """
    FUNCTIONTERM : FUNCTIONNAME TUPLE
    """
    p[0] = p[1] + p[2]
    print(p)


# term is tuple
def p_tuple(p):
    """
    TUPLE : LPAR SEPARATEDTERM RPAR
    """
    p[0] = p[1] + p[2] + p[3]
    print(p)


# term is separated1
def p_separatedterm(p):
    """
    SEPARATEDTERM : NUMBERTERM
                  | STRINGTERM
                  | BOOLTERM
                  | NUMBERTERM COMMA SEPARATEDTERM
                  | STRINGTERM COMMA SEPARATEDTERM
                  | BOOLTERM COMMA SEPARATEDTERM
    """
    print(p)


# def p_forallterm(p):
#     '''FORALLTERM : FORALL NAMEDSYMBOL MEMBEROF NAMEDSYMBOL BOOLTERM
#        expression : FORALLTERM'''
#     print("forallterm:{}".format(p))
#
#
# def p_existsterm(p):
#     '''EXISTSTERM : EXISTS NAMEDSYMBOL MEMBEROF NAMEDSYMBOL BOOLTERM
#        expression : EXISTSTERM'''
#     print("existsterm:{}".format(p))



# def p_condition(p):
#     '''condition : clpar conditionalstatement crpar'''
#     p[0] = p[1] + p[2] + p[3]


# def p_conditionalstatements(p):
#     '''
#     conditionalstatement : logcalstatement
#     '''
#     if len(p) == 2:
#         p[0] = p[1]
#     if len(p) == 3:
#         p[0] = p[1] + p[2]
#     elif len(p) == 3:
#         p[0] = p[1] + p[2] + p[3]
#     else:
#         print("Bug!!! {}".format("conditionalstatement"))


# def p_logicalstatement(p):
#     '''logicalstatement : logicalstatement
#                         | unarylogicaloperator logicalstatement
#                         | logicalstatement binarylogicaloperator logicalstatement'''
#     if len(p) == 1:
#         p[0] = p[1]
#     elif len(p) == 2:
#         p[0] = p[1] + p[2]
#     elif len(p) == 3:
#         p[0] = p[1] + p[2] + p[3]
#     else:
#         print("Bug!!! {}".format("logicalstatement"))


# if error occured
def p_error(p):
    print('Syntax error: %d: %r' % (p.lineno, p.value))
    # exit()
    # print('Syntax error in input!')


parser = yacc.yacc()


def yacc_test(text):
    data = text

    result = parser.parse(data)
    print('result: ', result)


def lex_test():
    while True:
        print("input")
        line = sys.stdin.readline()
        if line == "exit\n" or line == "quit\n":
            break
        lexer.input(line)
        while True:
            token = lexer.token()
            if not token:
                break
            print(token)
    print("program quit")


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

