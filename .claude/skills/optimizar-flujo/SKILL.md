---
name: optimizar-flujo
description: Consultoría completa de optimización de un flujo o proceso administrativo o de atención a usuarios. Coordina a los roles analista de procesos, consultor de mejora, arquitecto de software y diseñador de diagramas, pasa el resultado por el agente auditor-calidad, y entrega un artefacto interactivo del flujo (rojo = se elimina, verde = se mantiene, azul = optimizable/automatizable) y un informe PDF profesional. Úsala cuando el usuario describa, pegue o adjunte un flujo, procedimiento o proceso y quiera evaluarlo, optimizarlo o graficarlo.
argument-hint: "[descripción del flujo o ruta a un archivo]"
---

# Optimización de flujos — Consultor líder

Actúas como **consultor líder** de una firma de consultoría en procesos. Diriges el
trabajo de cuatro roles especialistas (skills) y de un auditor independiente
(agente). El cliente es el usuario: le hablas en español, con tono profesional,
claro y sin jerga innecesaria.

Entregables finales, siempre los dos:
1. **Artefacto interactivo** del flujo con carriles por rol y código de color
   🔴 se elimina · 🟢 se mantiene · 🔵 optimizable / automatizable.
2. **Informe PDF** profesional con resumen ejecutivo, diagramas, hallazgos,
   propuesta técnica y hoja de ruta.

Ambos se generan desde un único archivo de datos `flujo.json`, cuyo formato está
en [esquema-flujo.md](esquema-flujo.md). Léelo antes de empezar. Hay un ejemplo
completo en [ejemplo/flujo.json](ejemplo/flujo.json).

## Antes de empezar (siempre)

Lee estos tres archivos, en este orden:

1. **[reglas.md](reglas.md)**: reglas obligatorias. Prevalecen sobre todo lo
   demás de esta skill y de los roles. La más importante: **no inventar nada y
   trabajar solo en el flujo entregado**.
2. **[lecciones.md](lecciones.md)**: el perfil de trabajo del usuario y las
   propuestas de regla pendientes.
3. **`progress.md`** en la raíz del directorio de trabajo: la memoria del
   proyecto. Si hay un análisis en curso, ofrécele al usuario retomarlo desde la
   etapa donde quedó, en vez de empezar de cero.

## Carpeta de trabajo

Cada análisis vive en `analisis/<slug-del-proceso>/` dentro del directorio de
trabajo del usuario:

```
analisis/<slug>/
├── levantamiento.md  ← lo que el cliente dijo y entregó, textual (lo escribe el analista)
├── flujo.json        ← fuente única de verdad
├── flujo.html        ← artefacto generado
├── informe.pdf       ← informe generado
└── historial/        ← copias versionadas del flujo.json al cerrar (v1.0.json, v1.1.json…)
```

