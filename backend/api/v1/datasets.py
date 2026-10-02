from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from ml.datasets.storage import DatasetStorage

router = APIRouter(prefix="/datasets", tags=["Dataset Registry"])

@router.get("", response_model=List[Dict[str, Any]])
async def list_datasets():
    """List all saved datasets stored in separate folders."""
    return DatasetStorage.list_saved_datasets()

@router.get("/{dataset_id}")
async def get_dataset_info(dataset_id: str):
    """Get metadata for a specific dataset."""
    datasets = DatasetStorage.list_saved_datasets()
    for d in datasets:
        if d.get("dataset_id") == dataset_id:
            return d
    raise HTTPException(status_code=404, detail="Dataset not found")
