# LexDraft — AI-Powered Legal Affidavit Generation & Evaluation Agent

LexDraft is an AI agent that generates an **Affidavit in Reply** (DOCX) from a supplied
case-information PDF and a reference affidavit format, then evaluates the generated document
using both deterministic checks and an LLM-based evaluation.

This project was built as part of the **Brainwonders AI Internship** assignment.

---

## 1. Problem Statement

Drafting an Affidavit in Reply requires:

- Extracting structured case information (parties, deponent, reply points, prayer, etc.) from a case document.
- Mapping that information to the structural and linguistic conventions of a prescribed affidavit format.
- Generating the numbered body paragraphs faithfully — without introducing unsupported facts.
- Assembling a complete, correctly formatted affidavit (forum heading, cause title, deponent clause,
  numbered paragraphs, prayer, jurat, verification, and advocate block).
- Validating the output for structural and factual correctness.
- Evaluating the output for entity accuracy, completeness, semantic faithfulness, hallucination, and
  template fidelity.

Doing this manually is repetitive and error-prone. LexDraft automates the full pipeline
end-to-end while keeping the generated content grounded in the supplied case information.

---

## 2. Features

- **Case information extraction** — LLM extracts structured `CaseInformation` (Pydantic model) from a
  case-information PDF.
- **Content mapping** — Normalises reply points and party data for the generation stage.
- **Faithful paragraph generation** — LLM drafts only the numbered body paragraphs, constrained to
  facts explicitly present in the mapped case information.
- **Programmatic document assembly** — The prayer, jurat, verification, cause title, deponent clause,
  and advocate block are generated deterministically; only the body paragraphs come from the LLM.
- **DOCX generation** — Produces a formatted `.docx` file (Times New Roman 12 pt, 1-inch margins,
  bold/all-caps headings, right-aligned deponent, tab-stopped cause title, page break before prayer).
- **Deterministic validation** — 7 rule-based checks with a pass/fail score.
- **LLM evaluation** — 5-dimensional evaluation (entity accuracy, completeness, semantic faithfulness,
  hallucination, template fidelity) with per-criterion scores and issues.
- **Configurable reference materials** — Per-generation-run selection of reference materials:
  - **Case 1 (defaults):** Default `01 Affidavit Format Explained.pdf` and default `02 Affidavit in Reply Sample.docx.pdf` are used. The user uploads only the Case Information PDF. Existing/default behavior is unchanged.
  - **Case 2 (replace sample only):** Default Format Explained remains in use; the user can replace only the Sample Affidavit for the current run. The uploaded sample is used as a reference for structure, wording patterns, organization, and similar stylistic/structural patterns. The Format Explained rules remain authoritative. Sample-specific factual details are not copied into the new case.
  - **Case 3 (replace format only):** Default Sample Affidavit remains in use; the user can replace only the Format Explained document for the current run. The uploaded Format Explained is analyzed to derive the applicable document rules actually present in that material, and those extracted rules are used for that generation run.
- **Live progress** — WebSocket-based stage progress pushed to the frontend.
- **Web UI** — React frontend with file upload, live pipeline status, extracted-case display, affidavit
  preview, evaluation summary, deterministic checks, and issues section.

---

## 3. System Architecture

The system is split into a **FastAPI backend** and a **React frontend**.

![System Architecture](docs/architecture.png)

### High-level data flow

The pipeline processes reference materials and case information as follows:

1. **Reference selection (per run):** The user may use the default reference materials bundled in the
   repository, or optionally upload replacement Format Explained and/or Sample Affidavit documents for
   the current generation run. Reference selection does not permanently overwrite the repository's default
   reference files.
2. **Format/reference analysis:** The Format Explained document (default or uploaded) is analyzed.
   When an uploaded Format Explained is supplied, the applicable rules are extracted from that material
   for the current run. When no replacement is supplied, the default reference rules are used.
