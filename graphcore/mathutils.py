
import numpy as np
from networkml.network import NetworkClass
from networkml.network import NetworkClassInstance
from networkml.network import ExtensibleWrappedAccessor


def math_handler_class(meta: NetworkClass):
    clazz: NetworkClassInstance = meta(meta, ("MathHandler", (), ()))
    m = ExtensibleWrappedAccessor(clazz, "attributes", clazz, lambda ao,c,eo,ca,ea:ao.dump_attributes())
    clazz.register_method(clazz, m.signature, m, depth=0)
    clazz.accessor.set(clazz, "pi", np.pi)
    m = ExtensibleWrappedAccessor(clazz, "sqrt", None, lambda ao,c,eo,ca,ea:np.sqrt(ca[0]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "pow", None, lambda ao,c,eo,ca,ea:np.power(ca[0],ca[1]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "sin", None, lambda ao,c,eo,ca,ea:np.sin(ca[0]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "cos", None, lambda ao,c,eo,ca,ea:np.cos(ca[0]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "tan", None, lambda ao,c,eo,ca,ea:np.tan(ca[0]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "arcsin", None, lambda ao,c,eo,ca,ea:np.arcsin(ca[0]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "arccos", None, lambda ao,c,eo,ca,ea:np.arccos(ca[0]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "arctan", None, lambda ao,c,eo,ca,ea:np.arctan(ca[0]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "exp", None, lambda ao,c,eo,ca,ea:np.exp(ca[0]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "log", None, lambda ao,c,eo,ca,ea:np.log(ca[0]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "log2", None, lambda ao,c,eo,ca,ea:np.log2(ca[0]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "log10", None, lambda ao,c,eo,ca,ea:np.log10(ca[0]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "uniform", None, lambda ao,c,eo,ca,ea:np.random.uniform(ca[0],ca[1]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "normal", None, lambda ao,c,eo,ca,ea:np.random.normal(ca[0],ca[1],ca[2]))
    clazz.register_method(clazz, m.signature, m, depth=0)
    m = ExtensibleWrappedAccessor(clazz, "std_normal", None, lambda ao,c,eo,ca,ea:np.random.standard_normal(ca[0]))
    clazz.register_method(clazz, m.signature, m)
    return clazz