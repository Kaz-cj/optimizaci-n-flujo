"""Pruebas de la lógica central (vista optimizada, métricas, validación, diagrama).

Uso: python3 test_modelo.py        (desde cualquier carpeta)
Sale con código 1 si alguna prueba falla. Córrelas antes de cambiar los scripts.
"""
import copy
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import modelo  # noqa: E402

EJEMPLO = Path(__file__).parent.parent / "ejemplo" / "flujo.json"


def base():
    """Flujo mínimo válido: inicio → A → B → fin, dos roles."""
    return {
        "proceso": {"nombre": "Prueba"},
        "roles": [{"id": "u", "nombre": "Usuario", "tipo": "externo"},
                  {"id": "r", "nombre": "Rol", "tipo": "persona"},
                  {"id": "s", "nombre": "Sistema", "tipo": "sistema"}],
        "pasos": [
            {"id": "P01", "nombre": "Inicio", "rol": "u", "tipo": "inicio", "columna": 1, "estado": "queda", "fuente": "usuario"},
            {"id": "P02", "nombre": "A", "rol": "r", "tipo": "tarea", "columna": 2, "estado": "queda", "fuente": "usuario",
             "tiempo_min": 10, "espera_min": 50},
            {"id": "P03", "nombre": "B", "rol": "r", "tipo": "tarea", "columna": 3, "estado": "queda", "fuente": "usuario",
             "tiempo_min": 20, "espera_min": 100},
            {"id": "P04", "nombre": "Fin", "rol": "u", "tipo": "fin", "columna": 4, "estado": "queda", "fuente": "usuario"},
        ],
        "conexiones": [{"de": "P01", "a": "P02"}, {"de": "P02", "a": "P03"}, {"de": "P03", "a": "P04"}],
    }


def hallazgo(ahorro=0):
    return {"categoria": "x", "problema": "p", "propuesta": "q", "impacto": "alto", "esfuerzo": "bajo", "ahorro_min": ahorro}


def paso(d, pid):
    return next(p for p in d["pasos"] if p["id"] == pid)


PRUEBAS = []


def prueba(f):
    PRUEBAS.append(f)
    return f


@prueba
def flujo_base_es_valido():
    err, _ = modelo.validar(base())
    assert err == [], err
    m = modelo.metricas(base())
    assert m["pasos_actual"] == 4 and m["ciclo_actual_min"] == 180, m


@prueba
def paso_rojo_desaparece_y_se_reconecta():
    d = base()
    paso(d, "P02").update(estado="se_va", hallazgo=hallazgo(60))
    opt = modelo.vista_optimizada(d)
    ids = [p["id"] for p in opt["pasos"]]
    assert ids == ["P01", "P03", "P04"], ids
    assert {"de": "P01", "a": "P03", "etiqueta": None} in opt["conexiones"], opt["conexiones"]
    assert [p["columna"] for p in opt["pasos"]] == [1, 2, 3], "las columnas deben compactarse"
    m = modelo.metricas(d)
    assert m["ciclo_optimizado_min"] == 120 and m["se_va"] == 1


@prueba
def dos_rojos_seguidos_se_saltan_ambos():
    d = base()
    paso(d, "P02").update(estado="se_va", hallazgo=hallazgo())
    paso(d, "P03").update(estado="se_va", hallazgo=hallazgo())
    opt = modelo.vista_optimizada(d)
    assert [p["id"] for p in opt["pasos"]] == ["P01", "P04"]
    assert opt["conexiones"] == [{"de": "P01", "a": "P04", "etiqueta": None}], opt["conexiones"]


@prueba
def automatizacion_cambia_carril_nombre_y_tiempos():
    d = base()
    paso(d, "P02").update(estado="optimizable", hallazgo=hallazgo(55),
                          automatizacion={"tipo": "Regla de negocio", "descripcion": "d", "nombre_nuevo": "A auto",
                                          "rol_nuevo": "s", "tiempo_nuevo_min": 1, "espera_nueva_min": 0})
    opt = modelo.vista_optimizada(d)
    q = next(p for p in opt["pasos"] if p["id"] == "P02")
    assert q["nombre"] == "A auto" and q["rol"] == "s" and (q["tiempo_min"], q["espera_min"]) == (1, 0)
    m = modelo.metricas(d)
    assert m["ciclo_optimizado_min"] == 121 and m["automatizaciones"] == 1
    assert m["traspasos_optimizado"] == 3  # u→s, s→r, r→u