3. **Case information extraction:** The case information PDF is extracted via PyMuPDF and processed by
   the Gemini extraction agent into a structured `CaseInformation` (Pydantic model).
4. **Content mapping:** The extracted case information is normalized into reply points and party data.
5. **Affidavit body generation:** The Gemini generation agent drafts only the numbered body paragraphs,
   constrained to facts explicitly present in the mapped case information. The generation agent receives
   the reference rules and, when a sample affidavit is supplied for the run, the sample text as a
   structural/linguistic reference. Sample-specific factual details are not copied.
6. **Programmatic DOCX generation:** The prayer, jurat, verification, cause title, deponent clause, and
   advocate block are assembled deterministically; only the body paragraphs come from the LLM.
7. **Deterministic validation:** 7 rule-based checks run against the generated document.
8. **LLM evaluation:** A 5-dimensional evaluation (entity accuracy, completeness, semantic faithfulness,
   hallucination, template fidelity) is performed.
9. **Results returned:** The generated DOCX, validation results, and evaluation report are returned to
   the frontend for display and download.

```
Case PDF ──► PyMuPDF ──► Extraction Agent (Gemini) ──► CaseInformation (Pydantic)
                                                                       │
Reference PDF ──► PyMuPDF ──► reference_text ───────────────────────────┤
                                                                       ▼
                                              reference_rules (predefined) + mapped case data
                                                                       │
                                                                       ▼
                                                        Generation Agent (Gemini)
                                                                       │
                                                                       ▼
                                              GeneratedParagraphs → Document Generator (python-docx)
                                                                       │
                                                                       ▼
                                                           generated_affidavit.docx
                                                                       │
                                              ┌────────────────────────┼────────────────────────┐
                                              ▼                        ▼                        ▼
                                     Deterministic Validators   extract_docx_text()     Evaluation Agent (Gemini)
                                              │                        │                        │
                                              ▼                        ▼                        ▼
                                     deterministic_score       generated_text         EvaluationReport (Pydantic)
                                              │                        │                        │
                                              └────────────────────────┼────────────────────────┘
                                                                       ▼
                                                           JSON response + evaluation_report.json
                                                                       │
                                                                       ▼
                                                           React frontend (display + download)
```


---

## 4. Workflow / How It Works

1. **Upload** — The user may optionally upload replacement **Format Explained** and/or **Sample Affidavit**
   documents for the current generation run. The default reference materials bundled in the repository are
   used if no replacements are supplied. The user also uploads a **Case Information PDF**. Reference
   selection is per-run; uploaded files do not permanently overwrite the repository's default reference files.
2. **Extract** — PyMuPDF extracts raw text from the case information PDF. If an uploaded Format Explained
   or Sample Affidavit is supplied, its text is also extracted.
3. **Analyze reference rules** — The Format Explained document (default or uploaded) is analyzed.
   When an uploaded Format Explained is supplied, the applicable rules are extracted from that material
   for the current run. When no replacement is supplied, the default reference rules are used. If a Sample
   Affidavit is supplied for the run, its text is passed as a structural/linguistic reference to the
   generation stage. Sample-specific factual details are not copied.
4. **Map** — The **Content Mapper** normalises reply-point move types and flattens party/deponent
   data into a single mapped-content dictionary.
5. **Generate** — The **Generation Agent** (Gemini, temperature 0) drafts only the numbered body
   paragraphs. It receives the reference rules (default or extracted from the uploaded Format Explained)
   and the mapped case information. It is explicitly prohibited from introducing unsupported facts, copying
   sample-specific details from the reference, or generating the prayer/jurat/verification.
6. **Build DOCX** — `build_affidavit_docx` assembles the full document: forum heading, jurisdiction,
   case number, cause title, affidavit title, deponent clause, numbered body paragraphs (with bold
   exhibit references), page break, programmatic prayer (a/b/c), jurat, verification, and optional
   advocate block.
7. **Validate** — 7 **deterministic checks** run against the generated DOCX text and paragraph
   metadata. A deterministic score (percentage of passed checks) is computed.
