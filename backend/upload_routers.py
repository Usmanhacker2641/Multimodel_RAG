from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Dict, Any, Optional
import os
from pathlib import Path
from pipelines.full_pipeline import FullPipeline
import tempfile
from core.logger import setup_logger

# Configure logging
logger = setup_logger("backend.upload")

# Create router
router = APIRouter(prefix="/upload", tags=["Upload"])
pipeline = FullPipeline()

# Supported file types
SUPPORTED_EXTENSIONS = {
    '.pdf', '.docx', '.doc', '.txt', 
    '.mp3', '.wav', '.m4a', '.ogg',  # audio
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'  # images
}

MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limit


@router.post("/", response_model=Dict[str, Any])
async def upload_data(
    text: Optional[str] = Form(None),
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Upload and process various data types (text, URL, or file)
    
    - Extracts text from uploaded file
    - Cleans and preprocesses text
    - Chunks text into meaningful segments
    - Stores embeddings in vector database
    
    Returns:
        dict: Processing status and number of chunks stored
    """
    input_data = {}
    temp_file_path = None
    try:
        if file:
            if not file.filename:
                logger.warning("Upload attempt with no filename")
                raise HTTPException(status_code=400, detail="No filename provided")
            
            file_ext = Path(file.filename).suffix.lower()
            logger.info("Processing file upload: filename=%s extension=%s size=%s", file.filename, file_ext, file.size if hasattr(file, 'size') else 'unknown')
            
            if file_ext not in SUPPORTED_EXTENSIONS:
                logger.warning("Unsupported file type: %s", file_ext)
                raise HTTPException(
                    status_code=400, 
                    detail=f"Unsupported file type: {file_ext}. Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
                )

            # Save temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
                logger.info("Saved temporary file: path=%s size=%d", temp_file_path, len(content))
            
            input_data = {"file_path": temp_file_path}

        elif text:
            logger.info("Processing text upload: length=%d", len(text))
            input_data = {"text": text}
        elif url:
            logger.info("Processing URL upload: url=%s", url)
            input_data = {"url": url}
        else:
            logger.warning("Upload attempt with no input data")
            raise HTTPException(status_code=400, detail="No input data provided. Use 'text', 'url', or 'file'.")

        logger.info("Starting pipeline processing: input_type=%s", list(input_data.keys())[0])
        result = pipeline.process(input_data)
        logger.info("Pipeline processing complete: status=%s", result.get("status"))

        if result.get("status") == "error":
            logger.error("Pipeline returned error: %s", result.get("message"))
            raise HTTPException(status_code=500, detail=result.get("message"))

        logger.info("Upload successful: chunks=%s", result.get("chunks", 0))
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Upload failed with unexpected error: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            logger.debug("Cleaning up temporary file: %s", temp_file_path)
            os.remove(temp_file_path)