
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.services.security_analyzer import analyze_source
from backend.app.services.ml_detector import predict_source
from backend.app.services.robustness_service import run_robustness_probe
from backend.app.services.compiler_service import compile_c_source


app = FastAPI(
    title="AdversarialCompiler API",
    description="Source-code security and compiler robustness platform",
    version="0.1.0",
)

# Allow the local frontend to communicate with the API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    source_code: str = Field(min_length=1, max_length=50000)


@app.get("/")
def home():
    return {
        "project": "AdversarialCompiler",
        "status": "running",
        "version": "0.1.0",
    }


@app.get("/api/health")
def health():
    return {"status": "healthy"}


@app.post("/api/analyze")
def analyze_code(request: AnalyzeRequest):
    source = request.source_code

    analysis = analyze_source(source)
    ml_prediction = predict_source(source)
    compilation = compile_c_source(source)

    return {
        "status": "completed",
        "language": "C",
        "characters_analyzed": len(source),
        "static_analysis": analysis,
        "ml_prediction": ml_prediction,
        "compilation": {
            "compiled": compilation["compiled"],
            "return_code": compilation["return_code"],
            "diagnostics": compilation["stderr"],
            "compiler_output": compilation["stdout"],
        },
    }


@app.post("/api/compile")
def compile_code(request: AnalyzeRequest):
    result = compile_c_source(request.source_code)

    if result["return_code"] is None:
        return {
            "status": "error",
            **result,
        }

    return {
        "status": "completed",
        "language": "C",
        **result,
    }


@app.post("/api/robustness")
def test_robustness(request: AnalyzeRequest):
    return run_robustness_probe(request.source_code)
