from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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