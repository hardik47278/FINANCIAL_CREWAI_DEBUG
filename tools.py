from typing import Type
from dotenv import load_dotenv
load_dotenv()

from pydantic import BaseModel, Field
from crewai.tools import BaseTool#base tool addeed to make a tools base class instance
from crewai_tools import SerperDevTool#corrected import 
from langchain_community.document_loaders import PyPDFLoader#IMPORT WAS MISSING


# -----------------------------
# Search Tool
# -----------------------------
search_tool = SerperDevTool()


# -----------------------------
# Input Schema
# -----------------------------
class FinancialDocumentInput(BaseModel):#base model added to
    path: str = Field(..., description="Path to uploaded PDF")


# -----------------------------
# PDF Reader Tool
# -----------------------------
#CAUSED PYDANTIC ERROR EARLIER
#added base tool asfinancial document analysis was not implemented as a sub class of crewai's BaseTool
class FinancialDocumentTool(BaseTool):
    name: str = "Financial Document Reader"
    description: str = "Reads uploaded financial PDF document."
    args_schema: Type[BaseModel] = FinancialDocumentInput

    def _run(self, path: str) -> str:

        loader = PyPDFLoader(path)
        docs = loader.load()

        full_text = ""

        for d in docs:
            content = d.page_content or ""
            content = content.replace("\n\n", "\n")
            full_text += content + "\n"

        return full_text

    async def _arun(self, path: str) -> str:
        return self._run(path)
#AFTER THIS [FinancialDocumentTool()] WILL BE CORRECT
