from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ml.registry.registry import ModelRegistryManager

router = APIRouter(prefix="/models", tags=["Model Registry"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_registered_models():
    """List all registered models across isolated artifact folders."""
    return ModelRegistryManager.list_models()

@router.get("/{model_id}")
async def get_model_details(model_id: str):
    """Get metadata for a specific model ID."""
    all_models = ModelRegistryManager.list_models()
    for m in all_models:
        if m["model_id"] == model_id:
            return m
    raise HTTPException(status_code=404, detail="Model not found in registry")
