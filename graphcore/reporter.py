# -*- coding: utf-8 -*-

import traceback


# GraphCore Reporter class
class GraphCoreReporter:
    def __init__(self, report=None):
        self._report_func = report

    def report(self, expression):
        if self._report_func is None:
            print(expression)
        else:
            self._report_func(expression)

    def __call__(self, *args, **kwargs):
        self.report(" ".join([str(_) for _ in args]))

    @property
    def report_func(self):
        return self._report_func

    @report_func.setter
    def report_func(self, func):
        self._report_func = func


