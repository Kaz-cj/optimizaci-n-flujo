"""Genera el artefacto interactivo (HTML) desde flujo.json.

Uso: python3 construir_artefacto.py analisis/<slug>/flujo.json
Escribe flujo.html junto al JSON. Luego se publica con la herramienta Artifact.
"""
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import modelo  # noqa: E402

PLANTILLA = Path(__file__).parent.parent / "plantilla" / "flujo.html"


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 construir_artefacto.py <ruta/flujo.json>")
    ruta = Path(sys.argv[1])
    d = modelo.cargar(ruta)
    errores, _ = modelo.validar(d)
    if errores:
        print("\n".join(errores))
        sys.exit("El flujo tiene errores; corre validar.py y corrígelos primero.")

    paquete = json.dumps(modelo.paquete(d), ensure_ascii=False)
    # Evita que el contenido cierre la etiqueta <script> antes de tiempo
    paquete = paquete.replace("</", "<\\/")
    salida = (PLANTILLA.read_text(encoding="utf-8")
              .replace("__TITULO__", html.escape(d["proceso"]["nombre"]))
              .replace("__PAQUETE__", paquete))
    destino = ruta.with_name("flujo.html")
    destino.write_text(salida, encoding="utf-8")
    print(destino.resolve())


if __name__ == "__main__":
    main()
