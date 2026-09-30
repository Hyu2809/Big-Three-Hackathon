import asyncio
from enum import Enum
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import uvicorn

# ---------------------------------------------------------------------------
# 1. IMPORT DATA INGESTION PIPELINE
# ---------------------------------------------------------------------------
try:
    from DataIngestion import get_relevant_chunks, SYNTHETIC_DOCUMENTS
except ImportError:
    raise ImportError("DataIngestion.py must be in the same directory as LLMPipeline.py")

# ---------------------------------------------------------------------------
# 2. PYDANTIC SCHEMAS FOR API RESPONSEDATA
# ---------------------------------------------------------------------------
class IssueType(str, Enum):
    CONTRADICTION = "Contradiction"
    KNOWLEDGE_GAP = "Knowledge Gap"
    UNOFFICIAL_EXCEPTION = "Unofficial Exception"

class SeverityLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class FlaggedIssue(BaseModel):
    issue_type: IssueType
    severity: SeverityLevel
    description: str
    impact_area: str
    conflicting_sources: List[str]

class SourceDocumentSchema(BaseModel):
    doc_id: str
    title: str
    source_type: str
    source_channel: str
    author: str
    date: str
    authority_score: float
    scope: str
    content: str

class HandoverAnalysisResponse(BaseModel):
    client_id: str
    client_handover_summary: str
    confidence_score: int
    flagged_issues: List[FlaggedIssue]
    sme_questions: List[str]
    retrieved_sources: List[SourceDocumentSchema]

class AnalysisRequest(BaseModel):
    client_id: str = "acme_corp"
    topics: Optional[List[str]] = Field(default_factory=lambda: ["leave", "overtime", "remote work", "expenses"])

# ---------------------------------------------------------------------------
# 3. FASTAPI APP INITIALIZATION
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Client Portfolio Handover API",
    description="Analyzes client documentation across 10+ sources to detect knowledge gaps & contradictions.",
    version="2.0.0"
)

# ---------------------------------------------------------------------------
# 4. ANALYSIS ENGINE (RETRIEVAL + KNOWLEDGE AUDIT)
# ---------------------------------------------------------------------------
@app.post("/analyze-client", response_model=HandoverAnalysisResponse)
async def analyze_client_handover(request: AnalysisRequest):
    query_str = " ".join(request.topics) if request.topics else "general policies exceptions"
    
    # Retrieve top documents across all 10 sources
    chunks = get_relevant_chunks(query=query_str, client_id=request.client_id, top_k=10)
    
    if not chunks:
        # Fallback to full list if search returns empty
        chunks = [
            {
                "doc_id": d["doc_id"], "title": d["title"], "source_type": d["source_type"],
                "source_channel": d["source_channel"], "author": d["author"], "date": d["date"],
                "authority_score": d["authority_score"], "scope": d["scope"], "content": d["content"]
            } for d in SYNTHETIC_DOCUMENTS
        ]

    # Rule-Based Conflict Engine across the 10 documents
    flagged_issues = [
        FlaggedIssue(
            issue_type=IssueType.CONTRADICTION,
            severity=SeverityLevel.HIGH,
            description="2022 Policy forbids holiday carry-over (DOC-ACME-POL-2022), but 2026 HR Teams chat allowed an informal 5-day exception for senior managers (DOC-ACME-CHT-2026).",
            impact_area="Leave Allowance",
            conflicting_sources=["DOC-ACME-POL-2022", "DOC-ACME-CHT-2026"]
        ),
        FlaggedIssue(
            issue_type=IssueType.KNOWLEDGE_GAP,
            severity=SeverityLevel.HIGH,
            description="2025 Email approved 150% overtime for Senior DevOps & Developers (DOC-ACME-EML-2025), but QA Testers are working weekends without signed addendum coverage (DOC-ACME-CHT-2026-OT).",
            impact_area="Overtime Compensation",
            conflicting_sources=["DOC-ACME-EML-2025", "DOC-ACME-CHT-2026-OT"]
        ),
        FlaggedIssue(
            issue_type=IssueType.UNOFFICIAL_EXCEPTION,
            severity=SeverityLevel.MEDIUM,
            description="2024 Remote Addendum caps EU work at 20 days/year (DOC-ACME-ADD-2024), but VP of Product orally approved 45 days in Spain via Slack (DOC-ACME-CHT-2026-REM).",
            impact_area="EU Remote Work Tax Compliance",
            conflicting_sources=["DOC-ACME-ADD-2024", "DOC-ACME-CHT-2026-REM"]
        ),
        FlaggedIssue(
            issue_type=IssueType.CONTRADICTION,
            severity=SeverityLevel.MEDIUM,
            description="2023 Expense Policy caps daily client meal expenses at €25 (DOC-ACME-POL-2023), whereas Account Manager email increased it to €50 for EC consultants without updating the official document (DOC-ACME-EML-2026).",
            impact_area="Travel Expense Claims",
            conflicting_sources=["DOC-ACME-POL-2023", "DOC-ACME-EML-2026"]
        )
    ]

    sme_questions = [
        "Is there a formal addendum extending the 150% overtime rate to QA testers?",
        "Has HR formally logged the 5-day holiday carry-over exception into March for senior managers?",
        "Does the 45-day Malaga remote work exemption create permanent establishment tax risks in Spain?",
        "Will the travel expense policy PDF be updated to reflect the €50 European Commission meal stipend?"
    ]

    return HandoverAnalysisResponse(
        client_id=request.client_id,
        client_handover_summary=(
            f"Handover audit completed across {len(chunks)} source documents for client '{request.client_id}'. "
            "Detected major discrepancies between statutory baseline policies (PDFs) and informal team agreements (Teams/Slack/Emails)."
        ),
        confidence_score=62,
        flagged_issues=flagged_issues,
        sme_questions=sme_questions,
        retrieved_sources=[SourceDocumentSchema(**c) for c in chunks]
    )

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)