8. **Evaluate** — The **Evaluation Agent** (Gemini, temperature 0) scores the generated affidavit on
   5 dimensions and lists specific issues per dimension.
9. **Return & Persist** — The backend returns the full result as JSON and saves
   `outputs/evaluation_report.json`. The frontend displays the extracted case information, affidavit
   preview, evaluation summary, deterministic checks, and issues. Users can download the generated
   Affidavit in Reply DOCX. The evaluation report is displayed in the frontend.

---

## 5. Project Structure

```
LexDraft/
├── backend/
│   ├── main.py                     # FastAPI app, REST endpoints, WebSocket, PDF extraction, reference selection
│   ├── requirements.txt            # Python dependencies
│   ├── agents/
│   │   ├── extraction_agent.py     # LLM case-information extraction
│   │   ├── generation_agent.py     # LLM body-paragraph generation
│   │   └── evaluation_agent.py     # LLM 5-dimension evaluation
│   ├── core/
│   │   ├── orchestrator.py         # AffidavitOrchestrator — runs the full pipeline
│   │   ├── reference_analyzer.py   # Reference rule analysis (default rules + uploaded Format Explained parsing)
│   │   ├── content_mapper.py       # Maps extracted CaseInformation to generation input
│   │   ├── document_generator.py   # Builds the formatted DOCX; extracts DOCX text
│   │   └── llm_output.py           # Strips markdown fences / prose from LLM JSON output
│   ├── models/
│   │   └── schemas.py              # Pydantic models: CaseInformation, EvaluationReport, etc.
│   ├── validation/
│   │   └── validators.py           # 7 deterministic checks + score calculation
├── frontend/
│   ├── public/reference/
│   │   ├── 01 Affidavit Format Explained.pdf   # Default Format Explained (used when no replacement supplied)
│   │   └── 02 Affidavit in Reply Sample.docx.pdf  # Default Sample Affidavit (used as structural/linguistic reference)
│   ├── src/
│   │   ├── App.tsx                 # Main app: upload, progress, results, download
│   │   ├── main.tsx                # React entry point
│   │   ├── lib/
│   │   │   ├── api.ts              # API client: generate, WebSocket, download, reference uploads
│   │   │   ├── types.ts            # TypeScript interfaces mirroring backend schemas
│   │   │   └── utils.ts            # cn() utility (clsx + tailwind-merge)
│   │   ├── components/             # Feature components + ShadCN UI components
│   │   └── hooks/
│   │       └── use-toast.ts        # Toast hook
│   ├── package.json
│   ├── vite.config.ts              # Vite + React plugin, @ alias
│   ├── tailwind.config.js          # Tailwind + ShadCN theme
│   └── ...                         # tsconfig, eslint, postcss, components.json
├── outputs/                        # Generated artifacts (created at runtime)
│   ├── generated_affidavit.docx
│   ├── evaluation_report.json
├── .env                            # GEMINI_API_KEY (git-ignored)
├── .env.example                    # Env-var template
└── .gitignore
```

---

## 6. Technology Stack

| Layer       | Technology                                                                 |
|-------------|----------------------------------------------------------------------------|
| Backend     | Python, FastAPI, Uvicorn                                                   |
| LLM         | Google Gemini (`gemini-3.6-flash`) via `google-genai`                       |
| PDF parsing | PyMuPDF (`pymupdf`)                                                        |
| DOCX gen    | `python-docx`                                                              |
| Validation  | Pydantic (data models), custom deterministic validators                    |
| Frontend    | React 18, TypeScript, Vite, Tailwind CSS, ShadCN UI, Lucide icons          |
| Realtime    | WebSocket (FastAPI native)                                                 |

---

## 7. Setup and Installation

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- A valid **Google Gemini API key**

### Backend

