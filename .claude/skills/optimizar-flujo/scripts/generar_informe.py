"""Genera el informe PDF profesional desde flujo.json.

Uso: <python con reportlab> generar_informe.py analisis/<slug>/flujo.json
Escribe informe.pdf junto al JSON.
Requiere reportlab (en este proyecto: .venv/bin/python).
"""
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import modelo  # noqa: E402

try:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import landscape, letter
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable, Frame, KeepTogether,
                                    NextPageTemplate, PageBreak, PageTemplate, Paragraph, Spacer,
                                    Table, TableStyle)
except ImportError:
    sys.exit("Falta reportlab. Instálalo con: python3 -m venv .venv && .venv/bin/pip install reportlab")

# ------------------------------------------------------------------ estilo

C = {
    "tinta": colors.HexColor("#16202c"), "gris": colors.HexColor("#586473"),
    "linea": colors.HexColor("#d6dce4"), "linea2": colors.HexColor("#b5bfcb"),
    "fondo": colors.HexColor("#eef1f5"), "acento": colors.HexColor("#23384f"),
    "carril_a": colors.HexColor("#f8f9fb"), "carril_b": colors.HexColor("#f0f3f7"),
    "rojo": colors.HexColor("#b8322a"), "rojo_bg": colors.HexColor("#fcebe9"),
    "verde": colors.HexColor("#22744a"), "verde_bg": colors.HexColor("#e6f4ec"),
    "azul": colors.HexColor("#1c5bb8"), "azul_bg": colors.HexColor("#e6effc"),
}
COLOR_ESTADO = {"queda": ("verde", "verde_bg"), "se_va": ("rojo", "rojo_bg"), "optimizable": ("azul", "azul_bg")}
NOMBRE_ESTADO = {"queda": "Se mantiene", "se_va": "Se elimina", "optimizable": "Optimizable"}

FUENTES = [  # (regular, negrita) — la primera que exista
    ("/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf"),
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]
F, FB = "Helvetica", "Helvetica-Bold"
for reg, neg in FUENTES:
    if Path(reg).exists() and Path(neg).exists():
        pdfmetrics.registerFont(TTFont("Texto", reg))
        pdfmetrics.registerFont(TTFont("Texto-Negrita", neg))
        pdfmetrics.registerFontFamily("Texto", normal="Texto", bold="Texto-Negrita")
        F, FB = "Texto", "Texto-Negrita"
        break
FLECHA = "→" if F == "Texto" else "->"

E = {
    "cuerpo": ParagraphStyle("cuerpo", fontName=F, fontSize=9.5, leading=13.5, textColor=C["tinta"], alignment=TA_LEFT),
    "gris": ParagraphStyle("gris", fontName=F, fontSize=8.5, leading=12, textColor=C["gris"]),
    "h1": ParagraphStyle("h1", fontName=FB, fontSize=17, leading=21, textColor=C["tinta"], spaceBefore=4, spaceAfter=10),
    "h2": ParagraphStyle("h2", fontName=FB, fontSize=12, leading=15, textColor=C["tinta"], spaceBefore=12, spaceAfter=6),
    "eyebrow": ParagraphStyle("eyebrow", fontName=FB, fontSize=7.5, leading=10, textColor=C["gris"]),
    "celda": ParagraphStyle("celda", fontName=F, fontSize=8, leading=10.5, textColor=C["tinta"]),
    "celda_b": ParagraphStyle("celda_b", fontName=FB, fontSize=8, leading=10.5, textColor=C["tinta"]),
    "th": ParagraphStyle("th", fontName=FB, fontSize=7, leading=9, textColor=C["gris"]),
}


