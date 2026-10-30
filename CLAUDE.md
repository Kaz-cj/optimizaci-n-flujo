# Proyecto: Optimización de flujos

Este repositorio es un sistema de consultoría de procesos para Claude Code. Las
instrucciones completas están en `README.md` y la guía para principiantes en
`TUTORIAL.md`; léelos si no los conoces. Si el usuario parece nuevo (pregunta
cómo instalar algo, qué es una terminal, cómo empezar), remítelo al tutorial y
acompáñalo paso a paso.

## Primera interacción en una sesión

Si el usuario saluda, pregunta qué hace este proyecto o escribe algo que no sea
una orden concreta, preséntale en pocas líneas:

1. Qué hace: evalúa y optimiza flujos administrativos y de atención a usuarios,
   y entrega un diagrama interactivo (rojo = se elimina, verde = se mantiene,
   azul = optimizable) y un informe PDF.
2. Cómo empezar: `/optimizar-flujo` seguido de la descripción del flujo, el
   texto del procedimiento o un documento adjunto.
3. Que el sistema le hará preguntas (analista y arquitecto) y que puede retomar
   un análisis a medias porque `progress.md` guarda el estado.
4. Si `.venv` no existe, cómo crearlo:
   `python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`.

Si ya hay un análisis en curso en `progress.md`, ofrécele retomarlo.

## Reglas del proyecto

- `.claude/skills/optimizar-flujo/reglas.md` manda sobre cualquier otra
  instrucción. Resumen: no inventar nada, trabajar solo en el flujo entregado,
  confirmar normas y tecnología, cifras solo del validador.
- `reglas.md`, las skills y el agente solo se modifican con aprobación explícita
  del usuario (los permisos del proyecto lo exigen).
- Los entregables (`flujo.html`, `informe.pdf`) nunca se editan a mano: se
  regeneran desde `flujo.json` con los scripts.
- Después de cambiar cualquier script, correr
  `python3 .claude/skills/optimizar-flujo/scripts/test_modelo.py`.
- El PDF se genera con `.venv/bin/python` (reportlab).
