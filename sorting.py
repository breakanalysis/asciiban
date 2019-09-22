from sly import Lexer, Parser
from datetime import datetime
from constants import *
from settings import get_board_settings

class CalcLexer(Lexer):
    tokens = { FIELD, NUMBER, PLUS, TIMES, MINUS, DIVIDE, LPAREN, RPAREN }
    ignore = ' \t'

    # Tokens
    FIELD = r'[a-zA-Z_][a-zA-Z0-9_]*'
    NUMBER = r'\d+'

    # Special symbols
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'
    LPAREN = r'\('
    RPAREN = r'\)'

    # Ignored pattern
    ignore_newline = r'\n+'

    # Extra action for newlines
    def ignore_newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        print("Illegal character '%s'" % t.value[0])
        self.index += 1

class CalcParser(Parser):
    tokens = CalcLexer.tokens

    precedence = (
        ('left', PLUS, MINUS),
        ('left', TIMES, DIVIDE),
        ('right', UMINUS),
        )

    def __init__(self, issue):
        self.names = { }
        self.issue = issue
        settings = get_board_settings()
        self.custom_fields = settings[CUSTOM_FIELDS]
        self.sorting_expr = settings[BACKLOG_SORTING]

    @_('expr')
    def statement(self, p):
        return p.expr

    @_('expr PLUS expr')
    def expr(self, p):
        return p.expr0 + p.expr1

    @_('expr MINUS expr')
    def expr(self, p):
        return p.expr0 - p.expr1

    @_('expr TIMES expr')
    def expr(self, p):
        return p.expr0 * p.expr1

    @_('expr DIVIDE expr')
    def expr(self, p):
        return p.expr0 / p.expr1

    @_('MINUS expr %prec UMINUS')
    def expr(self, p):
        return -p.expr

    @_('LPAREN expr RPAREN')
    def expr(self, p):
        return p.expr

    @_('NUMBER')
    def expr(self, p):
        return int(p.NUMBER)

    @_('FIELD')
    def expr(self, p):
        if p.FIELD in self.issue:
            value = self.issue[p.FIELD]
            if isinstance(value, datetime):
                return (value.date() - datetime.now().date()).days
            return value
        elif p.FIELD in self.custom_fields:
            return self.custom_fields[p.FIELD]
        else:
            return 0

    def error(self, t):
        raise Exception(f"Unexpected token: {t} in {self.sorting_expr}")

def get_sort_value(issue):
    lexer = CalcLexer()
    parser = CalcParser(issue)
    tokens = lexer.tokenize(parser.sorting_expr)
    return parser.parse(tokens)
