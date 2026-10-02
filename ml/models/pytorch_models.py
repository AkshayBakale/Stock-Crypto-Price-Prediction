"""
Deep Learning Quantitative Models in PyTorch
- PyTorch Dataset & Sequence DataLoader
- Architectures: LSTM, GRU, CNN-LSTM, TimeSeries Transformer
- Multi-Task Output Heads: Expected Return, Direction Logits, Quantile Forecasts (10th, 25th, 50th, 75th, 90th)
"""
from __future__ import annotations

try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    from torch.utils.data import Dataset, DataLoader
    _TORCH_AVAILABLE = True
    nn_Module = nn.Module
except ImportError:
    torch = None
    nn = None
    F = None
    Dataset = object
    DataLoader = None
    _TORCH_AVAILABLE = False
    nn_Module = object

import numpy as np
import os
from typing import Dict, Any, Tuple, Optional, List

class TimeSeriesSequenceDataset(Dataset):
    """
    Constructs rolling sequence windows [batch, seq_len, n_features]
    strictly from historical bars up to time T, predicting targets at T+h.
    """
    def __init__(
        self,
        features: np.ndarray,
        returns: np.ndarray,
        directions: np.ndarray,
        seq_len: int = 20
    ):
        self.seq_len = seq_len
        self.X_seqs = []
        self.y_returns = []
        self.y_directions = []

        n_samples = len(features)
        if n_samples > seq_len:
            for i in range(seq_len, n_samples):
                self.X_seqs.append(features[i - seq_len : i])
                self.y_returns.append(returns[i])
                self.y_directions.append(directions[i])

        self.X_seqs = torch.tensor(np.array(self.X_seqs), dtype=torch.float32) if self.X_seqs else torch.empty((0, seq_len, features.shape[1] if len(features.shape)>1 else 1))
        self.y_returns = torch.tensor(np.array(self.y_returns), dtype=torch.float32).unsqueeze(-1) if self.y_returns else torch.empty((0, 1))
        self.y_directions = torch.tensor(np.array(self.y_directions), dtype=torch.long) if self.y_directions else torch.empty((0,), dtype=torch.long)

    def __len__(self):
        return len(self.X_seqs)

    def __getitem__(self, idx):
        return self.X_seqs[idx], self.y_returns[idx], self.y_directions[idx]


class QuantileLoss(nn_Module):
    """Pinball loss for quantile regression (10th, 25th, 50th, 75th, 90th percentiles)."""
    def __init__(self, quantiles: List[float] = [0.10, 0.25, 0.50, 0.75, 0.90]):
        super().__init__()
        self.quantiles = quantiles

    def forward(self, preds: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        losses = []
        for i, q in enumerate(self.quantiles):
            error = target - preds[:, i:i+1]
            loss = torch.max((q - 1) * error, q * error)
            losses.append(loss.mean())
        return torch.stack(losses).mean()


class MultiTaskHead(nn_Module):
    """Shared output heads for Return, Direction Classification, and Quantile Cones."""
    def __init__(self, hidden_dim: int, num_quantiles: int = 5):
        super().__init__()
        # 1. Future return head
        self.return_head = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 1)
        )
        # 2. Direction classification (0: DOWN, 1: SIDEWAYS, 2: UP)
        self.direction_head = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 3)
        )
        # 3. Quantile forecast head
        self.quantile_head = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Linear(32, num_quantiles)
        )

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        ret = self.return_head(x)
        dir_logits = self.direction_head(x)
        quantiles = self.quantile_head(x)
        return ret, dir_logits, quantiles


class PyTorchLSTMModel(nn_Module):
    def __init__(self, input_dim: int, hidden_dim: int = 64, num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.heads = MultiTaskHead(hidden_dim)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        out, (h_n, _) = self.lstm(x)
        last_step = out[:, -1, :] # [batch, hidden_dim]
        return self.heads(last_step)


class PyTorchGRUModel(nn_Module):
    def __init__(self, input_dim: int, hidden_dim: int = 64, num_layers: int = 2, dropout: float = 0.2):
        super().__init__()
        self.gru = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.heads = MultiTaskHead(hidden_dim)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        out, _ = self.gru(x)
        last_step = out[:, -1, :]
        return self.heads(last_step)


class PyTorchCNNLSTMModel(nn_Module):
    def __init__(self, input_dim: int, hidden_dim: int = 64, num_layers: int = 1, dropout: float = 0.2):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels=input_dim, out_channels=32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.lstm = nn.LSTM(
            input_size=64,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.heads = MultiTaskHead(hidden_dim)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        # x: [batch, seq_len, input_dim] -> permute to [batch, input_dim, seq_len]
        c = x.permute(0, 2, 1)
        c = F.relu(self.conv1(c))
        c = F.relu(self.conv2(c))
        # permute back to [batch, seq_len, 64]
        c = c.permute(0, 2, 1)
        out, _ = self.lstm(c)
        last_step = out[:, -1, :]
        return self.heads(last_step)


class PyTorchTransformerModel(nn_Module):
    def __init__(self, input_dim: int, d_model: int = 64, nhead: int = 4, num_layers: int = 2, dropout: float = 0.1):
        super().__init__()
        self.embedding = nn.Linear(input_dim, d_model)
        self.pos_encoder = nn.Parameter(torch.randn(1, 100, d_model) * 0.02)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 2,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.heads = MultiTaskHead(d_model)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        seq_len = x.size(1)
        emb = self.embedding(x) + self.pos_encoder[:, :seq_len, :]
        out = self.transformer(emb)
        last_step = out[:, -1, :]
        return self.heads(last_step)


def build_pytorch_model(
    model_type: str,
    input_dim: int,
    hidden_dim: int = 64,
    dropout: float = 0.2
) -> nn.Module:
    mtype = model_type.lower()
    if mtype == "lstm":
        return PyTorchLSTMModel(input_dim=input_dim, hidden_dim=hidden_dim, dropout=dropout)
    elif mtype == "gru":
        return PyTorchGRUModel(input_dim=input_dim, hidden_dim=hidden_dim, dropout=dropout)
    elif mtype == "cnn_lstm":
        return PyTorchCNNLSTMModel(input_dim=input_dim, hidden_dim=hidden_dim, dropout=dropout)
    elif mtype == "transformer":
        return PyTorchTransformerModel(input_dim=input_dim, d_model=hidden_dim, dropout=dropout)
    else:
        return PyTorchLSTMModel(input_dim=input_dim, hidden_dim=hidden_dim, dropout=dropout)
