# Optimización de flujos

Sistema para [Claude Code](https://claude.com/claude-code) que evalúa y optimiza
flujos administrativos y de atención a usuarios como lo haría un equipo de
consultoría: levanta el proceso, diagnostica, revisa la parte técnica, audita
de forma independiente y entrega un **diagrama interactivo** y un **informe PDF**.

```
🔴 se elimina   ·   🟢 se mantiene   ·   🔵 optimizable / automatizable
```

> **¿Primera vez?** Sigue el [**tutorial paso a paso**](TUTORIAL.md): desde
> instalar Claude Code hasta leer tu primer informe.

## Qué recibes en cada análisis

| Entregable | Contenido |
|---|---|
| **Artefacto interactivo** (página web privada) | Indicadores antes/después, diagrama de carriles por rol con las vistas *flujo actual* y *flujo optimizado*, filtros por color, detalle de cada paso, tabla de hallazgos, propuesta técnica, hoja de ruta y resultado de la auditoría |
| **Informe PDF** (tamaño carta) | Portada, resumen ejecutivo, ficha del proceso, diagramas, hallazgos detallados, arquitectura propuesta, hoja de ruta, auditoría y anexo con el inventario de pasos |

Los dos se generan desde un único archivo de datos (`flujo.json`), así que
siempre dicen lo mismo.

## Requisitos

- [Claude Code](https://claude.com/claude-code) instalado.
- Python 3.10 o superior.
- Para el PDF: las librerías de `requirements.txt` (se instalan abajo).

## Instalación

```bash
git clone https://github.com/Kaz-cj/optimizaci-n-flujo.git
cd optimizaci-n-flujo
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt      # Windows: .venv\Scripts\pip install -r requirements.txt
claude
```

Al abrir Claude Code dentro de la carpeta, carga automáticamente las skills, el
agente y los permisos del proyecto. Comprueba que todo funciona:

```bash
python3 .claude/skills/optimizar-flujo/scripts/test_modelo.py
```

Debe terminar con `15/15 pruebas pasaron`.

## Uso

Dentro de Claude Code, en la carpeta del proyecto:

```
/optimizar-flujo  <describe el flujo, pega el procedimiento o adjunta un documento>
```

Por ejemplo:

```
/optimizar-flujo Las solicitudes de certificado llegan por correo a la secretaria,
ella las registra en un Excel, las pasa al coordinador para aprobación, el
coordinador las devuelve firmadas, la secretaria imprime el certificado y lo
envía por correo físico.
```

El sistema te acompaña por seis etapas y **te hace preguntas** en dos de ellas:

| Etapa | Rol | Qué pasa |
|---|---|---|
| 1 · Levantamiento | Analista de procesos | Te entrevista: roles, pasos, decisiones, tiempos, sistemas. Confirmas el flujo antes de seguir. |
| 2 · Diagnóstico | Consultor de mejora | Clasifica cada paso en rojo, verde o azul y documenta el hallazgo. |
| 3 · Revisión técnica | Arquitecto de software | Te pregunta por sistemas, integraciones, firma, notificación, seguridad y volumen; propone automatizaciones. |
| 4 · Consolidación | Consultor líder | Resumen ejecutivo y hoja de ruta por prioridad. |
| 5 · Auditoría | Agente auditor (independiente) | Revisa todo sin haber participado y comprueba que nada se inventó. |
| 6 · Entregables | Diseñador de diagramas | Genera y publica el artefacto y el PDF. |

Cada análisis queda en `analisis/<nombre-del-proceso>/`:

```
analisis/<slug>/
├── levantamiento.md   lo que dijiste, textual (prueba de que nada se inventó)
├── flujo.json         fuente única de verdad
├── flujo.html         artefacto
├── informe.pdf        informe
└── historial/         versiones cerradas (v1.0.json, v1.1.json…)
```

También puedes usar un rol por separado: `/analista-procesos`,
`/consultor-mejora`, `/arquitecto-software` o `/disenador-diagramas`.

## Principios de trabajo

Están en [`.claude/skills/optimizar-flujo/reglas.md`](.claude/skills/optimizar-flujo/reglas.md)
y mandan sobre todo lo demás:

1. **No inventar nada.** Lo que falta se pregunta. Un estimado solo se usa si
   lo autorizas, y queda marcado.
2. **Solo el flujo entregado.** No se agregan pasos ni se analizan otros procesos.
3. **Normas y tecnología se confirman** contigo antes de usarlas.
4. **Las cifras salen del validador**, nunca del texto.
5. **El ejemplo es solo formato.**
6. **Se dice lo que no se sabe.**

El sistema **aprende** de cómo trabajas: registra lecciones en
[`lecciones.md`](.claude/skills/optimizar-flujo/lecciones.md) y, al cierre de
cada análisis, te propone reglas nuevas. Ninguna entra en vigor sin tu
aprobación; además, editar `reglas.md`, las skills o el agente siempre pide
confirmación (`.claude/settings.json`).

`progress.md` es la memoria del proyecto: qué análisis hay, en qué etapa van y
qué quedó pendiente. Puedes cerrar Claude Code y retomar después.

## Ejemplo incluido

`analisis/ejemplo-pqrs/` contiene un análisis completo de un proceso **ficticio**
de atención de PQRS, con su levantamiento, JSON, artefacto, PDF e historial.
Sirve para ver el resultado y como referencia de formato; nunca se copia su
contenido a un análisis real.

## Estructura del proyecto

```
.claude/
├── settings.json                     permisos: cambios a reglas/skills/agente piden confirmación
├── agents/auditor-calidad.md         agente auditor independiente
└── skills/
    ├── optimizar-flujo/              skill coordinadora
    │   ├── SKILL.md                  las seis etapas
    │   ├── reglas.md                 reglas obligatorias (solo cambian con tu aprobación)
    │   ├── lecciones.md              aprendizaje: lecciones → reglas propuestas → aprobación
    │   ├── esquema-flujo.md          formato de flujo.json
    │   ├── ejemplo/                  flujo.json y levantamiento.md de referencia
    │   ├── plantilla/flujo.html      plantilla del artefacto
    │   └── scripts/
    │       ├── modelo.py             validación, flujo optimizado, métricas, diagramación
    │       ├── validar.py            valida flujo.json y muestra las métricas
    │       ├── construir_artefacto.py
    │       ├── generar_informe.py    PDF (reportlab)
    │       ├── cerrar_analisis.py    guarda la versión en historial/
    │       └── test_modelo.py        15 pruebas
    ├── analista-procesos/
    ├── consultor-mejora/
    ├── arquitecto-software/
    └── disenador-diagramas/
analisis/                             un subdirectorio por análisis
progress.md                           memoria del proyecto
requirements.txt
```

## Comandos útiles

```bash
# Validar un análisis y ver sus métricas
python3 .claude/skills/optimizar-flujo/scripts/validar.py analisis/<slug>/flujo.json

# Regenerar los entregables
python3 .claude/skills/optimizar-flujo/scripts/construir_artefacto.py analisis/<slug>/flujo.json
.venv/bin/python .claude/skills/optimizar-flujo/scripts/generar_informe.py analisis/<slug>/flujo.json

# Guardar una versión cerrada
python3 .claude/skills/optimizar-flujo/scripts/cerrar_analisis.py analisis/<slug>/flujo.json
```

## Personalización

- **Criterios de diagnóstico:** `consultor-mejora/SKILL.md` (catálogo de categorías).
- **Preguntas técnicas:** `arquitecto-software/SKILL.md`.
- **Colores y estilo del artefacto:** variables `:root` en `plantilla/flujo.html`.
- **Estilo del PDF:** diccionario `C` y estilos `E` en `scripts/generar_informe.py`.

Después de tocar cualquier script, corre `test_modelo.py`.
