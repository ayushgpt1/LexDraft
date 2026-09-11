import os
from pathlib import Path
from dotenv import load_dotenv
import pymupdf
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from groq import Groq

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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Output directory for generated affidavits
OUTPUT_DIR = Path("outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# Groq client
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "openai/gpt-oss-120b"

client = Groq(api_key=GROQ_API_KEY)


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


@app.post("/generate")
async def generate_affidavit(
    reference_file: UploadFile = File(...),
    case_file: UploadFile = File(...)
):
    reference_path = OUTPUT_DIR / "reference.pdf"
    case_path = OUTPUT_DIR / "case_information.pdf"
    output_path = OUTPUT_DIR / "generated_affidavit.docx"

    reference_path.write_bytes(
        await reference_file.read()
    )

    case_path.write_bytes(
        await case_file.read()
    )

    reference_text = extract_pdf_text(reference_path)
    case_text = extract_pdf_text(case_path)

    result = orchestrator.run(
        case_text=case_text,
        reference_text=reference_text,
        reference_rules=reference_rules,
        output_path=str(output_path)
    )

    return {
        "message": "Affidavit generated successfully",
        "download_url": "/download",
        "deterministic_score": result["deterministic_score"],
        "validation_results": result["validation_results"],
        "evaluation_report": result["evaluation_report"].model_dump(),
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