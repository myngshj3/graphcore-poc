# -*- coding: utf-8 -*-

from networkml import config
from graphcore.reporter import GraphCoreReporter
config.set_log_config("log4p.conf")

import ply.lex as lex
import ply.yacc as yacc
import traceback
# import re
# import sys
import networkx as nx
# import openpyxl
# import os
# import json
# import sys
# import inspect
# from enum import Enum

# import our modules
from networkml.generic import GenericEvaluatee, debug, is_debug_mode
from networkml.error import NetworkError, NetworkParserError, NetworkLexerError
from networkml.validator import Validatee, ArithmeticModulusEvaluatee, ArithmeticMultiplicableEvaluatee
from networkml.validator import ArithmeticSubtractalEvaluatee, ArithmeticBinaryEvaluatee, ArithmeticAdditionalEvaluatee
from networkml.validator import ArithmeticDivideEvaluatee, ArithmeticBinaryEvaluatee
from networkml.validator import BooleanNegatee, BooleanBinaryEvaluatee
from networkml.validator import BooleanConjunctiveEvaluatee, BooleanDisjunctiveEvaluatee, BooleanGreaterOrEqualsEvaluatee
from networkml.validator import BooleanGreaterThanEvaluatee, BooleanLessOrEqualsEvaluatee, BooleanLessThanEvaluatee
from networkml.validator import BooleanEqualityEvaluatee, BooleanDifferenceEvaluatee, BooleanMatchee, BooleanUnmatchee
from networkml.validator import BooleanUnaryEvaluatee, TrueEvaluatee
from networkml.network import NetworkClassInstance, NetworkMethodCaller, WhileStatement, IfElifElseStatement
from networkml.network import ReachabilitySpecification, NetworkBreak
from networkml.network import NetworkMethod, ForeachStatement, NetworkSubstituter
from networkml.network import ReachNetworkConstructor, Interval, SimpleVariable, NetworkReturn
from networkml.network import Interval, Numberset, NumbersetOperator, CommandOption
from networkml.network import NetworkClass
from networkml.network import NetworkClassInstance
from networkml.network import NetworkInstance
from networkml.specnetwork import SpecValidator
from networkml.network import ExtensibleWrappedAccessor
from networkml.network import NetworkSymbol
from networkml.generic import GenericValidatorParam
from networkml.network import ForallStatement
from networkml.network import ExistsStatement
from networkml import config
import log4p


class Symbol(NetworkSymbol):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner, symbol):
        super().__init__(owner, symbol)


class Equal(BooleanEqualityEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, True, True)


class Different(BooleanDifferenceEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, True, False)


class LessThan(BooleanLessThanEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, 0, 1)


class LessOrEqual(BooleanLessOrEqualsEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, 0, 1)


class GreaterThan(BooleanGreaterThanEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, 1, 0)


class GreaterOrEqual(BooleanGreaterOrEqualsEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, 1, 0)


class Match(BooleanMatchee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, "", "")


class Unmatch(BooleanUnmatchee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, "a", "")


class Plus(ArithmeticAdditionalEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, 0, 0)


class Minus(ArithmeticSubtractalEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, 0, 0)


class Multiply(ArithmeticMultiplicableEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, 1, 0)


class Divide(ArithmeticDivideEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, 1, 1)


class Mod(ArithmeticModulusEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, 1, 1)


class And(BooleanConjunctiveEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner, l, r):
        super().__init__(owner, l, r)


class Or(BooleanDisjunctiveEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner, l, r):
        super().__init__(owner, l, r)


class Not(BooleanNegatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner, expr):
        super().__init__(owner, expr)


class Imply(BooleanDisjunctiveEvaluatee):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner):
        super().__init__(owner, False, True, sym="=>")

    def evaluate(self, caller=None):
        l, r = super().evaluate(caller)
        return not l or r


