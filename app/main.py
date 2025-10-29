from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.input_parser import FileParser
from app.services.research_assistant import ResearchAgent
from app.utils.logger import Logger

logger = Logger.get_logger()


class AgentResponse(BaseModel):
    response: str


app = FastAPI(
    title="Research Agent API",
    description=(
        "Upload a **PDF**, **DOCX**, or **TXT** file. The AI agent reads it, "
        "extracts insights, summarizes the content, and generates smart follow-up questions—all in one response."
    ),
    version="0.1.0",
)


@app.post(
    "/ask-agent",
    response_model=AgentResponse,
    summary="Parse input file and prompt AI agent for response.",
    description=(
        "Upload a research document (PDF, DOCX, TXT). "
        "The agent analyzes it and returns a one string incorporating "
        "containing a summary, insights, and follow-up questions."
    ),
)
async def ask_agent(
    file: UploadFile = File(..., description="Your research file (PDF, DOCX, or TXT)")
):
    logger.debug(f"UploadFile object: {file}")
    try:
        text = FileParser().parse_file(file)
        if text == "UNSUPPORTED FILE":
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Supported: PDF, DOCX, TXT",
            )

        agent_res = ResearchAgent().run(text)
        return JSONResponse(content=agent_res)
        return {"response": "fake agent_res"}

    except HTTPException as he:
        logger.warning(f"HTTP error: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
