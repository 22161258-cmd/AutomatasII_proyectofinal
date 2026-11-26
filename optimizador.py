import re
from decimal import Decimal
from codigo_intermedio import Quad, Const
from interprete import BIN, UNA, ErrorEjecucion, Interprete

BINARIAS = set(BIN)
UNARIAS = set(UNA)
PURAS = (BINARIAS - {'/'}) | UNARIAS | {'='}
CONOCIDAS = BINARIAS | UNARIAS | {'=', 'LABEL', 'SALTA', 'SI_FALSO', 'FUNC', 'PARAM', 'CALL', 'RETORNAR'}
ERRORES_CALCULO = (ErrorEjecucion, ArithmeticError, TypeError, ValueError)


def _conocida(op):
    return op in CONOCIDAS or op.startswith(('MOSTRAR_', 'ALERTA_'))


def _es_temporal(n):
    return isinstance(n, str) and re.fullmatch(r't\d+', n) is not None


def _define(q):
    return q.res if (q.op in BINARIAS or q.op in UNARIAS or q.op in ('=', 'CALL')) else None


def _lee(q):
    if q.op in ('LABEL', 'SALTA', 'FUNC', 'CALL'):
        return []
    return [a for a in (q.arg1, q.arg2) if isinstance(a, str)]


def _es_pura(q):
    if q.op in PURAS:
        return True
    return q.op == '/' and isinstance(q.arg2, Const) and q.arg2.valor != 0


def _copia(q):
    return Quad(q.op, q.arg1, q.arg2, q.res)


def _firma(quads):
    return tuple((q.op, q.arg1, q.arg2, q.res) for q in quads)


def _const_de(v):
    if isinstance(v, bool):
        return Const(v, 'logico')
    if isinstance(v, int):
        return Const(v, 'entero')
    if isinstance(v, float):
        return Const(v, 'decimal')
    if isinstance(v, Decimal):
        return Const(v, 'decimal')
    return Const(v, 'texto')


def _es_num(c, n):
    return isinstance(c, Const) and c.tipo in ('entero', 'decimal') and c.valor == n


def _es_entero(c, n):
    return isinstance(c, Const) and c.tipo == 'entero' and c.valor == n


def _simplificar(q):
    op, a, b = q.op, q.arg1, q.arg2

    def asigna(x):
        return Quad('=', x, None, q.res)

    if op == 'SI_FALSO' and isinstance(a, Const):
        return None if a.valor else Quad('SALTA', None, None, q.res)
    if op in UNA and isinstance(a, Const):
        try:
            return asigna(_const_de(UNA[op](a.valor)))
        except ERRORES_CALCULO:
            return q
    if op in BIN and isinstance(a, Const) and isinstance(b, Const):
        try:
            return asigna(_const_de(BIN[op](a.valor, b.valor)))
        except ERRORES_CALCULO:
            return q
    if op == '+':
        if _es_entero(b, 0):
            return asigna(a)
        if _es_entero(a, 0):
            return asigna(b)
    elif op ==