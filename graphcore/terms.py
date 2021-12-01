# -*- coding: utf-8 -*-

from graphcore.reporter import GraphCoreReporter
# from GraphCore.error import GraphCoreError
from graphcore.shell import GraphCoreContextHandler


# Term class
class Term(object):
    def __init__(self, handler: GraphCoreContextHandler, name=None, value=None, attr=None, reference=None, reporter=None):
        super().__init__()
        self._handler = handler
        self._name = name
        self._value = value
        self._attr = attr
        self._reference = reference
        self._reporter = reporter

    @property
    def handler(self) -> GraphCoreContextHandler:
        return self._handler

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def attr(self):
        return self._attr

    @attr.setter
    def attr(self, attr):
        self._attr = attr

    @property
    def reference(self):
        return self._reference

    @reference.setter
    def reference(self, reference):
        self._reference = reference

    @property
    def reporter(self) -> GraphCoreReporter:
        return self._reporter

    @reporter.setter
    def reporter(self, reporter: GraphCoreReporter):
        self._reporter = reporter

    def report(self, text):
        if self.reporter is None:
            print(text)
        else:
            self.reporter.report(text)

    def apply(self, name, value):
        pass

    def evaluate(self):
        return self.value

    def __repr__(self):
        return "Term(%r)" % self._value


# Variable Declaration class
class VariableDeclaration(Term):
    def __init__(self, handler, type_symbol, variable_symbol, reporter=None):
        super().__init__(handler, reporter=reporter)
        self._type_symbol = type_symbol
        self._variable_symbol = variable_symbol

    def apply(self, name, value):
        pass

    def evaluate(self):
        return self.value

    def __repr__(self):
        return "VariableDeclaration(%r %r)" % (self._type_symbol, self._variable_symbol)


# Function Declaration class
class FunctionDeclaration(Term):
    def __init__(self, handler, return_type, function_symbol, arg_types=None, reporter=None):
        super().__init__(handler, reporter=reporter)
        # self.report("FunctionDeclaration init({},{},{}".format(return_type, function_symbol, arg_types))
        self._return_type = return_type
        self._function_symbol = function_symbol
        self._arg_types = arg_types

    def apply(self, name, value):
        pass

    def evaluate(self):
        return self.value

    def __repr__(self):
        if self._arg_types is None:
            return "FunctionDeclaration(%r, %r)" % (self._return_type, self._function_symbol)
        else:
            return "FunctionDeclaration(%r %r %r)" % (self._return_type, self._function_symbol, self._arg_types)


# Constant class
class Constant(Term):
    def __init__(self, handler, value, reporter=None):
        super().__init__(handler, value=value, reporter=reporter)
        # self.report("Constant value={}".format(value))

    def apply(self, name, value):
        pass

    def evaluate(self):
        return self.value

    def __repr__(self):
        return "Constant(%r)" % self.value


# Named Symbol class
class Variable(Term):
    def __init__(self, handler, name, reference=None, value=None, attr=None, reporter=None):
        super().__init__(handler, name=name, value=value, attr=attr, reference=reference, reporter=reporter)
        if self.reference is None:
            if self.handler.context.has_variable(name):
                self.reference = self.handler.context.variable(name)
            else:
                self.handler.context.add_variable(name, self)
        # self.report("Variable name={}, attr={}, value={}".format(name, attr, value))

    def apply(self, name, value):
        pass

    @property
    def value(self):
        if self.reference is None:
            return self._value
        else:
            return self.reference.value

    @value.setter
    def value(self, value):
        if self.reference is None:
            self._value = value
            # self.value = value
        else:
            self.reference.value = value

    @property
    def attr(self):
        if self.reference is None:
            return self._attr
        else:
            return self.reference.attr

    @attr.setter
    def attr(self, attr):
        if self.reference is None:
            self._attr = attr
        else:
            self.reference.attr = attr

    def evaluate(self):
        if self.reference is not None:
            return self.reference.evaluate()
        else:
            if self.value is None:
                return None
            var = self.value
            if type(var) in (int, float, str, bool):
                # if isinstance(var, Constant):
                if self.attr is None:
                    return var
                else:
                    self.report("GraphCore Bug!!! {}[{}]={}".format(self.name, self.attr, self.value))
                    return None
            else:
                if self.attr is None:
                    return var
                else:
                    return var[self.attr]

    def __repr__(self):
        return "Variable(%r, %r, %r)" % (self.name, self.attr, self.value)


