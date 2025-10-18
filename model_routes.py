from fastapi import APIRouter, Form
from services.model_config import get_model_settings, update_model_settings

router = APIRouter(prefix="/model", tags=["Model Config"])


@router.post("/update")
async def update_config(
    temperature: float = Form(...),
    top_p: float = Form(...),
    max_tokens: int = Form(...),
    freq_penalty: float = Form(...),
    pres_penalty: float = Form(...),
    chunk_size: int = Form(...),
):
    update_model_settings(
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        frequency_penalty=freq_penalty,
        presence_penalty=pres_penalty,
        chunk_size=chunk_size,
    )
    
    return {"status": "Config updated"}


@router.get("/get")
async def get_config():
    return get_model_settings()