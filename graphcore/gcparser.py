# -*- coding: utf-8 -*-

import ply.lex as lex
import ply.yacc as yacc
import sys
import traceback
from networkml.sentenceparser import SentenceParser


class GCParser(SentenceParser):

    def __init__(self):
        super().__init__(None)
        self.lexer = lex.lex(module=self)
        self.parser = yacc.yacc(module=self)

    def test(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok:
                break
            print(tok)

    def parse(self, text):
        result = self.parser.parse(text, lexer=self.lexer)
        return result

    def run(self, script):
        pass

