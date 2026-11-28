from codigo_intermedio import Const
from decimal import Decimal, ROUND_HALF_UP


class ErrorEjecucion(Exception):
    pass


MIN32, MAX32 = -(2 ** 31), 2 ** 31 - 1


def _entero_32(valor):
    valor = int(valor) & 0xFFFFFFFF
    return valor - 0x100000000 if valor >= 0x80000000 else valor


def _div(a, b):
    if b == 0:
        raise ErrorEjecucion("división entre cero")
    return _decimal_centavos(a / b)


def _decimal_centavos(valor):
    if isinstance(valor, Decimal):
        valor = valor.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        return Decimal('0.00') if valor == 0 else valor
    return valor


def _aritmetica_32(op, a, b):
    valor = _decimal_centavos(op(a, b))
    return _entero_32(valor) if isinstance(valor, int) and not isinstance(valor, bool) else valor


def _neg_32(a):
    valor = _decimal_centavos(-a)
    return _entero_32(valor) if isinstance(valor, int) and not isinstance(valor, bool) else valor


BIN = {
    '+': lambda a, b: _aritmetica_32(lambda x, y: x + y, a, b),
    '-': lambda a, b: _aritmetica_32(lambda x, y: x - y, a, b),
    '*': lambda a, b: _aritmetica_32(lambda x, y: x * y, a, b), '/': _div,
    '<': lambda a, b: a < b, '>': lambda a, b: a > b, '<=': lambda a, b: a <= b,
    '>=': lambda a, b: a >= b, '==': lambda a, b: a == b, '!=': lambda a, b: a != b,
    'Y': lambda a, b: a and b, 'O': lambda a, b: a or b, 'CONCAT': lambda a, b: a + b,
}
UNA = {
    'NEG': _neg_32, 'NO': lambda a: not a,
    'ENT_A_DEC': lambda a: Decimal(a).quantize(Decimal('0.01')),
    'DEC_A_ENT': int, 'ENT_A_TXT': str,
    'DEC_A_TXT': lambda a: f"{a:.2f}", 'LOG_A_TXT': lambda a: 'verdadero' if a else 'falso',
}


def formato(v, sufijo):
    if sufijo == 'DEC':
        return f"{v:.2f}"
    if sufijo == 'LOG':
        return 'verdadero' if v else 'falso'
    return str(v)


class Memoria(dict):
    escrituras = 0

    def __setitem__(self, clave, valor):
        self.escrituras += 1
        super().__setitem__(clave, valor)


class Interprete:
    def __init__(self, quads, max_pasos=1_000_000, max_pila=2_000, al_emitir=None):
        self.quads, self.max_pasos, self.max_pila, self.mem = quads, max_pasos, max_pila, Memoria()
        self.al_emitir = al_emitir
        self.pasos = 0
        self.lecturas = 0

    def val(self, a):
        if isinstance(a, Const):
            return a.valor
        self.lecturas += 1
        if a not in self.mem:
            raise ErrorEjecucion(f"'{a}' no tiene valor asignado")
        return self.mem[a]

    def ejecutar(self):
        etiquetas = {q.res: i for i, q in enumerate(self.quads) if q.op == 'LABEL'}
        funciones = {q.arg1: i for i, q in enumerate(self.quads) if q.op == 'FUNC'}
        salida, pc, pasos = [], 0, 0
        args, pila = [], []
        while pc < len(self.quads):
            q = self.quads[pc]
            pc += 1
            pasos += 1
            if pasos > self.max_pasos:
                raise ErrorEjecucion("se excedió el máximo de pasos (¿ciclo infinito?)")
            op = q.op
            if op in ('LABEL', 'FUNC'):
                pasos -= 1