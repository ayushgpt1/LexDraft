import asyncio
import json
import os
from pathlib import Path
from dotenv import load_dotenv
import pymupdf
from fastapi import FastAPI, File, Query, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.core.llm_client import ResilientGeminiClient
from backend.agents.extraction_agent import ExtractionAgent
from backend.agents.generation_agent import GenerationAgent
from backend.agents.evaluation_agent import EvaluationAgent
from backend.core.orchestrator import AffidavitOrchestrator
from backend.core.reference_analyzer import reference_rules


app = FastAPI(
    title="LexDraft API",
    description="AI-powered Legal Affidavit Generation and Evaluation Agent",
    version="1.0.0"
)


# Allow the React frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://lexdraft-frontend-wafl.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Output directory for generated affidavits
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# Gemini client
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# gemini-2.5-flash is no longer available to new Gemini API users;
# the API recommends gemini-3.6-flash (verified live with this key).
MODEL_NAME = "gemini-3.6-flash"

client = ResilientGeminiClient(api_key=GEMINI_API_KEY)


# Agents
extraction_agent = ExtractionAgent(
    client=client,
    model=MODEL_NAME
)

generation_agent = GenerationAgent(
    client=client,
    model=MODEL_NAME
)

evaluation_agent = EvaluationAgent(
    client=client,
    model=MODEL_NAME
)


# Orchestrator
orchestrator = AffidavitOrchestrator(
    extraction_agent=extraction_agent,
    generation_agent=generation_agent,
    evaluation_agent=evaluation_agent
)


# In-memory registry matching a frontend-supplied run id to its
# progress WebSocket. The frontend connects BEFORE the /generate
# request so no stage event is missed. No external infrastructure.
progress_sockets: dict = {}


def extract_pdf_text(file_path):
    doc = pymupdf.open(file_path)

    pages = []

    for page in doc:
        pages.append(page.get_text())

    doc.close()

    return "\n".join(pages)


@app.get("/")
def root():
    return {
        "message": "LexDraft API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.websocket("/ws/progress")
async def progress_websocket(
    websocket: WebSocket,
    run_id: str = Query(default="")
):
    """
    Live generation progress events for the frontend.

    Registered under the same run id that the frontend passes to
    POST /generate (?run_id=...). The /generate task sends JSON
    events over this socket: {"stage": ..., "status": ...}.
    """

    await websocket.accept()

    if not run_id:
        await websocket.close(code=1008)
        return

    progress_sockets[run_id] = websocket

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        progress_sockets.pop(run_id, None)


@app.post("/generate")
async def generate_affidavit(
    reference_file: UploadFile = File(None),
    format_file: UploadFile = File(None),
    sample_file: UploadFile = File(None),
    case_file: UploadFile = File(...),
    run_id: str = Query(default="")
):
    # Output paths
    output_path = OUTPUT_DIR / "generated_affidavit.docx"

    # Case information is always required
    case_path = OUTPUT_DIR / "case_information.pdf"
    case_path.write_bytes(await case_file.read())
    case_text = extract_pdf_text(case_path)

    # Determine which reference files to use
    # Priority: uploaded files > default files
    from backend.core.reference_analyzer import (
        DEFAULT_FORMAT_PATH,
        DEFAULT_SAMPLE_PATH
    )

    # Handle Format Explained file
    if format_file is not None:
        format_path = OUTPUT_DIR / "format_explained.pdf"
        format_path.write_bytes(await format_file.read())
        reference_format_path = str(format_path)
    else:
        # Use default Format Explained
        reference_format_path = DEFAULT_FORMAT_PATH

    # Handle Sample Affidavit file
    if sample_file is not None:
        sample_path = OUTPUT_DIR / "sample_affidavit.pdf"
        sample_path.write_bytes(await sample_file.read())
        reference_sample_path = str(sample_path)
    else:
        # No sample uploaded; do not load the default sample.
        # The default sample was not loaded before the reference-selection
        # feature, so this preserves the prior behavior exactly.
        reference_sample_path = None

    # For backward compatibility, if reference_file is provided,
    # it overrides both format and sample (legacy behavior)
    if reference_file is not None:
        reference_path = OUTPUT_DIR / "reference.pdf"
        reference_path.write_bytes(await reference_file.read())
        reference_text = extract_pdf_text(reference_path)
        reference_format_path = None  # Don't analyze separately
        reference_sample_path = None   # Don't analyze separately
    else:
        # Extract reference text from Format Explained for the pipeline
        # (the sample is used for pattern analysis, not as reference_text)
        format_path = OUTPUT_DIR / "format_explained.pdf" if format_file else None
        if format_path and format_path.exists():
            reference_text = extract_pdf_text(format_path)
        elif reference_format_path == DEFAULT_FORMAT_PATH:
            reference_text = extract_pdf_text(reference_format_path)
        else:
            reference_text = ""

    # Progress reporting is optional: when a run id is supplied the
    # orchestrator runs in a worker thread (its LLM calls block) and
    # every stage event is forwarded over the matching WebSocket.
    progress_callback = None
    pump_task = None
    queue = None

    if run_id:

        queue = asyncio.Queue()
        loop = asyncio.get_running_loop()

        def progress_callback(event):
            # Called from the worker thread; hand the event to the
            # event loop in a thread-safe way.
            loop.call_soon_threadsafe(
                queue.put_nowait,
                event
            )

        async def pump_progress():
            while True:
                event = await queue.get()

                if event is None:
                    break

                websocket = progress_sockets.get(run_id)

                if websocket is None:
                    continue

                try:
                    await websocket.send_json(event)
                except Exception:
                    break

        pump_task = asyncio.create_task(pump_progress())

    try:
        result = await asyncio.to_thread(
            orchestrator.run,
            case_text=case_text,
            reference_text=reference_text,
            reference_rules=reference_rules,
            output_path=str(output_path),
            progress_callback=progress_callback,
            reference_format_path=reference_format_path,
            reference_sample_path=reference_sample_path
        )
    finally:

        if pump_task is not None and queue is not None:

            await queue.put(None)
            await pump_task

            websocket = progress_sockets.get(run_id)

            if websocket is not None:
                try:
                    await websocket.close(code=1000)
                except Exception:
                    pass

    # Persist the actual evaluation result returned by the
    # EvaluationAgent (reused as-is; no second evaluation and no
    # additional LLM call). The outputs directory is created on
    # demand so the artifact always has a valid JSON home.
    evaluation_report = result["evaluation_report"].model_dump()

    OUTPUT_DIR.mkdir(exist_ok=True)

    evaluation_report_path = OUTPUT_DIR / "evaluation_report.json"

    evaluation_report_path.write_text(
        json.dumps(
            evaluation_report,
            indent=2
        ),
        encoding="utf-8"
    )

    return {
        "message": "Affidavit generated successfully",
        "download_url": "/download",
        "deterministic_score": result["deterministic_score"],
        "validation_results": result["validation_results"],
        "evaluation_report": evaluation_report,
        "case_data": result["case_data"].model_dump(),
        "generated_paragraphs": (
            result["generated_paragraphs"].model_dump()
        )
    }


@app.get("/download")
def download_affidavit():
    return FileResponse(
        path="outputs/generated_affidavit.docx",
        filename="generated_affidavit.docx",
        media_type=(
            "application/vnd.openxmlformats-officedocument"
            ".wordprocessingml.document"
        )
    )