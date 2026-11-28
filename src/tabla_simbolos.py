import re

TAM = {'entero': 4, 'decimal': 8, 'texto': 4, 'logico': 4, 'categoria': 20}


class Simbolo:
    def __init__(self, nombre, clase, tipo, ambito, linea):
        self.nombre = nombre
        self.clase = clase
        self.tipo = tipo
        self.ambito = ambito
        self.linea = linea
        self.inicializado = False
        self.segmento = None
        self.offset = None
        self.id_unico = nombre
        self.params = []


class TablaSimbolos:
    def __init__(self):
        self.pila = [{}]
        self.todos = []
        self._ids = set()
        self._off = {'global': 0, 'local': 0}
        self.en_funcion = False

    @property
    def nivel(self):
        return len(self.pila) - 1

    def abrir_ambito(self):
        self.pila.append({})

    def cerrar_ambito(self):
        self.pila.pop()

    def iniciar_funcion(self):
        self.en_funcion = True
        self._off['local'] = 0

    def terminar_funcion(self):
        self.en_funcion = False

    def _id_unico(self, nombre):
        cand, n = nombre, 1
        while cand in self._ids or re.fullmatch(r"(?:t|L)\d+", cand):
            n += 1
            cand = f"{nombre}_{n}"
        self._ids.add(cand)
        return cand

    def insertar(self, nombre, clase, tipo, linea):
        if nombre in self.pila[-1]:
            return None
        s = Simbolo(nombre, clase, tipo, self.nivel, linea)
        s.id_unico = self._id_unico(nombre)
        if clase != 'funcion':
            seg = 'local' if self.en_funcion else 'global'
            s.segmento, s.offset = seg, self._off[seg]
            self._off[seg] += TAM[tipo]
        self.pila[-1][nombre] = s
        self.todos.append(s)
        return s

    def buscar(self, nombre):
        for ambito in reversed(self.pila):
            if nombre in ambito:
                return ambito[nombre]
        return None

    def como_texto(self):
        filas = [f"{'Nombre':<12}{'Id único':<12}{'Clase':<11}{'Tipo':<10}"
                 f"{'Ámbito':<8}{'Segmento':<10}{'Offset':<8}{'Línea'}"]
        filas.append('-' * 78)
        for s in self.todos:
            filas.append(f"{s.nombre:<12}{s.id_unico:<12}{s.clase:<11}{s.tipo:<10}"
                         f"{s.ambito:<8}{(s.segmento or '-'):<10}"
                         f"{('-' if s.offset is None else s.offset):<8}{s.linea}")
        return "\n".join(filas)