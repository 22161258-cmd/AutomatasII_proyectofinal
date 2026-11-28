import glob
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import os
os.chdir(ROOT)
from main import compilar
from errores import ERRORES
from interprete import Interprete
from pruebas_unitarias import ejecutar_todas
from codigo_objeto import generar_asm, NoSoportadoAsm
from ensamblar import ensamblar_y_correr, texto_esperado, HerramientasNoDisponibles


def correr(quads):
    return Interprete(quads).ejecutar()


def verificar_asm(r, opt, salida_ref):
    esperado = texto_esperado(salida_ref)
    try:
        for quads, regs in ((r.quads, True), (opt, True), (r.quads, False)):
            if ensamblar_y_correr(generar_asm(quads, r.tabla, r.tipos_temp, registros=regs)) != esperado:
                return False, f" | asm: ¡SALIDA DISTINTA! ({'con' if regs else 'sin'} registros)"
        return True, " | asm: ok (registros y memoria)"
    except NoSoportadoAsm:
        return True, " | asm: pendiente"
    except HerramientasNoDisponibles:
        return True, " | asm: omitido (sin nasm/ld)"


def main():
    fallos = ejecutar_todas()
    for ruta in sorted(glob.glob("tests/*/*.top")):
        carpeta = ruta.split("/")[1] if "/" in ruta else ruta.split("\\")[1]
        texto = open(ruta, encoding="utf-8").read()
        try:
            nombre = Path(ruta).name
            if carpeta == "semantic" or nombre in {"lexico.top", "sintactico.top"}:
                compilar(texto)
                tipos = {error[0] for error in ERRORES.lista}
                esperado = {
                    "lexico.top": "léxico",
                    "sintactico.top": "sintáctico",
                }.get(nombre)
                ok = ERRORES.hay() and (esperado is None or esperado in tipos)
                detalle = f"{len(ERRORES.lista)} error(es) detectados"
            else:
                r = compilar(texto, usar_opt=False)
                if not r.ok:
                    ok, detalle = False, ERRORES.reporte()
                else:
                    base = correr(r.quads)
                    opt = compilar(texto, usar_opt=True).quads_opt
                    ok = base == correr(opt)
                    detalle = f"instrucciones {len(r.quads)} -> {len(opt)}" + ("" if ok else "  ¡LA SALIDA CAMBIÓ!")
                    ok_asm, det_asm = verificar_asm(r, opt, base)
                    ok, detalle = ok and ok_asm, detalle + det_asm
        except NotImplementedError as e:
            ok, detalle = False, f"pendiente: {e}"
        fallos += 0 if ok else 1
        print(f"[{'OK ' if ok else 'FALLA'}] {ruta:<48} {detalle}")
    print(f"\n{'Todas las pruebas pasaron' if not fallos else str(fallos) + ' prueba(s) con fallas'}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
