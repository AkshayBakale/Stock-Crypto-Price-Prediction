import React, { useState, useEffect } from "react";
import { DatasetInfo } from "../types";
import { api } from "../services/api";
import { Database, Folder, FileText, CheckCircle2, RefreshCw, Layers } from "lucide-react";

export const DatasetsViewer: React.FC = () => {
  const [datasets, setDatasets] = useState<DatasetInfo[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState<DatasetInfo | null>(null);

  const loadDatasets = async () => {
    setIsLoading(true);
    try {
      const data = await api.getDatasets();
      setDatasets(data);
      if (data.length > 0 && !selectedDataset) {
        setSelectedDataset(data[0]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  return (
    <div className="space-y-6 font-mono">
      {/* Header Banner */}
      <div className="bg-[#0D1117] border border-[#232936] rounded-xl p-5 shadow-lg flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-blue-600/10 border border-blue-500/20 rounded-lg text-blue-400">
            <Database className="h-6 w-6" />
          </div>
          <div>
            <h2 className="text-base font-bold text-white uppercase tracking-wider">
              Training Dataset Records (Isolated Storage)
            </h2>
            <p className="text-xs text-[#8B949E]">
              Every dataset on which models are trained is strictly saved in its own isolated directory under <code className="text-blue-300">ml/datasets/records/</code>
            </p>
          </div>
        </div>

        <button
          onClick={loadDatasets}
          className="px-3 py-1.5 bg-[#151A22] hover:bg-[#1E2430] border border-[#232936] text-xs text-white rounded-lg flex items-center space-x-2 transition-colors"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${isLoading ? "animate-spin" : ""}`} />
          <span>Refresh Folders</span>
        </button>
      </div>

      {/* Datasets Table & Detail View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Dataset Folders List */}
        <div className="lg:col-span-2 bg-[#0D1117] border border-[#232936] rounded-xl p-5 shadow-lg">
          <h3 className="text-xs font-bold text-[#8B949E] uppercase mb-4 tracking-wider">
            SAVED DATASET FOLDERS ({datasets.length})
          </h3>

          {datasets.length === 0 ? (
            <div className="py-12 text-center text-xs text-[#8B949E]">
              No datasets generated yet. Training a model will automatically construct and persist its training dataset folder.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-[#151A22] text-[#8B949E] border-b border-[#232936]">
                  <tr>
                    <th className="py-2.5 px-3">Dataset ID</th>
                    <th className="py-2.5 px-3">Symbol</th>
                    <th className="py-2.5 px-3">Timeframe</th>
                    <th className="py-2.5 px-3">Rows</th>
                    <th className="py-2.5 px-3">Features</th>
                    <th className="py-2.5 px-3">Folder Path</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#232936]/60">
                  {datasets.map((d) => {
                    const isSelected = selectedDataset?.dataset_id === d.dataset_id;
                    return (
                      <tr
                        key={d.dataset_id}
                        onClick={() => setSelectedDataset(d)}
                        className={`cursor-pointer transition-colors ${
                          isSelected ? "bg-blue-600/15" : "hover:bg-[#151A22]/50"
                        }`}
                      >
                        <td className="py-3 px-3 font-bold text-white flex items-center space-x-2">
                          <Folder className="h-4 w-4 text-amber-400 shrink-0" />
                          <span className="truncate max-w-[160px]">{d.dataset_id}</span>
                        </td>
                        <td className="py-3 px-3 font-semibold text-blue-400">{d.symbol}</td>
                        <td className="py-3 px-3 text-[#8B949E]">{d.timeframe}</td>
                        <td className="py-3 px-3 text-white">{d.row_count}</td>
                        <td className="py-3 px-3 text-emerald-400">{d.feature_count} cols</td>
                        <td className="py-3 px-3 text-[10px] text-[#8B949E] truncate max-w-[150px]">
                          {d.folder_path}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Selected Dataset Detail Inspector */}
        <div className="bg-[#0D1117] border border-[#232936] rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center space-x-2 pb-4 border-b border-[#232936] mb-4">
              <FileText className="h-5 w-5 text-blue-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">Dataset Manifest</h3>
            </div>

            {selectedDataset ? (
              <div className="space-y-4 text-xs">
                <div>
                  <span className="text-[#8B949E] text-[10px] uppercase">Folder Directory</span>
                  <div className="p-2 bg-[#151A22] rounded border border-[#232936] text-[11px] text-emerald-300 break-all mt-1">
                    {selectedDataset.folder_path}
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-[#151A22] p-2.5 rounded border border-[#232936]">
                    <div className="text-[10px] text-[#8B949E]">Historical Start</div>
                    <div className="text-white text-[11px] truncate mt-0.5">{selectedDataset.date_range_start || "---"}</div>
                  </div>
                  <div className="bg-[#151A22] p-2.5 rounded border border-[#232936]">
                    <div className="text-[10px] text-[#8B949E]">Historical End</div>
                    <div className="text-white text-[11px] truncate mt-0.5">{selectedDataset.date_range_end || "---"}</div>
                  </div>
                </div>

                <div>
                  <span className="text-[#8B949E] text-[10px] uppercase">Contained Files</span>
                  <div className="mt-1 space-y-1 text-[11px] text-[#8B949E]">
                    <div className="flex items-center space-x-1 text-white">
                      <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                      <span>dataset.parquet (High-performance columnar matrix)</span>
                    </div>
                    <div className="flex items-center space-x-1 text-white">
                      <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                      <span>dataset.csv (Standard CSV dataset)</span>
                    </div>
                    <div className="flex items-center space-x-1 text-white">
                      <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                      <span>metadata.json (Walk-forward indices & split info)</span>
                    </div>
                    <div className="flex items-center space-x-1 text-white">
                      <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                      <span>features.json (Engineered technical feature list)</span>
                    </div>
                  </div>
                </div>

                <div>
                  <span className="text-[#8B949E] text-[10px] uppercase mb-1 block">
                    Engineered Features ({selectedDataset.feature_count})
                  </span>
                  <div className="flex flex-wrap gap-1 max-h-36 overflow-y-auto p-1 bg-[#151A22] rounded border border-[#232936]">
                    {selectedDataset.feature_names?.map((f) => (
                      <span key={f} className="px-1.5 py-0.5 bg-[#0B0E14] text-[10px] text-blue-300 rounded border border-[#232936]">
                        {f}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="py-12 text-center text-xs text-[#8B949E]">
                Select a dataset folder to inspect its schema and metadata.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