class Nodes:

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner: NetworkInstance, cond=None):
        self._owner = owner
        self._cond = cond

    @property
    def owner(self) -> NetworkInstance:
        return self._owner

    @property
    def symbol(self) -> str:
        return "Nodes"

    @property
    def cond(self) ->GenericEvaluatee:
        return self._cond

    def set_cond(self, cond):
        self._cond = cond

    def evaluate(self, caller: NetworkInstance):
        N = []
        for n in caller.G.nodes:
            caller.validator.set_evaluation_target(caller.G.nodes[n], GenericValidatorParam.VALIDATE_AS_TAG)
            if self.cond is None:
                N.append(caller.G.nodes[n])
            else:
                validator = caller.validator
                validator.set_evaluation_target(caller.G.nodes[n], GenericValidatorParam.VALIDATE_AS_TAG)
                # cond = validator.validate(self.cond)
                cond = self.cond.evaluate(caller)
                validator.reset_evaluation_policy()
                if cond:
                    N.append(caller.G.nodes[n])
        return tuple(N)


class Edges:
    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner: NetworkInstance, cond=None):
        self._owner = owner
        self._cond = cond

    @property
    def owner(self) -> NetworkInstance:
        return self._owner

    @property
    def symbol(self) -> str:
        return "Edges"

    @property
    def cond(self) -> GenericEvaluatee:
        return self._cond

    def set_cond(self, cond):
        self._cond = cond

    def evaluate(self, caller: NetworkInstance):
        E = []
        for e in caller.G.edges:
            caller.validator.set_evaluation_target(caller.G.edges[e[0], e[1]], GenericValidatorParam.VALIDATE_AS_TAG)
            if self.cond is None:
                E.append(caller.G.edges[e[0], e[1]])
            else:
                validator = caller.validator
                validator.set_evaluation_target(caller.G.edges[e[0], e[1]], GenericValidatorParam.VALIDATE_AS_TAG)
                # cond = validator.validate(self.cond)
                cond = self.cond.evaluate(caller)
                validator.reset_evaluation_policy()
                if cond:
                    E.append(caller.G.edges[e[0], e[1]])
        return tuple(E)


class Paths:

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner: NetworkInstance, cond=None):
        self._owner = owner
        self._cond = cond

    @property
    def owner(self) -> NetworkInstance:
        return self._owner

    @property
    def cond(self):
        return self._cond

    def set_cond(self, cond):
        self._cond = cond

    def evaluate(self, caller: NetworkInstance):
        P = []
        V = [_ for _ in caller.G.nodes]
        for u in V:
            for v in V:
                paths = nx.all_Simple_paths(caller.G, u, v)
                P.extend(paths)
        return tuple(P)

class Equation:

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner: NetworkInstance, eqn):
        self._owner = owner
        self._eqn = eqn

    @property
    def owner(self) -> NetworkInstance:
        return self._owner

    @property
    def eqn(self):
        return self._eqn

    def evaluate(self, caller: NetworkInstance):
        pass


class ForallEquation(ForallStatement):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner: NetworkInstance, var, fetchee, eqn):
        super().__init__(owner, var, fetchee)
        self.append_statements(eqn)

    def prepare(self, caller):
        if not super().prepare(caller):
            return False
        try:
            fetchee = caller.accessor.get(caller, self.fetchee)
            fetchee = fetchee.evaluate(caller)
            caller.accessor.set(caller, self.fetchee, fetchee)
            return True
        except Exception as ex:
            return False

    def fetch(self, caller):
        accessor = caller.accessor
        fetchee = accessor.get(caller, self.fetchee)
        pos = accessor.get(caller, self.fetch_pos_name)
        pos = pos + 1
        accessor.set(caller, self.fetch_pos_name, pos)
        if pos < len(fetchee):
            accessor.set(caller, self.var, fetchee[pos])
            return True
        else:
            return False

    def evaluate(self, caller: NetworkInstance):
        return self(caller)

    def __repr__(self):
        return "forall {} in {} : ...".format(self.var, self.fetchee)