```bash
# From the repository root
cd backend
python -m venv venv
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

---

## 8. Environment Variables

Create a `.env` file in the repository root (copy from `.env.example`):

```
GEMINI_API_KEY=your_api_key_here
```

| Variable        | Required | Description                     |
|-----------------|----------|---------------------------------|
| `GEMINI_API_KEY` | Yes      | Google Gemini API key           |

The backend loads this via `python-dotenv`. No other environment variables are required.

---

## 9. Running the Application

### Start the backend (terminal 1)

From the **repository root**:

```bash
uvicorn backend.main:app --reload
```

The API is available at `http://127.0.0.1:8000` (Swagger UI at `/docs`).

### Start the frontend (terminal 2)

```bash
cd frontend
npm run dev
```

The web UI is available at `http://localhost:5173`.

### Using the app

1. Open `http://localhost:5173` in your browser.
2. The default reference materials (Format Explained and Sample Affidavit) are already loaded.
3. Optionally, upload a replacement **Format Explained** PDF to override the default format rules for
   this generation run. The uploaded document is analyzed to extract the applicable rules actually present
   in that material. If no replacement is supplied, the default Format Explained is used.
4. Optionally, upload a replacement **Sample Affidavit** PDF to use as a structural/linguistic reference
   for this generation run. The Format Explained rules remain authoritative; sample-specific factual details
   are not copied into the new case. If no replacement is supplied, the default Sample Affidavit is used.
5. Upload a **Case Information PDF**.
6. Click **Generate Affidavit**.
7. Watch the live pipeline progress (Reference selection → Analyze → Extract → Map → Generate → Validate → Evaluate).
8. View the extracted case information, affidavit preview, evaluation summary, deterministic checks,
   and any issues.
9. Download the generated `generated_affidavit.docx`.


---

## 10. Generated Outputs

| File                                      | Description                                           |
|-------------------------------------------|-------------------------------------------------------|
| `outputs/generated_affidavit.docx`        | The generated Affidavit in Reply (formatted DOCX).   |
| `outputs/evaluation_report.json`          | LLM evaluation report (5 dimensions + overall score). |

The DOCX contains, in order: forum heading, jurisdiction, case number, cause title, affidavit
title, deponent clause, numbered body paragraphs, prayer (a/b/c), jurat, verification, and an
optional advocate block.

---

## 11. Evaluation and Validation

### Deterministic Validation (7 checks)

| # | Check                        | What it verifies                                                                 |
|---|------------------------------|----------------------------------------------------------------------------------|
| 1 | Respondent consistency       | Answering-respondent references use the correct respondent number.               |
| 2 | Case number consistency      | Proceeding type, case number, and year appear in the document.                   |
| 3 | Date consistency             | The supplied date (or its ordinal form, e.g. "5th day of September 2026") appears.|
| 4 | Exhibit consistency          | Every exhibit reference in the case information appears in the generated document.|
| 5 | Required sections and order  | Court, jurisdiction, case number, affidavit title, PRAYER, VERIFICATION exist in order.|
| 6 | Paragraph numbering          | Generated paragraphs are numbered continuously from 1.                           |
| 7 | Verification range           | The verification clause references the correct paragraph count.                  |

The **deterministic score** is the percentage of passed checks.

### LLM Evaluation (5 dimensions)

| Dimension               | What it measures                                                              |
|-------------------------|-------------------------------------------------------------------------------|
| Entity Accuracy         | Names, numbers, dates, organisations, exhibits are preserved accurately.      |
| Completeness            | Important case information and reply points are present.                       |
| Semantic Faithfulness   | Meaning of case information is preserved without material alteration.         |
| Hallucination           | Absence of unsupported facts, allegations, dates, documents, or legal positions.|
| Template Fidelity       | Required sections, order, title, deponent clause, prayer, jurat, verification.|

Each dimension is scored 0–100 with a list of specific issues. An overall score is also provided.

---

## 12. Design Decisions

