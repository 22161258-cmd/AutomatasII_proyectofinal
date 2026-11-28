import re
from decimal import Decimal, ROUND_HALF_UP
from codigo_intermedio import Const


class NoSoportadoAsm(NotImplementedError):
    pass


DEFINEN = {'=', '+', '-', '*', '/', '<', '>', '<=', '>=', '==', '!=', 'Y', 'O', 'NEG', 'NO',
           'ENT_A_DEC', 'DEC_A_ENT', 'ENT_A_TXT', 'DEC_A_TXT', 'LOG_A_TXT', 'CONCAT', 'CALL'}
SALIDAS = {f"{c}_{t}" for c in ('MOSTRAR', 'ALERTA') for t in ('ENT', 'DEC', 'LOG', 'TXT')}
SOPORTADAS = DEFINEN | SALIDAS | {'LABEL', 'SALTA', 'SI_FALSO', 'FUNC', 'PARAM', 'RETORNAR'}
INSTR = {'+': 'add', '-': 'sub', '*': 'imul', 'Y': 'and', 'O': 'or'}
SETCC = {'<': 'setl', '>': 'setg', '<=': 'setle', '>=': 'setge', '==': 'sete', '!=': 'setne'}
MIN32, MAX32 = -2 ** 31, 2 ** 31 - 1
REGS = ['ebx', 'esi', 'edi', 'ebp']
CC_INV = {'<': 'jge', '>': 'jle', '<=': 'jg', '>=': 'jl', '==': 'jne', '!=': 'je'}
BUF = 256


def centavos(valor):
    return int((Decimal(str(valor)) * 100).quantize(Decimal(1), rounding=ROUND_HALF_UP))


def _tipos(tabla, tipos_temp):
    t = dict(tipos_temp)
    for s in tabla.todos:
        if s.clase == 'categoria':
            t[f"{s.id_unico}.limite"] = t[f"{s.id_unico}.gastado"] = 'decimal'
            t[f"{s.id_unico}.nombre"] = 'texto'
        elif s.clase != 'funcion':
            t[s.id_unico] = s.tipo
    return t


def _leidos(q):
    if q.op in ('LABEL', 'SALTA', 'FUNC', 'CALL'):
        return []
    return [a for a in (q.arg1, q.arg2) if a is not None]


def _tipo(x, tipos):
    return x.tipo if isinstance(x, Const) else tipos[x]


def _validar(q, tipos):
    if q.op not in SOPORTADAS:
        raise NoSoportadoAsm(f"la operación {q.op} aún no tiene traducción a ensamblador: {q}")
    for x in _leidos(q) + ([q.res] if q.op in DEFINEN else []):
        if isinstance(x, Const) and x.tipo == 'entero' and not (MIN32 <= x.valor <= MAX32):
            raise NoSoportadoAsm(f"constante fuera del rango de 32 bits: {x}")
        if isinstance(x, Const) and x.tipo == 'decimal' and not (MIN32 <= centavos(x.valor) <= MAX32):
            raise NoSoportadoAsm(f"constante decimal fuera de rango (+-21 474 836.47): {x}")


def _etq(nombre):
    return "v_" + nombre.encode('utf-8').hex()


def _bytes(texto):
    datos = list(texto.encode('utf-8')) + [0]
    return ", ".join(str(b) for b in datos)


RUNTIME = """
print