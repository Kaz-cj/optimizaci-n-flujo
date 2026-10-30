"""Cierra un análisis: guarda una copia versionada del flujo.json en historial/.

Uso: python3 cerrar_analisis.py analisis/<slug>/flujo.json
Crea analisis/<slug>/historial/v<version>.json (la versión sale de proceso.version).
Si esa versión ya existe y el contenido cambió, se niega: sube proceso.version.
"""
import filecmp
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import modelo  # noqa: E402


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 cerrar_analisis.py <ruta/flujo.json>")
    ruta = Path(sys.argv[1])
    d = modelo.cargar(ruta)
    errores, _ = modelo.validar(d)
    if errores:
        print("\n".join(errores))
        sys.exit("El flujo tiene errores; no se cierra.")
    version = str(d["proceso"].get("version") or "1.0")
    carpeta = ruta.parent / "historial"
    carpeta.mkdir(exist_ok=True)
    destino = carpeta / f"v{version}.json"
    if destino.exists() and not filecmp.cmp(ruta, destino, shallow=False):
        sys.exit(f"Ya existe {destino} con otro contenido. Sube proceso.version "
                 f"(por ejemplo a {_siguiente(version)}) y vuelve a cerrar.")
    shutil.copyfile(ruta, destino)
    previas = sorted(p.name for p in carpeta.glob("v*.json"))
    print(destino.resolve())
    print("Versiones en historial:", ", ".join(previas))


def _siguiente(v):
    partes = v.split(".")
    try:
        partes[-1] = str(int(partes[-1]) + 1)
    except ValueError:
        return v + ".1"
    return ".".join(partes)


if __name__ == "__main__":
    main()
