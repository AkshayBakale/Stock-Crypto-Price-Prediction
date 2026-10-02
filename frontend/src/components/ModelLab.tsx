import React, { useState, useEffect } from "react";
import { ModelMetadata } from "../types";
import { api } from "../services/api";
import { 
  BrainCircuit, 
  Play, 
  CheckCircle2, 
  XCircle, 
  Folder, 
  TrendingUp, 
  Award, 
  Activity,
  Layers
} from "lucide-react";

interface ModelLabProps {
  activeSymbol: string;
  onTrainingFinished?: () => void;
  models: ModelMetadata[];
  onRefreshModels: () => void;
}

export const ModelLab: React.FC<ModelLabProps> = ({
  activeSymbol,
  onTrainingFinished,
  models,
  onRefreshModels,
}) => {
  const [selectedSymbol, setSelectedSymbol] = useState(activeSymbol || "BTCUSDT");
  const [modelType, setModelType] = useState("xgboost");
  const [timeframe, setTimeframe] = useState("1h");
  const [epochs, setEpochs] = useState(15);
  const [learningRate, setLearningRate] = useState(0.001);
  const [batchSize, setBatchSize] = useState(32);

  const [isTraining, setIsTraining] = useState(false);
  const [trainingStatus, setTrainingStatus] = useState<string | null>(null);
  const [currentEpoch, setCurrentEpoch] = useState(0);
  const [epochLogs, setEpochLogs] = useState<Array<{ epoch: number; train_loss: number; val_loss: number }>>([]);
  const [trainingError, setTrainingError] = useState<string | null>(null);
  const [completedResult, setCompletedResult] = useState<any | null>(null);

  useEffect(() => {
    setSelectedSymbol(activeSymbol);
  }, [activeSymbol]);

  const handleStartTraining = async () => {
    setIsTraining(true);
    setTrainingStatus("QUEUED");
    setTrainingError(null);
    setCompletedResult(null);
    setEpochLogs([]);
    setCurrentEpoch(0);

    try {
      const res = await api.triggerTraining({
        symbol: selectedSymbol,
        model_type: modelType,
        timeframe,
        epochs,
        learning_rate: learningRate,
        batch_size: batchSize,
      });

      setTrainingStatus(res.status);
    } catch (err: any) {
      setIsTraining(false);
      setTrainingError(err.message || "Failed to trigger training");
    }
  };

  // Process live training updates from parent/websocket
  useEffect(() => {
    const handleWsEvent = (e: any) => {
      const data = e.detail;
      if (!data) return;

      if (data.status === "TRAINING") {
        setTrainingStatus("TRAINING");
        setCurrentEpoch(data.epoch);
        setEpochLogs((prev) => [
          ...prev.filter((l) => l.epoch !== data.epoch),
          { epoch: data.epoch, train_loss: data.train_loss, val_loss: data.val_loss },
        ]);
      } else if (data.status === "COMPLETED") {
        setIsTraining(false);
        setTrainingStatus("COMPLETED");
        setCompletedResult(data.result);
        onRefreshModels();
        if (onTrainingFinished) onTrainingFinished();
      } else if (data.status === "FAILED") {
        setIsTraining(false);
        setTrainingStatus("FAILED");
        setTrainingError(data.error || "Training failed");
      }
    };

    window.addEventListener("app_training_update", handleWsEvent);
    return () => window.removeEventListener("app_training_update", handleWsEvent);
  }, [onRefreshModels, onTrainingFinished]);

  return (
    <div className="space-y-6">
      {/* Training Header & Launcher Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Configuration Form */}
        <div className="bg-[#0D1117] border border-[#232936] rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 pb-4 border-b border-[#232936] mb-4">
              <BrainCircuit className="h-5 w-5 text-blue-400" />
              <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider">
                Train New Model Architecture
              </h2>
            </div>

            <div className="space-y-4 text-xs font-mono">
              {/* Symbol */}
              <div>
                <label className="block text-[#8B949E] mb-1">Target Instrument</label>
                <input
                  type="text"
                  value={selectedSymbol}
                  onChange={(e) => setSelectedSymbol(e.target.value.toUpperCase())}
                  className="w-full bg-[#151A22] border border-[#232936] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-blue-500"
                />
              </div>

              {/* Model Architecture */}
              <div>
                <label className="block text-[#8B949E] mb-1">Model Architecture</label>
                <select
                  value={modelType}
                  onChange={(e) => setModelType(e.target.value)}
                  className="w-full bg-[#151A22] border border-[#232936] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-blue-500"
                >
                  <optgroup label="Gradient Boosted Trees">
                    <option value="xgboost">XGBoost Regressor & Classifier</option>
                    <option value="lightgbm">LightGBM Fast GBDT</option>
                  </optgroup>
                  <optgroup label="Deep Learning (PyTorch)">
                    <option value="lstm">Multi-Layer LSTM Network</option>
                    <option value="gru">Gated Recurrent Unit (GRU)</option>
                    <option value="cnn_lstm">CNN-LSTM Hybrid</option>
                    <option value="transformer">Time-Series Transformer</option>
                  </optgroup>
                  <optgroup label="Baselines">
                    <option value="naive">Naive Persistence Forecast</option>
                    <option value="linear_regression">Linear Ridge Regression</option>
                  </optgroup>
                </select>
              </div>

              {/* Timeframe & Epochs */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#8B949E] mb-1">Bar Timeframe</label>
                  <select
                    value={timeframe}
                    onChange={(e) => setTimeframe(e.target.value)}
                    className="w-full bg-[#151A22] border border-[#232936] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-blue-500"
                  >
                    <option value="1m">1 Minute</option>
                    <option value="5m">5 Minutes</option>
                    <option value="15m">15 Minutes</option>
                    <option value="1h">1 Hour</option>
                    <option value="1d">1 Day</option>
                  </select>
                </div>

                <div>
                  <label className="block text-[#8B949E] mb-1">Epochs ({epochs})</label>
                  <input
                    type="range"
                    min="5"
                    max="50"
                    value={epochs}
                    onChange={(e) => setEpochs(Number(e.target.value))}
                    disabled={modelType === "xgboost" || modelType === "lightgbm"}
                    className="w-full accent-blue-500 mt-2"
                  />
                </div>
              </div>

              {/* Learning Rate & Batch Size */}
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[#8B949E] mb-1">Learning Rate</label>
                  <input
                    type="number"
                    step="0.0005"
                    value={learningRate}
                    onChange={(e) => setLearningRate(Number(e.target.value))}
                    className="w-full bg-[#151A22] border border-[#232936] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-[#8B949E] mb-1">Batch Size</label>
                  <select
                    value={batchSize}
                    onChange={(e) => setBatchSize(Number(e.target.value))}
                    className="w-full bg-[#151A22] border border-[#232936] rounded-lg px-3 py-2 text-white font-mono focus:outline-none focus:border-blue-500"
                  >
                    <option value="16">16</option>
                    <option value="32">32</option>
                    <option value="64">64</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <button
            onClick={handleStartTraining}
            disabled={isTraining}
            className={`mt-6 w-full py-2.5 px-4 rounded-lg font-mono font-bold text-xs flex items-center justify-center space-x-2 transition-all shadow-lg ${
              isTraining
                ? "bg-blue-600/50 text-white cursor-not-allowed"
                : "bg-blue-600 hover:bg-blue-500 text-white shadow-blue-600/25"
            }`}
          >
            {isTraining ? (
              <>
                <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
                <span>Training in Background...</span>
              </>
            ) : (
              <>
                <Play className="h-4 w-4 fill-current" />
                <span>Execute Real Training Run</span>
              </>
            )}
          </button>
        </div>

        {/* Right 2 cols: Live Training Monitor & Real Loss Curves */}
        <div className="lg:col-span-2 bg-[#0D1117] border border-[#232936] rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-4 border-b border-[#232936] mb-4">
              <div className="flex items-center space-x-2">
                <Activity className="h-5 w-5 text-emerald-400" />
                <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider">
                  Live Training Telemetry & Loss Curves
                </h3>
              </div>
              {trainingStatus && (
                <span className="px-2.5 py-1 text-xs font-mono font-semibold rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
                  STATUS: {trainingStatus}
                </span>
              )}
            </div>

            {/* Live Progress Bar */}
            {isTraining && (
              <div className="mb-4 bg-[#151A22] p-4 rounded-lg border border-[#232936]">
                <div className="flex justify-between text-xs font-mono text-[#8B949E] mb-2">
                  <span>
                    Epoch {currentEpoch} of {epochs}
                  </span>
                  <span>{Math.round((currentEpoch / epochs) * 100)}%</span>
                </div>
                <div className="w-full bg-[#0B0E14] h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-blue-500 h-full rounded-full transition-all duration-300"
                    style={{ width: `${Math.max(5, (currentEpoch / epochs) * 100)}%` }}
                  />
                </div>
              </div>
            )}

            {/* Epoch Logs Table / Loss Graph representation */}
            <div className="bg-[#151A22] border border-[#232936] rounded-lg p-3 min-h-[220px]">
              <div className="text-xs font-mono text-[#8B949E] mb-2 flex justify-between">
                <span>EPOCH PROGRESSION LOG</span>
                <span>METRICS (MSE LOSS)</span>
              </div>
              {epochLogs.length === 0 ? (
                <div className="h-40 flex items-center justify-center text-xs font-mono text-[#6E7681]">
                  Launch a training run to view real epoch loss convergence.
                </div>
              ) : (
                <div className="space-y-1.5 max-h-44 overflow-y-auto pr-1">
                  {epochLogs.map((log) => (
                    <div
                      key={log.epoch}
                      className="flex items-center justify-between text-xs font-mono py-1 px-2 rounded bg-[#0B0E14] border border-[#232936]"
                    >
                      <span className="text-blue-400 font-bold">Epoch {log.epoch}</span>
                      <div className="space-x-4">
                        <span className="text-[#8B949E]">
                          Train Loss: <span className="text-white font-bold">{log.train_loss}</span>
                        </span>
                        <span className="text-[#8B949E]">
                          Val Loss: <span className="text-emerald-400 font-bold">{log.val_loss}</span>
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Error or Success Alert */}
            {trainingError && (
              <div className="mt-4 p-3 bg-red-950/40 border border-red-500/30 rounded-lg flex items-center space-x-2 text-xs font-mono text-red-400">
                <XCircle className="h-4 w-4 shrink-0" />
                <span>{trainingError}</span>
              </div>
            )}

            {completedResult && (
              <div className="mt-4 p-3 bg-emerald-950/40 border border-emerald-500/30 rounded-lg space-y-2 text-xs font-mono text-emerald-300">
                <div className="flex items-center space-x-2 font-bold">
                  <CheckCircle2 className="h-4 w-4 text-emerald-400 shrink-0" />
                  <span>Model Trained & Persisted Successfully!</span>
                </div>
                <div className="text-[11px] text-[#8B949E] space-y-1">
                  <div>
                    <span className="text-white font-medium">Model Artifacts: </span>
                    <span className="text-blue-300">{completedResult.model_folder}</span>
                  </div>
                  <div>
                    <span className="text-white font-medium">Training Dataset: </span>
                    <span className="text-emerald-400">{completedResult.dataset_folder}</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Model Registry Leaderboard */}
      <div className="bg-[#0D1117] border border-[#232936] rounded-xl p-5 shadow-lg">
        <div className="flex items-center justify-between pb-4 border-b border-[#232936] mb-4">
          <div className="flex items-center space-x-2">
            <Award className="h-5 w-5 text-amber-400" />
            <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider">
              Model Registry & Governance
            </h3>
          </div>
          <button
            onClick={onRefreshModels}
            className="px-3 py-1 bg-[#151A22] hover:bg-[#1E2430] border border-[#232936] text-xs font-mono text-white rounded transition-colors"
          >
            Refresh Registry
          </button>
        </div>

        {models.length === 0 ? (
          <div className="py-8 text-center text-xs font-mono text-[#8B949E]">
            No registered models found in filesystem storage. Train your first model above!
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead className="bg-[#151A22] text-[#8B949E] border-b border-[#232936]">
                <tr>
                  <th className="py-2.5 px-3">Model ID</th>
                  <th className="py-2.5 px-3">Symbol</th>
                  <th className="py-2.5 px-3">Architecture</th>
                  <th className="py-2.5 px-3">Status</th>
                  <th className="py-2.5 px-3">MAE</th>
                  <th className="py-2.5 px-3">RMSE</th>
                  <th className="py-2.5 px-3">Direction Hit %</th>
                  <th className="py-2.5 px-3">Sharpe Ratio</th>
                  <th className="py-2.5 px-3">Isolated Storage Folders</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[#232936]/60">
                {models.map((m) => (
                  <tr key={m.model_id} className="hover:bg-[#151A22]/50 transition-colors">
                    <td className="py-3 px-3 font-bold text-white">{m.model_id}</td>
                    <td className="py-3 px-3 text-blue-400 font-semibold">{m.symbol}</td>
                    <td className="py-3 px-3 uppercase text-[#8B949E]">{m.model_type}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {m.status}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-white">{m.metrics?.mae ?? "---"}</td>
                    <td className="py-3 px-3 text-white">{m.metrics?.rmse ?? "---"}</td>
                    <td className="py-3 px-3 text-emerald-400 font-bold">
                      {m.metrics?.directional_accuracy_pct ? `${m.metrics.directional_accuracy_pct}%` : "---"}
                    </td>
                    <td className="py-3 px-3 text-blue-400">{m.metrics?.sharpe_ratio ?? "---"}</td>
                    <td className="py-3 px-3 text-[10px] text-[#8B949E]">
                      <div className="flex items-center space-x-1 truncate max-w-xs">
                        <Folder className="h-3 w-3 text-amber-400 shrink-0" />
                        <span className="truncate">{m.folder_path}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
