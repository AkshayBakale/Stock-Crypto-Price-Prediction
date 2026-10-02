import React, { useEffect, useState } from "react";
import { api } from "../services/api";
import { Server, CheckCircle2, XCircle, X, Activity, Cpu, Database, Wifi } from "lucide-react";

interface SystemHealthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SystemHealthModal: React.FC<SystemHealthModalProps> = ({ isOpen, onClose }) => {
  const [health, setHealth] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      setIsLoading(true);
      api
        .getSystemHealth()
        .then((data) => setHealth(data))
        .catch(console.error)
        .finally(() => setIsLoading(false));
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm font-mono">
      <div className="bg-[#0D1117] border border-[#232936] rounded-xl w-full max-w-lg p-5 shadow-2xl space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between pb-3 border-b border-[#232936]">
          <div className="flex items-center space-x-2">
            <Server className="h-5 w-5 text-blue-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              System Telemetry & Health Diagnostics
            </h3>
          </div>
          <button onClick={onClose} className="text-[#8B949E] hover:text-white transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Content */}
        {isLoading || !health ? (
          <div className="py-12 text-center text-xs text-blue-400">
            <span className="animate-spin inline-block h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full mr-2" />
            Pinging backend telemetry...
          </div>
        ) : (
          <div className="space-y-3 text-xs">
            <div className="p-3 bg-emerald-950/40 border border-emerald-500/30 rounded-lg flex items-center justify-between">
              <span className="text-emerald-300 font-bold flex items-center space-x-2">
                <CheckCircle2 className="h-4 w-4" />
                <span>PLATFORM STATUS: {health.status}</span>
              </span>
              <span className="text-[#8B949E] text-[11px]">Uptime: {health.uptime_seconds}s</span>
            </div>

            <div className="grid grid-cols-2 gap-2.5">
              {/* API */}
              <div className="bg-[#151A22] p-3 rounded-lg border border-[#232936]">
                <div className="flex items-center space-x-1.5 text-[#8B949E] mb-1">
                  <Activity className="h-3.5 w-3.5 text-blue-400" />
                  <span>FastAPI Service</span>
                </div>
                <div className="text-white font-bold">{health.components?.api?.status} (v{health.components?.api?.version})</div>
              </div>

              {/* Database */}
              <div className="bg-[#151A22] p-3 rounded-lg border border-[#232936]">
                <div className="flex items-center space-x-1.5 text-[#8B949E] mb-1">
                  <Database className="h-3.5 w-3.5 text-emerald-400" />
                  <span>Database Engine</span>
                </div>
                <div className="text-white font-bold">{health.components?.database?.status}</div>
              </div>

              {/* Crypto Provider */}
              <div className="bg-[#151A22] p-3 rounded-lg border border-[#232936]">
                <div className="flex items-center space-x-1.5 text-[#8B949E] mb-1">
                  <Wifi className="h-3.5 w-3.5 text-amber-400" />
                  <span>Binance WebSocket</span>
                </div>
                <div className="text-white font-bold">
                  {health.components?.market_data?.crypto_provider?.status} ({health.components?.market_data?.crypto_provider?.latency_ms}ms)
                </div>
              </div>

              {/* ML Engine */}
              <div className="bg-[#151A22] p-3 rounded-lg border border-[#232936]">
                <div className="flex items-center space-x-1.5 text-[#8B949E] mb-1">
                  <Cpu className="h-3.5 w-3.5 text-indigo-400" />
                  <span>PyTorch / ML Engine</span>
                </div>
                <div className="text-white font-bold">
                  {health.components?.ml_engine?.registered_models_count} Models | {health.components?.ml_engine?.saved_datasets_count} Datasets
                </div>
              </div>
            </div>

            <div className="p-3 bg-[#151A22] rounded-lg border border-[#232936] text-[11px] text-[#8B949E] space-y-1">
              <div>• US Equities Provider: {health.components?.market_data?.us_equities_provider?.status}</div>
              <div>• Indian Equities Provider: {health.components?.market_data?.indian_equities_provider?.status}</div>
              <div>• Cache / Realtime Bus: {health.components?.cache?.status}</div>
            </div>
          </div>
        )}

        <div className="pt-2 text-right">
          <button
            onClick={onClose}
            className="px-4 py-1.5 bg-[#151A22] hover:bg-[#1E2430] border border-[#232936] rounded text-xs text-white"
          >
            Close Diagnostics
          </button>
        </div>
      </div>
    </div>
  );
};
