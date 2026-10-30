"""Modelo común: carga, validación, flujo optimizado, métricas y diagramación.

Lo usan validar.py, construir_artefacto.py y generar_informe.py para que el
artefacto y el PDF muestren exactamente lo mismo.
"""
import json
from pathlib import Path

ESTADOS = {"queda", "se_va", "optimizable"}
TIPOS = {"inicio", "tarea", "decision", "fin"}
NIVELES = {"alto", "medio", "bajo"}
# De dónde salió cada paso (regla R-01): lo dijo el usuario, está en un
# documento que entregó, o es un estimado que el usuario autorizó.
FUENTES = {"usuario", "documento", "estimado_autorizado"}

# Geometría del diagrama (unidades = px en el HTML, pt escalados en el PDF)
ETIQUETA_W = 150   # ancho de la columna con el nombre del rol
COL_W = 200        # ancho de cada columna
NODO_W = 156
NODO_H = 60
CARRIL_H = 120
MARGEN = 24        # espacio a la derecha/abajo


def cargar(ruta):
    return json.loads(Path(ruta).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- validación

def validar(d):
    """Devuelve (errores, advertencias)."""
    err, adv = [], []
    for clave in ("proceso", "roles", "pasos", "conexiones"):
        if clave not in d:
            err.append(f"Falta la sección '{clave}'.")
    if err:
        return err, adv

    roles = {r["id"] for r in d["roles"]}
    pasos = {}
    for p in d["pasos"]:
        pid = p.get("id", "?")
        if pid in pasos:
            err.append(f"{pid}: id repetido.")
        pasos[pid] = p
        if p.get("rol") not in roles:
            err.append(f"{pid}: el rol '{p.get('rol')}' no existe en 'roles'.")
        if p.get("tipo") not in TIPOS:
            err.append(f"{pid}: tipo '{p.get('tipo')}' inválido ({', '.join(sorted(TIPOS))}).")
        if p.get("estado") not in ESTADOS:
            err.append(f"{pid}: estado '{p.get('estado')}' inválido ({', '.join(sorted(ESTADOS))}).")
        if not isinstance(p.get("columna"), int) or p["columna"] < 1:
            err.append(f"{pid}: 'columna' debe ser un entero >= 1.")
        if p.get("tipo") in ("inicio", "fin") and p.get("estado") != "queda":
            err.append(f"{pid}: los pasos de inicio y fin siempre son 'queda'.")
        if p.get("fuente") not in FUENTES:
            err.append(f"{pid}: falta 'fuente' o es inválida ({', '.join(sorted(FUENTES))}). Regla R-01.")
        elif bool(p.get("estimado")) != (p["fuente"] == "estimado_autorizado"):
            err.append(f"{pid}: 'estimado' y 'fuente' no coinciden: un estimado lleva "
                       f"\"estimado\": true y \"fuente\": \"estimado_autorizado\". Regla R-01.")
        h = p.get("hallazgo")
        if p.get("estado") in ("se_va", "optimizable"):
            if not h:
                err.append(f"{pid}: un paso '{p['estado']}' necesita 'hallazgo'.")
            else:
                for c in ("problema", "propuesta", "impacto", "esfuerzo"):
                    if not h.get(c):
                        err.append(f"{pid}: al hallazgo le falta '{c}'.")
                for c in ("impacto", "esfuerzo"):
                    if h.get(c) and h[c] not in NIVELES:
                        err.append(f"{pid}: {c} '{h[c]}' debe ser alto, medio o bajo.")
                total = (p.get("tiempo_min") or 0) + (p.get("espera_min") or 0)
                if (h.get("ahorro_min") or 0) > total:
                    err.append(f"{pid}: el ahorro ({h['ahorro_min']} min) supera el tiempo del paso ({total} min). Regla R-04.")
        elif h:
            adv.append(f"{pid}: es 'queda' pero tiene hallazgo; no se mostrará como mejora.")
        a = p.get("automatizacion")
        if a and p.get("estado") != "optimizable":
            adv.append(f"{pid}: tiene 'automatizacion' pero no es 'optimizable'.")
        if a and a.get("rol_nuevo") and a["rol_nuevo"] not in roles:
            err.append(f"{pid}: rol_nuevo '{a['rol_nuevo']}' no existe en 'roles'.")
        if p.get("tipo") in ("tarea", "decision") and "tiempo_min" not in p:
            adv.append(f"{pid}: sin 'tiempo_min'; cuenta como 0 en las métricas.")

    tipos = [p.get("tipo") for p in d["pasos"]]
    if tipos.count("inicio") != 1:
        err.append(f"Debe haber exactamente un paso 'inicio' (hay {tipos.count('inicio')}).")
    if tipos.count("fin") < 1:
        err.append("Debe haber al menos un paso 'fin'.")

    salidas = {pid: [] for pid in pasos}
    entradas = {pid: 0 for pid in pasos}
    for c in d["conexiones"]:
        if c.get("de") not in pasos or c.get("a") not in pasos:
            err.append(f"Conexión {c.get('de')} → {c.get('a')}: apunta a un paso que no existe.")
            continue
        salidas[c["de"]].append(c)
        entradas[c["a"]] += 1
    for pid, p in pasos.items():
        if p.get("tipo") == "decision":
            if len(salidas[pid]) < 2:
                err.append(f"{pid}: una decisión necesita dos o más salidas.")
            if any(not c.get("etiqueta") for c in salidas[pid]):
                err.append(f"{pid}: todas las salidas de una decisión llevan 'etiqueta'.")
        if p.get("tipo") != "fin" and not salidas[pid]:
            err.append(f"{pid}: no tiene salida (solo los pasos 'fin' terminan el flujo).")
        if p.get("tipo") != "inicio" and not entradas[pid]:
            adv.append(f"{pid}: ningún paso llega a él.")

    _choques(d["pasos"], err, "flujo actual")
    if not err:
        opt = vista_optimizada(d)
        _choques(opt["pasos"], err, "flujo optimizado")
    if not err:
        for nombre, vista in (("flujo actual", vista_actual(d)), ("flujo optimizado", opt)):
            for c in diagramar(d, vista)["cruces"]:
                adv.append(f"{nombre}: la flecha {c['de']} → {c['a']} atraviesa la caja de {c['nodo']}; "
                           f"mueve ese paso de columna o carril.")
    return err, adv


def validar_carpeta(ruta_json):
    """Advertencias sobre los archivos que acompañan a flujo.json."""
    adv = []
    carpeta = Path(ruta_json).parent
    if not (carpeta / "levantamiento.md").exists():
        adv.append("No existe levantamiento.md junto al flujo.json; el auditor no podrá "
                   "comprobar la regla R-01 (no inventar). Lo escribe el analista de procesos.")
    return adv


def _choques(pasos, err, vista):
    vistos = {}
    for p in pasos:
        k = (p["rol"], p["columna"])
        if k in vistos:
            err.append(f"{vista}: {vistos[k]} y {p['id']} están en el mismo rol y la misma columna ({k[1]}).")
        vistos[k] = p["id"]


# ------------------------------------------------------ vistas y métricas

def vista_actual(d):
    return {"pasos": [dict(p) for p in d["pasos"]], "conexiones": [dict(c) for c in d["conexiones"]]}


def vista_optimizada(d):
    """Quita los pasos 'se_va', une predecesores con sucesores, aplica la
    automatización (nombre, rol y tiempos nuevos) y compacta las columnas."""
    por_id = {p["id"]: p for p in d["pasos"]}
    salidas = {}
    for c in d["conexiones"]:
        salidas.setdefault(c["de"], []).append(c)

    def destinos(pid, vistos):
        res = []
        for c in salidas.get(pid, []):
            if c["a"] in vistos:
                continue
            if por_id[c["a"]]["estado"] == "se_va":
                for sub in destinos(c["a"], vistos | {c["a"]}):
                    res.append({"a": sub["a"], "etiqueta": c.get("etiqueta") or sub.get("etiqueta")})
            else:
                res.append({"a": c["a"], "etiqueta": c.get("etiqueta")})
        return res

    pasos, conexiones, vistas = [], [], set()
    for p in d["pasos"]:
        if p["estado"] == "se_va":
            continue
        q = dict(p)
        a = p.get("automatizacion")
        if p["estado"] == "optimizable" and a:
            q["nombre"] = a.get("nombre_nuevo") or p["nombre"]
            q["rol"] = a.get("rol_nuevo") or p["rol"]
        q["tiempo_min"], q["espera_min"] = tiempos_optimizados(p)
        pasos.append(q)
        for t in destinos(p["id"], {p["id"]}):
            k = (p["id"], t["a"])
            if k not in vistas:
                vistas.add(k)
                conexiones.append({"de": p["id"], "a": t["a"], "etiqueta": t.get("etiqueta")})

    columnas = sorted({p["columna"] for p in pasos})
    nueva = {c: i + 1 for i, c in enumerate(columnas)}
    for p in pasos:
        p["columna"] = nueva[p["columna"]]
    return {"pasos": pasos, "conexiones": conexiones}


def tiempos_optimizados(p):
    t, e = p.get("tiempo_min", 0) or 0, p.get("espera_min", 0) or 0
    if p["estado"] != "optimizable":
        return t, e
    a = p.get("automatizacion")
    if a and ("tiempo_nuevo_min" in a or "espera_nueva_min" in a):
        return a.get("tiempo_nuevo_min", t), a.get("espera_nueva_min", e)
    ahorro = (p.get("hallazgo") or {}).get("ahorro_min", 0) or 0
    # El ahorro se descuenta primero de la espera
    de_espera = min(ahorro, e)
    return max(0, t - (ahorro - de_espera)), e - de_espera


def _traspasos(vista):
    rol = {p["id"]: p["rol"] for p in vista["pasos"]}
    return sum(1 for c in vista["conexiones"] if rol[c["de"]] != rol[c["a"]])


def metricas(d):
    act, opt = vista_actual(d), vista_optimizada(d)

    def ciclo(v):
        # Ruta más larga desde el inicio (peor caso en las decisiones); los
        # retornos por reproceso se ignoran para no contar ciclos.
        dur = {p["id"]: (p.get("tiempo_min") or 0) + (p.get("espera_min") or 0) for p in v["pasos"]}
        sal = {}
        for c in v["conexiones"]:
            sal.setdefault(c["de"], []).append(c["a"])
        memo = {}

        def largo(pid, camino):
            if pid in memo:
                return memo[pid]
            sig = [largo(a, camino | {a}) for a in sal.get(pid, []) if a not in camino]
            memo[pid] = dur[pid] + max(sig, default=0)
            return memo[pid]

        inicio = next(p["id"] for p in v["pasos"] if p["tipo"] == "inicio")
        return largo(inicio, {inicio})

    def trabajo(v):
        return sum(p.get("tiempo_min") or 0 for p in v["pasos"])

    c_act, c_opt = ciclo(act), ciclo(opt)
    cuenta = {e: sum(1 for p in d["pasos"] if p["estado"] == e) for e in ESTADOS}
    return {
        "pasos_actual": len(act["pasos"]),
        "pasos_optimizado": len(opt["pasos"]),
        "se_va": cuenta["se_va"],
        "queda": cuenta["queda"],
        "optimizable": cuenta["optimizable"],
        "automatizaciones": sum(1 for p in d["pasos"] if p["estado"] == "optimizable" and p.get("automatizacion")),
        "ciclo_actual_min": c_act,
        "ciclo_optimizado_min": c_opt,
        "reduccion_ciclo_pct": round(100 * (c_act - c_opt) / c_act) if c_act else 0,
        "trabajo_actual_min": trabajo(act),
        "trabajo_optimizado_min": trabajo(opt),
        "traspasos_actual": _traspasos(act),
        "traspasos_optimizado": _traspasos(opt),
        "roles_actual": len({p["rol"] for p in act["pasos"]}),
        "roles_optimizado": len({p["rol"] for p in opt["pasos"]}),
        "hay_estimados": any(p.get("estimado") for p in d["pasos"]),
    }


def formato_tiempo(minutos):
    m = int(round(minutos))
    if m < 60:
        return f"{m} min"
    if m < 60 * 8 * 2:
        h, r = divmod(m, 60)
        return f"{h} h {r} min" if r else f"{h} h"
    # Más de dos jornadas: expresar en días hábiles de 8 h
    return f"{m / (60 * 8):.1f} días hábiles".replace(".", ",")


# ------------------------------------------------------------ diagramación

def diagramar(d, vista):
    """Calcula posiciones de carriles, nodos y rutas ortogonales de las flechas.
    Devuelve coordenadas listas para dibujar en SVG (HTML) o en reportlab (PDF)."""
    usados = {p["rol"] for p in vista["pasos"]}
    roles = [r for r in d["roles"] if r["id"] in usados]
    idx = {r["id"]: i for i, r in enumerate(roles)}
    n_col = max(p["columna"] for p in vista["pasos"])
    ancho = ETIQUETA_W + n_col * COL_W + MARGEN
    alto = len(roles) * CARRIL_H

    nodos = {}
    for p in vista["pasos"]:
        cx = ETIQUETA_W + (p["columna"] - 0.5) * COL_W
        cy = idx[p["rol"]] * CARRIL_H + CARRIL_H / 2
        w = NODO_W if p["tipo"] in ("tarea", "decision") else 120
        h = NODO_H + (14 if p["tipo"] == "decision" else 0)
        nodos[p["id"]] = {"id": p["id"], "x": cx, "y": cy, "w": w, "h": h,
                          "carril": idx[p["rol"]], "columna": p["columna"]}

    ocupado = {(n["carril"], n["columna"]) for n in nodos.values()}

    def libre_horizontal(carril, c_desde, c_hasta):
        a, b = sorted((c_desde, c_hasta))
        return all((carril, c) not in ocupado for c in range(a + 1, b))

    def libre_vertical(columna, l_desde, l_hasta):
        a, b = sorted((l_desde, l_hasta))
        return all((l, columna) not in ocupado for l in range(a + 1, b))

    flechas = []
    for c in vista["conexiones"]:
        s, t = nodos[c["de"]], nodos[c["a"]]
        sx, sy = s["x"] + s["w"] / 2, s["y"]
        tx, ty = t["x"] - t["w"] / 2, t["y"]
        hueco = (COL_W - NODO_W) / 2
        if t["columna"] > s["columna"]:
            if s["carril"] == t["carril"] and libre_horizontal(s["carril"], s["columna"], t["columna"]):
                pts = [(sx, sy), (tx, ty)]
            elif libre_horizontal(t["carril"], s["columna"], t["columna"]):
                mx = s["x"] + COL_W / 2           # baja en el hueco junto al origen
                pts = [(sx, sy), (mx, sy), (mx, ty), (tx, ty)]
            elif libre_horizontal(s["carril"], s["columna"], t["columna"]):
                mx = t["x"] - COL_W / 2           # baja en el hueco junto al destino
                pts = [(sx, sy), (mx, sy), (mx, ty), (tx, ty)]
            else:                                  # va por el borde del carril
                abajo = t["carril"] > s["carril"]
                by = (s["carril"] + (1 if abajo else 0)) * CARRIL_H
                x1, x2 = s["x"] + COL_W / 2, t["x"] - COL_W / 2
                pts = [(sx, sy), (x1, sy), (x1, by), (x2, by), (x2, ty), (tx, ty)]
        elif t["columna"] == s["columna"]:
            # Misma columna, otro carril: sale por abajo/arriba
            abajo = t["carril"] > s["carril"]
            sy2 = s["y"] + (s["h"] / 2 if abajo else -s["h"] / 2)
            ty2 = t["y"] - (t["h"] / 2 if abajo else -t["h"] / 2)
            if libre_vertical(s["columna"], s["carril"], t["carril"]):
                pts = [(s["x"], sy2), (t["x"], ty2)]
            else:
                mx = s["x"] + COL_W / 2 - hueco / 2
                pts = [(sx, sy), (mx, sy), (mx, ty), (t["x"] + t["w"] / 2, ty)]
        else:
            # Retorno (reproceso): por debajo del carril inferior de los dos
            low = max(s["carril"], t["carril"])
            by = (low + 1) * CARRIL_H - 10
            x1 = s["x"] + COL_W / 2          # centro del hueco entre columnas
            x2 = t["x"] - COL_W / 2
            pts = [(sx, sy), (x1, sy), (x1, by), (x2, by), (x2, ty), (tx, ty)]
        etiqueta = None
        if c.get("etiqueta"):
            # En el más largo de los dos primeros tramos, para no tapar la forma
            tramos = [(pts[i], pts[i + 1]) for i in range(min(2, len(pts) - 1))]
            (x0, y0), (x1_, y1_) = max(tramos, key=lambda s: abs(s[1][0] - s[0][0]) + abs(s[1][1] - s[0][1]))
            etiqueta = {"texto": c["etiqueta"], "x": (x0 + x1_) / 2, "y": (y0 + y1_) / 2}
        flechas.append({"de": c["de"], "a": c["a"], "puntos": pts, "etiqueta": etiqueta,
                        "retorno": t["columna"] < s["columna"]})

    carriles = [{"id": r["id"], "nombre": r["nombre"], "tipo": r.get("tipo", "persona"),
                 "y": i * CARRIL_H, "h": CARRIL_H} for i, r in enumerate(roles)]
    return {"ancho": ancho, "alto": alto, "etiqueta_w": ETIQUETA_W, "col_w": COL_W,
            "n_columnas": n_col, "carriles": carriles, "nodos": nodos, "flechas": flechas,
            "cruces": _cruces(nodos, flechas)}


def _cruces(nodos, flechas):
    """Flechas cuyo trazo atraviesa la caja de un paso que no es su origen ni su destino."""
    res = []
    for f in flechas:
        for n in nodos.values():
            if n["id"] in (f["de"], f["a"]):
                continue
            x0, x1 = n["x"] - n["w"] / 2, n["x"] + n["w"] / 2
            y0, y1 = n["y"] - n["h"] / 2, n["y"] + n["h"] / 2
            for (ax, ay), (bx, by) in zip(f["puntos"], f["puntos"][1:]):
                if ay == by and y0 < ay < y1 and min(ax, bx) < x1 and max(ax, bx) > x0:
                    res.append({"de": f["de"], "a": f["a"], "nodo": n["id"]})
                    break
                if ax == bx and x0 < ax < x1 and min(ay, by) < y1 and max(ay, by) > y0:
                    res.append({"de": f["de"], "a": f["a"], "nodo": n["id"]})
                    break
    return res


def _con_textos(pasos):
    """Agrega a cada paso los tiempos ya formateados, para que el HTML y el PDF
    muestren exactamente el mismo texto."""
    res = []
    for p in pasos:
        q = dict(p)
        q["tiempo_txt"] = formato_tiempo(p.get("tiempo_min") or 0)
        q["espera_txt"] = formato_tiempo(p.get("espera_min") or 0)
        if p.get("hallazgo") and p["hallazgo"].get("ahorro_min"):
            q["hallazgo"] = dict(p["hallazgo"], ahorro_txt=formato_tiempo(p["hallazgo"]["ahorro_min"]))
        res.append(q)
    return res


def paquete(d):
    """Todo lo que necesitan el artefacto y el PDF. Los textos de tiempo salen
    de aquí: ni el JavaScript ni el PDF vuelven a formatear minutos."""
    act, opt = vista_actual(d), vista_optimizada(d)
    m = metricas(d)
    for k in ("ciclo_actual", "ciclo_optimizado", "trabajo_actual", "trabajo_optimizado"):
        m[k + "_txt"] = formato_tiempo(m[k + "_min"])
    datos = dict(d, pasos=_con_textos(d["pasos"]))
    return {
        "datos": datos,
        "metricas": m,
        "actual": {"pasos": _con_textos(act["pasos"]), "conexiones": act["conexiones"], "layout": diagramar(d, act)},
        "optimizado": {"pasos": _con_textos(opt["pasos"]), "conexiones": opt["conexiones"], "layout": diagramar(d, opt)},
    }