# Variable
class NamedSymbol(Variable):
    def __init__(self, handler, name, reporter=None):
        super().__init__(handler, name, reporter=reporter)
        pass


# Basic Equation class
class BasicEquation(Term):
    def __init__(self, handler, operator, operand1, operand2=None, reporter=None):
        super().__init__(handler, reporter=reporter)
        self._operator = operator
        self._operands = [operand1]
        if operand2 is not None:
            self._operands.append(operand2)

    @property
    def operator(self):
        return self._operator

    @property
    def operands(self):
        return self._operands

    def apply(self, name, value):
        pass

    def evaluate(self):
        if len(self.operands) == 1:
            return self.operator(self.operands[0].evaluate())
        else:
            return self.operator(self.operands[0].evaluate(), self.operands[1].evaluate())

    def __repr__(self):
        if len(self.operands) == 1:
            return "BasicEquation(%r, %r)" % (self.operator, self.operands[0])
        else:
            return "BasicEquation(%r, %r, %r)" % (self.operator, self.operands[0], self.operands[1])


# Forall Equation class
class ForallEquation(Term):
    def __init__(self, handler, variable_name=None, _set=None, _equation=None, reporter=None):
        super().__init__(handler, reporter=reporter)
        self._variable_name = variable_name
        self._set = _set
        self._equation = _equation

    @property
    def variable_name(self):
        return self._variable_name

    @variable_name.setter
    def variable_name(self, name):
        self._variable_name = name

    @property
    def collection(self):
        return self._set

    @collection.setter
    def collection(self, _set):
        self._set = _set

    @property
    def equation(self) -> Term:
        return self._equation

    @equation.setter
    def equation(self, equation):
        self._equation = equation

    def apply(self, name, value):
        pass

    def evaluate(self):
        if self.collection == "\\Graph":
            _collection = self.handler.context.graph
        elif self.collection == "\\Nodes":
            _collection = self.handler.context.nodes
        elif self.collection == "\\Edges":
            _collection = self.handler.context.edges
        else:
            self.report("GraphCore Bug!!!")
            return False
        for a in _collection:
            self.equation.apply(self.variable_name.name, _collection[a])
            if not self._equation.evaluate():
                return False
        return True

    def __repr__(self):
        return "ForallEquation(%r, %r, %r)" % (self.variable_name, self.collection, self.equation)


# Exists Equation class
class ExistsEquation(Term):
    def __init__(self, context, variable_name=None, _set=None, _equation=None, reporter=None):
        super().__init__(context, reporter=reporter)
        self._variable_name = variable_name
        self._set = _set
        self._equation = _equation

    def variable_name(self):
        return self._variable_name

    def set_variable_name(self, name):
        self._variable_name = name

    def collection(self):
        return self._set

    def set_collection(self, _set):
        self._set = _set

    def equation(self):
        return self._equation

    def set_equation(self, equation):
        self._equation = equation

    def apply(self, name, value):
        pass
        # # self._set.apply(name, value)
        # self._equation.apply(name, value)

    def evaluate(self, graph=None, reporter=None):
        if self.collection() == "\\Graph":
            _collection = graph
        elif self.collection() == "\\Nodes":
            _collection = graph.nodes
        elif self.collection() == "\\Edges":
            _collection = graph.edges
        else:
            self.report("GraphCore Bug!!!")
            return False
        for a in _collection:
            self._equation.apply(self.variable_name().name(), _collection[a])
            if self._equation.evaluate(graph):
                return True
        return False

    def __repr__(self):
        return "ExistsEquation(%r, %r, %r)" % (self._variable_name, self._set, self._equation)


