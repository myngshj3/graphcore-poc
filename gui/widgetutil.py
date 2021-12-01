# -*- coding: utf-8 -*-

from graphcore.shell import GraphCoreContextHandler, GraphCoreAsyncContextHandler
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget


class GraphCoreContextHandlerInterface:
    # def __init__(self, handler=None, async_handler=None):
    #     self._handler = handler
    #     self._async_handler = async_handler
    #
    @property
    def handler(self) -> GraphCoreContextHandler:
        return self._handler

    @handler.setter
    def handler(self, handler: GraphCoreContextHandler):
        self._handler = handler

    @property
    def async_handler(self) -> GraphCoreAsyncContextHandler:
        return self._async_handler

    @async_handler.setter
    def async_handler(self, async_handler: GraphCoreAsyncContextHandler):
        self._async_handler = async_handler

    def set_handler_pair(self, handler: GraphCoreContextHandler, async_handler: GraphCoreAsyncContextHandler):
        self.handler = handler
        self.async_handler = async_handler


# GraphCore Reporter class
class GraphCoreReportInterface:
    def __init__(self, reporter=None):
        self._reporters = []
        if reporter is not None:
            self.reporters.append(reporter)

    @property
    def reporters(self) -> list:
        return self._reporters

    def report(self, expression):
        for r in self.reporters:
            r.report(expression)

    def __call__(self, x):
        self.report(x)


class GraphCoreReporterUser(GraphCoreReportInterface):
    def __init__(self, reporter=None):
        super().__init__(reporter=reporter)

