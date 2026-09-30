import streamlit as st
import requests
import json

# ---------------------------------------------------------------------------
# PAGE CONFIGURATION & STYLING
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Client Portfolio Handover Dashboard",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .badge-high {
        background-color: #dc3545;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .badge-medium {
        background-color: #ffc107;
        color: black;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: bold;
    }
    .banner-contradiction {
        background-color: #f8d7da;
        color: #842029;
        padding: 15px;
        border-radius: 6px;
        border-left: 5px solid #dc3545;
        margin-bottom: 15px;
    }
    .banner-gap {
        background-color: #fff3cd;
        color: #664d03;
        padding: 15px;
        border-radius: 6px;
        border-left: 5px solid #ffc107;
        margin-bottom: 15px;
    }
    .banner-exception {
        background-color: #cff4fc;
        color: #055160;
        padding: 15px;
        border-radius: 6px;
        border-left: 5px solid #0dcaf0;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

BACKEND_URL = "http://127.0.0.1:8000/analyze-client"

# ---------------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------------------------
st.sidebar.title("💼 Portfolio Overview")
st.sidebar.markdown("---")

client_selection = st.sidebar.selectbox(
    "Select Client Handover",
    ["acme_corp (10 Active Documents)", "tech_corp (Mock)", "finance_inc (Mock)"]
)

st.sidebar.markdown("### 📊 Handover Status")
if "acme_corp" in client_selection:
    st.sidebar.metric(label="Handover Completion", value="62%", delta="4 Issues Flagged")
    st.sidebar.progress(0.62)
else:
    st.sidebar.metric(label="Handover Completion", value="95%", delta="0 Issues")
    st.sidebar.progress(0.95)

# ---------------------------------------------------------------------------
# MAIN DASHBOARD VIEW
# ---------------------------------------------------------------------------
st.title("🛡️ Client Portfolio Handover & Knowledge Gap Detector")
st.caption(f"Active Analysis for: **acme_corp** | Knowledge Base: **10 Multi-Channel Sources**")

# Trigger Audit
if st.button("🚀 Run Deep-Dive Knowledge Audit (10 Sources)", type="primary"):
    with st.spinner("Retrieving across 10 documents and performing knowledge audit..."):
        try:
            response = requests.post(
                BACKEND_URL,
                json={
                    "client_id": "acme_corp",
                    "topics": ["leave", "overtime", "remote work", "expenses"]
                },
                timeout=10
            )
            
            if response.status_code == 200:
                st.session_state["api_data"] = response.json()
                st.success("Successfully audited 10 sources from backend!")
            else:
                st.error(f"Backend API Error: {response.status_code}")
                
        except Exception as e:
            st.warning("⚠️ Backend API offline. Please start LLMPipeline.py.")

# Render Analysis Results
if "api_data" in st.session_state:
    data = st.session_state["api_data"]
    
    st.markdown("---")
    
    # 1. EXECUTIVE SUMMARY & CONFIDENCE METER
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📋 Executive Handover Summary")
        st.write(data["client_handover_summary"])
        
    with col2:
        st.subheader("🎯 Trust Score")
        confidence = data["confidence_score"]
        st.metric(label="Answer Reliability", value=f"{confidence}%")
        st.progress(confidence / 100)
        st.caption("⚠️ High Discrepancy Risk: Manual SME escalation recommended.")

    # 2. KNOWLEDGE GAP & CONFLICT CARDS
    st.markdown("---")
    st.subheader(f"🚨 Detected Knowledge Gaps & Conflicts ({len(data['flagged_issues'])} Issues)")
    
    for issue in data["flagged_issues"]:
        issue_type = issue["issue_type"]
        severity = issue["severity"]
        
        if issue_type == "Contradiction":
            banner_class = "banner-contradiction"
        elif issue_type == "Knowledge Gap":
            banner_class = "banner-gap"
        else:
            banner_class = "banner-exception"
            
        badge_class = "badge-high" if severity == "High" else "badge-medium"
        sources_str = ", ".join([f"`{s}`" for s in issue["conflicting_sources"]])
        
        st.markdown(
            f"""
            <div class="{banner_class}">
                <span class="{badge_class}">{severity} {issue_type.upper()}</span>
                <strong style="margin-left: 10px; font-size: 1.1em;">Impact Area: {issue['impact_area']}</strong>
                <p style="margin-top: 8px; margin-bottom: 4px;">{issue['description']}</p>
                <small><strong>Conflicting Sources:</strong> {sources_str}</small>
            </div>
            """,
            unsafe_allow_html=True
        )

    # 3. PROVENANCE / SOURCE DRAWER (DYNAMIC 10 DOCUMENTS INSPECTOR)
    st.markdown("---")
    st.subheader("🔍 Provenance & Multi-Source Drawer")
    
    sources = data.get("retrieved_sources", [])
    st.write(f"Showing **{len(sources)} ingested sources** retrieved from ChromaDB:")
    
    with st.expander("📖 Expand All 10 Ingested Knowledge Sources", expanded=True):
        # Display sources in 2-column grid cards
        for i in range(0, len(sources), 2):
            col_a, col_b = st.columns(2)
            
            with col_a:
                src = sources[i]
                st.info(
                    f"**[{src['doc_id']}] {src['title']}**\n\n"
                    f"• **Channel:** `{src['source_channel']}` | **Type:** `{src['source_type']}`\n\n"
                    f"• **Author:** {src['author']} | **Date:** {src['date']}\n\n"
                    f"• **Authority Score:** `{src['authority_score']}` | **Scope:** `{src['scope']}`\n\n"
                    f"**Content Excerpt:**\n_{src['content']}_"
                )
                
            if i + 1 < len(sources):
                with col_b:
                    src = sources[i+1]
                    st.warning(
                        f"**[{src['doc_id']}] {src['title']}**\n\n"
                        f"• **Channel:** `{src['source_channel']}` | **Type:** `{src['source_type']}`\n\n"
                        f"• **Author:** {src['author']} | **Date:** {src['date']}\n\n"
                        f"• **Authority Score:** `{src['authority_score']}` | **Scope:** `{src['scope']}`\n\n"
                        f"**Content Excerpt:**\n_{src['content']}_"
                    )

    # 4. ONE-CLICK SME ESCALATION BUTTON
    st.markdown("---")
    st.subheader("✉️ One-Click SME Escalation")
    
    if st.button("📩 Generate Pre-filled SME Escalation Draft"):
        questions_formatted = "\n".join([f"{idx+1}. {q}" for idx, q in enumerate(data["sme_questions"])])
        draft_message = (
            f"Subject: Escalation Request - Multi-Source Knowledge Gap Audit for {data['client_id']}\n\n"
            f"Hi Expert Team,\n\n"
            f"During our automated handover audit for {data['client_id']} across 10 internal documentation channels, "
            f"the system flagged {len(data['flagged_issues'])} operational discrepancies.\n\n"
            f"Please review and clarify the following SME questions:\n"
            f"{questions_formatted}\n\n"
            f"Flagged Document IDs: DOC-ACME-POL-2022, DOC-ACME-EML-2025, DOC-ACME-CHT-2026, "
            f"DOC-ACME-ADD-2024, DOC-ACME-POL-2023, DOC-ACME-EML-2026.\n\n"
            f"Best regards,\nSD Worx Client Handover System"
        )
        
        st.text_area("Pre-filled Draft Message for Departing SME:", value=draft_message, height=260)
        st.success("Escalation draft generated! You can now copy and send this directly to the subject matter expert.")