@prueba
def optimizable_sin_automatizacion_descuenta_ahorro_de_la_espera():
    d = base()
    paso(d, "P03").update(estado="optimizable", hallazgo=hallazgo(110))
    t, e = modelo.tiempos_optimizados(paso(d, "P03"))
    assert (t, e) == (10, 0), (t, e)  # 100 de espera y 10 de trabajo


@prueba
def decision_toma_la_rama_mas_larga():
    d = base()
    d["pasos"][2:2] = [
        {"id": "P05", "nombre": "¿Ok?", "rol": "r", "tipo": "decision", "columna": 3, "estado": "queda", "fuente": "usuario",
         "tiempo_min": 5, "espera_min": 0},
        {"id": "P06", "nombre": "Rama larga", "rol": "s", "tipo": "tarea", "columna": 4, "estado": "queda", "fuente": "usuario",
         "tiempo_min": 0, "espera_min": 1000},
    ]
    paso(d, "P03")["columna"] = 5
    paso(d, "P04")["columna"] = 6
    d["conexiones"] = [{"de": "P01", "a": "P02"}, {"de": "P02", "a": "P05"},
                       {"de": "P05", "a": "P06", "etiqueta": "Sí"}, {"de": "P05", "a": "P03", "etiqueta": "No"},
                       {"de": "P06", "a": "P03"}, {"de": "P03", "a": "P04"}]
    err, _ = modelo.validar(d)
    assert err == [], err
    assert modelo.metricas(d)["ciclo_actual_min"] == 60 + 5 + 1000 + 120


@prueba
def retorno_por_reproceso_no_cuenta_como_ciclo():
    d = base()
    d["conexiones"].append({"de": "P03", "a": "P02", "etiqueta": "Devuelto"})
    paso(d, "P03")["tipo"] = "decision"
    d["conexiones"][2]["etiqueta"] = "Ok"
    err, _ = modelo.validar(d)
    assert err == [], err
    assert modelo.metricas(d)["ciclo_actual_min"] == 180
    lay = modelo.diagramar(d, modelo.vista_actual(d))
    assert any(f["retorno"] for f in lay["flechas"])


@prueba
def ahorro_mayor_al_tiempo_es_error():
    d = base()
    paso(d, "P02").update(estado="se_va", hallazgo=hallazgo(61))
    err, _ = modelo.validar(d)
    assert any("R-04" in e for e in err), err


@prueba
def paso_sin_fuente_o_estimado_inconsistente_es_error():
    d = base()
    del paso(d, "P02")["fuente"]
    err, _ = modelo.validar(d)
    assert any("P02" in e and "fuente" in e for e in err), err
    d = base()
    paso(d, "P02")["estimado"] = True            # sin fuente estimado_autorizado
    err, _ = modelo.validar(d)
    assert any("P02" in e and "R-01" in e for e in err), err
    paso(d, "P02")["fuente"] = "estimado_autorizado"
    err, _ = modelo.validar(d)
    assert err == [], err


@prueba
def rojo_sin_hallazgo_y_decision_sin_etiquetas_son_error():
    d = base()
    paso(d, "P02")["estado"] = "se_va"
    err, _ = modelo.validar(d)
    assert any("P02" in e and "hallazgo" in e for e in err), err
    d = base()
    paso(d, "P02")["tipo"] = "decision"
    err, _ = modelo.validar(d)
    assert any("P02" in e and "salidas" in e for e in err), err


