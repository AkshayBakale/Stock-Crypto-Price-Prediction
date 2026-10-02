export interface TickerData {
  symbol: string;
  canonical_id: string;
  market: string;
  exchange: string;
  provider: string;
  price: number;
  change_24h_pct: number;
  high_24h: number;
  low_24h: number;
  volume_24h: number;
  timestamp: string;
  data_age_seconds: number;
  status: "LIVE" | "STALE" | "DISCONNECTED" | "UNAVAILABLE" | "NOT CONFIGURED";
  is_configured: boolean;
}

export interface CandleData {
  time: number;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PredictionData {
  symbol: string;
  canonical_id?: string;
  current_price: number;
  predicted_price?: number;
  expected_return_pct?: number;
  direction?: "UP" | "DOWN" | "SIDEWAYS";
  confidence?: number;
  calibrated_probability?: number;
  quantiles?: {
    p10?: number;
    p25?: number;
    p50?: number;
    p75?: number;
    p90?: number;
  };
  shap_values?: Record<string, number>;
  model_id?: string;
  model_type?: string;
  model_version?: string;
  dataset_id?: string;
  dataset_folder?: string;
  market_regime?: string;
  risk_metrics?: {
    var_95_pct?: number;
    var_99_pct?: number;
    expected_shortfall_95_pct?: number;
    annualized_volatility_pct?: number;
  };
  timestamp: string;
  status: "LIVE" | "MODEL NOT TRAINED" | "UNAVAILABLE" | "MODEL ERROR";
  message?: string;
}

export interface ModelMetadata {
  model_id: string;
  symbol: string;
  model_type: string;
  version: string;
  status: string;
  is_pytorch: boolean;
  hyperparameters: Record<string, any>;
  metrics: {
    mae?: number;
    rmse?: number;
    r2?: number;
    directional_accuracy_pct?: number;
    total_return_pct?: number;
    sharpe_ratio?: number;
    sortino_ratio?: number;
    max_drawdown_pct?: number;
    win_rate_pct?: number;
    profit_factor?: number;
    test_samples?: number;
  };
  dataset_id: string;
  dataset_folder_path: string;
  folder_path: string;
  created_at: string;
}

export interface DatasetInfo {
  dataset_id: string;
  symbol: string;
  timeframe: string;
  row_count: number;
  feature_count: number;
  feature_names: string[];
  target_column: string;
  date_range_start: string;
  date_range_end: string;
  folder_path: string;
  created_at: string;
}

export interface BacktestResult {
  symbol: string;
  timeframe: string;
  model_used: string;
  initial_capital: number;
  final_equity: number;
  total_return_pct: number;
  benchmark_return_pct: number;
  sharpe_ratio: number;
  sortino_ratio: number;
  max_drawdown_pct: number;
  win_rate_pct: number;
  profit_factor: number;
  total_trades: number;
  trades_log: Array<{
    trade_id: number;
    type: string;
    timestamp: string;
    price: number;
    qty: number;
    pnl: number;
    reason: string;
  }>;
  equity_curve: Array<{
    timestamp: string;
    equity: number;
    cash: number;
    position_value: number;
  }>;
  benchmark_curve: Array<{
    timestamp: string;
    benchmark_equity: number;
  }>;
}

export interface PaperPosition {
  symbol: string;
  quantity: number;
  avg_entry_price: number;
  current_price: number;
  position_value: number;
  unrealized_pnl: number;
  unrealized_pnl_pct: number;
}

export interface PaperPortfolio {
  mode: string;
  cash: number;
  total_equity: number;
  total_pnl: number;
  total_pnl_pct: number;
  positions: PaperPosition[];
  orders: Array<{
    order_id: string;
    symbol: string;
    side: string;
    quantity: number;
    price: number;
    fee: number;
    status: string;
    timestamp: string;
  }>;
}

// Information Retrieval (IR) Interfaces
export interface IRSearchResult {
  rank: number;
  doc_id: string;
  passage_id: number;
  score: number;
  method: string;
  text: string;
  matched_terms: string[];
  term_frequencies: Record<string, number>;
  passage_length: number;
  metadata: {
    title: string;
    symbol: string;
    category: string;
    source: string;
    timestamp: string;
    parent_text?: string;
  };
}

export interface IRSearchResponse {
  query: string;
  method: string;
  total_passages_indexed: number;
  total_corpus_tokens: number;
  results_count: number;
  results: IRSearchResult[];
}

export interface PageRankNode {
  entity: string;
  pagerank: number;
  influence_percentage: number;
  connections: Array<{
    target: string;
    weight: number;
  }>;
}

export interface PageRankResponse {
  damping_factor: number;
  nodes: PageRankNode[];
  edges: Array<{
    source: string;
    target: string;
    weight: number;
  }>;
}

export interface AssetRecommendation {
  symbol: string;
  name: string;
  asset_class: string;
  match_score?: number;
  similarity?: number;
  shared_traits?: string[];
  risk_level: string;
  volatility: number;
  momentum?: number;
  sharpe_ratio: number;
  rationale?: string;
  objective_score?: number;
  suggested_weight_pct?: number;
  allocation_rationale?: string;
  tags?: string[];
}

export interface RecommendationResponse {
  mode: "content_based" | "knowledge_based";
  target_symbol?: string;
  risk_tolerance?: string;
  strategy_objective?: string;
  max_volatility_cap?: number;
  recommendations: AssetRecommendation[];
}

export interface ExtractedData {
  tickers: string[];
  sentiment: "Bullish" | "Bearish" | "Neutral";
  sentiment_score: number;
  bullish_signals: number;
  bearish_signals: number;
  catalysts: string[];
  monetary_values: string[];
  percentages: string[];
  summary_tag: string;
}

export interface CrawledArticle {
  id: string;
  title: string;
  source: string;
  url: string;
  symbol: string;
  category: string;
  timestamp: string;
  text: string;
}

