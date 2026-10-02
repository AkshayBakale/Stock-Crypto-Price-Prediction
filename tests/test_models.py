import pytest
import numpy as np
from ml.models.baseline import BaselineModel

def test_pytorch_architectures():
    torch = pytest.importorskip("torch")
    from ml.models.pytorch_models import build_pytorch_model
    batch_size = 4
    seq_len = 10
    input_dim = 15

    dummy_input = torch.randn(batch_size, seq_len, input_dim)

    for arch in ["lstm", "gru", "cnn_lstm", "transformer"]:
        model = build_pytorch_model(arch, input_dim=input_dim, hidden_dim=32)
        model.eval()
        with torch.no_grad():
            ret, direction, quantiles = model(dummy_input)
            assert ret.shape == (batch_size, 1)
            assert direction.shape == (batch_size, 3) # 3-class logits
            assert quantiles.shape == (batch_size, 5) # 5 quantiles

def test_tree_and_baseline_models():
    X = np.random.randn(50, 10)
    y = np.random.randn(50)

    # Baseline
    base = BaselineModel(model_type="moving_average")
    base.fit(X, y)
    preds = base.predict(X)
    assert len(preds) == 50

    # XGBoost
    pytest.importorskip("xgboost")
    from ml.models.tree_models import QuantitativeTreeModel
    xgb_mod = QuantitativeTreeModel(model_type="xgboost", task="regression")
    xgb_mod.fit(X, y)
    preds_xgb = xgb_mod.predict(X)
    assert len(preds_xgb) == 50