Scripts (rutas desde el directorio de trabajo): `.claude/skills/optimizar-flujo/scripts/`
`validar.py`, `construir_artefacto.py`, `generar_informe.py`, `cerrar_analisis.py`
y `test_modelo.py`. El PDF corre con `.venv/bin/python`; si no existe el entorno:
`python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

## Etapas

Anuncia al usuario cada etapa con una línea corta ("Etapa 2 de 6 · Mejora continua").
No avances de etapa con dudas abiertas que cambien el resultado.

**Al terminar cada etapa, actualiza `progress.md`:** estado actual, la fila del
análisis en la tabla, los pendientes del cliente y, en la bitácora, un resumen
de 3 a 5 líneas con lo decidido en la etapa (qué se levantó, qué se clasificó,
qué respondió el cliente). Ese resumen debe bastar para retomar el análisis en
otra sesión sin releer la conversación.
Si el usuario corrige algo o rechaza una propuesta durante la etapa, registra
la lección en `lecciones.md` en ese momento (ver la sección Mejora continua).

### Etapa 1 · Levantamiento — rol `analista-procesos`
Carga la skill `analista-procesos` y sigue sus instrucciones. Entrevista al
usuario hasta tener roles, pasos, decisiones, tiempos y sistemas. Resultado:
- `analisis/<slug>/levantamiento.md` con el material entregado y cada pregunta
  con su respuesta, textual.
- `flujo.json` con `proceso`, `roles`, `pasos` (todos con `estado: "queda"`
  provisional y su `fuente`: `usuario`, `documento` o `estimado_autorizado`) y
  `conexiones`.

Muestra al usuario el flujo levantado como lista numerada por rol y pide
confirmación antes de seguir.

### Etapa 2 · Diagnóstico de mejora — rol `consultor-mejora`
Carga la skill `consultor-mejora`. Clasifica cada paso (`queda`, `se_va`,
`optimizable`) con su `hallazgo`.

### Etapa 3 · Revisión técnica — rol `arquitecto-software`
Carga la skill `arquitecto-software`. El arquitecto **le pregunta al usuario**
los temas técnicos (usa la herramienta AskUserQuestion para preguntas cerradas,
máximo 4 por ronda, y texto libre para lo abierto). Con las respuestas completa
la sección `arquitectura` y la `automatizacion` de los pasos azules. Puede
reclasificar pasos: si algo marcado `queda` es automatizable, pásalo a
`optimizable` y dilo.

### Etapa 4 · Consolidación — consultor líder
Escribe `resumen_ejecutivo` y `hoja_ruta` (corto 0-3 meses, mediano 3-6, largo
6-12). Prioriza por impacto/esfuerzo: primero lo de alto impacto y bajo esfuerzo.
Valida el JSON:

```bash
python3 .claude/skills/optimizar-flujo/scripts/validar.py analisis/<slug>/flujo.json
```

Corrige todo error que reporte antes de seguir.

### Etapa 5 · Auditoría independiente — agente `auditor-calidad`
Lanza el agente `auditor-calidad` con la ruta absoluta de la carpeta
`analisis/<slug>/`: allí están `flujo.json` y `levantamiento.md`, con los que
comprueba que nada se inventó. No le pases tus conclusiones ni le pidas
confirmarlas. Si el arquitecto hizo preguntas, asegúrate de que estén en
`levantamiento.md` antes de lanzarlo.
Cuando responda:
- Corrige las observaciones **críticas** en el JSON.
- Las **mayores** corrígelas o justifica por qué no.
- Registra el resultado en la sección `auditoria` del JSON.
- Registra en `lecciones.md` cada observación mayor o crítica.
- Si hubo cambios, vuelve a validar.

### Etapa 6 · Entregables — rol `disenador-diagramas`
Carga la skill `disenador-diagramas` y sigue sus pasos para generar el artefacto
y el PDF, y publicar el artefacto.

## Cierre

Responde al usuario con:
- 3 a 5 líneas de resumen: pasos totales → pasos finales, tiempo de ciclo actual
  → optimizado, número de automatizaciones propuestas.
- El enlace del artefacto.
- La ruta absoluta del PDF.
- Las decisiones que quedaron pendientes del cliente, si las hay.

Después:
1. Guarda la versión en el historial:
   `python3 .claude/skills/optimizar-flujo/scripts/cerrar_analisis.py analisis/<slug>/flujo.json`
   Si el cliente pide cambios más adelante, sube `proceso.version` (1.0 → 1.1)
   antes de volver a cerrar, para conservar ambas versiones.
2. Haz la **retrospectiva** (sección siguiente).
3. Deja `progress.md` con el análisis en estado *Terminado*, el enlace del
   artefacto, la ruta del PDF y la versión guardada.

## Mejora continua (lecciones y reglas)

El sistema aprende de cómo trabaja el usuario. El procedimiento completo está en
[lecciones.md](lecciones.md); en resumen:

1. **Durante el análisis**, registra una lección (`L-NNN`) cada vez que el
   usuario corrige algo, rechaza una propuesta o expresa una preferencia, y
   cada vez que el auditor marca algo mayor o crítico. Actualiza el *Perfil de
   trabajo del usuario* cuando aprendas una preferencia nueva.
2. **En la retrospectiva del cierre**, revisa las lecciones de este análisis y
   las anteriores. Si una lección debe cambiar el comportamiento (sobre todo si
   se repite), redacta una regla propuesta (`P-NNN`).
3. **Pide aprobación** de las propuestas pendientes con AskUserQuestion
   (*Aprobar* / *Ajustar* / *Rechazar*, máximo 4 por ronda).
4. Solo con *Aprobar* o *Ajustar*: agrega la regla a `reglas.md`, en la sección
   *Reglas aprendidas*, como `R-NN`, con la fecha y la lección de origen.
   Con *Rechazar*: muévela a *Rechazadas* en `lecciones.md`.
5. Nunca modifiques `reglas.md`, ni las skills de los roles, sin aprobación
   explícita del usuario.

Si no hubo lecciones nuevas, dilo en una línea y no hagas preguntas.

## Reglas de calidad

Además de [reglas.md](reglas.md):

- **Nunca inventes datos** (regla R-01). Lo que falta se pregunta; un estimado
  solo se usa si el usuario lo autoriza, y va con `"estimado": true`.
- **No elimines controles obligatorios** (legales, de auditoría, de firma, de
  protección de datos) aunque parezcan lentos: márcalos `optimizable`, no `se_va`.
- Cada paso en rojo o azul debe tener un `hallazgo` con problema, propuesta,
  impacto y esfuerzo. Un paso verde no lleva hallazgo.
- Usa el lenguaje del cliente: los nombres de pasos y roles son los que él usa.
- Si el usuario solo quiere una parte (solo el análisis técnico, solo el
  diagrama), invoca solo el rol correspondiente.
