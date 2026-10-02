"""
Model Registry & Artifact Manager
Saves and versions trained model artifacts, preprocessing scalers, configurations, metrics,
and explicit links to the training dataset folder in isolated directories.
Structure: models/<symbol>/<model_type>/<version>/
"""

import os
import json
import joblib
try:
    import torch
except ImportError:
    torch = None
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple

BASE_MODEL_DIR = os.path.abspath("models")

class ModelRegistryManager:
    @staticmethod
    def save_model(
        symbol: str,
        model_type: str,
        version: str,
        model_object: Any,
        preprocessor: Any,
        feature_names: List[str],
        hyperparameters: Dict[str, Any],
        metrics: Dict[str, Any],
        dataset_id: str,
        dataset_folder_path: str,
        status: str = "PRODUCTION"
    ) -> Dict[str, Any]:
        """
        Persists full model artifact bundle into dedicated isolated directory:
        models/<symbol>/<model_type>/<version>/
        """
        clean_sym = symbol.upper().replace("/", "").replace("-", "")
        target_dir = os.path.join(BASE_MODEL_DIR, clean_sym, model_type.lower(), version)
        os.makedirs(target_dir, exist_ok=True)

        model_id = f"MODEL_{clean_sym}_{model_type.upper()}_{version}"

        # 1. Save weights / model
        is_torch = isinstance(model_object, torch.nn.Module)
        if is_torch:
            model_file = os.path.join(target_dir, "model.pt")
            torch.save(model_object.state_dict(), model_file)
        else:
            model_file = os.path.join(target_dir, "model.joblib")
            joblib.dump(model_object, model_file)

        # 2. Save preprocessor scaler
        scaler_file = os.path.join(target_dir, "scaler.joblib")
        if preprocessor is not None:
            preprocessor.save(scaler_file)

        # 3. Save feature list
        features_file = os.path.join(target_dir, "features.json")
        with open(features_file, "w") as f:
            json.dump({"features": feature_names}, f, indent=2)

        # 4. Save metrics
        metrics_file = os.path.join(target_dir, "metrics.json")
        with open(metrics_file, "w") as f:
            json.dump(metrics, f, indent=2)

        # 5. Save training dataset link
        dataset_link_file = os.path.join(target_dir, "dataset_link.json")
        with open(dataset_link_file, "w") as f:
            json.dump({
                "dataset_id": dataset_id,
                "dataset_folder_path": dataset_folder_path
            }, f, indent=2)

        # 6. Save metadata
        metadata = {
            "model_id": model_id,
            "symbol": clean_sym,
            "model_type": model_type.lower(),
            "version": version,
            "status": status,
            "is_pytorch": is_torch,
            "hyperparameters": hyperparameters,
            "metrics": metrics,
            "dataset_id": dataset_id,
            "dataset_folder_path": dataset_folder_path,
            "folder_path": target_dir,
            "created_at": datetime.utcnow().isoformat()
        }
        meta_file = os.path.join(target_dir, "metadata.json")
        with open(meta_file, "w") as f:
            json.dump(metadata, f, indent=2)

        print(f"[ModelRegistry] Model saved to isolated folder: {target_dir}")
        return metadata

    @staticmethod
    def load_model_bundle(symbol: str, model_type: str, version: str = "v1.0") -> Tuple[Any, Any, Dict[str, Any]]:
        """Load model, scaler preprocessor, and metadata from registry folder."""
        from ml.preprocessing.scaler import DataPreprocessor
        from ml.models.pytorch_models import build_pytorch_model

        clean_sym = symbol.upper().replace("/", "").replace("-", "")
        target_dir = os.path.join(BASE_MODEL_DIR, clean_sym, model_type.lower(), version)
        
        if not os.path.exists(target_dir):
            raise FileNotFoundError(f"Model directory not found: {target_dir}")

        meta_file = os.path.join(target_dir, "metadata.json")
        with open(meta_file, "r") as f:
            metadata = json.load(f)

        scaler_file = os.path.join(target_dir, "scaler.joblib")
        preprocessor = DataPreprocessor.load(scaler_file) if os.path.exists(scaler_file) else None

        if metadata.get("is_pytorch", False):
            input_dim = len(metadata.get("hyperparameters", {}).get("feature_names", []))
            if input_dim == 0 and preprocessor:
                input_dim = len(preprocessor.feature_names)
            hidden_dim = metadata.get("hyperparameters", {}).get("hidden_dim", 64)
            
            model = build_pytorch_model(model_type, input_dim=input_dim, hidden_dim=hidden_dim)
            model_pt = os.path.join(target_dir, "model.pt")
            model.load_state_dict(torch.load(model_pt, map_location=torch.device("cpu")))
            model.eval()
        else:
            model_file = os.path.join(target_dir, "model.joblib")
            model = joblib.load(model_file)

        return model, preprocessor, metadata

    @staticmethod
    def list_models() -> List[Dict[str, Any]]:
        """List all models currently in the filesystem registry."""
        if not os.path.exists(BASE_MODEL_DIR):
            return []

        models_list = []
        for sym in os.listdir(BASE_MODEL_DIR):
            sym_path = os.path.join(BASE_MODEL_DIR, sym)
            if os.path.isdir(sym_path):
                for mtype in os.listdir(sym_path):
                    mtype_path = os.path.join(sym_path, mtype)
                    if os.path.isdir(mtype_path):
                        for ver in os.listdir(mtype_path):
                            ver_path = os.path.join(mtype_path, ver)
                            meta_path = os.path.join(ver_path, "metadata.json")
                            if os.path.exists(meta_path):
                                try:
                                    with open(meta_path, "r") as f:
                                        meta = json.load(f)
                                    models_list.append(meta)
                                except Exception:
                                    pass
        models_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return models_list