class ExistsEquation(ExistsStatement):

    log = log4p.GetLogger(logger_name=__name__, config=config.get_log_config()).logger

    def __init__(self, owner: NetworkInstance, var, fetchee, eqn):
        super().__init__(owner, var, fetchee)
        self.append_statements(eqn)

    def prepare(self, caller):
        if not super().prepare(caller):
            return False
        try:
            fetchee = caller.accessor.get(caller, self.fetchee)
            fetchee = fetchee.evaluate(caller)
            caller.accessor.set(caller, self.fetchee, fetchee)
            return True
        except Exception as ex:
            return False

    def fetch(self, caller):
        accessor = caller.accessor
        fetchee = accessor.get(caller, self.fetchee)
        pos = accessor.get(caller, self.fetch_pos_name)
        pos = pos + 1
        accessor.set(caller, self.fetch_pos_name, pos)
        if pos < len(fetchee):
            accessor.set(caller, self.var, fetchee[pos])
            return True
        else:
            return False

    def evaluate(self, caller: NetworkInstance):
        return self(caller)

    def __repr__(self):
        return "exists {} in {} : ...".format(self.var, self.fetchee)


class GCConstraintParser:

    def __init__(self, owner: NetworkInstance, reporter: GraphCoreReporter=GraphCoreReporter(print)):
        self._owner = owner
        self._reporter = reporter
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)

    @property
    def owner(self) -> NetworkInstance:
        return self._owner

    @property
    def reporter(self) -> GraphCoreReporter:
        return self._reporter

    def set_reporter(self, value: GraphCoreReporter):
        self._reporter = value

    def parse(self, text):
        return self.parse_script(text)

    def parse_script(self, text):
        result = self.parser.parse(text, lexer=self.lexer)
        return result

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            self.reporter.report(tok)

    # Word analysis
    reserved = {
        'forall': 'FORALL',
        'exists': 'EXISTS',
        'in': 'IN',
        'and': 'AND',
        'or': 'OR',
        'not': 'NOT',
        'null': 'NULL',
        'true': 'TRUE',
        'false': 'FALSE',
        'Nodes': 'NODES',
        'Edges': 'EDGES',
        'Paths': 'PATHS'
    }
    tokens = [
              'SYMBOL',
              'EQUAL', 'DIFFERENT', 'LESS_THAN', 'LESS_OR_EQUAL', 'GREATER_THAN', 'GREATER_OR_EQUAL',
              'MATCH', 'UNMATCH',
              'LPAR', 'RPAR', 'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
              'COMMA', 'DOUBLE_PERIOD',
              'POSITIVE_INT', 'NEGATIVE_INT', 'POSITIVE_FLOAT', 'NEGATIVE_FLOAT', 'LITERAL', 'PATTERN',
              'PLUS', 'MINUS', 'MULTIPLY', 'DIVIDE', 'MOD',
              'EDGESTART',
              'OUTBOUND',
              'OPTION',
              'CORON',
              'SEMICORON',
              'IMPLY',
              'PROPERTY'
              # 'COMMENT'
              ] + list(reserved.values())
    token_list = (
        # Reserved words
    )
    token = tokens

    t_ignore_COMMENT = r"/\*\[\s\S]*\*/|//.*"
    t_ignore = " \t"

    # t_INDEX = r""

    def t_SYMBOL(self, t):
        r"[a-zA-Z_]+[a-zA-Z_0-9]*"
        if t.value in self.reserved:
            t.type = self.reserved[t.value]
            return t
        else:
            return t
    t_EQUAL = r"=="
    t_DIFFERENT = r"!="
    t_LESS_THAN = r"<"
    t_LESS_OR_EQUAL = r"<="
    t_GREATER_THAN = r">"
    t_GREATER_OR_EQUAL = r">="
    t_MATCH = r"=~"
    t_UNMATCH = r"!=~"
    t_LPAR = r"\("
    t_RPAR = r"\)"
    t_LBRACE = r"\["
    t_RBRACE = r"\]"
    t_LBRACKET = r"\{"
    t_RBRACKET = r"\}"
    t_COMMA = r","
    t_DOUBLE_PERIOD = r"\.\."
    t_POSITIVE_INT = r"[0-9]+"
    t_NEGATIVE_INT = r"\-[0-9]+"
    t_POSITIVE_FLOAT = r"[0-9]+\.[0-9]+"
    t_NEGATIVE_FLOAT = r"\-[0-9]+\.[0-9]+"
    t_LITERAL = r"\"(\"\"|[^\"])*\""
    t_PATTERN = r"/[^/]+/"
    t_PLUS = r"\+"
    t_MINUS = r"\-"
    t_MULTIPLY = r"\*"
    t_DIVIDE = r"\/"
    t_MOD = r"\%"
    t_EDGESTART = r"\-{2,100}"
    t_OUTBOUND = r"\-{1,100}>"
    t_OPTION = r"\-\-[a-zA-Z]+([_]+[a-zA-Z0-9]+)*"
    t_CORON = r":"
    t_SEMICORON = r";"
    t_IMPLY = r"={1,10}>"
    t_PROPERTY = r"'[a-zA-Z]+([a-zA-Z0-9_]+)*'"

    def t_error(self, t):
        # _print("Illegal character {}".format(t.value[0]))
        t.lexer.skip(1)

    def p_available_equation(self, p):
        """
        available_equation : constraint
        """
        p[0] = p[1]

    def p_constraint(self, p):
        """
        constraint : forall_equation
        constraint : exists_equation
        constraint : basic_equation
        """
        p[0] = p[1]

    def p_set_symbol(self, p):
        """
        set_symbol : nodes
        set_symbol : edges
        """
        p[0] = p[1]

    def p_forall_equation(self, p):
        """
        forall_equation : forall symbol in set_symbol coron constraint
        """
        if isinstance(p[4], Nodes):
            fetchee = Symbol(self.owner, "Nodes")
        else:
            fetchee = Symbol(self.owner, "Edges")
        p[0] = ForallEquation(self.owner, p[2], fetchee, p[6])

    def p_exists_equation(self, p):
        """
        exists_equation : exists symbol in set_symbol coron constraint
        """
        if isinstance(p[4], Nodes):
            fetchee = Symbol(self.owner, "Nodes")
        else:
            fetchee = Symbol(self.owner, "Edges")
        p[0] = ExistsEquation(self.owner, p[2], fetchee, p[6])

    def p_basic_equation(self, p):
        """
        basic_equation : cond
        """
        p[0] = p[1]

    def p_cond(self, p):
        """
        cond : cond_and
        cond : cond_or
        cond : cond_not
        cond : cond_equal
        cond : cond_different
        cond : cond_less_than
        cond : cond_less_or_equal
        cond : cond_greater_than
        cond : cond_greater_or_equal
        cond : cond_match
        cond : cond_unmatch
        cond : cond_imply
        cond : LPAR cond RPAR
        """
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = p[2]

    def p_cond_and(self, p):
        """
        cond_and : cond and cond
        """
        p[0] = p[2]
        p[0].set_l(p[1])
        p[0].set_r(p[3])

    def p_cond_or(self, p):
        """
        cond_or : cond or cond
        """
        p[0] = p[2]
        p[0].set_l(p[1])
        p[0].set_l(p[1])
        p[0].set_r(p[3])

    def p_cond_not(self, p):
        """
        cond_not : not cond
        """
        p[0] = p[1]
        p[0].set_expr(p[2])

    def p_cond_equal(self, p):
        """
        cond_equal : property_name equal number
        cond_equal : property_name equal literal
        cond_equal : property_name equal bool
        cond_equal : property_name equal property_name
        cond_equal : property_name equal property
        cond_equal : property      equal number
        cond_equal : property      equal literal
        cond_equal : property      equal bool
        cond_equal : property      equal property_name
        cond_equal : property      equal property
        """
        p[0] = p[2]
        p[0].set_l(p[1])
        l_sym = True
        p[0].l_symbol = l_sym
        p[0].set_r(p[3])
        if type(p[3]) is int or type(p[3]) is float or type(p[3]) is str or type(p[3]) is bool:
            r_sym = False
        else:
            r_sym = True
        p[0].r_symbol = r_sym

    def p_cond_different(self, p):
        """
        cond_different : property_name different number
        cond_different : property_name different literal
        cond_different : property_name different bool
        cond_different : property_name different property_name
        cond_different : property_name different property
        cond_different : property      different number
        cond_different : property      different literal
        cond_different : property      different bool
        cond_different : property      different property_name
        cond_different : property      different property
        """
        p[0] = p[2]
        p[0].set_l(p[1])
        l_sym = True
        p[0].l_symbol = l_sym
        p[0].set_r(p[3])
        if type(p[3]) is int or type(p[3]) is float or type(p[3]) is str or type(p[3]) is bool:
            r_sym = False
        else:
            r_sym = True
        p[0].r_symbol = r_sym

    def p_cond_less_than(self, p):
        """
        cond_less_than : property_name less_than number
        cond_less_than : property_name less_than property_name
        cond_less_than : property_name less_than property
        cond_less_than : property      less_than number
        cond_less_than : property      less_than property_name
        cond_less_than : property      less_than property
        """
        p[0] = p[2]
        p[0].set_l(p[1])
        l_sym = True
        p[0].l_symbol = l_sym
        p[0].set_r(p[3])
        if type(p[3]) is int or type(p[3]) is float or type(p[3]) is str:
            r_sym = False
        else:
            r_sym = True
        p[0].r_symbol = r_sym

    def p_cond_less_or_equal(self, p):
        """
        cond_less_or_equal : property_name less_or_equal number
        cond_less_or_equal : property_name less_or_equal property_name
        cond_less_or_equal : property_name less_or_equal property
        cond_less_or_equal : property      less_or_equal number
        cond_less_or_equal : property      less_or_equal property_name
        cond_less_or_equal : property      less_or_equal property
        """
        p[0] = p[2]
        p[0].set_l(p[1])
        l_sym = True
        p[0].l_symbol = l_sym
        p[0].set_r(p[3])
        if type(p[3]) is int or type(p[3]) is float or type(p[3]) is str:
            r_sym = False
        else:
            r_sym = True
        p[0].r_symbol = r_sym

    def p_cond_greater_than(self, p):
        """
        cond_greater_than : property_name greater_than number
        cond_greater_than : property_name greater_than property_name
        cond_greater_than : property_name greater_than property
        cond_greater_than : property      greater_than number
        cond_greater_than : property      greater_than property_name
        cond_greater_than : property      greater_than property
        """
        p[0] = p[2]
        p[0].set_l(p[1])
        l_sym = True
        p[0].l_symbol = l_sym
        p[0].set_r(p[3])
        if type(p[3]) is int or type(p[3]) is float or type(p[3]) is str:
            r_sym = False
        else:
            r_sym = True
        p[0].r_symbol = r_sym

    def p_cond_greater_or_equal(self, p):
        """
        cond_greater_or_equal : property_name greater_or_equal number
        cond_greater_or_equal : property_name greater_or_equal property_name
        cond_greater_or_equal : property_name greater_or_equal property
        cond_greater_or_equal : property      greater_or_equal number
        cond_greater_or_equal : property      greater_or_equal property_name
        cond_greater_or_equal : property      greater_or_equal property
        """
        p[0] = p[2]
        p[0].set_l(p[1])
        l_sym = True
        p[0].l_symbol = l_sym
        p[0].set_r(p[3])
        if type(p[3]) is int or type(p[3]) is float or type(p[3]) is str:
            r_sym = False
        else:
            r_sym = True
        p[0].r_symbol = r_sym

    def p_cond_match(self, p):
        """
        cond_match : property_name match pattern
        cond_match : property_name match property_name
        cond_match : property_name match property
        cond_match : property      match pattern
        cond_match : property      match property_name
        cond_match : property      match property
        """
        p[0] = p[2]
        p[0].set_l(p[1])
        l_sym = True
        p[0].l_symbol = l_sym
        p[0].set_r(p[3])
        if type(p[3]) is int or type(p[3]) is float or type(p[3]) is str:
            r_sym = False
        else:
            r_sym = True
        p[0].r_symbol = r_sym

    def p_cond_unmatch(self, p):
        """
        cond_unmatch : property_name unmatch pattern
        cond_unmatch : property_name unmatch property_name
        cond_unmatch : property_name unmatch property
        cond_unmatch : property      unmatch pattern
        cond_unmatch : property      unmatch property_name
        cond_unmatch : property      unmatch property
        """
        p[0] = p[2]
        p[0].set_l(p[1])
        l_sym = True
        p[0].l_symbol = l_sym
        p[0].set_r(p[3])
        if type(p[3]) is int or type(p[3]) is float or type(p[3]) is str:
            r_sym = False
        else:
            r_sym = True
        p[0].r_symbol = r_sym

    def p_cond_imply(self, p):
        """
        cond_imply : property_name imply bool
        cond_imply : property_name imply property_name
        cond_imply : property_name imply property
        cond_imply : property      imply bool
        cond_imply : property      imply property_name
        cond_imply : property      imply property
        cond_imply : bool          imply bool
        cond_imply : bool          imply property_name
        cond_imply : bool          imply property
        cond_imply : cond          imply cond
        cond_imply : cond          imply bool
        cond_imply : bool          imply cond
        """
        p[0] = p[2]
        p[0].set_l(p[1])
        if type(p[1]) is bool:
            l_sym = False
        else:
            l_sym = True
        p[0].l_symbol = l_sym
        p[0].set_r(p[3])
        if type(p[3]) is int or type(p[3]) is float or type(p[3]) is str:
            r_sym = False
        else:
            r_sym = True
        p[0].r_symbol = r_sym

    def p_path_cond(self, p):
        """
        path_cond : node reach
        """
        p[0] = p[1]

    def p_node(self, p):
        """
        node : LBRACE cond RBRACE
        """
        p[0] = p[1]

    def p_edge(self, p):
        """
        edge : edgestart lbrace cond rbrace outbound
        """
        p[0] = p[1]

    def p_forall(self, p):
        """
        forall : FORALL
        """
        p[0] = p[1]

    def p_exists(self, p):
        """
        exists : EXISTS
        """
        p[0] = p[1]

    def p_in(self, p):
        """
        in : IN
        """
        p[0] = p[1]

    def p_and(self, p):
        """
        and : AND
        """
        p[0] = And(self.owner, True, True)

    def p_or(self, p):
        """
        or : OR
        """
        p[0] = Or(self.owner, True, False)

    def p_not(self, p):
        """
        not : NOT
        """
        p[0] = Not(self.owner, False)

    def p_null(self, p):
        """
        null : NULL
        """
        p[0] = None

    def p_true(self, p):
        """
        true : TRUE
        """
        p[0] = True

    def p_false(self, p):
        """
        false : FALSE
        """
        p[0] = False

    def p_bool(self, p):
        """
        bool : true
        bool : false
        """
        p[0] = p[1]

    def p_nodes(self, p):
        """
        nodes : NODES
        nodes : NODES lpar cond rpar
        """
        if len(p) == 2:
            p[0] = Nodes(self.owner)
            self.owner.accessor.set(self.owner, "Nodes", p[0])
        else:
            p[0] = Nodes(self.owner, p[3])
            # self.owner.accessor.set(self.owner, "Nodes({})".format(str(p[3])), p[0])
            self.owner.accessor.set(self.owner, "Nodes", p[0])

    def p_edges(self, p):
        """
        edges : EDGES
        edges : EDGES lpar cond rpar
        """
        if len(p) == 2:
            p[0] = Edges(self.owner)
            self.owner.accessor.set(self.owner, "Edges", p[0])
            # var = SimpleVariable(self.owner, "Edges", p[0])
            # self.owner.declare_var(var)
        else:
            p[0] = Edges(self.owner, p[3])
            self.owner.accessor.set(self.owner, "Edges", p[0])
            # var = SimpleVariable(self.owner, "Edges({})".format(str(p[3])), p[0])
            # self.owner.declare_var(var)

    def p_paths(self, p):
        """
        paths : PATHS
        paths : PATHS lpar cond rpar
        """
        if len(p) == 2:
            p[0] = Paths(self.owner)
        else:
            p[0] = Paths(self.owner, p[3])

    def p_symbol(self, p):
        """
        symbol : SYMBOL
        """
        p[0] = Symbol(self.owner, p[1])

    def p_equal(self, p):
        """
        equal : EQUAL
        """
        p[0] = Equal(self.owner)

    def p_different(self, p):
        """
        different : DIFFERENT
        """
        p[0] = Different(self.owner)

    def p_less_than(self, p):
        """
        less_than : LESS_THAN
        """
        p[0] = LessThan(self.owner)

    def p_less_or_equal(self, p):
        """
        less_or_equal : LESS_OR_EQUAL
        """
        p[0] = LessOrEqual(self.owner)

    def p_greater_than(self, p):
        """
        greater_than : GREATER_THAN
        """
        p[0] = GreaterThan(self.owner)

    def p_greater_or_equal(self, p):
        """
        greater_or_equal : GREATER_OR_EQUAL
        """
        p[0] = GreaterOrEqual(self.owner)

    def p_match(self, p):
        """
        match : MATCH
        """
        p[0] = Match(self.owner)

    def p_unmatch(self, p):
        """
        unmatch : UNMATCH
        """
        p[0] = Unmatch(self.owner)

    def p_lpar(self, p):
        """
        lpar : LPAR
        """
        p[0] = p[1]

    def p_rpar(self, p):
        """
        rpar : RPAR
        """
        p[0] = p[1]

    def p_lbrace(self, p):
        """
        lbrace : LBRACE
        """
        p[0] = p[1]

    def p_rbrace(self, p):
        """
        rbrace : RBRACE
        """
        p[0] = p[1]

    def p_lbrackcet(self, p):
        """
        lbracket : LBRACKET
        """
        p[0] = p[1]

    def p_rbracket(self, p):
        """
        rbracket : RBRACKET
        """
        p[0] = p[1]

    def p_comma(self, p):
        """
        comma : COMMA
        """
        p[0] = p[1]

    def p_double_period(self, p):
        """
        double_period : DOUBLE_PERIOD
        """
        p[0] = p[1]

    def p_postive_int(self, p):
        """
        positive_int : POSITIVE_INT
        """
        p[0] = int(p[1])

    def p_negative_int(self, p):
        """
        negative_int : NEGATIVE_INT
        """
        p[0] = int(p[1])

    def p_int(self, p):
        """
        int : positive_int
        int : negative_int
        """
        p[0] = p[1]

    def p_postive_float(self, p):
        """
        positive_float : POSITIVE_FLOAT
        """
        p[0] = float(p[1])

    def p_negative_float(self, p):
        """
        negative_float : NEGATIVE_FLOAT
        """
        p[0] = float(p[1])

    def p_float(self, p):
        """
        float : positive_float
        float : negative_float
        """
        p[0] = p[1]

    def p_number(self, p):
        """
        number : int
        number : float
        """
        p[0] = p[1]

    def p_literal(self, p):
        """
        literal : LITERAL
        """
        p[0] = p[1][1:len(p[1])-1]

    def p_pattern(self, p):
        """
        pattern : PATTERN
        """
        p[0] = p[1]

    def p_plus(self, p):
        """
        plus : PLUS
        """
        p[0] = Plus(self.owner)

    def p_minus(self, p):
        """
        minus : MINUS
        """
        p[0] = Minus(self.owner)

    def p_multiply(self, p):
        """
        multiply : MULTIPLY
        """
        p[0] = Multiply(self.owner)

    def p_divide(self, p):
        """
        divide : DIVIDE
        """
        p[0] = Divide(self.owner)

    def p_mod(self, p):
        """
        mod : MOD
        """
        p[0] = Mod(self.owner)

    def p_edgestart(self, p):
        """
        edgestart : EDGESTART
        """
        p[0] = p[1]

    def p_outbound(self, p):
        """
        outbound : OUTBOUND
        """
        p[0] = p[1]

    def p_option(self, p):
        """
        option : OPTION
        """
        p[0] = p[1]

    def p_coron(self, p):
        """
        coron : CORON
        """
        p[0] = p[1]

    def p_semicoron(self, p):
        """
        semicoron : SEMICORON
        """
        p[0] = p[1]

    def p_imply(self, p):
        """
        imply : IMPLY
        """
        p[0] = Imply(self.owner)

    def p_property(self, p):
        """
        property : SYMBOL LBRACE PROPERTY RBRACE
        """
        # sym = "{0}[{1}]".format(p[1], p[3][1:len(p[3])-1])
        sym = "{0}[{1}]".format(p[1], p[3])
        p[0] = Symbol(self.owner, symbol=sym)

    def p_property_name(self, p):
        """
        property_name : PROPERTY
        """
        p[0] = Symbol(self.owner, symbol=p[1][1:len(p[1])-1])

    def p_asterisk(self, p):
        """
        asterisk : MULTIPLY
        """
        p[0] = p[1]

    def p_reach(self, p):
        """
        reach : edge node
        reach : reach reach
        reach : lpar reach rpar
        reach : lpar reach rpar repetition
        """
        p[0] = p[1]

    def p_repetition(self, p):
        """
        repetition : lbracket positive_int rbracket
        repetition : lbracket positive_int double_period positive_int rbracket
        repetition : lbracket positive_int double_period asterisk rbracket
        """
        if len(p) == 4:
            numbers = Numberset(p[2])
        else:
            numbers = Numberset(p[2])
            if p[4] == "*":
                numbers.infinitize()
            else:
                for n in range(p[2]+1, p[4]+1):
                    numbers.add_number(n)
        p[0] = numbers

    # if error occurred
    def p_error(self, p):
        self.reporter.report('Syntax error: %d: %d: %r' % (p.lineno, p.lexpos, p.value))
        raise NetworkParserError(p)


