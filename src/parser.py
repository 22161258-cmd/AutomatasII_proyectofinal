import ply.yacc as yacc
from lexer import tokens, construir_lexer
from errores import ERRORES
from ast_nodes import *

precedence = (
    ('left', 'O'),
    ('left', 'Y'),
    ('right', 'NO'),
    ('nonassoc', 'LT', 'GT', 'LE', 'GE', 'EQ', 'NE'),
    ('left', 'MAS', 'MENOS'),
    ('left', 'POR', 'DIV'),
    ('right', 'UMENOS'),
)
start = 'programa'


def p_programa(p):
    'programa : PRESUPUESTO STRING LBRACE sentencias RBRACE'
    p[0] = Programa(p[2], p[4], linea=p.lineno(1))


def p_sentencias(p):
    '''sentencias : sentencias sentencia
                  | empty'''
    p[0] = [] if len(p) == 2 else p[1] + [p[2]]


def p_empty(p):
    'empty :'
    pass


def p_sentencia(p):
    '''sentencia : declaracion
                 | asignacion
                 | categoria
                 | gasto
                 | condicional
                 | ciclo
                 | accion
                 | funcion
                 | retorno
                 | llamada_sent'''
    p[0] = p[1]


def p_tipo(p):
    '''tipo : T_ENTERO
            | T_DECIMAL
            | T_TEXTO
            | T_LOGICO'''
    p[0] = p[1]


def p_declaracion(p):
    '''declaracion : tipo ID SEMI
                   | tipo ID ASIGNA expr SEMI
                   | CONSTANTE tipo ID ASIGNA expr SEMI'''
    if p[1] == 'constante':
        p[0] = Declaracion(p[2], p[3], p[5], True, linea=p.lineno(3))
    elif len(p) == 4:
        p[0] = Declaracion(p[1], p[2], None, False, linea=p.lineno(2))
    else:
        p[0] = Declaracion(p[1], p[2], p[4], False, linea=p.lineno(2))


def p_asignacion(p):
    'asignacion : ID ASIGNA expr SEMI'
    p[0] = Asignacion(p[1], p[3], linea=p.lineno(1))


def p_categoria(p):
    'categoria : CATEGORIA ID LIMITE expr bloque'
    p[0] = Categoria(p[2], p[4], p[5], linea=p.lineno(1))


def p_gasto(p):
    'gasto : GASTO expr DESCRIPCION expr SEMI'
    p[0] = Gasto(p[2], p[4], linea=p.lineno(1))


def p_condicional(p):
    '''condicional : SI LPAREN expr RPAREN bloque
                   | SI LPAREN expr RPAREN bloque SINO bloque'''
    p[0] = Si(p[3], p[5], p[7] if len(p) == 8 else None, linea=p.lineno(1))


def p_ciclo(p):
    'ciclo : MIENTRAS LPAREN expr RPAREN bloque'
    p[0] = Mientras(p[3], p[5], linea=p.lineno(1))


def p_bloque(p):
    'bloque : LBRACE sentencias RBRACE'
    p[0] = p[2]


def p_accion(p):
    '''accion : ALERTA LPAREN expr RPAREN SEMI
              | MOSTRAR LPAREN expr RPAREN SEMI'''
    p[0] = Accion(p[1], p[3], linea=p.lineno(1))


def p_funcion(p):
    'funcion : FUNCION tipo ID LPAREN params RPAREN bloque'
    p