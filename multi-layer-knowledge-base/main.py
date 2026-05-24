"""
Multi-Department Knowledge Base Demo

This application demonstrates metadata-filtering based access control
for a RAG (Retrieval-Augmented Generation) knowledge base using:
- LangChain for the LLM and embedding pipeline
- Qdrant (local storage) as the vector database
- Gradio for the web UI

Architecture: Single Collection with Metadata Filtering (Recommended)
"""

import os
import shutil
from typing import List, Dict, Any

from dotenv import load_dotenv
import gradio as gr
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from qdrant_client import QdrantClient
from qdrant_client.models import (
    PointStruct,
    VectorParams,
    Distance,
    Filter,
    FieldCondition,
    MatchAny,
)

load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

QDRANT_PATH = "./qdrant_storage_knowledge_base"
COLLECTION_NAME = "company_knowledge"
EMBED_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"
TOP_K = 5

# =============================================================================
# SAMPLE DATA
# =============================================================================

DEPARTMENTS = {
    "hr": {
        "name": "Human Resources",
        "documents": [
            {
                "title": "Employee Vacation Policy 2026",
                "content": (
                    "All full-time employees are entitled to 20 days of paid vacation per year. "
                    "Vacation requests must be submitted at least 2 weeks in advance through the HR portal. "
                    "Unused vacation days can be rolled over up to a maximum of 10 days into the next calendar year. "
                    "Part-time employees receive prorated vacation based on their scheduled hours."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["hr", "executive"],
            },
            {
                "title": "Q3 Headcount Reduction Plan (CONFIDENTIAL)",
                "content": (
                    "CONFIDENTIAL - HR ONLY: The company is planning a strategic 15% headcount reduction in Q3 2026. "
                    "Affected departments will be notified individually starting August 1st. "
                    "Severance packages will include 3 months of base salary plus benefits continuation. "
                    "This information is restricted to HR leadership and executives until public announcement."
                ),
                "confidentiality": "confidential",
                "allowed_groups": ["hr", "executive"],
            },
            {
                "title": "Remote Work and Flexible Hours Policy",
                "content": (
                    "Employees may work remotely up to 3 days per week with manager approval. "
                    "All remote workers must maintain core collaboration hours from 10 AM to 3 PM in their local timezone. "
                    "IT equipment for remote work can be requested through the HR portal. "
                    "Quarterly in-person team gatherings are mandatory for all hybrid teams."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["hr", "engineering", "sales", "finance", "executive"],
            },
            {
                "title": "Company Benefits Overview",
                "content": (
                    "All full-time employees enjoy comprehensive benefits including: 20 days paid vacation, "
                    "health/dental/vision insurance, 401(k) matching up to 4%, and annual professional development budget of $2,000. "
                    "Remote work is available up to 3 days per week. Parental leave: 12 weeks paid for all new parents. "
                    "For detailed policies, contact HR or check the employee handbook."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["hr", "engineering", "sales", "finance", "executive"],
            },
            {
                "title": "Employee Performance Review Guidelines",
                "content": (
                    "Performance reviews are conducted twice yearly in June and December. "
                    "Managers must complete calibration sessions before finalizing ratings. "
                    "Promotion criteria include: exceeding role expectations for 2 consecutive review cycles, "
                    "demonstrating leadership impact, and receiving peer endorsements from 3+ cross-functional partners. "
                    "Underperformers are placed on a 60-day Performance Improvement Plan with weekly check-ins."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["hr", "executive"],
            },
            {
                "title": "2026 Salary Bands and Compensation Structure (CONFIDENTIAL)",
                "content": (
                    "HR CONFIDENTIAL: 2026 salary bands have been updated effective March 1. "
                    "Software Engineer L3: $110K-$140K. Senior Engineer L4: $145K-$185K. Staff Engineer L5: $190K-$250K. "
                    "Sales AE: $80K base + up to $120K OTE. Sales Director: $150K base + $150K OTE. "
                    "Finance Analyst: $85K-$110K. Finance Manager: $120K-$155K. "
                    "All offers above band require VP+ approval. Market adjustment reviews happen quarterly."
                ),
                "confidentiality": "confidential",
                "allowed_groups": ["hr", "executive"],
            },
            {
                "title": "Diversity, Equity, and Inclusion (DEI) 2026 Strategy",
                "content": (
                    "Our 2026 DEI strategy focuses on three pillars: equitable hiring practices, inclusive leadership training, "
                    "and pay transparency. Target: 40% underrepresented groups in leadership by end of 2026. "
                    "All managers must complete inclusive leadership certification by Q2. "
                    "Employee Resource Groups (ERGs) now receive dedicated budgets of $10K each per quarter. "
                    "Annual DEI survey results will be shared company-wide."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["hr", "engineering", "sales", "finance", "executive"],
            },
        ],
    },
    "engineering": {
        "name": "Engineering",
        "documents": [
            {
                "title": "Microservices Architecture Overview",
                "content": (
                    "The platform runs on Kubernetes with Istio service mesh for traffic management. "
                    "Core services include: Auth Service (Go), API Gateway (Node.js), Data Pipeline (Python), "
                    "and ML Inference Service (Python/TorchServe). All services communicate via gRPC internally "
                    "and REST externally. Service discovery is handled by Consul. Database per service pattern is enforced."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["engineering", "executive"],
            },
            {
                "title": "API v2 Migration Plan (INTERNAL)",
                "content": (
                    "ENGINEERING INTERNAL: The new API v2 will be released in July 2026 with breaking changes. "
                    "Key changes include: OAuth 2.1 support, rate limiting improvements, and deprecated v1 endpoints. "
                    "All internal services must migrate by September 30th. "
                    "External partner migration deadline is December 31st. Contact the Platform team for support."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["engineering", "executive"],
            },
            {
                "title": "Security Incident Response Playbook",
                "content": (
                    "In case of a security incident: 1) Immediately isolate affected systems. "
                    "2) Notify the Security team via Slack #security-incidents. "
                    "3) Document all actions in the incident log. "
                    "4) Do NOT communicate with external parties without Legal approval. "
                    "5) Post-incident review must be scheduled within 48 hours of resolution."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["engineering", "executive"],
            },
            {
                "title": "Sprint Retrospective: Q2 Platform Stability",
                "content": (
                    "Q2 2026 Engineering Retrospective: We reduced P99 latency from 450ms to 180ms by optimizing "
                    "database connection pooling and adding Redis caching layers. Incident count dropped 40% after "
                    "implementing circuit breakers in the API Gateway. On-call rotation is now 1 week on, 3 weeks off. "
                    "Terraform state management was moved to S3 with DynamoDB locking to prevent concurrent applies."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["engineering", "executive"],
            },
            {
                "title": "Unpatched CVE-2026-8841 Assessment (CONFIDENTIAL)",
                "content": (
                    "ENGINEERING CONFIDENTIAL: CVE-2026-8841 affects our Auth Service dependency on libjwt 2.4.x. "
                    "Exploit allows JWT forgery via algorithm confusion. Patch available in libjwt 2.5.1. "
                    "Migration timeline: staging by June 15, production by June 22. "
                    "External disclosure embargo until July 1 per vendor agreement. Do not mention in public commits."
                ),
                "confidentiality": "confidential",
                "allowed_groups": ["engineering", "executive"],
            },
            {
                "title": "Developer Onboarding Checklist",
                "content": (
                    "Welcome to Engineering! Your first week checklist: 1) Set up local dev environment using the "
                    "docker-compose file in /infra/local. 2) Complete security training modules A, B, and C in the LMS. "
                    "3) Shadow an on-call engineer for one full rotation. 4) Pick up a good-first-issue from the backlog. "
                    "5) Schedule 1:1s with your tech lead, product manager, and designated buddy. "
                    "Team standups are at 9:30 AM PT daily."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["engineering", "sales", "finance", "hr", "executive"],
            },
            {
                "title": "Internal Tools and Developer Productivity Report",
                "content": (
                    "Our internal developer portal (Backstage) now serves 150+ engineers with self-service templates "
                    "for microservice scaffolding, CI/CD pipelines, and observability dashboards. "
                    "Average time to production for a new service dropped from 3 weeks to 4 days. "
                    "We use Datadog for APM, PagerDuty for incident management, and Linear for project tracking. "
                    "All engineers have access to GPU workstations for ML experimentation via the internal cloud scheduler."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["engineering", "executive"],
            },
        ],
    },
    "sales": {
        "name": "Sales",
        "documents": [
            {
                "title": "Q2 2026 Sales Report",
                "content": (
                    "Q2 2026 Sales Report: Total revenue reached $2.4M, exceeding target by 8%. "
                    "Top performing regions: North America (+12%), EMEA (+5%). "
                    "New customer acquisitions: 42. Customer churn rate decreased to 4.2%. "
                    "Average deal size increased to $28,000. Key wins include TechCorp ($450K) and GlobalRetail ($380K)."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["sales", "executive"],
            },
            {
                "title": "Enterprise Sales Playbook",
                "content": (
                    "When pitching to enterprise clients, always emphasize our SOC 2 Type II compliance and 99.99% uptime SLA. "
                    "Lead with ROI calculations showing average 35% cost reduction within 12 months. "
                    "Reference customers in similar industries should be prepared in advance. "
                    "Technical demos should be scheduled with the Solutions Engineering team at least 1 week before the pitch."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["sales", "executive"],
            },
            {
                "title": "Q3 Pricing Strategy (CONFIDENTIAL)",
                "content": (
                    "SALES CONFIDENTIAL: New pricing tiers effective Q3 2026. Starter tier: $499/month (was $599). "
                    "Professional tier: $1,499/month with new AI features. Enterprise tier: Custom pricing starting at $5K/month. "
                    "Existing customers will be grandfathered for 6 months. "
                    "Competitive positioning against MegaCorp remains focused on ease of use and faster implementation."
                ),
                "confidentiality": "confidential",
                "allowed_groups": ["sales", "executive"],
            },
            {
                "title": "Lost Deal Analysis: MegaCorp RFP",
                "content": (
                    "SALES INTERNAL: We lost the MegaCorp RFP worth $2.1M ARR to competitor CloudNova. "
                    "Primary reasons: CloudNova offered 20% lower pricing and had a pre-existing relationship with MegaCorp's CTO. "
                    "Lessons learned: 1) Engage C-level sponsors earlier in the sales cycle. 2) Improve competitive intelligence. "
                    "3) Develop a more aggressive volume discount schedule for deals above $1M. Action items assigned to VP Sales."
                ),
                "confidentiality": "confidential",
                "allowed_groups": ["sales", "executive"],
            },
            {
                "title": "Sales Compensation Plan 2026",
                "content": (
                    "2026 Sales Comp Plan: Base salaries remain unchanged. Commission rates increased for enterprise deals: "
                    "10% for first $500K, 12% for $500K-$1M, 15% above $1M. Quarterly accelerators kick in at 110% quota attainment. "
                    "SPIFs: $5K for first deal in new vertical, $2K for customer expansion above 50% ACV. "
                    "Clawback policy applies if customer churns within 6 months of signing."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["sales", "executive"],
            },
            {
                "title": "Customer Success Handoff Process",
                "content": (
                    "After a deal closes, the AE must complete the handoff to Customer Success within 48 hours. "
                    "Required handoff documents: signed contract, technical requirements doc, stakeholder map, and success criteria. "
                    "CSM onboarding calls must be scheduled within 5 business days. "
                    "First value realization milestone should be achieved within 30 days to reduce early churn risk."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["sales", "executive"],
            },
            {
                "title": "Partner Channel Strategy",
                "content": (
                    "Our partner channel now contributes 25% of total pipeline. Key partners: Deloitte, Accenture, and 12 regional SI partners. "
                    "Partner deal registration process is handled in Salesforce. Partner discounts range from 15% to 30% depending on tier. "
                    "Joint marketing funds are available for co-branded events and webinars. "
                    "All partner-facing collateral must be approved by the Channel Marketing team."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["sales", "executive"],
            },
        ],
    },
    "finance": {
        "name": "Finance",
        "documents": [
            {
                "title": "Q2 Budget Allocation Review",
                "content": (
                    "Q2 2026 Budget Review: Engineering received 45% of the total budget ($1.8M out of $4M). "
                    "Sales and Marketing combined: 30% ($1.2M). Operations: 15% ($600K). "
                    "HR and Administrative: 10% ($400K). The remaining budget surplus of $200K will be allocated "
                    "to the cloud infrastructure reserve fund. Q3 budget planning begins July 15th."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["finance", "executive"],
            },
            {
                "title": "IPO Preparation Timeline (STRICTLY CONFIDENTIAL)",
                "content": (
                    "STRICTLY CONFIDENTIAL - FINANCE & EXECUTIVE ONLY: The CFO is preparing for an IPO in Q4 2026. "
                    "Goldman Sachs and Morgan Stanley have been selected as lead underwriters. "
                    "Target valuation: $800M - $1.2B. Audit firm Deloitte has commenced financial review. "
                    "Employee stock option adjustments will be announced 30 days before S-1 filing. "
                    "NO public discussion until official announcement."
                ),
                "confidentiality": "confidential",
                "allowed_groups": ["finance", "executive"],
            },
            {
                "title": "Expense Reimbursement Policy",
                "content": (
                    "All business expenses over $50 require pre-approval through the Finance portal. "
                    "Reimbursement requests must be submitted within 30 days of the expense date. "
                    "Travel expenses include: flights (economy class, <$1,500), hotels (<$300/night), meals ($75/day limit). "
                    "Conference and training expenses are reimbursable up to $2,000 annually per employee with manager approval."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["finance", "executive"],
            },
            {
                "title": "2026 Revenue Forecast and Cash Flow Projections (CONFIDENTIAL)",
                "content": (
                    "FINANCE CONFIDENTIAL: 2026 full-year revenue forecast revised to $12.5M (up from $11M). "
                    "ARR growth projected at 35% YoY. Cash runway extended to 24 months following the Series B extension. "
                    "Burn rate target: <$380K/month by Q4. Break-even expected Q2 2027. "
                    "Investor board deck materials are restricted to CFO, CEO, and board members only."
                ),
                "confidentiality": "confidential",
                "allowed_groups": ["finance", "executive"],
            },
            {
                "title": "Vendor Contract Renewal Calendar",
                "content": (
                    "Upcoming renewals: AWS Enterprise Agreement expires September 2026 (estimated $480K/year). "
                    "Salesforce contract expires November 2026 (estimated $120K/year). Datadog expires August 2026 ($85K/year). "
                    "All renewals above $50K require competitive bidding and Finance approval. "
                    "Early renewal discounts of up to 15% are available if signed 90 days before expiration."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["finance", "engineering", "sales", "hr", "executive"],
            },
            {
                "title": "Audit Findings and Remediation Plan",
                "content": (
                    "External audit findings for FY2025: 2 material weaknesses identified in revenue recognition controls. "
                    "Remediation actions: implement automated contract-to-revenue matching, mandatory SOC 2 evidence collection, "
                    "and quarterly control self-assessments. All remediation must be complete by September 30, 2026. "
                    "Finance team leads the remediation with support from Engineering and Legal."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["finance", "executive"],
            },
            {
                "title": "Tax Strategy and International Compliance",
                "content": (
                    "Our tax strategy focuses on optimizing our corporate structure across US, Ireland, and Singapore entities. "
                    "Transfer pricing documentation must be updated annually and reviewed by external counsel. "
                    "GST/VAT compliance is now automated via Avalara integration. "
                    "R&D tax credits for FY2025 are estimated at $180K. All international employees must submit tax residency declarations."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["finance", "executive"],
            },
        ],
    },
    "operations": {
        "name": "Operations",
        "documents": [
            {
                "title": "Office Relocation Plan 2026",
                "content": (
                    "We are relocating our headquarters to the new downtown campus in Q4 2026. "
                    "The new office features 300 desks, 20 meeting rooms, 4 conference halls, and a rooftop event space. "
                    "All employees will receive assigned seating with ergonomic equipment. "
                    "Parking passes and transit subsidies will be managed through the Operations portal."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["hr", "engineering", "sales", "finance", "executive"],
            },
            {
                "title": "IT Asset Management Policy",
                "content": (
                    "All company-issued laptops must be enrolled in MDM (Jamf) within 24 hours of receipt. "
                    "Laptop refresh cycle is 3 years. Lost or stolen devices must be reported to IT within 1 hour. "
                    "Personal devices may NOT access company email or Slack without BYOD enrollment. "
                    "Data classification labels (Public, Internal, Confidential, Restricted) must be applied to all shared drives."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["engineering", "hr", "sales", "finance", "executive"],
            },
            {
                "title": "Business Continuity and Disaster Recovery Plan",
                "content": (
                    "Our primary data center is in AWS us-east-1 with failover to us-west-2. "
                    "RPO target: 1 hour. RTO target: 4 hours. Critical systems include: customer-facing APIs, billing, and authentication. "
                    "Quarterly DR drills are scheduled for the first week of each quarter. "
                    "All department heads must maintain up-to-date contact trees and escalation procedures."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["engineering", "finance", "executive"],
            },
            {
                "title": "Vendor Security Assessment Results (CONFIDENTIAL)",
                "content": (
                    "OPERATIONS CONFIDENTIAL: Q2 vendor security assessments flagged 3 critical vendors with overdue penetration tests. "
                    "Vendors on probation: CloudPrint Inc, DataBridge LLC, and MobileFirst Corp. "
                    "Remediation deadlines: July 15, 2026. If not resolved, contracts will be terminated and data migrated per the exit plan. "
                    "No public communication until remediation is complete."
                ),
                "confidentiality": "confidential",
                "allowed_groups": ["executive"],
            },
            {
                "title": "Company-Wide All-Hands Schedule",
                "content": (
                    "All-hands meetings are held on the first Friday of every month at 10 AM PT / 1 PM ET / 6 PM GMT. "
                    "All employees are expected to attend live or watch the recording within 48 hours. "
                    "Department-specific Q&A sessions follow the main presentation. "
                    "Meeting recordings and slide decks are posted in the Internal Communications Slack channel and the company wiki."
                ),
                "confidentiality": "internal",
                "allowed_groups": ["hr", "engineering", "sales", "finance", "executive"],
            },
        ],
    },
}

# =============================================================================
# USER ROLES & ACCESS GROUPS
# =============================================================================

USER_ROLES = {
    "HR Employee": ["hr"],
    "Engineering Employee": ["engineering"],
    "Sales Employee": ["sales"],
    "Finance Employee": ["finance"],
    "Executive / Admin": ["hr", "engineering", "sales", "finance", "executive"],
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_embeddings() -> OpenAIEmbeddings:
    """Initialize OpenAI embeddings."""
    return OpenAIEmbeddings(model=EMBED_MODEL)


def get_llm() -> ChatOpenAI:
    """Initialize ChatGPT LLM."""
    return ChatOpenAI(model=LLM_MODEL, temperature=0)


def check_api_key() -> tuple[bool, str]:
    """Check if the OpenAI API key is configured."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return False, "⚠️ OPENAI_API_KEY not found. Please check your .env file."
    return True, "✅ OpenAI API key found."


def check_database_exists() -> bool:
    """Check if the Qdrant database has been initialized."""
    if not os.path.exists(QDRANT_PATH):
        return False
    try:
        client = QdrantClient(path=QDRANT_PATH)
        exists = client.collection_exists(COLLECTION_NAME)
        client.close()
        return exists
    except Exception:
        return False


# =============================================================================
# INGESTION
# =============================================================================

def ingest_sample_data() -> str:
    """
    Ingest sample documents into Qdrant with metadata.
    This creates a fresh database each time it runs.
    """
    # Check API key
    ok, msg = check_api_key()
    if not ok:
        return msg

    try:
        # Remove existing database for a clean slate
        if os.path.exists(QDRANT_PATH):
            shutil.rmtree(QDRANT_PATH)
            print(f"Removed existing database at {QDRANT_PATH}")

        # Initialize
        embedding = get_embeddings()
        client = QdrantClient(path=QDRANT_PATH)

        # Determine vector size
        sample_vector = embedding.embed_query("sample")
        vector_size = len(sample_vector)

        # Create collection
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )
        print(f"Created collection: {COLLECTION_NAME}")

        # Build documents
        documents: List[Document] = []
        for dept_key, dept_data in DEPARTMENTS.items():
            for doc in dept_data["documents"]:
                metadata = {
                    "title": doc["title"],
                    "source_file": f"{dept_key}/{doc['title'].replace(' ', '_').lower()}.txt",
                    "department": dept_key,
                    "department_name": dept_data["name"],
                    "allowed_groups": doc["allowed_groups"],
                    "confidentiality": doc["confidentiality"],
                }
                documents.append(Document(page_content=doc["content"], metadata=metadata))

        print(f"Prepared {len(documents)} documents")

        # Embed and upsert in batches
        batch_size = 10
        total_ingested = 0
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            points: List[PointStruct] = []

            for j, doc in enumerate(batch):
                point_id = i + j
                vector = embedding.embed_query(doc.page_content)
                points.append(PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={
                        "text": doc.page_content,
                        "title": doc.metadata["title"],
                        "source_file": doc.metadata["source_file"],
                        "department": doc.metadata["department"],
                        "department_name": doc.metadata["department_name"],
                        "allowed_groups": doc.metadata["allowed_groups"],
                        "confidentiality": doc.metadata["confidentiality"],
                    }
                ))

            client.upsert(collection_name=COLLECTION_NAME, points=points)
            total_ingested += len(batch)
            print(f"  Ingested batch {i//batch_size + 1}: {len(batch)} documents")

        client.close()

        status = (
            f"✅ Successfully created database with {total_ingested} documents!\n\n"
            f"📁 Storage: {QDRANT_PATH}\n"
            f"📊 Collection: {COLLECTION_NAME}\n"
            f"🔢 Vector size: {vector_size}\n"
            f"📚 Documents by department:\n"
        )
        for dept_key, dept_data in DEPARTMENTS.items():
            status += f"   • {dept_data['name']}: {len(dept_data['documents'])} documents\n"

        return status

    except Exception as e:
        return f"❌ Error during ingestion: {str(e)}"


# =============================================================================
# SEARCH WITH METADATA FILTERING
# =============================================================================

def search_knowledge_base(query: str, user_role: str) -> tuple[str, List[Dict], str]:
    """
    Search the knowledge base with metadata filtering based on user's role.

    CRITICAL SECURITY ENFORCEMENT:
    The access filter is injected server-side based on the user's resolved role.
    It is NEVER accepted from client input.
    """
    # Validate inputs
    if not query or not query.strip():
        return "Please enter a question.", [], "No filter applied."

    if not user_role:
        return "Please select a user role.", [], "No filter applied."

    # Check prerequisites
    ok, msg = check_api_key()
    if not ok:
        return msg, [], "No filter applied."

    if not check_database_exists():
        return (
            "⚠️ Database not found. Please go to the 'Ingest Sample Data' tab and create the sample database first.",
            [],
            "No filter applied."
        )

    try:
        # Resolve user's allowed groups from their role
        user_groups = USER_ROLES[user_role]

        # Initialize
        embedding = get_embeddings()
        client = QdrantClient(path=QDRANT_PATH)

        # Embed query
        query_vector = embedding.embed_query(query)

        # =====================================================================
        # CRITICAL: BUILD ACCESS FILTER
        # =====================================================================
        # This filter ensures users can ONLY see documents whose allowed_groups
        # overlap with their own groups. It is injected server-side.
        access_filter = Filter(
            must=[
                FieldCondition(
                    key="allowed_groups",
                    match=MatchAny(any=user_groups)
                )
            ]
        )

        filter_info = (
            f"**Applied Security Filter:**\n"
            f"- Your role: `{user_role}`\n"
            f"- Resolved groups: `{user_groups}`\n"
            f"- Filter: `allowed_groups MATCH ANY {user_groups}`\n"
            f"- Documents accessible: Only those tagged with at least one of these groups"
        )

        # Search Qdrant with the access filter (using query_points for newer client versions)
        result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=access_filter,
            limit=TOP_K,
            with_payload=True,
        )
        search_results = result.points

        client.close()

        # Reconstruct documents from results
        docs: List[Document] = []
        for result in search_results:
            payload = result.payload
            metadata = {
                "title": payload.get("title", "Unknown"),
                "department_name": payload.get("department_name", "Unknown"),
                "department": payload.get("department", "Unknown"),
                "source_file": payload.get("source_file", "Unknown"),
                "allowed_groups": payload.get("allowed_groups", []),
                "confidentiality": payload.get("confidentiality", "unknown"),
                "score": round(result.score, 4),
            }
            docs.append(Document(
                page_content=payload.get("text", ""),
                metadata=metadata
            ))

        # Format sources for display
        sources = []
        for doc in docs:
            sources.append({
                "Title": doc.metadata["title"],
                "Department": doc.metadata["department_name"],
                "Confidentiality": doc.metadata["confidentiality"],
                "Allowed Groups": ", ".join(doc.metadata["allowed_groups"]),
                "Similarity Score": doc.metadata["score"],
                "Content Preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
            })

        # Generate RAG answer using LangChain
        if docs:
            context = "\n\n---\n\n".join([
                f"Source: {doc.metadata['title']} ({doc.metadata['department_name']})\n{doc.page_content}"
                for doc in docs
            ])

            template = """Answer the question based ONLY on the following context.
If the context doesn't contain enough information, say so clearly.

Context:
{context}

Question: {question}

Answer:"""

            prompt = ChatPromptTemplate.from_template(template)
            llm = get_llm()
            chain = prompt | llm | StrOutputParser()

            answer = chain.invoke({"context": context, "question": query})
        else:
            answer = "No documents were found matching your access level and query. Try a different question or check your role permissions."

        return answer, sources, filter_info

    except Exception as e:
        return f"❌ Error during search: {str(e)}", [], f"Error: {str(e)}"


# =============================================================================
# GRADIO UI
# =============================================================================

def create_gradio_ui() -> gr.Blocks:
    """Create the Gradio demonstration UI."""

    with gr.Blocks(title="Multi-Department Knowledge Base Demo") as demo:
        gr.Markdown(
            """
            # 🏢 Multi-Department Knowledge Base Demo

            This demonstration shows **metadata-filtering based access control** for a RAG knowledge base.

            ### How it works:
            1. Documents are tagged with metadata including `department` and `allowed_groups`
            2. When a user searches, their role is resolved server-side to determine their `allowed_groups`
            3. A **Qdrant metadata filter** is injected into every query, ensuring users can ONLY see documents they have permission to access
            4. Executives can search across all departments simultaneously

            ### Architecture: Single Collection with Metadata Filtering ✅
            """
        )

        with gr.Tabs():
            # -----------------------------------------------------------------
            # TAB 1: Search
            # -----------------------------------------------------------------
            with gr.Tab("🔍 Search Knowledge Base"):
                gr.Markdown(
                    """
                    Select your role and search the knowledge base.
                    **Notice how different roles see different results!**
                    """
                )

                with gr.Row():
                    with gr.Column(scale=1):
                        user_role = gr.Dropdown(
                            choices=list(USER_ROLES.keys()),
                            value="Executive / Admin",
                            label="Your Role",
                            info="Simulates role-based access from your identity provider"
                        )
                        query_input = gr.Textbox(
                            label="Your Question",
                            placeholder="e.g., What are the Q3 plans? What is the vacation policy?",
                            lines=3
                        )
                        search_btn = gr.Button("🔍 Search", variant="primary")

                        gr.Markdown("### Try These Questions")
                        gr.Markdown(
                            """
                            #### 🎯 Questions That Show Role-Based Filtering

                            | Question | Expected Result |
                            |---|---|
                            | What are the Q3 plans? | Different answers per role |
                            | What is the vacation policy? | HR sees full policy, others see general info |
                            | Tell me about the IPO | Only Finance & Executive |
                            | What is our revenue forecast? | Only Finance & Executive |
                            | How do we handle security incidents? | Only Engineering & Executive |
                            | What happened with the MegaCorp deal? | Only Sales & Executive |
                            | What are the 2026 salary bands? | Only HR & Executive |
                            | Tell me about the unpatched CVE | Only Engineering & Executive |
                            | Which vendors failed security assessments? | Only Executive |

                            #### 🌐 Cross-Department & Company-Wide Questions

                            | Question | Who Can Answer |
                            |---|---|
                            | What are our remote work policies? | All employees |
                            | When is the next all-hands meeting? | All employees |
                            | What are our company benefits? | All employees |
                            | Tell me about the DEI strategy | All employees |
                            | What is our office relocation plan? | All employees |
                            | How do I onboard as a new engineer? | All employees |
                            | What are our vendor renewal dates? | All employees |

                            #### 🔒 Confidential vs Internal Access Tests

                            | Question | Level | Accessible By |
                            |---|---|---|
                            | What are the salary bands? | Confidential | HR + Executive only |
                            | Tell me about the IPO | Confidential | Finance + Executive only |
                            | What is our revenue forecast? | Confidential | Finance + Executive only |
                            | What is the new pricing strategy? | Confidential | Sales + Executive only |
                            | Tell me about the MegaCorp loss | Confidential | Sales + Executive only |
                            | What is the unpatched security vulnerability? | Confidential | Engineering + Executive only |
                            | Which vendors failed security? | Confidential | Executive only |
                            | What is the vacation policy? | Internal | HR (full) + All (general) |
                            | What is our tech stack? | Internal | Engineering + Executive |
                            | What are our sales numbers? | Internal | Sales + Executive |

                            #### 🏢 Department-Specific Deep Dives

                            **HR:** How does the performance review process work? What are the DEI targets for 2026?

                            **Engineering:** Tell me about our microservices architecture. What was improved in Q2 platform stability? What internal tools do engineers use?

                            **Sales:** What is our enterprise sales playbook? How does the customer success handoff work? Tell me about our partner channel strategy.

                            **Finance:** What is the expense reimbursement policy? What are the audit findings? Tell me about our tax strategy.

                            **Operations:** What is our disaster recovery plan? What is the IT asset management policy?
                            """
                        )

                    with gr.Column(scale=2):
                        answer_output = gr.Markdown(label="💡 Answer")
                        filter_info_output = gr.Markdown(label="🔒 Security Filter Applied")
                        sources_output = gr.JSON(label="📚 Retrieved Sources (with metadata)")

                search_btn.click(
                    fn=search_knowledge_base,
                    inputs=[query_input, user_role],
                    outputs=[answer_output, sources_output, filter_info_output],
                )

            # -----------------------------------------------------------------
            # TAB 2: Ingest
            # -----------------------------------------------------------------
            with gr.Tab("🗄️ Ingest Sample Data"):
                gr.Markdown(
                    """
                    Create or reset the sample knowledge base with department documents.
                    This will erase any existing data and create fresh embeddings.
                    """
                )

                with gr.Row():
                    with gr.Column():
                        ingest_btn = gr.Button("🔄 Create / Reset Sample Database", variant="primary")
                        ingest_status = gr.Textbox(
                            label="Status",
                            interactive=False,
                            lines=10
                        )

                        ingest_btn.click(
                            fn=ingest_sample_data,
                            inputs=[],
                            outputs=[ingest_status],
                        )

                    with gr.Column():
                        gr.Markdown("### Sample Documents by Department")

                        doc_list = ""
                        for dept_key, dept_data in DEPARTMENTS.items():
                            doc_list += f"\n**{dept_data['name']} ({len(dept_data['documents'])} documents):**\n"
                            for doc in dept_data["documents"]:
                                groups = ", ".join(doc["allowed_groups"])
                                doc_list += f"- {doc['title']} (access: `{groups}`)\n"

                        gr.Markdown(doc_list)

            # -----------------------------------------------------------------
            # TAB 3: Security Demo
            # -----------------------------------------------------------------
            with gr.Tab("📊 Security Demo"):
                gr.Markdown(
                    """
                    ## Security Enforcement Demonstration

                    This tab visualizes how metadata filtering enforces access control at the database level.
                    """
                )

                gr.Markdown("### Access Matrix: Which roles can access which departments?")

                # Build access matrix as list of lists for Gradio compatibility
                dept_names = [dept_data["name"] for dept_data in DEPARTMENTS.values()]
                matrix_headers = ["Role"] + dept_names
                matrix_data = []
                for role_name, groups in USER_ROLES.items():
                    row = [role_name]
                    for dept_key, dept_data in DEPARTMENTS.items():
                        can_access = any(
                            any(g in groups for g in doc["allowed_groups"])
                            for doc in dept_data["documents"]
                        )
                        row.append("Yes" if can_access else "No")
                    matrix_data.append(row)

                gr.Dataframe(
                    headers=matrix_headers,
                    value=matrix_data,
                    label="Department Access by Role",
                    interactive=False,
                )

                gr.Markdown("""
                ### Key Security Principles

                1. **Server-side filtering**: The `allowed_groups` filter is injected by the backend, never from the client
                2. **No trust in client**: The user's role is resolved from the identity provider (simulated here with a dropdown)
                3. **Defense in depth**: Even if the UI is bypassed, the database filter prevents unauthorized access
                4. **Cross-department search**: Executives can search across all departments in a single query
                5. **Array-based permissions**: Using `allowed_groups` arrays allows complex permissions (e.g., managers in multiple departments)
                """)

                gr.Markdown("### Sample Document Metadata")

                sample_headers = ["Title", "Department", "Confidentiality", "Allowed Groups"]
                sample_metadata = []
                for dept_key, dept_data in DEPARTMENTS.items():
                    for doc in dept_data["documents"]:
                        sample_metadata.append([
                            doc["title"],
                            dept_data["name"],
                            doc["confidentiality"],
                            ", ".join(doc["allowed_groups"]),
                        ])

                gr.Dataframe(
                    headers=sample_headers,
                    value=sample_metadata,
                    label="Document Metadata Tags",
                    interactive=False,
                )

    return demo


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    demo = create_gradio_ui()
    demo.launch()




