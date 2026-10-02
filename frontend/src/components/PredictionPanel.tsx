import React from "react";
import { PredictionData } from "../types";
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  ShieldAlert, 
  Layers, 
  Info, 
  BrainCircuit, 
  Gauge,
  Folder
} from "lucide-react";

interface PredictionPanelProps {
  prediction: PredictionData | null;
  activeSymbol: string;
  onNavigateToTrain: () => void;
}

export const PredictionPanel: React.FC<PredictionPanelProps> = ({
  prediction,
  activeSymbol,
  onNavigateToTrain,
}) => {
  if (!prediction || prediction.status === "MODEL NOT TRAINED") {
    return (
      <div className="bg-[#0D1117] border border-[#232936] rounded-xl p-5 shadow-lg flex flex-col justify-between">
        <div>
          <div className="flex items-center space-x-2 pb-3 border-b border-[#232936]">
            <BrainCircuit className="h-4 w-4 text-amber-400" />
            <h3 className="text-sm font-mono font-bold text-white uppercase tracking-wider">AI Forecast & Inference</h3>
          </div>
          <div className="py-8 text-center">
            <div className="inline-flex p-3 bg-amber-500/10 border border-amber-500/20 rounded-full text-amber-400 mb-3">
              <Info className="h-6 w-6" />
            </div>
            <h4 className="text-sm font-semibold text-white mb-1">Model Not Trained For {activeSymbol}</h4>
            <p className="text-xs text-[#8B949E] max-w-xs mx-auto mb-4">
              Antigravity enforces strict zero-fake-data rules. Please train a PyTorch DL or XGBoost model on actual historical data to generate predictions.
            </p>
            <button
              onClick={onNavigateToTrain}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-mono font-semibold transition-all shadow-md shadow-blue-600/20"
            >
              Open AI Model Lab & Train
            </button>
          </div>
        </div>

        {/* Disclaimer */}
        <div className="text-[10px] text-[#6E7681] border-t border-[#1E2430] pt-3">
          AI forecasts are probabilistic estimates. They are not guaranteed and not financial advice.
        </div>
      </div>
    );
  }

  const isUp = prediction.direction === "UP";
  const isDown = prediction.direction === "DOWN";
  const directionColor = isUp
    ? "text-emerald-400 bg-emerald-950/40 border-emerald-500/30"
    : isDown
    ? "text-rose-400 bg-rose-950/40 border-rose-500/30"
    : "text-amber-400 bg-amber-950/40 border-amber-500/30";

  return (
    <div className="bg-[#0D1117] border border-[#232936] rounded-xl p-4 shadow-lg flex flex-col space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-[#232936]">
        <div className="flex items-center space-x-2">
          <BrainCircuit className="h-4 w-4 text-blue-400" />
          <h3 className="text-xs font-mono font-bold text-white uppercase tracking-wider">AI Forecast & Inference</h3>
        </div>
        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
          {prediction.model_type?.toUpperCase()} {prediction.model_version}
        </span>
      </div>

      {/* Main Direction Banner */}
      <div className={`p-3.5 rounded-lg border flex items-center justify-between ${directionColor}`}>
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-[#0B0E14]/60 rounded-lg">
            {isUp ? (
              <TrendingUp className="h-5 w-5 text-emerald-400" />
            ) : isDown ? (
              <TrendingDown className="h-5 w-5 text-rose-400" />
            ) : (
              <Minus className="h-5 w-5 text-amber-400" />
            )}
          </div>
          <div>
            <div className="text-[10px] uppercase font-mono tracking-wider opacity-80">Predicted Direction</div>
            <div className="text-lg font-mono font-bold tracking-tight">{prediction.direction}</div>
          </div>
        </div>

        <div className="text-right font-mono">
          <div className="text-[10px] uppercase tracking-wider opacity-80">Expected Return</div>
          <div className="text-sm font-bold">
            {prediction.expected_return_pct && prediction.expected_return_pct > 0 ? "+" : ""}
            {prediction.expected_return_pct?.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Confidence & Target Price */}
      <div className="grid grid-cols-2 gap-2">
        <div className="bg-[#151A22] border border-[#232936] p-3 rounded-lg">
          <div className="text-[10px] text-[#8B949E] font-mono uppercase mb-1">Target Price (1h)</div>
          <div className="text-base font-mono font-bold text-white">
            ${prediction.predicted_price?.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </div>
        </div>

        <div className="bg-[#151A22] border border-[#232936] p-3 rounded-lg">
          <div className="text-[10px] text-[#8B949E] font-mono uppercase mb-1">Calibrated Prob</div>
          <div className="text-base font-mono font-bold text-emerald-400">
            {((prediction.calibrated_probability || 0.5) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Quantile Intervals */}
      {prediction.quantiles && (
        <div className="bg-[#151A22] border border-[#232936] p-3 rounded-lg">
          <div className="text-[11px] font-mono font-semibold text-white mb-2 flex items-center justify-between">
            <span>Quantile Forecast Intervals</span>
            <span className="text-[9px] text-[#8B949E]">10th - 90th percentile</span>
          </div>
          <div className="grid grid-cols-5 gap-1 text-center font-mono text-[10px]">
            <div className="bg-[#0B0E14] p-1.5 rounded border border-[#232936]">
              <div className="text-[#8B949E] text-[9px]">p10</div>
              <div className="text-rose-400 font-bold">${prediction.quantiles.p10}</div>
            </div>
            <div className="bg-[#0B0E14] p-1.5 rounded border border-[#232936]">
              <div className="text-[#8B949E] text-[9px]">p25</div>
              <div className="text-rose-300">${prediction.quantiles.p25}</div>
            </div>
            <div className="bg-[#0B0E14] p-1.5 rounded border border-blue-500/30">
              <div className="text-blue-400 text-[9px]">p50</div>
              <div className="text-blue-300 font-bold">${prediction.quantiles.p50}</div>
            </div>
            <div className="bg-[#0B0E14] p-1.5 rounded border border-[#232936]">
              <div className="text-[#8B949E] text-[9px]">p75</div>
              <div className="text-emerald-300">${prediction.quantiles.p75}</div>
            </div>
            <div className="bg-[#0B0E14] p-1.5 rounded border border-[#232936]">
              <div className="text-[#8B949E] text-[9px]">p90</div>
              <div className="text-emerald-400 font-bold">${prediction.quantiles.p90}</div>
            </div>
          </div>
        </div>
      )}

      {/* SHAP Feature Importance */}
      {prediction.shap_values && Object.keys(prediction.shap_values).length > 0 && (
        <div className="bg-[#151A22] border border-[#232936] p-3 rounded-lg">
          <div className="text-[11px] font-mono font-semibold text-white mb-2 flex items-center justify-between">
            <span className="flex items-center space-x-1">
              <Layers className="h-3 w-3 text-indigo-400" />
              <span>SHAP Feature Attribution</span>
            </span>
            <span className="text-[9px] text-[#8B949E]">Importance %</span>
          </div>
          <div className="space-y-1.5">
            {Object.entries(prediction.shap_values).slice(0, 5).map(([feat, val]) => (
              <div key={feat} className="flex items-center space-x-2 text-xs font-mono">
                <span className="w-28 truncate text-[#8B949E] text-[10px]">{feat}</span>
                <div className="flex-1 bg-[#0B0E14] h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-indigo-500 h-full rounded-full transition-all"
                    style={{ width: `${Math.min(100, Math.max(5, val * 100))}%` }}
                  />
                </div>
                <span className="text-[10px] text-white w-10 text-right">{(val * 100).toFixed(1)}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Market Regime & Risk Profile */}
      <div className="bg-[#151A22] border border-[#232936] p-3 rounded-lg flex items-center justify-between text-xs font-mono">
        <div>
          <div className="text-[10px] text-[#8B949E] uppercase">Market Regime</div>
          <span className="font-bold text-blue-400">{prediction.market_regime || "SIDEWAYS"}</span>
        </div>
        <div>
          <div className="text-[10px] text-[#8B949E] uppercase">VaR (95%)</div>
          <span className="font-bold text-rose-400">{prediction.risk_metrics?.var_95_pct ?? 0}%</span>
        </div>
        <div>
          <div className="text-[10px] text-[#8B949E] uppercase">Exp Shortfall</div>
          <span className="font-bold text-amber-400">{prediction.risk_metrics?.expected_shortfall_95_pct ?? 0}%</span>
        </div>
      </div>

      {/* Dataset & Model Linkage */}
      {prediction.dataset_id && (
        <div className="flex items-center space-x-1.5 text-[10px] font-mono text-[#8B949E] bg-[#0B0E14] px-2.5 py-1.5 rounded border border-[#232936] truncate">
          <Folder className="h-3 w-3 text-blue-400 shrink-0" />
          <span className="truncate">Trained on: {prediction.dataset_id}</span>
        </div>
      )}

      {/* Mandatory Financial Disclaimer */}
      <div className="text-[9px] text-[#6E7681] border-t border-[#1E2430] pt-2">
        AI forecasts are probabilistic estimates based on real market data. They are not guaranteed and not financial advice.
      </div>
    </div>
  );
};
