<p align="center">
  <h1 align="center">az-skills</h1>
  <p align="center">
    Un conjunto curado de habilidades que uso con mis agentes. Siéntete libre de tomar lo que te sea útil.
  </p>
</p>

<p align="center">
  <a href="#install">Instalar</a> &nbsp;&middot;&nbsp;
  <a href="#whats-inside">Habilidades</a> &nbsp;&middot;&nbsp;
  <a href="#update">Actualizar</a>
</p>

---

Cada habilidad es un pequeño paquete de instrucciones y código que le da a un agente una nueva capacidad: como reparar pipelines de CI fallidos, explorar problemas desde múltiples ángulos, o limpiar código desordenado. Este repositorio se actualiza a medida que construyo y refino nuevas habilidades.

## Instalar

```bash
git clone https://github.com/zvadaadam/az-skills.git
cd az-skills
./scripts/install.sh
```

Esto conecta las habilidades con tu agente. Solo necesitas hacerlo una vez.

## Actualizar

Toma la última versión y ya está todo listo: las nuevas y mejoradas habilidades se cargan automáticamente:

```bash
cd az-skills
git pull
```

## Desinstalar

```bash
./scripts/uninstall.sh
```

---

## Qué hay dentro

### Ingeniería
- **call-advisor** — Llama al asesor premium de Fable a través de Claude Code CLI para juicios difíciles, crítica de arquitectura y frontend/diseño, con sesiones reanudables y artefactos de salida guardados
- **call-worker** — Llama al trabajador Codex GPT-5.5 a través de Codex CLI para implementación limpia de código, exploración de repositorios, pruebas y tareas de ingeniería acotadas
- **code-review** — Revisión multi-lente de código con 3 sub-agentes paralelos (correctitud, seguridad, diseño) que valida y reporta solo hallazgos de alta señal
- **devs-roundtable** — 5 legendarios ingenieros (Carmack, Hickey, Metz, Torvalds, Beck) debaten tu problema en paralelo, luego construyen consenso
- **code-simplifier** — Revisa código en busca de claridad y mantenibilidad, luego lo limpia
- **deslop** — Detecta y elimina código de mala calidad generado por IA (abstracciones innecesarias, sobreingeniería, patrones verbosos)
- **pre-factor** — Se dispara automáticamente antes de una característica o cambio no trivial: mapea el código donde aterrizará el cambio y expone las refactorizaciones preparatorias que facilitan el cambio (remodelar la costura, agregar una red de seguridad, eliminar duplicación) — cada una rastreada al cambio venidero, aterrizada como su propio commit primero. El antepenúltimo libro a `complexity-check`
- **skill-feedback** — Ayudante de telemetría compartido usado por cada habilidad; envía retroalimentación concisa más eventos de lectura/activación de habilidades directamente a PostHog, con ganchos automáticos en Claude Code e IDs de instalación anónimos para recuentos de instalaciones activas

### Diseño
- **design-roundtable** — 5 legendarios diseñadores (Rams, Ive, Vignelli, Fukasawa, Jongerius) debaten tu brief en paralelo, luego construyen consenso

### Marketing
- **brand-name-explore** — Genera nombres para productos/empresas usando múltiples personajes creativos (metodología Lexicon, poeta, lingüista, hacker cultural, futurista)
- **ai-answer-audit** — Reverse-engineera una respuesta "mejor X" de IA de regreso a las búsquedas, fuentes y suposiciones detrás de ella: un libro de evidencias, una separación capa de modelo vs contenido, el camino de búsqueda multi-hopp, y qué afirmaciones son suposiciones sin soporte del modelo. Ejecutable por el usuario y de solo lectura: nunca altera la respuesta
- **geo-optimize** — Convierte un `ai-answer-audit` en un plan priorizado para que una marca sea citada en respuestas de IA (ChatGPT, Perplexity, Google AI Overviews): brecha de autoridad, cuatro palancas (get-cited / fix-open-territory / open-a-lane / upgrade-evidence), movimientos por motor, y un road map Fast Wins / Roadmap / Backlog

### DevOps
- **greenlight-pr** — Toma un PR, corrige fallos de CI, aborda comentarios de revisión, e itera hasta que todo pase

### Productividad
- **interview-me** — Entrevista contigo sobre un plan o diseño hasta que tenga todo el contexto para construir la cosa correcta
- **plan-for-goal** — Convierte el contexto de conversación en un solo prompt para el bucle de orquestación `/goal` de un agente de codificación: resultado direccional, línea de calidad, y un camino de auto-verificación que el bucle puede iterar contra