# Assignment Statement class
class AssignmentStatement(Term):
    def __init__(self, handler: GraphCoreContextHandler, variable=None, value=None, reporter=None):
        super().__init__(handler, value=value, reporter=reporter)
        # self.report("AssignmentStatement variable={}, value={}".format(variable, value))
        self._variable = variable
        self._assigner = None

    @property
    def assigner(self):
        return self._assigner

    @assigner.setter
    def assigner(self, assigner):
        self._assigner = assigner

    @property
    def variable(self) -> Variable:
        return self._variable

    @variable.setter
    def variable(self, variable: Variable):
        self._variable = variable

    def apply(self, name, value):
        pass

    def evaluate(self):
        if self.assigner is not None:
            value = self.value.evaluate()
            self.assigner(self.variable.evaluate(), value)
            # return value
        else:
            self.variable.value = self.value.evaluate()

    def __repr__(self):
        return "AssignmentDeclaration(variable=%r value=%r)" % (self.variable, self.value)


# Conditional Statement class
class ConditionalStatement(Term):
    def __init__(self, handler, _condition=None, _execution=None, reporter=None):
        super().__init__(handler, reporter=reporter)
        self._condition = _condition
        self._execution = _execution

    @property
    def condition(self) -> Term:
        return self._condition

    @condition.setter
    def condition(self, condition: Term):
        self._condition = condition

    @property
    def execution(self) -> list:
        return self._execution

    @execution.setter
    def execution(self, execution: list):
        self._execution = execution

    def evaluate(self):
        cond = self.condition.evaluate()
        if cond:
            for e in self.execution:
                e.evaluate()

    def __repr__(self):
        return "ConditionalStatement(%r, %r)" % (self.condition, self.execution)


# If Statement class
class IfStatement(ConditionalStatement):
    def __init__(self, handler, _condition=None, _execution=None, reporter=None):
        super().__init__(handler, _condition, _execution, reporter=reporter)

    def __repr__(self):
        return "IfStatement(%r, %r)" % (self.condition, self.execution)


# For Statement class
class ForStatement(Term):
    def __init__(self, handler, _variable=None, _collection=None, _execution=None, reporter=None):
        super().__init__(handler, reporter=reporter)
        self._variable = _variable
        self._collection = _collection
        self._execution = _execution

    @property
    def variable(self) -> Variable:
        return self._variable

    @variable.setter
    def variable(self, var: Variable):
        self._variable = var

    @property
    def collection(self):
        return self._collection

    @collection.setter
    def collection(self, _collection):
        self._collection = _collection

    @property
    def execution(self) -> list:
        return self._execution

    @execution.setter
    def execution(self, execution):
        self._execution = execution

    def apply(self, name, value):
        pass

    def evaluate(self):
        for x in self.collection.evaluate():
            self.variable.value = x
            for e in self.execution:
                e.evaluate()
        return None

    def __repr__(self):
        return "ForStatement(%r, %r, %r)" % (self.variable, self.collection, self.execution)


# While Statement class
class WhileStatement(ConditionalStatement):
    def __init__(self, handler, _condition=None, _execution=None, reporter=None):
        super().__init__(handler, _condition, _execution, reporter=reporter)

    def evaluate(self):
        while self.condition.evaluate():
            for e in self.execution:
                e.evaluate()
        return None

    def __repr__(self):
        return "WhileStatement(condition=%r, execution=%r)" % (self.condition, self.execution)


# Execution Statement class
class ExecutionStatement(Term):
    def __init__(self, handler, execution_steps=None, reporter=None):
        super().__init__(handler, reporter=reporter)
        self._execution_steps = execution_steps

    @property
    def execution_steps(self) -> list:
        return self._execution_steps

    @execution_steps.setter
    def execution_steps(self, execution_steps):
        self._execution_steps = execution_steps

    def apply(self, name, value):
        pass

    def evaluate(self):
        for s in self.execution_steps:
            s.evaluate()
        return None

    def __repr__(self):
        return "ExecutionStatement(%r)" % self.execution_steps


