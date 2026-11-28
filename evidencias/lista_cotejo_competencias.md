# Lista de Cotejo de Competencias Desarrolladas — Lenguajes y Autómatas II

**Proyecto:** TopScript (DSL y compilador/máquina virtual para presupuestos personales)
**Asignatura:** Lenguajes y Autómatas II
**Repositorio:** `AutomatasII_proyectofinal`

## 1. Diseño del Lenguaje y Análisis Léxico-Sintáctico
- [ ] **Definición formal del lenguaje (DSL):** Palabras clave, literales, operadores y estructura de archivos `.top`. *Evidencia:* `README.md`, `ejemplos/*.top`
- [ ] **Análisis léxico (`src/lexer.py`):** Reconocimiento de tokens y manejo de errores/codificación (`ejemplos/prueba_bom.top`). *Evidencia:* `src/lexer.py`
- [ ] **Análisis sintáctico y AST (`src/parser.py`, `src/ast_nodes.py`):** Gramática y construcción del AST. *Evidencia:* `src/parser.py`, `src/ast_nodes.py`
- [ ] **Manejo de errores (`src/errores.py`):** Diagnóstico de errores léxicos/sintácticos. *Evidencia:* `src/errores.py`

## 2. Análisis Semántico y Tabla de Símbolos
- [ ] **Tabla de símbolos y ámbitos (`src/tabla_simbolos.py`):** Control de identificadores, tipos y alcances. *Evidencia:* `src/tabla_simbolos.py`, `tests/semantic/errores_ambitos.top`
- [ ] **Análisis semántico (`src/semantico.py`):** Validación de tipos y reglas semánticas. *Evidencia:* `src/semantico.py`, `tests/semantic/errores_tipos.top`

## 3. Código Intermedio, Optimización y Ejecución
- [ ] **Código intermedio y notaciones (`src/codigo_intermedio.py`, `src/notaciones.py`):** Generación de código intermedio y notaciones. *Evidencia:* `src/codigo_intermedio.py`, `src/notaciones.py`, `tests/intermediate/*.top`
- [ ] **Optimización (`src/optimizador.py`):** Reducción de redundancias, invariantes o constantes. *Evidencia:* `src/optimizador.py`, `tests/intermediate/redundante.top`, `tests/intermediate/invariante.top`
- [ ] **Código objeto e intérprete (`src/codigo_objeto.py`, `src/ensamblar.py`, `src/interprete.py`):** Generación/ensamblado y ejecución en VM. *Evidencia:* `src/codigo_objeto.py`, `src/ensamblar.py`, `src/interprete.py`, `tests/execution/*.top`

## 4. Pruebas, Control de Versiones y Portafolio
- [ ] **Pruebas (`tests/`):** Scripts y casos de prueba por categoría. *Evidencia:* `tests/run_tests.py`, `tests/pruebas_unitarias.py`, `tests/`
- [ ] **Control de versiones y portafolio (`evidencias/`):** Historial en Git, `.gitignore`, reportes de práctica, matriz de valoración y lista de cotejo. *Evidencia:* `.gitignore`, `evidencias/`
