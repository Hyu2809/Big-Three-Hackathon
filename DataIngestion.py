import datetime
from typing import Any, Dict, List
import chromadb
from chromadb.utils import embedding_functions

# ---------------------------------------------------------------------------
# 10 SYNTHETIC DOCUMENTS (SD WORX CLIENT HANDOVER CONTEXT)
# ---------------------------------------------------------------------------
SYNTHETIC_DOCUMENTS = [
    {
        "doc_id": "DOC-ACME-POL-2022",
        "client_id": "acme_corp",
        "title": "Acme Corp Employee Handbook - Belgian Branch (2022)",
        "source_type": "Official Policy",
        "source_channel": "PDF Document",
        "author": "HR Central Brussels",
        "date": "2022-03-15",
        "authority_score": 0.9,
        "scope": "Leave",
        "content": (
            "Section 4.2 - Annual Leave & Holiday Allowance: Employees receive standard statutory holiday allowance "
            "calculated strictly according to Joint Committee 200 (PC 200). Unused holiday allowance cannot be carried "
            "over to subsequent calendar years under any circumstances. All untaken days lapse automatically on December 31st."
        )
    },
    {
        "doc_id": "DOC-ACME-EML-2025",
        "client_id": "acme_corp",
        "title": "Email Thread: Custom Overtime Agreement for Tech Department",
        "source_type": "Email",
        "source_channel": "Outlook Inbox",
        "author": "Marc Peeters (Account Director) to Acme CFO",
        "date": "2025-11-20",
        "authority_score": 0.7,
        "scope": "Overtime",
        "content": (
            "Confirmation regarding Acme Corp Engineering Team overtime: Effective Q1 2026, all Senior DevOps and "
            "Software Engineers are entitled to a 150% overtime compensation rate for weekend work during product launches, "
            "pending formal written addendum signing."
        )
    },
    {
        "doc_id": "DOC-ACME-CHT-2026",
        "client_id": "acme_corp",
        "title": "Teams Chat: HR Exception for Senior Management Carry-over",
        "source_type": "Chat",
        "source_channel": "MS Teams - #hr-general",
        "author": "Sophie Willems (HR Lead)",
        "date": "2026-01-10",
        "authority_score": 0.4,
        "scope": "Leave",
        "content": (
            "Even though the 2022 manual says holidays expire strictly on Dec 31st, Acme HR director agreed off-the-record "
            "to let senior managers carry over up to 5 days into March due to the heavy Q4 workload."
        )
    },
    {
        "doc_id": "DOC-ACME-CHT-2026-OT",
        "client_id": "acme_corp",
        "title": "Teams Chat: QA Testers Overtime Eligibility Question",
        "source_type": "Chat",
        "source_channel": "MS Teams - #engineering-leads",
        "author": "David Claes (QA Lead)",
        "date": "2026-02-04",
        "authority_score": 0.4,
        "scope": "Overtime",
        "content": (
            "QA Testers are working full weekends for the release but accounting says the 150% rate only applies to Senior "
            "DevOps and Developers. We need clarification if QA qualifies without a signed addendum."
        )
    },
    {
        "doc_id": "DOC-ACME-ADD-2024",
        "client_id": "acme_corp",
        "title": "Addendum: Remote Work & Work From Abroad Policy (2024)",
        "source_type": "Official Policy",
        "source_channel": "Signed PDF",
        "author": "Legal & HR Dept",
        "date": "2024-06-01",
        "authority_score": 0.9,
        "scope": "Remote Work",
        "content": (
            "Employees are allowed a maximum of 20 days of remote work from EU countries per calendar year, "
            "subject to prior manager approval and tax residency checks."
        )
    },
    {
        "doc_id": "DOC-ACME-CHT-2026-REM",
        "client_id": "acme_corp",
        "title": "Slack Thread: Summer Work from Spain Exemption",
        "source_type": "Chat",
        "source_channel": "Slack - #remote-culture",
        "author": "Luc De Smet (VP Product)",
        "date": "2026-02-15",
        "authority_score": 0.3,
        "scope": "Remote Work",
        "content": (
            "We told the mobile team they can stay in Malaga for up to 45 days this summer as long as core sprint goals "
            "are met. No need to log it in the HR portal."
        )
    },
    {
        "doc_id": "DOC-ACME-NOT-2025",
        "client_id": "acme_corp",
        "title": "Board Meeting Minutes: Mobility Budget & Company Cars",
        "source_type": "Meeting Notes",
        "source_channel": "Notion Workspace",
        "author": "Executive Committee",
        "date": "2025-09-12",
        "authority_score": 0.8,
        "scope": "Benefits",
        "content": (
            "Pillar 2 Mobility Budget allocation approved for all Band 3 employees replacing electric lease cars. "
            "Budget cap fixed at €750/month effective January 2026."
        )
    },
    {
        "doc_id": "DOC-ACME-TCK-2026",
        "client_id": "acme_corp",
        "title": "IT Support Ticket #4412: Home Ergonomic Allowance",
        "source_type": "Ticket",
        "source_channel": "Jira Service Desk",
        "author": "IT Helpdesk",
        "date": "2026-01-22",
        "authority_score": 0.5,
        "scope": "Expenses",
        "content": (
            "One-off €500 home office equipment allowance was paid directly via payroll to new hires in Jan 2026. "
            "Finance flagged that this was never recorded in the formal benefits catalog."
        )
    },
    {
        "doc_id": "DOC-ACME-POL-2023",
        "client_id": "acme_corp",
        "title": "Travel & Expense Guidelines (2023)",
        "source_type": "Official Policy",
        "source_channel": "PDF Document",
        "author": "Finance Dept",
        "date": "2023-01-10",
        "authority_score": 0.85,
        "scope": "Expenses",
        "content": (
            "Daily meal allowance during domestic client travel is capped at €25 per day with itemized receipts. "
            "Alcoholic beverages are non-reimbursable."
        )
    },
    {
        "doc_id": "DOC-ACME-EML-2026",
        "client_id": "acme_corp",
        "title": "Email: Client On-Site Meal Stipend Exemption",
        "source_type": "Email",
        "source_channel": "Outlook",
        "author": "Karel Janssens (Account Manager)",
        "date": "2026-02-18",
        "authority_score": 0.6,
        "scope": "Expenses",
        "content": (
            "For consultants deployed on-site at European Commission premises, meal allowance cap is raised to €50/day. "
            "Expense team was notified via email but policy PDF was not updated."
        )
    }
]