"""
test program
"""
def main():
    script = """
    forall n in Nodes n['x'] != n['y']
    """
    G = nx.DiGraph()
    G.add_node('1', x=0, y=0, ready=True)
    G.add_node('2', x=0, y=10, ready=True)
    G.add_node('3', x=10, y=10, ready=False)
    G.add_node('4', x=10, y=0, ready=False)
    G.add_node('5', x=0, y=0, ready=True)
    G.add_edge('1', '2', v=5, w=1, t='dataflow')
    G.add_edge('2', '3', v=4, w=0, t='dataflow')
    G.add_edge('3', '4', v=3, w=1, t='dataflow')
    G.add_edge('1', '4', v=2, w=0.5, t='dataflow')
    G.add_edge('2', '4', v=0, w=0.5, t='dataflow')
    G.add_edge('5', '1', v=10, t='folding')
    G.add_edge('5', '2', v=20, t='folding')
    G.add_edge('5', '3', v=30, t='folding')
    G.add_edge('5', '4', v=40, t='folding')
    meta = NetworkClass(None, "GCScriptClass")
    clazz_sig = "{}[{}]".format("NetworkML", 1)
    embedded = [("G", G)]
    args = ()
    clazz = meta(meta, (clazz_sig, embedded, args))
    sig = "{}.{}".format(clazz.signature, clazz.next_instance_id)
    initializer_args = ()
    embedded = ()
    toplevel: NetworkInstance = clazz(clazz, (sig, embedded, initializer_args))
    toplevel.set_stack_enable(True)
    # validator/evaluator
    validator = SpecValidator(owner=toplevel)
    toplevel.set_validator(validator)
    # methods
    printer = ExtensibleWrappedAccessor(toplevel, "print", None,
                                        lambda ao, c, eo, ca, ea: print(" ".join([str(_) for _ in ca])),
                                        globally=True)
    toplevel.declare_method(printer, globally=True)

    m = GCConstraintParser(toplevel)
    while True:
        try:
            txt = input("script-> ")
            if txt == "exit" or txt == "quit":
                break
            # TEST
            # m.test(txt)
            # PARSE
            r = m.parse_script(txt)
            if r is None:
                continue
            rtn = r.evaluate(toplevel)
            print(rtn)
            # print(type(r))
        except Exception as ex:
            print(traceback.format_exc())
    pass


if __name__ == "__main__":
    main()
