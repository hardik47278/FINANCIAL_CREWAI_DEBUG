# task.py
from crewai import Task

from agent import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import FinancialDocumentTool


financial_doc_tool = FinancialDocumentTool()  # CREATED SINGLE INSTANCE


analyze_financial_document = Task(
    description=(
        "Answer the user's query using ONLY the uploaded financial document.\n\n"
        "Document path: {path}\n"
        "User query: {query}\n\n"
        "You MUST first read the document using the Financial Document Reader tool.\n\n"
        "Rules:\n"
        "- Do NOT fabricate facts.\n"
        "- Use only document information.\n"
        "- If information is missing, state it clearly.\n"
        "- Return ONLY raw JSON (no markdown, no backticks, no code fences).\n"
        "- Output MUST start with '{' and end with '}' only.\n"
        "- Every evidence.snippet MUST be an exact substring from the Financial Document Reader tool output text.\n"
        "- Include a \"market_insights\" list (macro, competition, demand, pricing, regulation, AI/energy strategy) ONLY if supported by the document.\n\n"
        "Steps:\n"
        "1. Read the financial document.\n"
        "2. Extract relevant financial data.\n"
        "3. Answer the query using evidence.\n"
        "4. Add market_insights grounded in document evidence.\n"
        "5. Ensure evidence snippets are direct quotes from the document text.\n"
    ),
    expected_output=(
        "Return VALID JSON ONLY (no markdown/backticks):\n"
        "{\n"
        '  "answer": string,\n'
        '  "key_points": [string],\n'
        '  "market_insights": [string],\n'
        '  "evidence": [{"snippet": string, "location": string}],\n'
        '  "missing_info": [string]\n'
        "}"
    ),
    agent=financial_analyst,
    tools=[financial_doc_tool],
    async_execution=False,
)


investment_analysis = Task(
    description=(
        "Create investment analysis using ONLY the uploaded financial document.\n\n"
        "Document path: {path}\n"
        "User query: {query}\n\n"
        "You MUST first read the document using the Financial Document Reader tool.\n\n"
        "Rules:\n"
        "- Do NOT fabricate facts.\n"
        "- Use only document information.\n"
        "- If information is missing, state it clearly.\n"
        "- Return ONLY raw JSON (no markdown, no backticks, no code fences).\n"
        "- Output MUST start with '{' and end with '}' only.\n"
        "- Every evidence.snippet MUST be an exact substring from the Financial Document Reader tool output text.\n"
        "- recommendation MUST be one of: \"buy\", \"hold\", \"sell\", \"insufficient_evidence\".\n"
        "- You MUST look for an Outlook or Forward-Looking section in the document for catalysts and guidance.\n"  # ✅ ADDED
        "- Only return insufficient_evidence if the document has NO financial data whatsoever.\n\n"  # ✅ ADDED
        "Return a concise investment analysis grounded in evidence from the document. "
        "Ensure evidence snippets are direct quotes from the document text."
    ),
    expected_output=(
        "Return VALID JSON ONLY (no markdown/backticks):\n"
        "{\n"
        '  "recommendation": string,\n'
        '  "time_horizon": string,\n'
        '  "confidence": string,\n'
        '  "thesis": [string],\n'
        '  "catalysts": [string],\n'
        '  "risks": [string],\n'
        '  "evidence": [{"snippet": string, "location": string}],\n'
        '  "missing_info": [string]\n'
        "}"
    ),
    agent=investment_advisor,
    context=[analyze_financial_document],
    tools=[financial_doc_tool],
    async_execution=False,
)


risk_assessment = Task(
    description=(
        "Identify risks using ONLY the uploaded financial document.\n\n"
        "Document path: {path}\n"
        "User query: {query}\n\n"
        "You MUST first read the document using the Financial Document Reader tool.\n\n"
        "Rules:\n"
        "- Do NOT fabricate facts.\n"
        "- Use only document information.\n"
        "- If information is missing, state it clearly.\n"
        "- Return ONLY raw JSON (no markdown, no backticks, no code fences).\n"
        "- Output MUST start with '{' and end with '}' only.\n"
        "- Every evidence.snippet MUST be an exact substring from the Financial Document Reader tool output text.\n\n"
        "Return risks that are explicitly mentioned in the document. "
        "Ensure evidence snippets are direct quotes from the document text."
    ),
    expected_output=(
        "Return VALID JSON ONLY (no markdown/backticks):\n"
        "{\n"
        '  "risks": [{"risk": string, "severity": string, "evidence": {"snippet": string, "location": string}}],\n'
        '  "missing_info": [string]\n'
        "}"
    ),
    agent=risk_assessor,
    context=[analyze_financial_document],
    tools=[financial_doc_tool],
    async_execution=False,
)


verification = Task(
    description=(
        "Verify whether the uploaded file is a financial document using ONLY its content.\n\n"
        "Document path: {path}\n\n"
        "You MUST first read the document using the Financial Document Reader tool.\n\n"
        "Rules:\n"
        "- Do NOT fabricate facts.\n"
        "- Use only document information.\n"
        "- If information is missing, state it clearly.\n"
        "- Return ONLY raw JSON (no markdown, no backticks, no code fences).\n"
        "- Output MUST start with '{' and end with '}' only.\n"
        "- You MUST look for terms like: \"revenues\", \"net income\", \"cash flows\", \"balance sheet\", \"GAAP\", \"non-GAAP\".\n"
        "- If any of these exist in the document, is_financial_document MUST be true.\n"
        "- Every evidence.snippet MUST be an exact substring from the Financial Document Reader tool output text.\n\n"
        "Steps:\n"
        "1. Read the document using the Financial Document Reader tool.\n"
        "2. Check for the required financial keywords in the returned text.\n"
        "3. If any exist, set is_financial_document=true and document_type to an appropriate type (e.g., \"earnings update\", \"annual report\", \"10-Q\", \"10-K\").\n"
        "4. Return verification based on document evidence.\n"
    ),
    expected_output=(
        "Return VALID JSON ONLY (no markdown/backticks):\n"
        "{\n"
        '  "is_financial_document": boolean,\n'
        '  "document_type": string,\n'
        '  "rationale": [string],\n'
        '  "evidence": [{"snippet": string, "location": string}],\n'
        '  "missing_info": [string]\n'
        "}"
    ),
    agent=verifier,
    tools=[financial_doc_tool],
    context=[analyze_financial_document],
    async_execution=False,
)
