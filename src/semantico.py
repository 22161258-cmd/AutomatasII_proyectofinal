from ast_nodes import *
from tabla_simbolos import TablaSimbolos

NUM = ('entero', 'decimal')
ATRIBUTOS = {'limite': 'decimal', 'gastado': 'decimal', 'nombre': 'texto'}


def tiene_retorno(stmts):
    for s in stmts:
        if isinstance(s, Retornar):
            return True
        if isinstance(s, Si) and (tiene_retorno(s.entonces) or (s.sino and tiene_retorno(s.sino))):
            return True
        if isinstance(s, Mientras) and tiene_retorno(s.cuerpo):
            return True
    return False


class Semantico:
    def __init__(self, errores):
        self.err = errores
        self.tabla = TablaSimbolos()
        self.cats = []
        self.funcs = []

    def error(self, linea, msg):
        self.err.add('semántico', linea, msg)

    def analizar(self, prog):
        for s in prog.sentencias:
            self.stmt(s)
        return self.tabla

    def stmt(self, n):
        getattr(self, 'v_' + type(n).__name__)(n)

    def bloque(self, lista):
        self.tabla.abrir_ambito()
        for s in lista:
            self.stmt(s)
        self.tabla.cerrar_ambito()

    def expr(self, n):
        n.tipo = getattr(self, 'e_' + type(n).__name__)(n)
        return n.tipo

    def coercion(self, nodo, destino):
        if nodo.tipo is None or nodo.tipo == destino:
            return nodo
        c = Conversion(destino, nodo, linea=nodo.linea)
        c.origen, c.tipo = nodo.tipo, destino
        return c

    def compat(self, destino, nodo, linea, ctx):
        t = nodo.tipo
        if t is None or t == destino:
            return nodo
        if destino == 'decimal' and t == 'entero':
            return self.coercion(nodo, 'decimal')
        self.error(linea, f"tipos incompatibles en {ctx}: no se puede asignar {t} a {destino}")
        return nodo

    def condicion(self, nodo, linea, que):
        t = self.expr(nodo)
        if t is not None and t != 'logico':
            self.error(linea, f"la condición de '{que}' debe ser lógica, no {t}")

    def e_Literal(self, n):
        return n.tipo

    def e_Variable(self, n):
        s = self.tabla.buscar(n.nombre)
        if s is None:
            self.error(n.linea, f"variable '{n.nombre}' no declarada en este ámbito")
            return None
        if s.clase in ('funcion', 'categoria'):
            self.error(n.linea, f"'{n.nombre}' es una {s.clase}, no una variable")
            return None
        n.simbolo = s
        return s.tipo

    def e_Acceso(self, n):
        s = self.tabla.buscar(n.obj)
        if s is None or s.clase != 'categoria':
            self.error(n.linea, f"'{n.obj}' no es una categoría declarada")
            return None
        if n.attr not in ATRIBUTOS:
            self.error(n.linea, f"la categoría '{n.obj}' no tiene el atributo '{n.attr}'")
            return None
        n.simbolo = s
        return ATRIBUTOS[n.attr]

    def e_Unario(self, n):
        t = self.expr(n