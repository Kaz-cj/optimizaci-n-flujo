# Progreso del proyecto

Memoria del proyecto de optimización de flujos. La skill `/optimizar-flujo` lo
lee al empezar y lo actualiza al terminar cada etapa, para poder retomar el
trabajo en otra sesión sin perder contexto.

## Estado actual

- **Análisis en curso:** ninguno
- **Etapa:** —
- **Próxima acción:** recibir el primer flujo real del usuario.

## Análisis

| Slug | Proceso | Estado | Etapa | Última actualización | Artefacto | PDF |
|---|---|---|---|---|---|---|
| ejemplo-pqrs | Atención de PQRS (ficticio, de prueba) | Terminado · v1.0 y v1.1 en historial | 6/6 | 2026-10-30 | https://claude.ai/artifact/U9oAGS3Da6qGBVReDo3TL6 | analisis/ejemplo-pqrs/informe.pdf |

Estados: En levantamiento · En diagnóstico · En revisión técnica · En auditoría ·
Terminado · En pausa

## Pendientes del cliente

Datos que faltan, preguntas sin respuesta y decisiones por tomar, por análisis.

_Ninguno._

## Bitácora

Más reciente arriba. Una entrada por sesión o por etapa terminada.

### 2026-10-30 (tarde) · Mejoras de arquitectura
- Permisos: editar `reglas.md`, las skills de rol y el agente ahora pide
  confirmación al usuario (`.claude/settings.json`).
- Trazabilidad: cada análisis lleva `levantamiento.md` (lo que dijo el cliente,
  textual) y cada paso del JSON lleva `fuente`; el validador y el auditor lo
  exigen.
- Los textos de tiempo se formatean una sola vez en Python; el HTML solo pinta.
- Pruebas: `scripts/test_modelo.py` (15 casos). El validador avisa si una
  flecha atraviesa una caja.
- `requirements.txt`, historial de versiones (`cerrar_analisis.py`) y resúmenes
  por etapa en esta bitácora.
- Prueba completa con `ejemplo-pqrs`: validación, artefacto, PDF y cierre sin
  errores. El auditor recibió una copia alterada a propósito (paso inventado,
  tiempo cambiado y norma no confirmada) y detectó las tres como críticas.
- El auditor también encontró inconsistencias reales del ejemplo ("un día"
  codificado como 480 y 1440 min; tiempo de P07 sin respaldo). Se corrigieron y
  el ejemplo pasó a v1.1 (ciclo 10,1 → 6,4 días hábiles, −37 %).

### 2026-10-30
- Se creó el sistema: skill `/optimizar-flujo`, roles `analista-procesos`,
  `consultor-mejora`, `arquitecto-software` y `disenador-diagramas`, y el
  agente `auditor-calidad`.
- Se agregaron `reglas.md`, `lecciones.md` y este `progress.md`.
- Se probó con el flujo ficticio `ejemplo-pqrs`: artefacto y PDF generados.
