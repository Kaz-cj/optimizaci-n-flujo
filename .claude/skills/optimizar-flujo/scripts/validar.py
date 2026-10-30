"""Valida un flujo.json y muestra las métricas calculadas.

Uso: python3 validar.py analisis/<slug>/flujo.json
Sale con código 1 si hay errores.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import modelo  # noqa: E402


def main():
    if len(sys.argv) != 2:
        sys.exit("Uso: python3 validar.py <ruta/flujo.json>")
    d = modelo.cargar(sys.argv[1])
    errores, advertencias = modelo.validar(d)
    advertencias += modelo.validar_carpeta(sys.argv[1])
    for e in errores:
        print(f"ERROR        {e}")
    for a in advertencias:
        print(f"ADVERTENCIA  {a}")
    if errores:
        print(f"\n{len(errores)} error(es). Corrige el JSON y vuelve a validar.")
        sys.exit(1)

    m = modelo.metricas(d)
    t = modelo.formato_tiempo
    print("OK: el flujo es válido.\n")
    print(f"Pasos           {m['pasos_actual']} → {m['pasos_optimizado']}"
          f"   (se van {m['se_va']}, quedan {m['queda']}, optimizables {m['optimizable']})")
    print(f"Ciclo por caso  {t(m['ciclo_actual_min'])} → {t(m['ciclo_optimizado_min'])}"
          f"   (-{m['reduccion_ciclo_pct']} %)")
    print(f"Trabajo         {t(m['trabajo_actual_min'])} → {t(m['trabajo_optimizado_min'])}")
    print(f"Traspasos       {m['traspasos_actual']} → {m['traspasos_optimizado']}")
    print(f"Automatizaciones propuestas: {m['automatizaciones']}")
    if m["hay_estimados"]:
        print("Nota: hay tiempos estimados; se señalan en el informe.")


if __name__ == "__main__":
    main()
