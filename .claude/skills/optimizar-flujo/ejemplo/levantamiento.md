# Levantamiento · Atención de PQRS (ejemplo ficticio)

Este archivo muestra el **formato** del levantamiento. En un análisis real lo
escribe el analista de procesos con las palabras del cliente, sin resumir ni
interpretar. El auditor lo cruza con `flujo.json` para comprobar que nada se
inventó (regla R-01).

## Material entregado

- 2026-10-30 · Descripción verbal del proceso en la sesión (no se entregaron documentos).

## Descripción inicial del cliente (textual)

> Las PQRS nos llegan por correo, por la ventanilla o por el formulario de la
> página. La funcionaria de ventanilla las radica en el gestor documental y les
> pone número. Las que llegan por correo las imprime y las escanea para subirlas.
> Después la coordinadora de atención las clasifica y las manda al área que
> responde. El área hace la respuesta; si es un tema jurídico la manda a la
> oficina jurídica para concepto. El jefe del área da el visto bueno, luego la
> coordinación la vuelve a revisar, se imprime, se firma, se escanea y se envía
> por correo certificado. Al final se anota el cierre en un Excel de control.

## Entrevista · Analista de procesos

| # | Pregunta | Respuesta del cliente | Pasos |
|---|---|---|---|
| 1 | ¿Cuántas solicitudes reciben al mes? | Unas 320. | proceso.volumen |
| 2 | ¿Cuánto tarda radicar y cuánto espera una solicitud antes de radicarse? | Radicar toma unos 10 minutos; en cola puede estar media hora. | P02 |
| 3 | ¿Cuánto tarda imprimir y escanear? | No lo hemos medido. **Autoriza usar un estimado**: "pongan unos 8 minutos y una hora de espera, luego lo medimos". | P03 |
| 4 | ¿Cuánto espera una solicitud en la bandeja de la coordinadora? | En promedio 4 horas; clasificar le toma 5 minutos y asignar otros 5, con unas 2 horas más de cola. | P04, P05 |
| 5 | ¿Cuánto tarda el área en elaborar la respuesta? | Hora y media de trabajo, pero espera unos dos días en la bandeja. | P06 |
| 6 | ¿Y el concepto jurídico? | Una hora de trabajo. La espera no la tenemos medida; **autoriza estimar** tres días. | P08 |
| 7 | ¿El visto bueno del jefe? | 15 minutos, y suele esperar un día. | P09 |
| 8 | ¿La segunda revisión de la coordinación? | 20 minutos, espera un día. En seis meses no ha cambiado nada de fondo. | P10 |
| 9 | ¿Imprimir y firmar? | 10 minutos, pero el documento espera medio día a que el jefe firme. | P11 |
| 10 | ¿El envío? | 15 minutos de alistar y un día hábil de mensajería. | P12 |
| 11 | ¿El registro en Excel? | 5 minutos, a veces se acumula una hora. | P13 |
| 12 | ¿Cuánto le toma al profesional decidir si el caso va a jurídica? | Unos 5 minutos, lo decide al terminar de proyectar. | P07 |
| 13 | ¿Qué normas rigen el proceso? | La Ley 1755 de 2015 del derecho de petición. | proceso.normatividad |

## Entrevista · Arquitecto de software

| # | Pregunta | Respuesta del cliente |
|---|---|---|
| 1 | ¿Qué sistema usan hoy para radicar y tramitar las PQRS? | Un gestor documental web con módulo de PQRS; tiene API REST pero no se ha usado. |
| 2 | ¿Por qué canales llegan las solicitudes y en qué proporción? | Correo 60 %, ventanilla física 25 %, formulario web 15 %. La ventanilla tiene que seguir atendiendo a quien viene en persona. |
| 3 | ¿Cuentan con firma electrónica o digital? | No. El gestor documental ofrece un módulo de firma electrónica que no está contratado. |
| 4 | ¿Dónde se guardan los datos del usuario y quién tiene acceso? | En el gestor documental, con perfiles por área. El Excel de control está en una carpeta compartida sin restricción. |
| 5 | ¿Cómo se controlan los vencimientos? | Manualmente con el Excel; no hay alertas. |
| 6 | Sugerencia a verificar: la notificación electrónica requiere autorización del usuario (Ley 1437 de 2011, art. 56) y la firma electrónica se rige por la Ley 527 de 1999 y el Decreto 2364 de 2012. ¿Confirma que apliquen? | Sí, confirmado por la oficina jurídica. |

## Pendientes

- Medir los tiempos de P03 y P08 (hoy estimados con autorización).
