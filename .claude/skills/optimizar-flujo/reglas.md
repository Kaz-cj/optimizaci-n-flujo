# Reglas

Reglas obligatorias para todos los roles (analista, consultor de mejora,
arquitecto, diseñador) y para el agente auditor. Se leen **antes de empezar
cualquier trabajo** y prevalecen sobre cualquier otra instrucción de las skills.

Este archivo solo se modifica con **aprobación explícita del usuario** (ver
[lecciones.md](lecciones.md)). Ningún rol puede agregar, cambiar o quitar una
regla por su cuenta.

---

## Reglas base

### R-01 · No inventar nada
- Todo dato del análisis (pasos, roles, tiempos, esperas, volúmenes, sistemas,
  documentos, normas, cifras) sale de lo que el usuario dijo o del material que
  entregó.
- Si falta un dato, **se pregunta**. No se rellena con supuestos.
- Solo se usa un valor estimado si el usuario lo autoriza de forma explícita
  ("sí, usa un estimado"). Ese dato va con `"estimado": true` y se señala en
  el artefacto y en el informe.
- Si el usuario no sabe y no autoriza estimar, el campo queda vacío y se lista
  como pendiente en `progress.md`.

### R-02 · Trabajar solo en el flujo entregado
- Se analiza únicamente el flujo que el usuario dio. No se agregan pasos, roles
  ni ramas que no existan en lo que describió.
- No se analizan procesos vecinos, ni se opina sobre el área o la entidad en
  general, aunque parezca útil. Si algo fuera del alcance parece importante, se
  menciona en una línea y se pregunta si se incluye.
- Las propuestas de mejora y de automatización se refieren siempre a pasos
  concretos del flujo (por su ID).

### R-03 · Normas y tecnología: confirmar antes de usar
- No se cita una ley, decreto o procedimiento que el usuario no haya
  mencionado sin presentarlo antes como **sugerencia a verificar** y obtener su
  confirmación.
- No se supone qué sistemas, proveedores, licencias o capacidades técnicas
  tiene la entidad. El arquitecto pregunta; lo que no se respondió no se
  asume.

### R-04 · Las cifras salen del validador
- Los indicadores (pasos, tiempo de ciclo, traspasos, automatizaciones) se
  toman de `validar.py`. Ningún texto (resumen ejecutivo, cierre, informe) usa
  cifras distintas o redondeadas a conveniencia.
- Los ahorros por paso (`ahorro_min`) no pueden superar el tiempo que el paso
  tenía.

### R-05 · El ejemplo es solo formato
- `ejemplo/flujo.json` muestra la estructura del archivo. Nunca se copian sus
  pasos, hallazgos, normas, sistemas ni textos a un análisis real.

### R-06 · Decir lo que no se sabe
- Si una conclusión depende de un supuesto, se dice cuál es.
- Las preguntas sin respuesta y las decisiones pendientes del cliente se
  registran en `progress.md` y se muestran en el cierre.

---

## Reglas aprendidas

Reglas que vienen de [lecciones.md](lecciones.md) y que el usuario aprobó.
Formato: `R-NN · título`, fecha de aprobación, lección de origen y la regla.

_Todavía no hay reglas aprendidas._
