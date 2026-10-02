import React, { useEffect, useRef } from "react";
import { 
  createChart, 
  IChartApi, 
  ISeriesApi, 
  CandlestickData, 
  Time,
  CandlestickSeries,
  HistogramSeries,
  LineSeries
} from "lightweight-charts";
import { CandleData, PredictionData } from "../types";

interface TradingChartProps {
  symbol: string;
  candles: CandleData[];
  prediction?: PredictionData | null;
  timeframe: string;
  onChangeTimeframe: (tf: string) => void;
  isLoading: boolean;
}

const TIMEFRAMES = ["1m", "5m", "15m", "1h", "1d"];

export const TradingChart: React.FC<TradingChartProps> = ({
  symbol,
  candles,
  prediction,
  timeframe,
  onChangeTimeframe,
  isLoading,
}) => {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candlestickSeriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);
  const volumeSeriesRef = useRef<ISeriesApi<"Histogram"> | null>(null);
  const lineSeriesRef = useRef<ISeriesApi<"Line"> | null>(null);

  useEffect(() => {
    if (!chartContainerRef.current) return;

    try {
      // Initialize Lightweight Chart
      const chart = createChart(chartContainerRef.current, {
        width: chartContainerRef.current.clientWidth || 800,
        height: 480,
        layout: {
          background: { color: "#0B0E14" },
          textColor: "#8B949E",
          fontSize: 11,
          fontFamily: "'JetBrains Mono', monospace",
        },
        grid: {
          vertLines: { color: "#161B22" },
          horzLines: { color: "#161B22" },
        },
        crosshair: {
          mode: 1,
          vertLine: { color: "#388BFD", width: 1, style: 3 },
          horzLine: { color: "#388BFD", width: 1, style: 3 },
        },
        rightPriceScale: {
          borderColor: "#232936",
          scaleMargins: { top: 0.1, bottom: 0.2 },
        },
        timeScale: {
          borderColor: "#232936",
          timeVisible: true,
          secondsVisible: false,
        },
      });

      const candlestickSeries = chart.addSeries(CandlestickSeries, {
        upColor: "#00E676",
        downColor: "#FF5252",
        borderVisible: false,
        wickUpColor: "#00E676",
        wickDownColor: "#FF5252",
      });

      const volumeSeries = chart.addSeries(HistogramSeries, {
        color: "#26a69a",
        priceFormat: { type: "volume" },
        priceScaleId: "",
      });
      volumeSeries.priceScale().applyOptions({
        scaleMargins: { top: 0.8, bottom: 0 },
      });

      const lineSeries = chart.addSeries(LineSeries, {
        color: "#2979FF",
        lineWidth: 2,
        title: "AI Forecast",
      });

      chartRef.current = chart;
      candlestickSeriesRef.current = candlestickSeries;
      volumeSeriesRef.current = volumeSeries;
      lineSeriesRef.current = lineSeries;

      const handleResize = () => {
        if (chartContainerRef.current && chartRef.current) {
          chartRef.current.applyOptions({ width: chartContainerRef.current.clientWidth });
        }
      };
      window.addEventListener("resize", handleResize);

      return () => {
        window.removeEventListener("resize", handleResize);
        chart.remove();
      };
    } catch (err) {
      console.error("Chart creation error:", err);
    }
  }, []);

  // Update Candle & Volume Data
  useEffect(() => {
    if (!candlestickSeriesRef.current || !volumeSeriesRef.current || !candles || candles.length === 0) return;

    try {
      // Sort strictly ascending and deduplicate timestamps
      const sorted = [...candles].sort((a, b) => a.time - b.time);
      const uniqueCandles: CandleData[] = [];
      const seenTimes = new Set<number>();
      for (const c of sorted) {
        if (!seenTimes.has(c.time) && c.time > 0 && !isNaN(c.close)) {
          seenTimes.add(c.time);
          uniqueCandles.push(c);
        }
      }

      if (uniqueCandles.length === 0) return;

      const formattedCandles: CandlestickData<Time>[] = uniqueCandles.map((c) => ({
        time: (c.time) as Time,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      }));

      const formattedVolume = uniqueCandles.map((c) => ({
        time: (c.time) as Time,
        value: c.volume || 0,
        color: c.close >= c.open ? "rgba(0, 230, 118, 0.25)" : "rgba(255, 82, 82, 0.25)",
      }));

      candlestickSeriesRef.current.setData(formattedCandles);
      volumeSeriesRef.current.setData(formattedVolume as any);

      // If prediction exists, add forecast line
      if (prediction && prediction.predicted_price && lineSeriesRef.current && uniqueCandles.length > 0) {
        const lastCandle = uniqueCandles[uniqueCandles.length - 1];
        const stepSeconds = timeframe === "1m" ? 60 : timeframe === "5m" ? 300 : timeframe === "15m" ? 900 : 3600;
        const nextTime = (lastCandle.time + stepSeconds) as Time;

        lineSeriesRef.current.setData([
          { time: lastCandle.time as Time, value: lastCandle.close },
          { time: nextTime, value: prediction.predicted_price },
        ]);
      }

      if (chartRef.current) {
        chartRef.current.timeScale().fitContent();
      }
    } catch (e) {
      console.warn("Error updating chart data:", e);
    }
  }, [candles, prediction, timeframe]);

  return (
    <div className="bg-[#0D1117] border border-[#232936] rounded-xl overflow-hidden shadow-lg flex flex-col">
      {/* Chart Toolbar */}
      <div className="px-4 py-2.5 bg-[#151A22] border-b border-[#232936] flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className="text-xs font-mono font-bold text-white tracking-wide">{symbol} / Real-Time OHLCV</span>
          <span className="text-[10px] px-1.5 py-0.5 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded font-mono">
            TradingView Lightweight Charts
          </span>
        </div>

        {/* Timeframe selector buttons */}
        <div className="flex items-center space-x-1 bg-[#0B0E14] p-0.5 rounded border border-[#232936]">
          {TIMEFRAMES.map((tf) => (
            <button
              key={tf}
              onClick={() => onChangeTimeframe(tf)}
              className={`px-2 py-0.5 text-xs font-mono rounded transition-colors ${
                timeframe === tf
                  ? "bg-blue-600 text-white font-bold"
                  : "text-[#8B949E] hover:text-white"
              }`}
            >
              {tf.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Main Chart Area */}
      <div className="relative w-full h-[480px]">
        {isLoading && (
          <div className="absolute inset-0 bg-[#0B0E14]/70 z-10 flex items-center justify-center backdrop-blur-[2px]">
            <div className="flex items-center space-x-2 text-xs font-mono text-blue-400">
              <span className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full" />
              <span>Streaming Historical Candles...</span>
            </div>
          </div>
        )}
        <div ref={chartContainerRef} className="w-full h-full min-h-[480px]" />
      </div>
    </div>
  );
};
