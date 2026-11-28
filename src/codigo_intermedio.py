from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import re
from ast_nodes import *


@dataclass(frozen=True)
class Const:
    valor: object
    tipo: str

    def __post_init__(self):
        if self.tipo == 'decimal':
            valor = self.valor if isinstance(self.valor, Decimal) else Decimal(str(self.valor))
            object.__setattr__(self, 'valor', valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))

    def __repr__(self):
        if self.tipo == 'texto':
            return f'"{self.valor}"'
        if self.tipo == 'logico':
            return 'verdadero' if self.valor else 'falso'
        if self.tipo == 'decimal':
            return format(self.valor, '.2f')
        return repr(self.valor)


class Quad:
    def __init__(self, op, arg1=None, arg2=None, res=None):
        self.op, self.arg1, self.arg2, self.res = op, arg1, arg2, res

    def __repr__(self):
        f = lambda x: '_' if x is None else repr(x) if isinstance(x, Const) else str(x)
        return f"({self.op}, {f(self.arg1)}, {f(self.arg2)}, {f(self.res)})"


@dataclass(frozen=True)
class Tripleta:
    op: str
    arg1: object = None
    arg2: object = None


def convertir_a_tripletas(quads):
    posiciones = {
        q.res: i for i, q in enumerate(quads)
        if isinstance(q.res, str) and re.fullmatch(r't\d+', q.res)
    }

    def resolver(x):
        if isinstance(x, str) and x in posiciones:
            return f'({posiciones[x]})'
        return x

    out = []
    for q in quads:
        if q.op == '=':
            out.append(Tripleta(q.op, q.res, resolver(q.arg1)))
        elif q.op == 'SI_FALSO':
            out.append(Tripleta(q.op, resolver(q.arg1), q.res))
        elif q.op in ('LABEL', 'SALTA'):
            out.append(Tripleta(q.op, q.res, None))
        elif q.op == 'FUNC':
            out.append(Tripleta(q.op, (q.arg1, q.arg2), q.res))
        else:
            out.append(Tripleta(q.op, resolver(q.arg1), resolver(q.arg2)))
    return out


def formatear_tripletas(quads):
    def formato(x):
        if x is None:
            return '_'
        if isinstance(x, Const):
            return repr(x)
        if isinstance(x, tuple):
            return '(' + ', '.join(formato(v) for v in x) + ')'
        return str(x)

    tripletas = convertir_a_tripletas(quads)
    return '\n'.join(
        f"({i}) ({t.op}, {formato(t.arg1)}, {formato(t.arg2)})"
        for i, t in enumerate(tripletas)
    )


def formatear(quads):
    return "\n".join(f"{i + 1:>3}  {q}" for i, q in enumerate(quads))


CONV = {('entero', 'decimal'): 'ENT_A_DEC', ('entero', 'texto'): 'ENT_A_TXT',
        ('decimal', 'texto'): 'DEC_A_TXT', ('logico', 'texto'): 'LOG_A_TXT'}
ABREV = {'entero': 'ENT', 'decimal': 'DEC', 'texto': 'TXT', 'logico': 'LOG'}
DEFECTO = {'entero': Const(0, 'entero'), 'decimal': Const(0.0, 'decimal'),
           'texto': Const('', 'texto'), 'logico': Const(False, 'logico')}
OPS = {'y': 'Y', 'o': 'O'}


def _declaradas(stmts):
    out = []
    for s in stmts:
        if isinstance(s, Declaracion) and s.simbolo is not None:
            out.append(s.simbolo.id_unico)
        elif isinstance(s, Si):
            out += _declaradas(s.entonces) + _declaradas(s.sino or [])
        elif isinstance(s, Mientras):
            out += _declaradas(s.cuerpo)
    return out


class GeneradorCI:
    def __init__(self):
        self.quads = []
        self.tipos_temp = {}
        self._t = 0
        self._l = 0

    def nueva_temp(self, tipo):
        self._t += 1
        t = f"t{self._t}"
        self.tipos_temp[t] = tipo
        return t

    def nueva_etiqueta(self):
        self._l += 1
        return f"L{self._l}"

    def emitir(self, op, a1=None, a2=None, res=None):
        self.quads.append