# Function Call class
class Function(Variable):
    def __init__(self, handler, name, reference=None, operator=None, assigner=None, arity=None, args=(), reporter=None):
        super().__init__(handler, name, reference, reporter=reporter)
        # self.report("Function(name:{})".format(name))
        self._operator = operator
        self._assigner = assigner
        self._arity = arity
        self._args = args

    @property
    def assigner(self):
        return self._assigner

    @assigner.setter
    def assigner(self, assigner):
        self._assigner = assigner

    @property
    def operator(self):
        return self._operator

    @operator.setter
    def operator(self, operator):
        self._operator = operator

    @property
    def arity(self):
        return self._arity

    @arity.setter
    def arity(self, arity):
        self._arity = arity

    @property
    def args(self):
        return self._args

    @args.setter
    def args(self, args):
        self._args = args

    def apply(self, name, value):
        pass

    def evaluate(self):
        if self.reference is not None:
            if self.arity is not None and self.arity != len(self.args):
                self.reporter.report("GraphCore Error: Argument number unmatched. {} expected {} got.".
                                     format(self.arity, len(self.args)))
                return None
            self.reference.args = self.args
            self.reference.evaluate()
        if self.arity == 0:
            self.reporter.report("Nullary operator is not supported")
            return None
        elif self.arity == 1:
            if len(self.args) != 1:
                self.reporter.report("Unary operator got 2 or more args")
                return None
            return self._operator(self.args[0].evaluate())
        else:
            idx = 0
            left_operand = self.args[idx].evaluate()
            idx += 1
            while idx < len(self.args):
                right_operand = self.args[idx].evaluate()
                left_operand = self._operator(left_operand, right_operand)
                idx += 1
            return left_operand

    def __repr__(self):
        return "Function(operator=%r, args=%r)" % (self.operator, self.args)


# Function Call class
class BuiltinFunction(Function):
    def __init__(self, handler, name, function, arity=None, args=(), reporter=None):
        super().__init__(handler, name, arity=arity, reporter=reporter)
        # self.report("BuiltinFunction(name:{})".format(name))
        self._function = function
        # self._arity = arity
        # self._args = args

    @property
    def function(self):
        return self._function

    def evaluate(self):
        args = []
        for a in self.args:
            args.append(a.evaluate())
        handler = self.handler
        if self.arity == 0:
            return handler.call(self.name, None)
        else:
            return handler.call(self.name, args)

    def __repr__(self):
        return "BuiltinFunction(name=%r, args=%r)" % (self.name, self.args)


# Print Function class
class PrintFunction(Function):
    def __init__(self, handler, reporter=None):
        super().__init__(handler, "print", reporter=reporter)

    def evaluate(self):
        if self.arity == 0:
            self.reporter.report("Nullary operator is not supported")
            return None
        else:
            idx = 0
            left_operand = str(self.args[idx].evaluate())
            idx += 1
            while idx < len(self.args):
                right_operand = str(self.args[idx].evaluate())
                left_operand = left_operand + " " + right_operand
                idx += 1
            self.report(left_operand)
            return left_operand

    def __repr__(self):
        return "print(args=%r)" % self.args()


# Graph Object class
class GraphObject(Term):
    def __init__(self, context, reporter=None):
        super().__init__(context, reporter=reporter)

    def evaluate(self, graph=None):
        return self.handler.context.graph

    def __repr__(self):
        return "Graph"  # % self.args()


# Nodes Object class
class NodesObject(Term):
    def __init__(self, handler, reporter=None):
        super().__init__(handler, reporter=reporter)

    def evaluate(self):
        nodes = []
        for n in self.handler.context.nodes:
            nodes.append(self.handler.context.nodes[n])
            # nodes.append(Constant(self.handler, n))
        return nodes

    def __repr__(self):
        return "Nodes"


# Edges Object class
class EdgesObject(Term):
    def __init__(self, context, reporter=None):
        super().__init__(context, reporter=reporter)

    def evaluate(self):
        edges = []
        for e in self.handler.context.edges:
            edges.append(Constant(self.handler, e))
        return edges

    def __repr__(self):
        return "Edges"