def esc(s):
    return str(s if s is not None else "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def P(texto, estilo="cuerpo"):
    return Paragraph(texto, E[estilo])


def estado_html(estado):
    col = C[COLOR_ESTADO[estado][0]].hexval()[2:]
    return f'<font color="#{col}"><b>● {NOMBRE_ESTADO[estado]}</b></font>'


def tabla(filas, anchos, cabecera=True, zebra=True):
    datos = [[c if isinstance(c, Flowable) else P(esc(c), "celda") for c in f] for f in filas]
    if cabecera:
        datos[0] = [P(esc(c).upper(), "th") if not isinstance(c, Flowable) else c for c in filas[0]]
    t = Table(datos, colWidths=anchos, repeatRows=1 if cabecera else 0)
    st = [("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LINEBELOW", (0, 0), (-1, -1), 0.5, C["linea"]),
          ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
          ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]
    if cabecera:
        st += [("BACKGROUND", (0, 0), (-1, 0), C["fondo"]), ("LINEBELOW", (0, 0), (-1, 0), 0.8, C["linea2"])]
    t.setStyle(TableStyle(st))
    return t


# --------------------------------------------------------------- diagrama

def partir(texto, maximo, max_lineas=3):
    lineas, actual = [], ""
    for w in str(texto).split():
        if len((actual + " " + w).strip()) > maximo and actual:
            lineas.append(actual)
            actual = w
        else:
            actual = (actual + " " + w).strip()
    if actual:
        lineas.append(actual)
    if len(lineas) > max_lineas:
        lineas = lineas[:max_lineas]
        lineas[-1] = lineas[-1][:-1] + "…"
    return lineas


class Diagrama(Flowable):
    """Dibuja un tramo de columnas [col_ini, col_fin] del diagrama de carriles."""

    def __init__(self, vista, vista_nombre, col_ini, col_fin, ancho_disp, alto_disp, por_id):
        super().__init__()
        self.L, self.pasos = vista["layout"], {p["id"]: p for p in vista["pasos"]}
        self.vista_nombre, self.por_id = vista_nombre, por_id
        self.c0, self.c1 = col_ini, col_fin
        L = self.L
        self.ancho_px = L["etiqueta_w"] + (col_fin - col_ini + 1) * L["col_w"] + 12
        self.s = min(ancho_disp / self.ancho_px, alto_disp / L["alto"], 0.8)
        self.width, self.height = self.ancho_px * self.s, L["alto"] * self.s

    # px (y hacia abajo) → pt (y hacia arriba), con desplazamiento de columnas
    def _x(self, x):
        return (x - (self.c0 - 1) * self.L["col_w"]) * self.s

    def _y(self, y):
        return (self.L["alto"] - y) * self.s

    def _texto(self, c, cx, cy, lineas, fuente, tam, color):
        c.setFont(fuente, tam)
        c.setFillColor(color)
        alto = tam * 1.2
        y0 = cy + (len(lineas) - 1) * alto / 2 - tam * 0.35
        for i, l in enumerate(lineas):
            c.drawCentredString(cx, y0 - i * alto, l)

    def draw(self):
        c, L, s = self.canv, self.L, self.s
        ew = L["etiqueta_w"] * s
        for i, car in enumerate(L["carriles"]):
            y = self._y(car["y"] + car["h"])
            c.setFillColor(C["carril_b"] if i % 2 else C["carril_a"])
            c.setStrokeColor(C["linea"])
            c.setLineWidth(0.5)
            c.rect(0, y, self.width, car["h"] * s, stroke=1, fill=1)
            tipo = {"externo": "EXTERNO", "sistema": "SISTEMA"}.get(car["tipo"], "ROL")
            lineas = partir(car["nombre"], 16)
            cy = y + car["h"] * s / 2
            self._texto(c, ew / 2, cy + 4 * s, lineas, FB, 12 * s, C["tinta"])
            self._texto(c, ew / 2, cy - (len(lineas) * 7.5 + 6) * s, [tipo], FB, 9 * s, C["gris"])
        c.line(ew, 0, ew, self.height)

        # Recorte al tramo de columnas
        c.saveState()
        p = c.beginPath()
        p.rect(ew, 0, self.width - ew, self.height)
        c.clipPath(p, stroke=0, fill=0)
        c.translate(0, 0)
        for f in L["flechas"]:
            corta = self.vista_nombre == "actual" and (
                self.por_id[f["de"]]["estado"] == "se_va" or self.por_id[f["a"]]["estado"] == "se_va")
            c.setStrokeColor(C["rojo"] if corta else C["linea2"])
            c.setLineWidth(1.3 * s + 0.3)
            c.setDash([4 * s, 3 * s] if (corta or f["retorno"]) else [])
            pts = [(self._x(x) , self._y(y)) for x, y in f["puntos"]]
            path = c.beginPath()
            path.moveTo(*pts[0])
            for q in pts[1:]:
                path.lineTo(*q)
            c.drawPath(path, stroke=1, fill=0)
            c.setDash([])
            (x1, y1), (x2, y2) = pts[-2], pts[-1]
            ang = math.atan2(y2 - y1, x2 - x1)
            t = 7 * s + 1.5
            c.setFillColor(C["rojo"] if corta else C["linea2"])
            tri = c.beginPath()
            tri.moveTo(x2, y2)
            tri.lineTo(x2 - t * math.cos(ang - 0.45), y2 - t * math.sin(ang - 0.45))
            tri.lineTo(x2 - t * math.cos(ang + 0.45), y2 - t * math.sin(ang + 0.45))
            tri.close()
            c.drawPath(tri, stroke=0, fill=1)
            if f["etiqueta"]:
                ex, ey = self._x(f["etiqueta"]["x"]), self._y(f["etiqueta"]["y"])
                w = (len(f["etiqueta"]["texto"]) * 7 + 12) * s
                c.setFillColor(colors.white)
                c.setStrokeColor(C["linea"])
                c.roundRect(ex - w / 2, ey - 9 * s, w, 18 * s, 9 * s, stroke=1, fill=1)
                self._texto(c, ex, ey, [f["etiqueta"]["texto"]], FB, 10 * s, C["gris"])

        for n in L["nodos"].values():
            p_ = self.pasos[n["id"]]
            borde, fondo = (C[k] for k in COLOR_ESTADO[p_["estado"]])
            cx, cy, w, h = self._x(n["x"]), self._y(n["y"]), n["w"] * s, n["h"] * s
            c.setFillColor(fondo)
            c.setStrokeColor(borde)
            c.setLineWidth(1.4 * s + 0.2)
            c.setDash([5 * s, 3 * s] if p_["estado"] == "se_va" else [])
            if p_["tipo"] == "decision":
                d = c.beginPath()
                d.moveTo(cx, cy + h / 2)
                d.lineTo(cx + w / 2, cy)
                d.lineTo(cx, cy - h / 2)
                d.lineTo(cx - w / 2, cy)
                d.close()
                c.drawPath(d, stroke=1, fill=1)
                lineas, maximo = partir(p_["nombre"], 17), 17
            else:
                r = 8 * s if p_["tipo"] == "tarea" else h / 2
                c.roundRect(cx - w / 2, cy - h / 2, w, h, r, stroke=1, fill=1)
                maximo = 21 if p_["tipo"] == "tarea" else 15
                lineas = partir(p_["nombre"], maximo)
            c.setDash([])
            self._texto(c, cx, cy - 4 * s, lineas, FB, 11 * s, C["rojo"] if p_["estado"] == "se_va" else C["tinta"])
            self._texto(c, cx, cy + h / 2 - 11 * s, [n["id"]], FB, 9 * s, borde)
            if self.vista_nombre == "optimizado" and p_["estado"] == "optimizable" and self.por_id[n["id"]].get("automatizacion"):
                c.setFillColor(C["azul"])
                c.roundRect(cx + w / 2 - 46 * s, cy + h / 2 - 8 * s, 50 * s, 16 * s, 8 * s, stroke=0, fill=1)
                self._texto(c, cx + w / 2 - 21 * s, cy + h / 2, ["AUTO"], FB, 9 * s, colors.white)
        c.restoreState()

        c.setFont(F, 7)
        c.setFillColor(C["gris"])
        if self.c0 > 1:
            c.drawString(ew + 4, self.height + 3, f"viene de la columna {self.c0 - 1}")
        if self.c1 < L["n_columnas"]:
            c.drawRightString(self.width, self.height + 3, f"continúa en la columna {self.c1 + 1} {FLECHA}")


def diagrama_por_tramos(vista, nombre, ancho, alto, por_id):
    L = vista["layout"]
    escala_min = 0.55
    por_pagina = max(3, int((ancho / escala_min - L["etiqueta_w"] - 12) // L["col_w"]))
    n = L["n_columnas"]
    paginas = math.ceil(n / por_pagina)
    tam = math.ceil(n / paginas)
    return [(i + 1, min(n, i + tam)) for i in range(0, n, tam)]


def leyenda(vista):
    if vista == "actual":
        estados, nota = ("se_va", "queda", "optimizable"), "Las flechas rojas punteadas tocan pasos que se eliminan."
    else:
        estados, nota = ("queda", "optimizable"), "AUTO = paso automatizado."
    celdas = [P(estado_html(e), "celda") for e in estados] + [P(nota, "gris")]
    t = Table([celdas], colWidths=[3 * cm] * len(estados) + [None])
    t.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    return t


# ------------------------------------------------------------- documento

def construir(ruta_json):
    d = modelo.cargar(ruta_json)
    errores, _ = modelo.validar(d)
    if errores:
        print("\n".join(errores))
        sys.exit("El flujo tiene errores; corre validar.py y corrígelos primero.")
    paq = modelo.paquete(d)
    M, pr = paq["metricas"], d["proceso"]
    por_id = {p["id"]: p for p in d["pasos"]}
    rol = {r["id"]: r["nombre"] for r in d["roles"]}
    t = modelo.formato_tiempo
    destino = Path(ruta_json).with_name("informe.pdf")

    margen = 1.8 * cm
    vert, horiz = letter, landscape(letter)

    def pie(c, doc):
        c.saveState()
        ancho, alto = c._pagesize   # doc.pagesize no cambia con la plantilla horizontal
        c.setStrokeColor(C["linea"])
        c.line(margen, alto - margen + 14, ancho - margen, alto - margen + 14)
        c.setFont(F, 7.5)
        c.setFillColor(C["gris"])
        c.drawString(margen, alto - margen + 19, f"{pr['nombre']} · Informe de optimización")
        c.drawRightString(ancho - margen, alto - margen + 19, pr.get("organizacion", ""))
        c.drawString(margen, margen - 22, f"Versión {pr.get('version', '1.0')} · {pr.get('fecha', '')}")
        c.drawRightString(ancho - margen, margen - 22, f"Página {doc.page}")
        c.restoreState()

    def portada(c, doc):
        ancho, alto = doc.pagesize
        c.saveState()
        c.setFillColor(C["acento"])
        c.rect(0, alto - 9 * cm, ancho, 9 * cm, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont(FB, 9)
        c.drawString(margen, alto - 3 * cm, "INFORME DE OPTIMIZACIÓN DE FLUJO")
        c.setFont(FB, 28)
        for i, l in enumerate(partir(pr["nombre"], 32, 2)):
            c.drawString(margen, alto - 4.6 * cm - i * 1.2 * cm, l)
        c.setFont(F, 11)
        c.drawString(margen, alto - 7.6 * cm, " · ".join(x for x in (pr.get("organizacion"), pr.get("area")) if x))
        filas = [("Código", pr.get("codigo")), ("Versión", pr.get("version")), ("Fecha", pr.get("fecha")),
                 ("Volumen", pr.get("volumen")),
                 ("Auditoría", (d.get("auditoria") or {}).get("estado"))]
        y = alto - 11 * cm
        for k, v in filas:
            if not v:
                continue
            c.setFillColor(C["gris"])
            c.setFont(FB, 8)
            c.drawString(margen, y, k.upper())
            c.setFillColor(C["tinta"])
            c.setFont(F, 11)
            c.drawString(margen + 3.2 * cm, y, str(v))
            y -= 0.9 * cm
        # Mini resumen de colores
        y -= 0.6 * cm
        for e, n in (("se_va", M["se_va"]), ("queda", M["queda"]), ("optimizable", M["optimizable"])):
            borde, fondo = (C[k] for k in COLOR_ESTADO[e])
            c.setFillColor(fondo)
            c.setStrokeColor(borde)
            c.roundRect(margen, y - 4, 0.9 * cm, 0.55 * cm, 3, stroke=1, fill=1)
            c.setFillColor(C["tinta"])
            c.setFont(F, 10)
            c.drawString(margen + 1.2 * cm, y, f"{NOMBRE_ESTADO[e]}: {n} pasos")
            y -= 0.8 * cm
        c.setFont(F, 8)
        c.setFillColor(C["gris"])
        c.drawString(margen, margen, "Documento de trabajo. Los tiempos marcados como estimados deben validarse con medición real.")
        c.restoreState()

    doc = BaseDocTemplate(str(destino), pagesize=vert, leftMargin=margen, rightMargin=margen,
                          topMargin=margen, bottomMargin=margen,
                          title=f"{pr['nombre']} · Informe de optimización", author=pr.get("organizacion", ""))
    fv = Frame(margen, margen, vert[0] - 2 * margen, vert[1] - 2 * margen, id="v")
    fh = Frame(margen, margen, horiz[0] - 2 * margen, horiz[1] - 2 * margen, id="h")
    doc.addPageTemplates([
        PageTemplate("portada", [fv], onPage=portada, pagesize=vert),
        PageTemplate("vertical", [fv], onPage=pie, pagesize=vert),
        PageTemplate("horizontal", [fh], onPage=pie, pagesize=horiz),
    ])
    ancho_v = vert[0] - 2 * margen
    ancho_h = horiz[0] - 2 * margen

    h = [NextPageTemplate("vertical"), PageBreak()]

    # 1. Resumen ejecutivo
    h += [P("1 · RESUMEN EJECUTIVO", "eyebrow"), P("Resultado del análisis", "h1"),
          P(esc(d.get("resumen_ejecutivo", ""))), Spacer(1, 12)]
    ind = [["Indicador", "Actual", "Optimizado", "Variación"],
           ["Pasos del proceso", M["pasos_actual"], M["pasos_optimizado"], f"−{M['pasos_actual'] - M['pasos_optimizado']}"],
           ["Tiempo de ciclo por caso", t(M["ciclo_actual_min"]), t(M["ciclo_optimizado_min"]), f"−{M['reduccion_ciclo_pct']} %"],
           ["Trabajo efectivo por caso", t(M["trabajo_actual_min"]), t(M["trabajo_optimizado_min"]), ""],
           ["Traspasos entre roles", M["traspasos_actual"], M["traspasos_optimizado"], f"−{M['traspasos_actual'] - M['traspasos_optimizado']}"],
           ["Roles que intervienen", M["roles_actual"], M["roles_optimizado"], ""],
           ["Pasos eliminados / optimizables", "", f"{M['se_va']} / {M['optimizable']}", f"{M['automatizaciones']} automatizaciones"]]
    h.append(tabla(ind, [ancho_v * 0.38, ancho_v * 0.2, ancho_v * 0.2, ancho_v * 0.22]))
    h.append(Spacer(1, 4))
    h.append(P("Tiempo de ciclo: ruta más larga del inicio al fin (peor caso en las decisiones), en días hábiles de 8 horas."
               + (" Incluye tiempos estimados." if M["hay_estimados"] else ""), "gris"))

    # 2. Descripción
    h += [P("2 · DESCRIPCIÓN DEL PROCESO", "eyebrow"), P("Ficha del proceso", "h1")]
    ficha = [("Objetivo", pr.get("objetivo")), ("Alcance", pr.get("alcance")), ("Disparador", pr.get("disparador")),
             ("Resultado", pr.get("resultado")), ("Volumen", pr.get("volumen")),
             ("Normatividad", "; ".join(pr.get("normatividad", []))),
             ("Roles", ", ".join(r["nombre"] for r in d["roles"]))]
    h.append(tabla([[P(k, "celda_b"), v] for k, v in ficha if v], [ancho_v * 0.22, ancho_v * 0.78], cabecera=False))

    # 3 y 4. Diagramas
    alto_diag = horiz[1] - 2 * margen - 3.2 * cm
    for num, clave, titulo, texto in (
            (3, "actual", "Flujo actual", "Diagnóstico sobre el flujo como opera hoy."),
            (4, "optimizado", "Flujo optimizado", "Cómo queda el proceso al aplicar las mejoras. Los pasos eliminados ya no aparecen y sus conexiones se reconectan.")):
        tramos = diagrama_por_tramos(paq[clave], clave, ancho_h, alto_diag, por_id)
        for i, (a, b) in enumerate(tramos):
            h += [NextPageTemplate("horizontal"), PageBreak()]
            sub = f" (parte {i + 1} de {len(tramos)})" if len(tramos) > 1 else ""
            h += [P(f"{num} · {titulo.upper()}", "eyebrow"), P(titulo + sub, "h1"), P(texto, "gris"), Spacer(1, 4),
                  leyenda(clave), Spacer(1, 14), Diagrama(paq[clave], clave, a, b, ancho_h, alto_diag, por_id)]
    h += [NextPageTemplate("vertical"), PageBreak()]

    # 5. Hallazgos
    peso = {"alto": 3, "medio": 2, "bajo": 1}
    hall = sorted((p for p in d["pasos"] if p.get("hallazgo") and p["estado"] != "queda"),
                  key=lambda p: (-(peso[p["hallazgo"]["impacto"]] - peso[p["hallazgo"]["esfuerzo"]]),
                                 -(p["hallazgo"].get("ahorro_min") or 0)))
    h += [P("5 · HALLAZGOS", "eyebrow"), P("Qué se elimina y qué se optimiza", "h1"),
          P("Ordenados por prioridad: primero el mayor impacto con el menor esfuerzo.", "gris"), Spacer(1, 6)]
    filas = [["Paso", "Estado", "Categoría", "Impacto", "Esfuerzo", "Ahorro"]]
    for p in hall:
        hh = p["hallazgo"]
        filas.append([P(f"<b>{p['id']}</b> {esc(p['nombre'])}", "celda"), P(estado_html(p["estado"]), "celda"),
                      hh.get("categoria", ""), hh["impacto"].capitalize(), hh["esfuerzo"].capitalize(),
                      t(hh["ahorro_min"]) if hh.get("ahorro_min") else "—"])
    h.append(tabla(filas, [ancho_v * x for x in (0.3, 0.15, 0.2, 0.1, 0.1, 0.15)]))
    h.append(Spacer(1, 10))
    for p in hall:
        hh, a = p["hallazgo"], p.get("automatizacion")
        borde, fondo = (C[k] for k in COLOR_ESTADO[p["estado"]])
        cuerpo = [P(f"<b>{p['id']} · {esc(p['nombre'])}</b> &nbsp; {estado_html(p['estado'])} &nbsp; "
                    f"<font color='#586473'>{esc(rol[p['rol']])}</font>", "cuerpo"),
                  P(f"<b>Problema.</b> {esc(hh['problema'])}", "celda"),
                  P(f"<b>Propuesta.</b> {esc(hh['propuesta'])}", "celda")]
        if a:
            cuerpo.append(P(f"<b>Automatización ({esc(a.get('tipo', ''))}).</b> {esc(a.get('descripcion', ''))}", "celda"))
        bloque = Table([[x] for x in cuerpo], colWidths=[ancho_v])
        bloque.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), fondo), ("LINEBEFORE", (0, 0), (0, -1), 2.5, borde),
                                    ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 3),
                                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
        h += [KeepTogether([bloque]), Spacer(1, 6)]

    # 6. Propuesta técnica
    A = d.get("arquitectura")
    if A:
        h += [CondPageBreak(8 * cm), P("6 · PROPUESTA TÉCNICA", "eyebrow"), P("Arquitectura de software", "h1")]
        if A.get("propuestas"):
            h.append(P("Propuestas", "h2"))
            h.append(tabla([["Propuesta", "Descripción", "Pasos", "Esfuerzo"]] +
                           [[P(f"<b>{esc(x['titulo'])}</b>", "celda"), x["descripcion"], ", ".join(x.get("pasos", [])),
                             str(x.get("esfuerzo", "")).capitalize()] for x in A["propuestas"]],
                           [ancho_v * x for x in (0.25, 0.5, 0.13, 0.12)]))
        if A.get("sistemas"):
            tipo = {"existente": "Existente", "nuevo": "Nuevo", "a_reemplazar": "Se retira"}
            h.append(P("Sistemas", "h2"))
            h.append(tabla([["Sistema", "Situación", "Rol en el flujo"]] +
                           [[P(f"<b>{esc(s['nombre'])}</b>", "celda"), tipo.get(s["tipo"], s["tipo"]), s.get("descripcion", "")]
                            for s in A["sistemas"]], [ancho_v * 0.3, ancho_v * 0.15, ancho_v * 0.55]))
        if A.get("integraciones"):
            nom = {s["id"]: s["nombre"] for s in A.get("sistemas", [])}
            h.append(P("Integraciones", "h2"))
            h.append(tabla([["Origen", "Destino", "Mecanismo", "Descripción", "Estado"]] +
                           [[nom.get(i["de"], i["de"]), nom.get(i["a"], i["a"]), i.get("mecanismo", ""),
                             i.get("descripcion", ""), str(i.get("estado", "")).capitalize()] for i in A["integraciones"]],
                           [ancho_v * x for x in (0.18, 0.18, 0.16, 0.36, 0.12)]))
        if A.get("riesgos"):
            h.append(P("Riesgos", "h2"))
            h.append(tabla([["Riesgo", "Mitigación", "Nivel"]] +
                           [[r["riesgo"], r["mitigacion"], str(r.get("nivel", "")).capitalize()] for r in A["riesgos"]],
                           [ancho_v * 0.42, ancho_v * 0.46, ancho_v * 0.12]))
        if A.get("preguntas"):
            h.append(P("Levantamiento técnico", "h2"))
            h.append(tabla([["Tema", "Pregunta", "Respuesta"]] +
                           [[q.get("tema", ""), q["pregunta"], q.get("respuesta", "")] for q in A["preguntas"]],
                           [ancho_v * 0.16, ancho_v * 0.38, ancho_v * 0.46]))

    # 7. Hoja de ruta
    if d.get("hoja_ruta"):
        h += [CondPageBreak(7 * cm), P("7 · IMPLEMENTACIÓN", "eyebrow"), P("Hoja de ruta", "h1")]
        h.append(tabla([["Fase", "Plazo", "Acciones", "Pasos"]] +
                       [[P(f"<b>{esc(f['fase'])}</b>", "celda"), f.get("plazo", ""),
                         P("<br/>".join("• " + esc(x) for x in f["acciones"]), "celda"), ", ".join(f.get("pasos", []))]
                        for f in d["hoja_ruta"]], [ancho_v * x for x in (0.16, 0.14, 0.55, 0.15)]))

    # 8. Auditoría
    au = d.get("auditoria")
    if au:
        h += [CondPageBreak(6 * cm), P("8 · CONTROL DE CALIDAD", "eyebrow"), P("Auditoría independiente", "h1"),
              P(f"Estado: <b>{esc(au.get('estado'))}</b> · {esc(au.get('fecha', ''))}"), Spacer(1, 6)]
        if au.get("observaciones"):
            h.append(tabla([["Severidad", "Observación", "Acción"]] +
                           [[str(o["severidad"]).capitalize(), o["observacion"], o.get("accion", "")] for o in au["observaciones"]],
                           [ancho_v * 0.14, ancho_v * 0.43, ancho_v * 0.43]))

    # Anexo: inventario
    h += [PageBreak(), P("ANEXO", "eyebrow"), P("Inventario de pasos", "h1")]
    filas = [["ID", "Paso", "Rol", "Estado", "Trabajo", "Espera"]]
    for p in d["pasos"]:
        est = " *" if p.get("estimado") else ""
        filas.append([p["id"], p["nombre"], rol[p["rol"]], P(estado_html(p["estado"]), "celda"),
                      t(p.get("tiempo_min") or 0) + est, t(p.get("espera_min") or 0) + est])
    h.append(tabla(filas, [ancho_v * x for x in (0.07, 0.31, 0.2, 0.16, 0.13, 0.13)]))
    if M["hay_estimados"]:
        h += [Spacer(1, 4), P("* Tiempo estimado; validar con medición.", "gris")]

    doc.build(h)
    print(destino.resolve())


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Uso: generar_informe.py <ruta/flujo.json>")
    construir(sys.argv[1])