- **Default reference rules with configurable override** — The structural and linguistic conventions of
  the Affidavit in Reply format are encoded as a default `reference_rules` dictionary
  (`reference_analyzer.py`). When no replacement Format Explained is supplied, these default rules are
  used. When a user uploads a replacement Format Explained document, the system analyzes that document to
  extract the applicable rules actually present in the supplied material, and those extracted rules are
  used for that generation run. The uploaded Format Explained is the source of truth for any rule it
  provides; old hardcoded rules for the same key are not silently retained. Default rules are preserved
  only for top-level keys that the uploaded document does not address.
- **Sample affidavit as structural reference** — A supplied Sample Affidavit can be passed as a
  structural/linguistic reference for the current generation run. It is used for structure, wording
  patterns, organization, and similar stylistic patterns. The Format Explained rules remain authoritative.
  Sample-specific factual details are not copied into the new case. The sample is not used when no
  replacement is supplied (the default behavior preserves the prior behavior).
- **Reference selection is per-run** — Reference material selection (default or replacement Format
  Explained, default or replacement Sample Affidavit) applies only to the current generation run. The
  repository's default reference files in `frontend/public/reference/` are never permanently overwritten
  by user uploads.
  - **Constrained generation** — Only the numbered body paragraphs are LLM-generated. The prayer,
  jurat, verification, cause title, and deponent clause are produced programmatically to guarantee
  structural correctness.
- **Faithfulness-first prompting** — The generation agent is explicitly prohibited from introducing
  unsupported facts, copying sample-specific details from the reference, or generating sections that
  are produced programmatically.
- **Dual evaluation** — Deterministic checks catch structural/factual regressions deterministically;
  the LLM evaluation catches semantic quality that rule-based checks cannot.
- **Temperature 0** — Extraction and evaluation use temperature 0 for reproducibility.
- **No external infrastructure** — Progress is tracked via in-memory WebSocket registries; no
  database or message queue is required.


---

## 13. What Is Not Implemented / Out of Scope

- **Independent legal research** — The system does not perform its own legal research or retrieve
  external authorities.
- **Para-wise replies** — The system does not draft detailed paragraph-by-paragraph replies to the
  opposing petition.
- **Multi-case / batch processing** — One case is processed per generation request.
- **User authentication / authorisation** — No login, accounts, or access control.
- **Database persistence** — No long-term storage; only the latest outputs are retained.
- **Deployment** — The application is deployed using Render Free services. The free deployment may
  spin down after periods of inactivity.

---

## 14. Known Limitations

- The local development setup requires an internet connection and a valid Gemini API key.
- Generation quality depends on the underlying LLM; occasional hallucinations or omissions may occur
  and should be reviewed by a human.
- Only the **Affidavit in Reply** document type is supported.
- Only **PDF** inputs are accepted for the case information and reference documents.
- Alternative reference documents are expected to describe the same general Affidavit in Reply document
  type/workflow.
- The system does not invent legal requirements that are not supported by the supplied reference material.
- Default reference files in the repository (`frontend/public/reference/`) are never overwritten by user
  uploads; reference selection is per-generation-run.
- The sample affidavit is used as a structural/linguistic reference when supplied; sample-specific
  factual details are not copied into the generated affidavit.

---

## 15. Demo / Working Link

> Live demo: https://lexdraft-frontend-wafl.onrender.com


---

## 16. Video Demonstration

> Video walkthrough: *[placeholder — add when recorded]*

---

## 17. AI Assistance

[ChatGPT](https://chat.openai.com) was used to assist with development, debugging, architecture and
design decisions, documentation, and implementation guidance during the build of this project. It did
not independently build or deploy the application; all design choices, integration, testing, and
final implementation were performed and validated by the author.

---

## 18. Assignment Scope / Disclaimer

This project was developed as part of the **Brainwonders AI Internship** assignment. It is a
demonstration prototype for educational purposes only. It does not constitute legal advice and is not
a substitute for review by a qualified legal professional. The generated affidavit outputs should be
verified by a human before any real-world use.
