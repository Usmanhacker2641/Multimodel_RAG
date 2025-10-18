from fastapi import APIRouter, Form, HTTPException
from typing import Optional, Dict, Any, List
from pipelines.full_pipeline import FullPipeline
from core.logger import setup_logger

# Configure logging
logger = setup_logger("backend.query")

# Initialize router
router = APIRouter(prefix="/query", tags=["Query"])
pipeline = FullPipeline()

@router.post("/")
async def query_rag(
    question: str = Form(...),
    mode: str = Form("rag"),
    top_k: int = Form(5),
    hf_api_key: Optional[str] = Form(None),
    deepseek_api_key: Optional[str] = Form(None),
    gemini_api_key: Optional[str] = Form(None)
) -> Dict[str, Any]:
    """
    Handle RAG + Multi-LLM query processing.
    
    Args:
        question: User's question
        mode: Query mode - "rag" (with context) or "direct" (without context)
        top_k: Number of top relevant chunks to retrieve
        hf_api_key: Hugging Face API key
        deepseek_api_key: DeepSeek API key
        gemini_api_key: Gemini API key
    
    Returns:
        Dictionary containing context, multiple LLM answers, and final answer
    """
    try:
        logger.info("Query received: question=%s mode=%s top_k=%d", question[:100], mode, top_k)
        
        # Prepare API keys dictionary
        api_keys = {}
        if hf_api_key:
            api_keys["hf_api_key"] = hf_api_key
            logger.debug("HuggingFace API key provided")
        if deepseek_api_key:
            api_keys["deepseek_api_key"] = deepseek_api_key
            logger.debug("DeepSeek API key provided")
        if gemini_api_key:
            api_keys["gemini_api_key"] = gemini_api_key
            logger.debug("Gemini API key provided")

        logger.info("Starting query processing: mode=%s api_keys_count=%d", mode, len(api_keys))
        
        if mode == "rag":
            result = pipeline.query(question, top_k=top_k, api_keys=api_keys)
        else: # direct
            # Simplified direct query for now
            result = pipeline.query(question, top_k=0, api_keys=api_keys) 
        
        if result.get("status") == "error":
            logger.error("Pipeline query returned error: %s", result.get("message"))
            raise HTTPException(status_code=500, detail=result.get("message"))
        
        logger.info("Query successful: llm_count=%d context_chunks=%d", 
                   len(result.get("llm_answers", [])),
                   len(result.get("context", [])))
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Query failed with unexpected error: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for query service.
    """
    return {
        "status": "healthy",
        "service": "query_routes"
    }