@prueba
def choque_de_celda_en_vista_optimizada_es_error():
    d = base()
    # Al automatizar P02 hacia el sistema, choca con otro paso del sistema en la misma columna
    d["pasos"].insert(2, {"id": "P09", "nombre": "S", "rol": "s", "tipo": "tarea", "columna": 2, "estado": "queda",
                          "fuente": "usuario", "tiempo_min": 1, "espera_min": 0})
    d["conexiones"] = [{"de": "P01", "a": "P02"}, {"de": "P01", "a": "P09"}, {"de": "P02", "a": "P03"},
                       {"de": "P09", "a": "P03"}, {"de": "P03", "a": "P04"}]
    err, _ = modelo.validar(d)
    assert err == [], err
    paso(d, "P02").update(estado="optimizable", hallazgo=hallazgo(),
                          automatizacion={"tipo": "RPA", "descripcion": "d", "rol_nuevo": "s"})
    err, _ = modelo.validar(d)
    assert any("flujo optimizado" in e and "P09" in e for e in err), err


@prueba
def detector_de_cruces_y_enrutador_limpio():
    # El detector encuentra una flecha que pasa por el centro de una caja ajena
    nodos = {"A": {"id": "A", "x": 100, "y": 60, "w": 156, "h": 60},
             "B": {"id": "B", "x": 300, "y": 60, "w": 156, "h": 60},
             "C": {"id": "C", "x": 500, "y": 60, "w": 156, "h": 60}}
    flechas = [{"de": "A", "a": "C", "puntos": [(178, 60), (422, 60)]},
               {"de": "A", "a": "B", "puntos": [(178, 60), (222, 60)]}]
    cruces = modelo._cruces(nodos, flechas)
    assert cruces == [{"de": "A", "a": "C", "nodo": "B"}], cruces
    # Y el enrutador evita cruces en el ejemplo y en un salto de dos columnas con estorbo
    d = base()
    d["pasos"].insert(3, {"id": "P08", "nombre": "Estorbo", "rol": "u", "tipo": "tarea", "columna": 3, "estado": "queda",
                          "fuente": "usuario", "tiempo_min": 1, "espera_min": 0})
    d["conexiones"] = [{"de": "P01", "a": "P02"}, {"de": "P02", "a": "P04"}, {"de": "P02", "a": "P03"},
                       {"de": "P03", "a": "P08"}, {"de": "P08", "a": "P04"}]
    paso(d, "P03")["rol"] = "s"
    for datos in (d, modelo.cargar(EJEMPLO)):
        err, adv = modelo.validar(datos)
        assert err == [], err
        assert not any("atraviesa" in a for a in adv), adv


@prueba
def formato_tiempo():
    f = modelo.formato_tiempo
    assert f(0) == "0 min" and f(59) == "59 min" and f(60) == "1 h" and f(125) == "2 h 5 min"
    assert f(959) == "15 h 59 min" and f(960) == "2,0 días hábiles" and f(5808) == "12,1 días hábiles"


@prueba
def paquete_trae_textos_y_no_muta_el_original():
    d = base()
    copia = copy.deepcopy(d)
    paq = modelo.paquete(d)
    assert d == copia
    assert paq["metricas"]["ciclo_actual_txt"] == "3 h"
    assert paq["datos"]["pasos"][1]["tiempo_txt"] == "10 min"
    json.dumps(paq)  # serializable


@prueba
def el_ejemplo_sigue_valido():
    d = modelo.cargar(EJEMPLO)
    err, _ = modelo.validar(d)
    assert err == [], err
    m = modelo.metricas(d)
    assert (m["pasos_actual"], m["pasos_optimizado"]) == (14, 11), m


def main():
    fallos = 0
    for f in PRUEBAS:
        try:
            f()
            print(f"ok    {f.__name__}")
        except AssertionError as e:
            fallos += 1
            print(f"FALLA {f.__name__}: {e}")
        except Exception as e:  # noqa: BLE001
            fallos += 1
            print(f"ERROR {f.__name__}: {type(e).__name__}: {e}")
    print(f"\n{len(PRUEBAS) - fallos}/{len(PRUEBAS)} pruebas pasaron.")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
