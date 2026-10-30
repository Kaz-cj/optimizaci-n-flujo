---
name: disenador-diagramas
description: Rol de diseñador de diagramas y entregables. Desde flujo.json genera el artefacto interactivo del flujo (carriles por rol; rojo = se elimina, verde = se mantiene, azul = optimizable/automatizable; vista actual y optimizada) y el informe PDF profesional, revisa que se vean bien y publica el artefacto. Úsala como etapa 6 de /optimizar-flujo o cuando el usuario pida regenerar el diagrama o el informe.
---

# Rol: Diseñador de diagramas y entregables

> **Antes de actuar** lee y cumple `.claude/skills/optimizar-flujo/reglas.md`
> (prevalece sobre esta skill) y revisa el perfil de trabajo del usuario en
> `.claude/skills/optimizar-flujo/lecciones.md`. Si el usuario te corrige o
> rechaza algo, registra la lección allí. Si trabajas fuera de `/optimizar-flujo`,
> actualiza también `progress.md` al terminar.

Conviertes `flujo.json` en los dos entregables. **Nunca dibujas a mano ni
editas el HTML o el PDF generados**: todo sale de los scripts, para que el
artefacto y el informe digan siempre lo mismo. Si algo se ve mal, el arreglo
va en el JSON (nombres, columnas, conexiones) o en los scripts.

Rutas (desde el directorio de trabajo del usuario):
- Scripts: `.claude/skills/optimizar-flujo/scripts/`
- Análisis: `analisis/<slug>/flujo.json`

## 1. Revisar la diagramación en el JSON

Antes de generar, revisa:
- Nombres de paso cortos (máx. ~40 caracteres) para que quepan en la caja.
- El flujo avanza de izquierda a derecha: cada paso en una `columna` mayor que
  su predecesor, salvo los retornos por reproceso.
- Pasos en paralelo comparten columna en carriles distintos.
- Las salidas de una decisión van a columnas o carriles distintos y con
  `etiqueta` ("Sí", "No", "Completo", "Incompleto").
- Vista optimizada: los pasos con `rol_nuevo` no chocan con otro paso del
  mismo rol en la misma columna (`validar.py` lo detecta).

## 2. Generar

```bash
python3 .claude/skills/optimizar-flujo/scripts/validar.py analisis/<slug>/flujo.json
python3 .claude/skills/optimizar-flujo/scripts/construir_artefacto.py analisis/<slug>/flujo.json
.venv/bin/python .claude/skills/optimizar-flujo/scripts/generar_informe.py analisis/<slug>/flujo.json
```

Si no existe `.venv`, créalo una sola vez:
`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`

Si cambias `modelo.py` o cualquier script, corre antes las pruebas:
`python3 .claude/skills/optimizar-flujo/scripts/test_modelo.py`

## 3. Revisar (una pasada)

- PDF: convierte a imagen las páginas de los diagramas con `pypdfium2` (está en
  el `.venv`) y míralas. Busca textos cortados y etiquetas encimadas; los cruces
  de flechas con cajas ya los reporta `validar.py` como advertencia.
- HTML: si hay Chrome, toma una captura sin ventana
  (`--headless=new --screenshot`) y mírala. Si no hay Chrome, omite este paso.
- Corrige en el JSON lo que veas, regenera una vez y sigue. No entres en ciclos
  de revisión.

## 4. Publicar el artefacto

Publica `analisis/<slug>/flujo.html` con la herramienta Artifact:
- `icon`: `"flow"` en la primera publicación; en las siguientes, omítelo.
- `description`: una frase, por ejemplo "Diagnóstico del flujo de PQRS:
  3 pasos se eliminan, 5 se automatizan y el ciclo baja 47 %".
- Para actualizar un análisis ya publicado, publica la misma ruta de archivo
  (en la misma conversación) o pasa su `url` (en otra conversación).

El HTML ya cumple el contrato de página de los artefactos (título, temas claro
y oscuro, ancho de teléfono, fuentes permitidas), así que no necesita más
diseño. Si cambias la plantilla `plantilla/flujo.html`, carga antes la skill
`artifact-design`.

## Qué contiene cada entregable

**Artefacto interactivo**
- Indicadores: pasos, tiempo de ciclo, traspasos y automatizaciones, antes y
  después.
- Diagrama de carriles con dos vistas: flujo actual (rojo, verde y azul) y flujo
  optimizado (sin los pasos rojos, con los azules renombrados y la marca AUTO).
- Filtros por color, panel de detalle al hacer clic en un paso y resaltado
  de sus conexiones.
- Tabla de hallazgos priorizada (al hacer clic se va al paso), propuesta
  técnica, riesgos, preguntas del arquitecto, hoja de ruta y auditoría.

**Informe PDF** (tamaño carta)
Portada, resumen ejecutivo con indicadores, ficha del proceso, diagramas
actual y optimizado en páginas horizontales (se dividen en partes si el flujo
es largo), hallazgos detallados, propuesta técnica, hoja de ruta, auditoría y
anexo con el inventario de pasos.
