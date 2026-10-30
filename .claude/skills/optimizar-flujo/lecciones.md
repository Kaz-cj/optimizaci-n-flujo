# Lecciones

Así mejora el sistema con el uso: aprende cómo trabaja el usuario y lo que sale
bien o mal en cada análisis, y propone reglas nuevas. **Una regla solo entra en
vigor cuando el usuario la aprueba.**

## Ciclo

```
Algo pasa en un análisis
   → se registra como lección (L-NNN)
   → si debe cambiar el comportamiento, se redacta una regla propuesta (P-NNN)
   → se le pide aprobación al usuario
        ├─ aprobada  → se copia a reglas.md (sección "Reglas aprendidas") como R-NN
        ├─ ajustada  → se reescribe con sus palabras y se copia a reglas.md
        └─ rechazada → se mueve a "Rechazadas" y no se vuelve a proponer
```

### Cuándo se registra una lección
- El usuario **corrige** algo (un dato, una clasificación, un nombre, el tono,
  el formato).
- El usuario **rechaza** una propuesta (por ejemplo, un paso en rojo que sí
  debía quedarse).
- El auditor marca una observación **mayor o crítica**.
- La misma observación del auditor o la misma corrección aparece **en dos
  análisis distintos**: esa es la señal más fuerte para proponer una regla.
- El usuario expresa una **preferencia** de trabajo ("siempre pregúntame
  primero por…", "no me muestres…").

### Cómo se pide la aprobación
- Al **cierre** de cada análisis (o antes, si el usuario lo pide), se muestran
  las reglas propuestas pendientes con AskUserQuestion: una pregunta por regla,
  con las opciones *Aprobar*, *Ajustar* (el usuario escribe su versión en
  "Otro") y *Rechazar*. Máximo 4 por ronda.
- Nunca se escribe en `reglas.md` sin una respuesta *Aprobar* o *Ajustar*.
- Las propuestas que cambien una skill de rol (por ejemplo, "el arquitecto
  debe preguntar siempre por X") siguen el mismo camino: se aprueban y se
  agregan como regla, que los roles aplican porque leen `reglas.md`.
- Una regla aprendida **no puede contradecir** las reglas base R-01 a R-06. Si
  la propuesta lo hace, se le dice al usuario cuál regla base cambiaría, y solo
  el usuario decide si la regla base se modifica.

### Cómo se redacta una regla propuesta
- Una sola conducta, verificable: qué se hace, cuándo y en qué rol.
- Con su origen (la lección y el análisis donde ocurrió).
- Sin generalizar de más: si pasó una vez en un tipo de flujo, la regla se
  limita a ese tipo de flujo.

---

## Perfil de trabajo del usuario

Preferencias observadas o dichas por el usuario. Se usan para adaptar la forma
de trabajar (no son reglas; si una preferencia debe ser obligatoria, se propone
como regla).

- Quiere un trabajo profesional, con roles definidos.
- Tipos de flujo: administrativos y de atención a usuarios.
- Código de colores: rojo = se elimina, verde = se mantiene, azul = optimizable
  o automatizable.
- Entregables: artefacto interactivo del flujo e informe PDF.
- Prefiere que el sistema no invente nada y trabaje solo sobre el flujo dado.
- Pide que las mejoras se prueben de punta a punta antes de darlas por hechas
  (2026-10-30): tras cambiar scripts, correr `test_modelo.py` y regenerar el
  ejemplo completo.

---

## Registro de lecciones

Más reciente arriba. Formato:

```
### L-NNN · AAAA-MM-DD · <análisis>
- Qué pasó:
- Origen: corrección del usuario | rechazo | auditor | preferencia | repetición
- Lección:
- Regla propuesta: P-NNN | ninguna
```

_Todavía no hay lecciones._

---

## Reglas propuestas (pendientes de aprobación)

Formato:

```
### P-NNN · <título>
- Origen: L-NNN
- Aplica a: <rol o etapa>
- Regla: <texto>
- Estado: pendiente
```

_No hay propuestas pendientes._

---

## Rechazadas

Propuestas que el usuario rechazó. No se vuelven a proponer salvo que él lo pida.

_Ninguna._
