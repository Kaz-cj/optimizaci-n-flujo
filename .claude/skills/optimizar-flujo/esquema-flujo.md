# Formato de `flujo.json`

Es la fuente única de verdad del análisis. El artefacto interactivo y el informe
PDF se generan desde aquí; nunca edites el HTML o el PDF a mano.

## Estructura completa

```jsonc
{
  "proceso": {
    "nombre": "Atención de PQRS",               // nombre que usa el cliente
    "codigo": "PR-ATU-04",                      // opcional, código del SGC
    "organizacion": "Nombre de la entidad",
    "area": "Atención al usuario",
    "objetivo": "Responder peticiones dentro del término legal",
    "alcance": "Desde la radicación hasta la respuesta al usuario",
    "disparador": "El usuario radica una PQRS",
    "resultado": "Respuesta de fondo notificada",
    "volumen": "320 solicitudes/mes",           // texto libre
    "normatividad": ["Ley 1755 de 2015"],
    "fecha": "2026-10-30",
    "version": "1.0"
  },

  "roles": [
    { "id": "usuario", "nombre": "Usuario", "tipo": "externo" },   // externo | persona | sistema
    { "id": "ventanilla", "nombre": "Ventanilla única", "tipo": "persona" }
  ],

  "pasos": [
    {
      "id": "P01",                    // único, formato P01, P02…
      "nombre": "Radicar solicitud",  // verbo + objeto, máx. ~40 caracteres
      "rol": "ventanilla",            // id de un rol
      "tipo": "tarea",                // inicio | tarea | decision | fin
      "columna": 1,                   // posición horizontal (1, 2, 3…). Un rol no puede
                                      // tener dos pasos en la misma columna.
      "estado": "queda",              // queda (verde) | se_va (rojo) | optimizable (azul)
      "descripcion": "Qué se hace, con qué insumo y qué produce",
      "tiempo_min": 10,               // tiempo de trabajo efectivo
      "espera_min": 60,               // tiempo en cola antes del paso
      "fuente": "usuario",            // usuario | documento | estimado_autorizado (regla R-01)
      "estimado": false,              // true solo si fuente es estimado_autorizado
      "sistema": "Ventanilla virtual",// sistema o herramienta usada, si hay
      "documentos": ["Formato PQRS"], // opcional

      // Solo en pasos se_va u optimizable:
      "hallazgo": {
        "categoria": "Aprobación redundante",   // ver catálogo en consultor-mejora
        "problema": "Qué está mal y por qué",
        "propuesta": "Qué hacer en su lugar",
        "impacto": "alto",            // alto | medio | bajo
        "esfuerzo": "bajo",           // alto | medio | bajo
        "ahorro_min": 45              // minutos ahorrados por caso
      },

      // Solo en pasos optimizable que se automatizan:
      "automatizacion": {
        "tipo": "Regla de negocio",   // Integración | RPA | Regla de negocio | Formulario digital | Notificación | Firma electrónica | IA
        "descripcion": "Cómo se automatiza",
        "nombre_nuevo": "Clasificación automática", // nombre del paso en la vista optimizada
        "tiempo_nuevo_min": 1,
        "espera_nueva_min": 0
      }
    }
  ],

  "conexiones": [
    { "de": "P01", "a": "P02" },
    { "de": "P03", "a": "P04", "etiqueta": "Sí" }   // etiqueta solo en salidas de decisión
  ],

  "arquitectura": {
    "preguntas": [
      { "tema": "Integraciones", "pregunta": "…", "respuesta": "…" }
    ],
    "sistemas": [
      { "id": "ventanilla", "nombre": "Ventanilla virtual", "tipo": "existente", "descripcion": "…" }
      // tipo: existente | nuevo | a_reemplazar
    ],
    "integraciones": [
      { "de": "ventanilla", "a": "gestor_doc", "mecanismo": "API REST", "descripcion": "…", "estado": "propuesta" }
      // estado: existente | propuesta
    ],
    "propuestas": [
      { "titulo": "…", "descripcion": "…", "pasos": ["P03"], "esfuerzo": "medio" }
    ],
    "riesgos": [
      { "riesgo": "…", "mitigacion": "…", "nivel": "alto" }
    ]
  },

  "resumen_ejecutivo": "Párrafo de 4-6 líneas para la gerencia.",

  "hoja_ruta": [
    { "fase": "Corto plazo", "plazo": "0-3 meses", "acciones": ["…"], "pasos": ["P02", "P05"] },
    { "fase": "Mediano plazo", "plazo": "3-6 meses", "acciones": ["…"], "pasos": [] },
    { "fase": "Largo plazo", "plazo": "6-12 meses", "acciones": ["…"], "pasos": [] }
  ],

  "auditoria": {
    "estado": "aprobado con observaciones",   // aprobado | aprobado con observaciones | rechazado
    "fecha": "2026-10-30",
    "observaciones": [
      { "severidad": "mayor", "observacion": "…", "accion": "Corregido: …" }
      // severidad: critica | mayor | menor
    ]
  }
}
```

## Archivos que acompañan a `flujo.json`

- **`levantamiento.md`**: el material que entregó el cliente y cada pregunta
  con su respuesta, textual, con los pasos a los que alimenta. Es la prueba de
  la regla R-01: cada dato del JSON debe poder rastrearse hasta aquí. Formato
  en [ejemplo/levantamiento.md](ejemplo/levantamiento.md).
- **`historial/vX.Y.json`**: copias del `flujo.json` al cerrar cada versión
  (`cerrar_analisis.py`).

## Reglas

- Todo paso lleva `fuente`. Un paso con `"estimado": true` lleva
  `"fuente": "estimado_autorizado"`, y viceversa; el validador lo exige.
- `id` de pasos únicos; toda conexión apunta a pasos existentes.
- Exactamente un paso `inicio` y al menos un `fin`.
- Una `decision` tiene dos o más salidas, todas con `etiqueta`.
- No puede haber dos pasos del mismo `rol` en la misma `columna`.
- Un paso `se_va` u `optimizable` lleva `hallazgo`. Un `queda` no.
- Pasos `inicio` y `fin` siempre son `queda`.
- Cuando un paso `se_va`, el diagrama optimizado une automáticamente sus
  predecesores con sus sucesores. Revisa que eso tenga sentido; si no, ajusta
  las conexiones o el estado.
- El validador avisa si una flecha atraviesa la caja de otro paso; se corrige
  moviendo ese paso de columna o carril.

## Métricas que se calculan solas

El validador, el artefacto y el PDF calculan:
- Pasos actuales vs. pasos en el flujo optimizado.
- Tiempo de ciclo = `tiempo_min + espera_min` sumados por la ruta más larga
  del inicio al fin (peor caso en las decisiones; los retornos no se cuentan).
- En el optimizado no están los pasos `se_va`, y los `optimizable` usan
  `tiempo_nuevo_min + espera_nueva_min` (o restan `ahorro_min` si no hay
  automatización).
- Días hábiles = jornadas de 8 horas.
- Traspasos entre roles (conexiones que cambian de carril) antes y después.
