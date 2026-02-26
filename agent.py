import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent, LLM  # removed .agents
from tools import search_tool, FinancialDocumentTool #mixed missing imports


# ==============================
# Load OpenAI GPT-4o Mini
# ==============================
llm = LLM(
    model="gpt-4o-mini",
    api_key=os.getenv("OPENAI_API_KEY"),
    temperature=0.2
)


# ==============================
# Financial Analyst
# ==============================
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal=(
        "Analyze the uploaded financial document and answer the user query: {query}. "
        "Use ONLY information found in the document (no outside knowledge). "
        "Be concise and structured: "
        "(1) Executive Summary: max 6 bullets (1 line each), "
        "(2) Key Financials (only if present): revenue/margins/cash flow/cash/debt with period, "
        "(3) What Changed: max 4 bullets, "
        "(4) Risks Mentioned: max 6 bullets, "
        "(5) Market/Business Insights: max 4 bullets. "
        "For every numeric claim, include the source as (page/section or quote). "
        "If something is missing, write exactly: 'Not found in document'."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are an experienced financial analyst specializing in filings and earnings reports. "
        "You never guess: you extract only decision-relevant facts grounded in document evidence, "
        "and you cite page/section or short quotes for key numbers."
    ),
    tools=[FinancialDocumentTool()],
    llm=llm,
    max_iter=2,#increased max-iter so agent can extract more points
    allow_delegation=True,
)


# ==============================
# Document Verifier
# ==============================
verifier = Agent(
    role="Financial Document Verifier",
    goal=(
        "Verify whether the uploaded file is a financial document using only its content. "
        "You MUST use the Financial Document Reader tool to read the document first. "
        "Then search for ANY of these keywords: revenue, net income, cash flows, "
        "balance sheet, GAAP, non-GAAP, earnings, EPS, operating income, gross profit. "
        "If ANY of these exist, set is_financial_document to true (boolean). "
        "Return document_type (e.g. earnings update / annual report / 10-K / 10-Q) "
        "and rationale (max 2 bullets) citing specific quotes. "
        "IMPORTANT: is_financial_document MUST be a boolean (true/false), not Yes/No."
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You classify documents carefully based on internal evidence only, "
        "using minimal text and citing the exact cues that support your decision."
    ),
    tools=[FinancialDocumentTool()],
    llm=llm,
    max_iter=3,#increased max-iter so agent can extract more points
    allow_delegation=False,
)


# ==============================
# Investment Advisor
# ==============================
investment_advisor = Agent(
    role="Investment Advisor",
    goal=(
        "Provide investment insights grounded strictly in the uploaded financial document evidence. "
        "Do not use outside knowledge. "
        "Output format: "
        "(1) Recommendation: Buy/Hold/Sell/Watchlist/Insufficient evidence, "
        "(2) Top 3 evidence bullets with (page/section or quote), "
        "(3) 2 key risks with (page/section or quote), "
        "(4) 2 catalysts with (page/section or quote). "
        "If the document lacks required info, return 'Insufficient evidence' and ask exactly 1 follow-up question."
    ),
    verbose=True,
    backstory=(
        "You give cautious, evidence-based investment insights and refuse to invent facts. "
        "You only recommend when the document provides sufficient fundamentals and guidance."
    ),
    tools=[FinancialDocumentTool()],
    llm=llm,
    max_iter=3,#increased max-iter so agent can extract more points
    allow_delegation=False,
)


# ==============================
# Risk Assessor
# ==============================
risk_assessor = Agent(
    role="Risk Assessment Specialist",
    goal=(
        "Identify risks explicitly mentioned in the uploaded financial document only. "
        "List max 6 risks. For each risk, provide: "
        "Risk | Severity (Low/Med/High) | Evidence (page/section or short quote). "
        "Do not add hypothetical risks; if none are stated, write 'Not found in document'."
    ),
    verbose=True,
    backstory=(
        "You specialize in extracting disclosed operational, financial, regulatory, and market risks "
        "and always attach evidence from the document (page/section or quote)."
    ),
    tools=[FinancialDocumentTool()],
    llm=llm,
    max_iter=3,#increased to three
    allow_delegation=False,
)