# Initialize ChromaDB Vector Store
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection(
    name="client_handover_docs",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

# Ingest Documents
if collection.count() == 0:
    collection.add(
        documents=[doc["content"] for doc in SYNTHETIC_DOCUMENTS],
        metadatas=[{
            "doc_id": doc["doc_id"],
            "client_id": doc["client_id"],
            "title": doc["title"],
            "source_type": doc["source_type"],
            "source_channel": doc["source_channel"],
            "author": doc["author"],
            "date": doc["date"],
            "authority_score": doc["authority_score"],
            "scope": doc["scope"]
        } for doc in SYNTHETIC_DOCUMENTS],
        ids=[doc["doc_id"] for doc in SYNTHETIC_DOCUMENTS]
    )
    print(f"[DataIngestion] Ingested {len(SYNTHETIC_DOCUMENTS)} document chunks into ChromaDB.")

def get_relevant_chunks(query: str, client_id: str = "acme_corp", top_k: int = 10) -> List[Dict[str, Any]]:
    """Retrieve top_k matching document chunks filtered by client_id."""
    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where={"client_id": client_id}
    )
    
    retrieved_docs = []
    if results and "documents" in results and results["documents"]:
        docs = results["documents"][0]
        metas = results["metadatas"][0]
        distances = results["distances"][0] if "distances" in results else [0.0] * len(docs)
        
        for doc_text, meta, dist in zip(docs, metas, distances):
            retrieved_docs.append({
                "doc_id": meta["doc_id"],
                "title": meta["title"],
                "source_type": meta["source_type"],
                "source_channel": meta["source_channel"],
                "author": meta["author"],
                "date": meta["date"],
                "authority_score": meta["authority_score"],
                "scope": meta["scope"],
                "content": doc_text,
                "relevance_score": round(1.0 - (dist / 2.0), 2)
            })
    return retrieved_docs

if __name__ == "__main__":
    test_results = get_relevant_chunks("holiday allowance and overtime rate", top_k=10)
    print("\n--- Testing Retrieval ---")
    for r in test_results:
        print(f"ID: {r['doc_id']} | Type: {r['source_type']} | Score: {r['authority_score']} | Scope: {r['scope']}")