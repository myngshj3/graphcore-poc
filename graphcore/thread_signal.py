# GraphCore Shell Thread Signal class
class GraphCoreThreadSignal:
    def __init__(self, sig, data, func=None, args=None):
        self._sig = sig
        self._data = data
        self._func = func
        self._args = args
        self._result = None

    @property
    def signal(self):
        return self._sig

    @property
    def data(self):
        return self._data

    @property
    def func(self):
        return self._func

    @property
    def args(self):
        return self._args

    @property
    def result(self):        return self._result

    @result.setter
    def result(self, _result):
        self._result = _result

