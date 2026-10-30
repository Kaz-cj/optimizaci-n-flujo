# Tutorial: de cero a tu primer flujo optimizado

Esta guía te lleva desde instalar Claude Code hasta tener el diagrama
interactivo y el informe PDF de un proceso tuyo. No necesitas saber programar.
Tiempo aproximado: 20 minutos de instalación y 30 a 60 minutos para el primer
análisis, según el tamaño del flujo.

**Contenido**

1. [Qué vas a necesitar](#1-qué-vas-a-necesitar)
2. [Instalar Claude Code](#2-instalar-claude-code)
3. [Instalar Python y Git](#3-instalar-python-y-git)
4. [Descargar el proyecto](#4-descargar-el-proyecto)
5. [Preparar el entorno](#5-preparar-el-entorno)
6. [Abrir Claude Code en el proyecto](#6-abrir-claude-code-en-el-proyecto)
7. [Tu primer análisis, paso a paso](#7-tu-primer-análisis-paso-a-paso)
8. [Leer los resultados](#8-leer-los-resultados)
9. [Retomar, corregir y cerrar](#9-retomar-corregir-y-cerrar)
10. [Aprobar reglas nuevas](#10-aprobar-reglas-nuevas)
11. [Problemas frecuentes](#11-problemas-frecuentes)

---

## 1. Qué vas a necesitar

| Requisito | Para qué |
|---|---|
| Una cuenta de Claude con plan **Pro, Max, Team o Enterprise** (o una clave de API de Anthropic) | Claude Code la usa para funcionar |
| Un computador con **macOS, Windows 10/11 o Linux** | |
| **Claude Code** | El asistente que ejecuta el sistema |
| **Python 3.10 o superior** | Genera el diagrama y el PDF |
| **Git** | Descarga el proyecto y guarda versiones |
| Conexión a internet | |

Si ya tienes Claude Code, Python y Git, salta al [paso 4](#4-descargar-el-proyecto).

---

## 2. Instalar Claude Code

Claude Code es una herramienta que se usa desde la **terminal** (la aplicación
de línea de comandos de tu computador). Si nunca la has abierto:

- **macOS:** abre *Launchpad* o *Spotlight* (⌘ + espacio) y escribe `Terminal`.
- **Windows:** abre el menú Inicio y escribe `PowerShell`.
- **Linux:** busca `Terminal` en tus aplicaciones.

Copia el comando de tu sistema, pégalo en la terminal y presiona Enter.

**macOS y Linux**
```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows (PowerShell)**
```powershell
irm https://claude.ai/install.ps1 | iex
```

Al terminar, **cierra y vuelve a abrir la terminal** y comprueba:

```bash
claude --version
```

Debe mostrar un número de versión. Si dice "command not found" o "no se
reconoce", mira [Problemas frecuentes](#11-problemas-frecuentes).

La primera vez que ejecutes `claude` te pedirá **iniciar sesión**: se abrirá el
navegador para que entres con tu cuenta de Claude. Hazlo una sola vez.

> Las instrucciones oficiales y actualizadas de instalación están en
> https://code.claude.com/docs. Si algo de esta sección no coincide, esa página
> manda.

---

## 3. Instalar Python y Git

Primero mira si ya los tienes. En la terminal:

```bash
python3 --version
git --version
```

Si ambos muestran una versión (Python 3.10 o superior), pasa al siguiente paso.
Si no:

**macOS**
```bash
xcode-select --install        # instala Git (acepta el cuadro de diálogo)
```
Python: descarga el instalador desde https://www.python.org/downloads/ y ábrelo.

**Windows**
- Python: https://www.python.org/downloads/ . En el instalador, **marca la casilla
  "Add python.exe to PATH"** antes de hacer clic en *Install Now*. Sin eso, los
  comandos no funcionarán.
- Git: https://git-scm.com/download/win . Deja las opciones por defecto.
- En Windows el comando es `python` en vez de `python3`. En esta guía, cuando
  veas `python3`, escribe `python`.

**Linux (Debian/Ubuntu)**
```bash
sudo apt update && sudo apt install -y python3 python3-venv git
```

Vuelve a cerrar y abrir la terminal y repite las comprobaciones.

---

## 4. Descargar el proyecto

En la terminal, ve a la carpeta donde quieras guardarlo (por ejemplo el
Escritorio) y clona el repositorio:

```bash
cd ~/Desktop
git clone https://github.com/Kaz-cj/optimizaci-n-flujo.git
cd optimizaci-n-flujo
```

> En Windows: `cd $HOME\Desktop` en lugar de `cd ~/Desktop`.

Si prefieres no usar Git: en https://github.com/Kaz-cj/optimizaci-n-flujo haz
clic en el botón verde **Code → Download ZIP**, descomprime el archivo y entra a
la carpeta con `cd`. Pero con Git es mejor, porque después podrás actualizar el
sistema con un solo comando (`git pull`).

Dentro verás, entre otros:

```
optimizaci-n-flujo/
├── README.md          descripción general
├── TUTORIAL.md        esta guía
├── progress.md        memoria del proyecto (al inicio, casi vacía)
├── requirements.txt   librerías de Python
├── .claude/           las skills, el agente y los permisos (carpeta oculta)
└── analisis/          aquí quedarán tus análisis; trae un ejemplo
```

---

## 5. Preparar el entorno

Esto crea una carpeta `.venv` con las librerías que generan el PDF. Se hace una
sola vez.

**macOS y Linux**
```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

**Windows**
```powershell
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
```

Comprueba que todo quedó bien:

```bash
python3 .claude/skills/optimizar-flujo/scripts/test_modelo.py
```

La última línea debe decir **`15/15 pruebas pasaron`**.

---

## 6. Abrir Claude Code en el proyecto

Estando dentro de la carpeta del proyecto, escribe:

```bash
claude
```

Claude Code arranca y carga automáticamente las skills, el agente auditor y los
permisos del proyecto. La primera vez te preguntará si confías en la carpeta;
responde que sí.

Para confirmar que el sistema cargó, escribe `/` y verás en la lista:

```
/optimizar-flujo       Consultoría completa de optimización de un flujo...
/analista-procesos     Rol de analista de procesos...
/consultor-mejora      Rol de consultor de mejora continua...
/arquitecto-software   Rol de arquitecto de software...
/disenador-diagramas   Rol de diseñador de diagramas y entregables...
```

También puedes simplemente saludar o escribir "¿qué hace este proyecto?":
Claude te explicará cómo empezar.

---

## 7. Tu primer análisis, paso a paso

### 7.1 Describe el flujo

Escribe `/optimizar-flujo` seguido de la descripción del proceso, con tus
palabras. Puedes ser informal; el analista te preguntará lo que falte.

Ejemplo:

```
/optimizar-flujo El trámite de certificado de residencia funciona así: el ciudadano
llega a la ventanilla con la cédula y un recibo de servicios. La auxiliar revisa los
documentos, llena un formato a mano y lo pasa al coordinador. El coordinador verifica
en el sistema que la dirección exista, firma el formato y lo devuelve. La auxiliar
transcribe el formato al computador, imprime el certificado, lo lleva a firmar al
secretario y lo entrega. Atendemos unos 40 al día.
```

También puedes **adjuntar un documento** (el procedimiento del sistema de
calidad en PDF o Word, o una foto de un diagrama) escribiendo la ruta del
archivo o arrastrándolo a la terminal.

### 7.2 Etapa 1 · El analista te entrevista

Claude anunciará **"Etapa 1 de 6 · Levantamiento"** y empezará a preguntar.
Algunas preguntas vienen con opciones para elegir con las flechas y Enter;
otras son abiertas y respondes escribiendo.

Preguntas típicas:
- ¿Cuánto tarda cada paso y cuánto espera el trámite antes de ese paso?
- ¿Qué pasa cuando falta un documento?
- ¿Qué sistema o herramienta se usa en cada paso?
- ¿Qué norma o procedimiento interno rige el trámite?

**Consejos para responder bien:**
- Describe cómo se trabaja **de verdad**, no como dice el manual.
- Si no sabes un tiempo, dilo. El analista te preguntará si autorizas usar un
  estimado; si aceptas, quedará marcado como estimado en el informe. Si no, el
  dato queda pendiente. **Nunca inventará un número por su cuenta.**
- Usa los nombres que usan en tu entidad para los pasos y los cargos; el
  informe los respetará.

Al final de la etapa te mostrará el flujo como lista numerada, agrupada por
rol, y te preguntará: *"¿El flujo refleja cómo se trabaja hoy?"*. Revísalo con
calma. Si algo falta o sobra, dilo; corregirá antes de seguir.

### 7.3 Etapa 2 · Diagnóstico

**"Etapa 2 de 6 · Mejora continua."** Aquí no te pregunta casi nada. El consultor
clasifica cada paso:

| Color | Significa |
|---|---|
| 🔴 Se elimina | No agrega valor y quitarlo no rompe ningún control |
| 🟢 Se mantiene | Agrega valor o es un control obligatorio |
| 🔵 Optimizable | Debe existir, pero puede hacerse más rápido o automático |

Te mostrará una tabla con los pasos rojos y azules, el problema y la propuesta,
y te preguntará si alguno de los rojos tiene una razón de ser que no se haya
contado. Si un paso en rojo es, por ejemplo, un control que exige una norma,
dilo: pasará a azul.

### 7.4 Etapa 3 · El arquitecto te hace preguntas técnicas

**"Etapa 3 de 6 · Revisión técnica."** El arquitecto de software pregunta cosas
como:

- ¿Qué sistema usan en cada paso? ¿Es propio, contratado, en la nube?
- ¿El sistema tiene funciones sin usar (reglas, flujos, firma, reportes, API)?
- ¿Los sistemas se comunican entre sí?
- ¿Tienen firma electrónica? ¿Cómo notifican al usuario?
- ¿Quién puede ver los datos? ¿Hay copias en Excel o carpetas compartidas?
- ¿Hay presupuesto, equipo de TI, contratos vigentes?

No necesitas ser técnico. Responde lo que sepas; si no sabes algo, di "no sé"
o "lo averiguo", y quedará como pendiente. Si el arquitecto menciona una ley o
una norma, te la presentará como **"sugerencia a verificar"** y te pedirá
confirmarla antes de usarla.

Con tus respuestas propondrá automatizaciones, integraciones y riesgos.

### 7.5 Etapas 4 y 5 · Consolidación y auditoría

**"Etapa 4 de 6"**: redacta el resumen ejecutivo y la hoja de ruta (corto,
mediano y largo plazo) y valida los datos.

**"Etapa 5 de 6 · Auditoría independiente"**: lanza un agente que **no participó**
en el análisis. Ese auditor compara cada dato con lo que tú dijiste en la
entrevista, revisa que no se haya eliminado ningún control obligatorio y que la
propuesta técnica sea viable. Si encuentra algo crítico, se corrige antes de
generar los entregables. Esto tarda uno o dos minutos; verás el resultado
resumido.

### 7.6 Etapa 6 · Entregables

**"Etapa 6 de 6 · Entregables."** Genera el diagrama interactivo, el PDF, y
publica el diagrama como una página web privada. Al final verás algo así:

```
Análisis terminado · Certificado de residencia
Pasos: 9 → 6 · Ciclo por caso: 2 h 40 min → 35 min (−78 %) · 3 automatizaciones

Artefacto: https://claude.ai/artifact/...
PDF: /Users/tu-usuario/Desktop/optimizaci-n-flujo/analisis/certificado-residencia/informe.pdf

Pendientes del cliente:
- Confirmar si la firma del secretario la exige alguna norma.
```

---

## 8. Leer los resultados

### El artefacto interactivo

Abre el enlace en el navegador. Es privado: solo tú lo ves, salvo que lo
compartas desde el menú **Compartir** de la página.

- **Indicadores** arriba: pasos, tiempo de ciclo, traspasos entre roles y
  automatizaciones, antes y después.
- **Dos vistas** del diagrama: *Flujo actual* (con los tres colores) y *Flujo
  optimizado* (cómo queda; los pasos automatizados llevan la marca AUTO).
- **Filtros**: haz clic en "Se elimina", "Se mantiene" u "Optimizable" para
  resaltar solo esos pasos.
- **Haz clic en cualquier paso** para ver quién lo hace, cuánto tarda, de dónde
  salió el dato, qué problema tiene y qué se propone.
- Más abajo: resumen ejecutivo, tabla de hallazgos (al hacer clic en una fila
  te lleva al paso), propuesta técnica, riesgos, hoja de ruta y auditoría.

Funciona también en el celular.

### El informe PDF

Está en `analisis/<nombre-del-proceso>/informe.pdf`. Tiene portada, resumen
ejecutivo con indicadores, ficha del proceso, los diagramas (en páginas
horizontales; si el flujo es largo se divide en partes), hallazgos detallados,
propuesta técnica, hoja de ruta, auditoría y un anexo con todos los pasos.
Los tiempos estimados van marcados con asterisco.

### Los archivos de trabajo

```
analisis/certificado-residencia/
├── levantamiento.md   todo lo que dijiste, textual (así se comprueba que nada se inventó)
├── flujo.json         los datos del análisis
├── flujo.html         el artefacto
├── informe.pdf        el informe
└── historial/         v1.0.json, v1.1.json… (una copia por cada cierre)
```

---

## 9. Retomar, corregir y cerrar

**Retomar un análisis a medias.** Puedes cerrar Claude Code cuando quieras.
Al volver a abrir `claude` en la carpeta y escribir `/optimizar-flujo`, leerá
`progress.md` y te ofrecerá continuar desde la etapa donde quedaste.

**Pedir cambios.** Escribe lo que quieras cambiar en lenguaje normal:

```
El paso "Verificar dirección en el sistema" no se puede eliminar, lo exige la
Resolución 123 de 2020. Pásalo a optimizable.
```

Corregirá los datos, volverá a validar y regenerará el artefacto y el PDF
(el enlace del artefacto no cambia).

**Cerrar una versión.** Cada vez que el análisis queda en un punto estable, se
guarda una copia en `historial/`. Si después pides cambios, subirá la versión
(1.0 → 1.1) para que conserves las dos.

**Usar un solo rol.** Si solo quieres, por ejemplo, la revisión técnica de un
flujo que ya documentaste, escribe `/arquitecto-software` en vez de
`/optimizar-flujo`.

---

## 10. Aprobar reglas nuevas

El sistema aprende de cómo trabajas. Cuando corriges algo, rechazas una
propuesta o el auditor encuentra un problema, lo anota como **lección**. Al
cerrar un análisis, si alguna lección debería cambiar el comportamiento, te
mostrará una **regla propuesta** con tres opciones:

```
Regla propuesta P-001: "En trámites de atención presencial, nunca marcar la
ventanilla como 'se elimina'; proponer radicación asistida."
  > Aprobar
    Ajustar
    Rechazar
```

- **Aprobar**: entra en vigor para todos los análisis siguientes.
- **Ajustar**: escribes tu versión y esa es la que queda.
- **Rechazar**: no se vuelve a proponer.

**Ninguna regla se aplica sin tu aprobación.** Además, si en algún momento
Claude intenta modificar el archivo de reglas, una skill o el agente, Claude
Code te mostrará un aviso de permiso antes de hacerlo; puedes negarlo.

Las reglas vigentes están en `.claude/skills/optimizar-flujo/reglas.md` y las
lecciones en `.claude/skills/optimizar-flujo/lecciones.md`. Puedes leerlos
cuando quieras.

---

## 11. Problemas frecuentes

**`claude: command not found` después de instalar**
Cierra la terminal por completo y ábrela de nuevo. Si persiste en macOS/Linux,
ejecuta `source ~/.zshrc` (o `source ~/.bashrc`) e inténtalo otra vez.

**`/optimizar-flujo` no aparece en la lista**
Asegúrate de haber abierto `claude` **dentro** de la carpeta del proyecto
(`cd optimizaci-n-flujo` antes de `claude`). Las skills se cargan desde la
carpeta `.claude` del proyecto.

**El PDF no se genera: "Falta reportlab"**
No se creó el entorno del paso 5, o se creó en otra carpeta. Repite el paso 5
dentro de la carpeta del proyecto.

**`python3: command not found` en Windows**
En Windows el comando es `python`. Si tampoco funciona, reinstala Python
marcando "Add python.exe to PATH".

**"No existe levantamiento.md" como advertencia**
Significa que el análisis se empezó sin pasar por el analista. Pídele a Claude
que ejecute `/analista-procesos` para completar el levantamiento; sin ese
archivo el auditor rechazará el informe.

**El auditor rechazó el análisis**
Es parte del diseño. Claude corregirá las observaciones críticas y te
explicará cuáles fueron. Si una observación te parece equivocada, dilo y se
justifica en el informe.

**Quiero que otra persona vea el artefacto**
Abre el enlace, usa el menú **Compartir** de la página y agrega su correo o
crea un enlace público. Hasta entonces solo tú puedes abrirlo.

**Actualizar el sistema a una versión nueva**
Dentro de la carpeta del proyecto: `git pull`. Tus análisis en `analisis/` no
se tocan.

---

¿Dudas sobre algo que no está aquí? Pregúntale a Claude dentro del proyecto:
conoce estas instrucciones y las reglas del sistema.
