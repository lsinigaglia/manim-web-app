# Tiny Manim Web App - Documentazione Completa

## Indice
1. [Panoramica](#panoramica)
2. [Architettura del Sistema](#architettura-del-sistema)
3. [Come Funziona](#come-funziona)
4. [Componenti Principali](#componenti-principali)
5. [Flusso di Generazione](#flusso-di-generazione)
6. [API e Endpoint](#api-e-endpoint)
7. [Sistema di Esempi](#sistema-di-esempi)
8. [Gestione Errori](#gestione-errori)
9. [Installazione e Configurazione](#installazione-e-configurazione)
10. [Utilizzo](#utilizzo)
11. [Struttura dei File](#struttura-dei-file)
12. [Sicurezza](#sicurezza)
13. [Limitazioni](#limitazioni)
14. [Troubleshooting](#troubleshooting)

---

## Panoramica

**Tiny Manim Web App** è un'applicazione web che permette di generare animazioni matematiche utilizzando Manim Community attraverso prompt testuali. L'app utilizza l'intelligenza artificiale (Claude Sonnet 4.5 di Anthropic) per convertire descrizioni in linguaggio naturale in codice Manim funzionante.

### Caratteristiche Principali
- Generazione di animazioni da prompt testuali
- Interfaccia web semplice e intuitiva
- Rendering programmatico locale (no Docker, no subprocess)
- Sistema di esempi curati per guidare la generazione
- Correzione automatica degli errori
- Preview video in tempo reale

---

## Architettura del Sistema

L'applicazione è costruita con un'architettura a tre livelli:

```
┌─────────────────────────────────────────────────┐
│           Frontend (HTML/JS)                    │
│  - Interfaccia utente                           │
│  - Player video                                 │
│  - Gestione eventi                              │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           Backend (FastAPI)                     │
│  - Routing HTTP                                 │
│  - Validazione richieste                        │
│  - Orchestrazione componenti                    │
└─────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────┐
│           Servizi Core                          │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  Generator   │  │   Renderer   │            │
│  │  (LLM)       │  │   (Manim)    │            │
│  └──────────────┘  └──────────────┘            │
│  ┌──────────────────────────────────┐          │
│  │    Example Manager               │          │
│  │    (Ricerca e retrieval)         │          │
│  └──────────────────────────────────┘          │
└─────────────────────────────────────────────────┘
```

### Stack Tecnologico
- **Backend**: FastAPI (Python 3.11+)
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **LLM**: Claude Sonnet 4.5 (Anthropic API)
- **Rendering**: Manim Community v0.18.0 (programmatico, no container)
- **Storage**: Filesystem (no database)

---

## Come Funziona

### Flusso Generale

```
1. UTENTE digita un prompt
   ↓
2. FRONTEND invia POST /generate
   ↓
3. BACKEND seleziona esempi rilevanti
   ↓
4. GENERATOR (LLM) crea codice Manim
   ↓
5. BACKEND salva scene.py
   ↓
6. RENDERER esegue Manim programmaticamente
   ↓
7. BACKEND copia video in latest.mp4
   ↓
8. FRONTEND mostra video nel player
```

### Esempio Concreto

**Input**: "Plot y = sin(x) on axes and animate a dot moving along it"

**Processo**:
1. ExampleManager cerca esempi correlati (trova "01_axes_plot" e "05_moving_dot")
2. ManimGenerator costruisce un prompt con sistema + esempi + richiesta utente
3. Claude genera JSON con: imports, scene_code, plan, notes
4. Il codice viene salvato in `generated/scene.py`
5. ManimRenderer carica dinamicamente il modulo e chiama scene.render()
6. Manim genera video in `generated/media/videos/720p30/`
7. Il video finale viene copiato in `generated/latest.mp4`
8. L'interfaccia mostra il video con `/video/latest.mp4`

---

## Componenti Principali

### 1. ManimGenerator (`app/generator.py`)

**Responsabilità**: Generazione di codice Manim tramite LLM

**Metodi Chiave**:

```python
async def generate(prompt: str, examples: List[Dict]) -> Dict
```
- Prende il prompt utente e gli esempi
- Costruisce il system prompt con regole e vincoli
- Chiama Claude Sonnet 4.5 con API Anthropic
- Estrae JSON dalla risposta
- Costruisce il file scene.py completo

**Formato Output**:
```json
{
    "status": "success",
    "plan": "Step-by-step plan",
    "scene_code": "Complete Python code",
    "notes": "Assumptions and tweaks"
}
```

```python
async def fix_error(original_code: str, prompt: str, traceback: str) -> Dict
```
- Analizza l'errore dal traceback
- Genera una patch minimale
- Ritorna il codice corretto completo

**System Prompt**: Include regole critiche come:
- Usare SOLO Manim Community v0.18.0
- Animazioni brevi (8-15 secondi)
- NO Text, MathTex, Tex (LaTeX non configurato)
- Output JSON stretto
- Una sola classe Scene

### 2. ManimRenderer (`app/renderer.py`)

**Responsabilità**: Rendering programmatico delle scene Manim

**Metodi Chiave**:

```python
async def render(scene_path: Path) -> Dict
```
- Legge il file scene.py
- Estrae il nome della classe Scene
- Importa dinamicamente il modulo con importlib
- Configura ffmpeg via imageio-ffmpeg
- Usa `tempconfig` di Manim per configurazione temporanea
- Instanzia e renderizza la scena
- Trova il video generato (escludendo partial_movie_files)
- Copia in latest.mp4

**Caratteristiche Importanti**:
- **Nessun subprocess**: tutto in-process per prestazioni migliori
- **Gestione file locks Windows**: retry con timeout per permessi
- **Cleanup automatico**: rimuove media dir tra render
- **Configurazione dinamica**: usa tempconfig per non modificare config globale

### 3. ExampleManager (`app/examples.py`)

**Responsabilità**: Gestione esempi curati

**Metodi Chiave**:

```python
def list_examples() -> List[Dict]
```
- Carica tutti gli esempi da `examples/`
- Legge metadata (meta.json), code (example.py), notes (notes.md)
- Ritorna lista completa con cache

```python
def search_examples(query: str, max_results: int = 2) -> List[Dict]
```
- Keyword matching semplice
- Scoring su: nome, tags, notes
- Ritorna i migliori N esempi

**Struttura di un Esempio**:
```
examples/01_axes_plot/
├── meta.json       # Nome, tags, difficoltà, descrizione
├── example.py      # Codice Manim
└── notes.md        # Note tecniche
```

### 4. FastAPI Server (`app/main.py`)

**Responsabilità**: HTTP routing e orchestrazione

**Endpoint**:

| Endpoint | Metodo | Descrizione |
|----------|--------|-------------|
| `/` | GET | Serve interfaccia HTML |
| `/examples` | GET | Lista esempi disponibili |
| `/generate` | POST | Genera animazione da prompt |
| `/fix` | POST | Corregge errori di compilazione |
| `/video/latest.mp4` | GET | Stream video renderizzato |

**Modelli Pydantic**:
```python
class GenerateRequest(BaseModel):
    prompt: str
    example_ids: Optional[List[str]] = None

class GenerateResponse(BaseModel):
    status: str
    video_url: Optional[str] = None
    plan: Optional[str] = None
    errors: Optional[str] = None
    code: Optional[str] = None
```

### 5. Frontend (`app/templates/index.html`)

**Responsabilità**: Interfaccia utente

**Componenti UI**:
- **Textarea**: Input prompt utente
- **Select**: Dropdown esempi (auto-select o manuale)
- **Buttons**: Generate, Fix Error
- **Video Player**: Preview MP4
- **Debug Panel**: Mostra plan/code/errori

**Funzionalità JavaScript**:
```javascript
async function generate()
```
- Invia POST /generate
- Gestisce loading state
- Mostra video o errori
- Abilita button "Fix" se errore

```javascript
async function fixError()
```
- Invia POST /fix con traceback
- Re-renderizza e mostra risultato

**UX Features**:
- Ctrl+Enter per submit
- Cache-busting per video (timestamp query param)
- Loading spinner durante rendering
- Colori: successo (verde), errore (rosso)

---

## Flusso di Generazione

### Step-by-Step Dettagliato

#### 1. Input Utente
```javascript
// Frontend
const prompt = "Create a circle that transforms into a square"
const exampleIds = null  // Auto-select
```

#### 2. Backend Riceve Richiesta
```python
# app/main.py - /generate endpoint
@app.post("/generate")
async def generate(req: GenerateRequest):
    # Carica esempi
    if req.example_ids:
        example_snippets = [examples_manager.get_example(id)
                           for id in req.example_ids]
    else:
        # Auto-select basato su keyword
        example_snippets = examples_manager.search_examples(
            req.prompt, max_results=2
        )
```

#### 3. Generazione Codice
```python
# app/generator.py
result = await generator.generate(prompt, example_snippets)

# Internamente:
# 1. Build system prompt con esempi
system_prompt = """
You are a Manim Community expert...
[regole e vincoli]
[esempio 1 code]
[esempio 2 code]
"""

# 2. Call Claude API
response = await self.client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    system=system_prompt,
    messages=[{"role": "user", "content": prompt}]
)

# 3. Extract JSON
content = response.content[0].text
result = self._extract_json(content)  # Regex su ```json{...}```

# 4. Build scene file
scene_code = f'''"""
Generated Manim scene.
Notes: {result['notes']}
"""

{result['imports']}

{result['scene_code']}
'''
```

#### 4. Salvataggio su Disco
```python
scene_path = GENERATED_DIR / "scene.py"
scene_path.write_text(result["scene_code"], encoding="utf-8")
```

#### 5. Rendering
```python
# app/renderer.py
render_result = await renderer.render(scene_path)

# Internamente:
# 1. Importa modulo dinamicamente
spec = importlib.util.spec_from_file_location("generated_scene", scene_path)
scene_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scene_module)

# 2. Get classe Scene
scene_class = getattr(scene_module, "MyScene")

# 3. Configura e renderizza
import imageio_ffmpeg
from manim import config, tempconfig

with tempconfig({
    "ffmpeg_executable": imageio_ffmpeg.get_ffmpeg_exe(),
    "quality": "medium_quality",
    "disable_caching": True,
    "output_file": "output",
    "media_dir": str(media_dir)
}):
    scene = scene_class()
    scene.render()

# 4. Trova video (skip partial_movie_files)
output_video = None
for video_file in media_dir.rglob("*.mp4"):
    if "partial_movie_files" not in str(video_file):
        output_video = video_file
        break

# 5. Copia in latest.mp4
shutil.copy(output_video, GENERATED_DIR / "latest.mp4")
```

#### 6. Response al Frontend
```python
return GenerateResponse(
    status="success",
    video_url=f"/video/latest.mp4?t={timestamp}",
    plan=result["plan"],
    code=result["scene_code"]
)
```

#### 7. Display Video
```javascript
// Frontend
const videoSource = document.getElementById('videoSource');
videoSource.src = result.video_url;  // latest.mp4?t=timestamp
videoPreview.load();
```

---

## API e Endpoint

### POST /generate

**Request**:
```json
{
    "prompt": "Plot a parabola and show its vertex",
    "example_ids": ["01_axes_plot"]  // Optional
}
```

**Response Success**:
```json
{
    "status": "success",
    "video_url": "/video/latest.mp4?t=1234567890",
    "plan": "1. Create axes\n2. Plot parabola\n3. Add vertex dot",
    "code": "from manim import *\n\nclass MyScene(Scene):\n    ..."
}
```

**Response Error**:
```json
{
    "status": "error",
    "errors": "Traceback (most recent call last):\n  ...",
    "plan": "1. ...",
    "code": "from manim import *\n..."
}
```

### POST /fix

**Request**:
```json
{
    "prompt": "Original prompt",
    "traceback": "Error traceback from first attempt"
}
```

**Response**: Stesso formato di /generate

**Logica**:
1. Legge scene.py corrente
2. Invia a LLM: codice + prompt + traceback
3. LLM analizza e corregge con patch minimale
4. Salva codice corretto
5. Re-renderizza
6. Ritorna risultato

### GET /video/latest.mp4

**Response**: Binary MP4 stream

**Headers**:
```
Content-Type: video/mp4
Cache-Control: no-cache
```

**Note**: Query param `?t=timestamp` per cache-busting

### GET /examples

**Response**:
```json
[
    {
        "id": "01_axes_plot",
        "name": "Axes and Function Plot",
        "tags": ["axes", "plot", "function"],
        "difficulty": "easy",
        "description": "Basic plotting with sine waves",
        "code": "from manim import *...",
        "notes": "Uses Axes object..."
    },
    ...
]
```

---

## Sistema di Esempi

### Struttura Directory

```
examples/
├── 01_axes_plot/
│   ├── meta.json
│   ├── example.py
│   └── notes.md
├── 02_riemann_sums/
│   ├── meta.json
│   ├── example.py
│   └── notes.md
├── 03_vector_addition/
│   ├── meta.json
│   ├── example.py
│   └── notes.md
├── 04_transform_shapes/
│   ├── meta.json
│   ├── example.py
│   └── notes.md
└── 05_moving_dot/
    ├── meta.json
    ├── example.py
    └── notes.md
```

### File meta.json

```json
{
    "name": "Axes and Function Plot",
    "tags": ["axes", "plot", "function", "sine"],
    "difficulty": "easy",
    "description": "Demonstrates how to create axes and plot a function"
}
```

### File example.py

```python
from manim import *

class AxesPlotExample(Scene):
    def construct(self):
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 2, 1],
            axis_config={"color": BLUE}
        )
        graph = axes.plot(lambda x: np.sin(x), color=YELLOW)
        self.play(Create(axes))
        self.play(Create(graph))
```

### File notes.md

```markdown
Uses Axes object for coordinate system.
Demonstrates basic function plotting.
Suitable for calculus visualizations.
```

### Algoritmo di Ricerca

**Scoring System**:
```python
score = 0
if query in example.name.lower():
    score += 10
for tag in example.tags:
    if query in tag.lower():
        score += 5
if query in example.notes.lower():
    score += 2
```

**Esempio**:
- Query: "plot function"
- 01_axes_plot: score = 10 (name) + 5 (tag "plot") + 5 (tag "function") = 20
- 03_vector_addition: score = 0

---

## Gestione Errori

### Tipi di Errori

#### 1. Errori di Generazione LLM
- **Causa**: API key mancante, rate limit, JSON malformato
- **Handling**: Ritorna errore immediato al frontend
- **Response**: `{status: "error", errors: "Generation failed: ..."}`

#### 2. Errori di Compilazione Python
- **Causa**: Syntax error, import mancante
- **Handling**: Cattura traceback, mostra al frontend, abilita "Fix"
- **Response**: Include codice + plan + errori

#### 3. Errori di Rendering Manim
- **Causa**: API incompatibile, attributo mancante, ffmpeg fallito
- **Handling**: Stesso di compilazione, traceback completo
- **Fix Strategy**: LLM legge traceback e corregge API calls

#### 4. Errori File System
- **Causa**: Permessi, file locks (Windows)
- **Handling**: Retry con backoff (max 3 tentativi)
- **Fallback**: Log warning, continua se possibile

### Flusso di Fix

```
1. USER click "Fix Error"
   ↓
2. FRONTEND send POST /fix
   {
       prompt: "original prompt",
       traceback: "Python traceback..."
   }
   ↓
3. BACKEND read generated/scene.py
   ↓
4. GENERATOR call fix_error()
   System Prompt:
   "You are a Manim expert fixing compilation errors.
    Make the SMALLEST possible change.
    Return complete fixed code."
   ↓
5. LLM analyze traceback
   - Identifica linea problematica
   - Corregge API call (es. Text → Circle)
   - Ritorna codice completo
   ↓
6. BACKEND overwrite scene.py
   ↓
7. RENDERER re-render
   ↓
8. SUCCESS or ERROR (max 1 retry)
```

### Example Error Fix

**Original Code**:
```python
text = Text("Hello")  # LaTeX not configured!
```

**Traceback**:
```
FileNotFoundError: LaTeX executable not found
```

**LLM Fix**:
```python
circle = Circle()  # Rimpiazza Text con shape
```

---

## Installazione e Configurazione

### Requisiti

- Python 3.11+
- pip
- Anthropic API Key

### Dipendenze Python

```txt
fastapi
uvicorn[standard]
anthropic
python-dotenv
manim
imageio-ffmpeg
jinja2
pydantic
```

### Setup Step-by-Step

#### 1. Clone Repository
```bash
git clone <repository-url>
cd manim-web-app
```

#### 2. Crea Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oppure
venv\Scripts\activate  # Windows
```

#### 3. Installa Dipendenze
```bash
pip install -r requirements.txt
```

#### 4. Configura API Key

Crea file `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

Oppure esporta variabile:
```bash
export ANTHROPIC_API_KEY='sk-ant-api03-your-key-here'
```

#### 5. Verifica Installazione

```bash
python -c "import manim; print(manim.__version__)"
# Output: 0.18.0 (o versione installata)

python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
# Output: path/to/ffmpeg
```

---

## Utilizzo

### Avvio Server

```bash
python -m app.main
```

Output atteso:
```
============================================================
Starting Tiny Manim Web App
============================================================
Server: http://localhost:8000
Generated files: C:\...\manim-web-app\generated
============================================================

INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Utilizzo Interfaccia Web

1. Apri browser: `http://localhost:8000`
2. Digita prompt: "Create a circle that morphs into a square"
3. (Opzionale) Seleziona esempio di riferimento
4. Click "Generate Animation"
5. Attendi rendering (10-30 secondi)
6. Guarda video nel player
7. Se errore, click "Fix Error" per correzione automatica

### Esempi di Prompt

**Base**:
- "Plot y = x^2 on axes"
- "Create a red circle and a blue square"
- "Animate a dot moving in a circle"

**Avanzati**:
- "Show Riemann sum rectangles for integral of x^2"
- "Demonstrate vector addition with arrows"
- "Transform a square into a circle with rotation"

**Con Vincoli**:
- "Create axes and plot sine, keep it simple"
- "Animate shapes without text labels"
- "Show geometric transformation in 10 seconds"

---

## Struttura dei File

```
manim-web-app/
├── app/
│   ├── __init__.py           # Package init
│   ├── main.py               # FastAPI server (226 righe)
│   ├── generator.py          # LLM integration (253 righe)
│   ├── renderer.py           # Manim rendering (180 righe)
│   ├── examples.py           # Example manager (121 righe)
│   └── templates/
│       └── index.html        # Frontend UI (403 righe)
│
├── examples/                 # Curated examples
│   ├── 01_axes_plot/
│   ├── 02_riemann_sums/
│   ├── 03_vector_addition/
│   ├── 04_transform_shapes/
│   └── 05_moving_dot/
│
├── generated/                # Runtime files (gitignored)
│   ├── scene.py              # Generated code
│   ├── latest.mp4            # Last rendered video
│   └── media/                # Manim output dir
│
├── requirements.txt          # Python dependencies
├── .env                      # API key (gitignored)
├── .env.example              # Template for API key
├── README.md                 # This file
├── PROJECT_STATUS.md         # Project summary
└── STRUCTURE.txt             # File tree
```

### File Importanti

**app/main.py**:
- Entry point dell'applicazione
- Definisce tutti gli endpoint
- Gestisce lifecycle FastAPI

**app/generator.py**:
- Prompt engineering per Claude
- JSON parsing e validation
- Error fixing logic

**app/renderer.py**:
- Import dinamico moduli Python
- Configurazione Manim programmatica
- File handling e cleanup

**app/examples.py**:
- Loading esempi da filesystem
- Keyword search
- Caching in memoria

**app/templates/index.html**:
- Single-page application
- Dark theme UI
- Async fetch API calls

---

## Sicurezza

### Misure Implementate

#### 1. Rendering Locale (No Network)
- Nessun accesso esterno durante rendering
- Processo completamente locale
- No container, ma stesso livello di isolamento

#### 2. Validazione Input
```python
class GenerateRequest(BaseModel):
    prompt: str  # Pydantic validation
    example_ids: Optional[List[str]] = None
```

#### 3. Sanitizzazione Codice
- LLM istruito a generare solo codice Manim
- No `import os`, `import subprocess`, etc.
- No file I/O esterno

#### 4. File System Isolation
```python
# Solo lettura da examples/
# Solo scrittura in generated/
BASE_DIR = Path(__file__).parent.parent
GENERATED_DIR = BASE_DIR / "generated"
```

#### 5. Error Handling Robusto
```python
try:
    # Rendering code
except Exception as e:
    return {"status": "error", "error": str(e)}
```

### Considerazioni

**NON implementato** (per design minimal):
- Autenticazione/autorizzazione
- Rate limiting
- Input sanitization avanzata
- Sandboxing OS-level

**Uso raccomandato**: Solo locale, trusted users

---

## Limitazioni

### By Design

1. **Single User**: Un solo render alla volta
2. **No Database**: Tutto su filesystem
3. **No Queue**: Rendering sequenziale
4. **Fixed Version**: Manim v0.18.0 hardcoded
5. **Local Only**: Non pensato per deployment cloud
6. **No History**: Ogni render sovrascrive latest.mp4

### Tecniche

1. **LaTeX Not Configured**:
   - NO Text, MathTex, Tex
   - Solo shape-based animations

2. **Rendering Lento**:
   - Manim è computazionally intensive
   - 10-30 secondi per animazione semplice
   - No progress bar

3. **LLM Non Deterministico**:
   - Stesso prompt può generare codice diverso
   - Qualità varia
   - Può richiedere "Fix" anche su prompt validi

4. **Error Recovery Limitato**:
   - Max 1 tentativo di fix
   - Se fix fallisce, utente deve modificare prompt

### Workaround

**Per testo**: Usa forme geometriche invece di Text
**Per velocità**: Genera animazioni brevi (8-10 sec)
**Per affidabilità**: Usa esempi di riferimento
**Per debugging**: Controlla generated/scene.py manualmente

---

## Troubleshooting

### Problema: "ANTHROPIC_API_KEY not set"

**Soluzione**:
```bash
# Verifica file .env
cat .env

# Oppure esporta manualmente
export ANTHROPIC_API_KEY='your-key'

# Windows
set ANTHROPIC_API_KEY=your-key
```

### Problema: "ModuleNotFoundError: No module named 'manim'"

**Soluzione**:
```bash
# Verifica virtual environment attivo
which python  # Deve essere in venv/

# Reinstalla dipendenze
pip install -r requirements.txt

# Verifica Manim installato
python -c "import manim; print(manim.__version__)"
```

### Problema: "ffmpeg not found"

**Soluzione**:
```bash
# Verifica imageio-ffmpeg
python -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"

# Se fallisce, reinstalla
pip install --force-reinstall imageio-ffmpeg
```

### Problema: Video non si genera

**Debug**:
1. Controlla `generated/scene.py` per syntax errors
2. Prova a eseguire manualmente:
   ```bash
   cd generated
   manim scene.py MyScene -pql
   ```
3. Controlla log server per traceback completo
4. Verifica che `generated/media/` contenga file

### Problema: "PermissionError" su Windows

**Soluzione**:
- Chiudi tutti i player video
- Attendi qualche secondo per release file locks
- Riprova rendering
- Il renderer ha retry automatico (3 tentativi)

### Problema: LLM genera codice non funzionante

**Soluzione**:
1. Click "Fix Error" per correzione automatica
2. Prova a modificare il prompt (più specifico o più semplice)
3. Seleziona manualmente un esempio di riferimento
4. Verifica che non stia chiedendo features non supportate (Text, LaTeX)

### Problema: Rendering troppo lento

**Soluzione**:
- Riduci lunghezza animazione (prompt: "in 8 seconds")
- Riduci numero oggetti (prompt: "keep it simple")
- Usa quality=low nel renderer (richiede modifica codice):
  ```python
  "quality": "low_quality"  # invece di medium_quality
  ```

---

## Appendice: Esempi Codice

### Esempio Completo: Generated scene.py

```python
"""
Generated Manim scene.

Notes:
Creates a simple circular motion animation.
Uses ValueTracker for parametric movement.
"""

from manim import *

class CircleMotion(Scene):
    def construct(self):
        # Create a circle path
        circle_path = Circle(radius=2, color=BLUE)

        # Create a moving dot
        dot = Dot(color=RED)

        # ValueTracker for angle
        angle = ValueTracker(0)

        # Update function
        def update_dot(mob):
            theta = angle.get_value()
            x = 2 * np.cos(theta)
            y = 2 * np.sin(theta)
            mob.move_to([x, y, 0])

        dot.add_updater(update_dot)

        # Animate
        self.play(Create(circle_path))
        self.add(dot)
        self.play(angle.animate.set_value(2 * PI), run_time=3)
        self.wait()
```

### Esempio: Chiamata API Diretta

```python
import asyncio
from app.generator import ManimGenerator

async def test_generation():
    generator = ManimGenerator()

    examples = [
        {
            "name": "Axes Plot",
            "tags": ["axes", "plot"],
            "code": "...",
            "notes": "..."
        }
    ]

    result = await generator.generate(
        prompt="Plot a sine wave",
        examples=examples
    )

    print(result["status"])
    print(result["plan"])
    print(result["scene_code"])

asyncio.run(test_generation())
```

### Esempio: Test Endpoint

```python
import requests

# Generate
response = requests.post("http://localhost:8000/generate", json={
    "prompt": "Create a red circle",
    "example_ids": None
})

result = response.json()
print(result["status"])

if result["status"] == "success":
    # Download video
    video_response = requests.get(f"http://localhost:8000{result['video_url']}")
    with open("output.mp4", "wb") as f:
        f.write(video_response.content)
```

---

## Crediti e Licenze

- **Manim Community**: MIT License (https://www.manim.community/)
- **FastAPI**: MIT License
- **Anthropic Claude**: API terms (https://www.anthropic.com/legal/terms)
- **Tiny Manim Web App**: Progetto dimostrativo

---

## Quick Start

### Per iniziare rapidamente:

1. **Configura API Key**:
   ```bash
   echo "ANTHROPIC_API_KEY=your-key-here" > .env
   ```

2. **Installa e Avvia**:
   ```bash
   pip install -r requirements.txt
   python -m app.main
   ```

3. **Apri Browser**:
   ```
   http://localhost:8000
   ```

4. **Prova un prompt**:
   ```
   Plot y = sin(x) on axes and animate a dot moving along it
   ```

---

**Ultimo aggiornamento**: 2026-02-10
**Versione**: 0.1.0
