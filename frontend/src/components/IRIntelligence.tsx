import React, { useState, useEffect } from "react";
import {
  Search,
  Globe,
  Sliders,
  Sparkles,
  Share2,
  FileText,
  TrendingUp,
  TrendingDown,
  CheckCircle2,
  Layers,
  Activity,
  ArrowRight,
  RefreshCw,
  Cpu
} from "lucide-react";
import { api } from "../services/api";
import {
  IRSearchResult,
  PageRankNode,
  AssetRecommendation,
  ExtractedData,
  CrawledArticle
} from "../types";

interface IRIntelligenceProps {
  activeSymbol: string;
  onSelectSymbol: (symbol: string) => void;
}

export const IRIntelligence: React.FC<IRIntelligenceProps> = ({ activeSymbol, onSelectSymbol }) => {
  const [activeSubTab, setActiveSubTab] = useState<"search" | "crawler_pagerank" | "recommender">("search");

  // --- Sub-Tab 1: Language Model Search State ---
  const [searchQuery, setSearchQuery] = useState("Bitcoin ETF inflows liquidity");
  const [rankingMethod, setRankingMethod] = useState<"dirichlet" | "jelinek_mercer" | "dfr">("dirichlet");
  const [dirichletMu, setDirichletMu] = useState(1000);
  const [jmLambda, setJmLambda] = useState(0.4);
  const [searchResults, setSearchResults] = useState<IRSearchResult[]>([]);
  const [searchMeta, setSearchMeta] = useState<{ totalPassages: number; totalTokens: number } | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  // --- Sub-Tab 2: Web Crawler & PageRank State ---
  const [articles, setArticles] = useState<CrawledArticle[]>([]);
  const [pageRankNodes, setPageRankNodes] = useState<PageRankNode[]>([]);
  const [crawlUrl, setCrawlUrl] = useState("https://finance.yahoo.com/news/bitcoin-crypto-update");
  const [crawlSource, setCrawlSource] = useState("Yahoo Finance");
  const [isCrawling, setIsCrawling] = useState(false);
  const [crawlMsg, setCrawlMsg] = useState<string | null>(null);

  // --- Sub-Tab 3: Recommender & Extraction State ---
  const [recMode, setRecMode] = useState<"content" | "knowledge">("content");
  const [recSymbol, setRecSymbol] = useState(activeSymbol || "BTCUSDT");
  const [riskTolerance, setRiskTolerance] = useState<"Conservative" | "Moderate" | "Aggressive">("Moderate");
  const [maxVolatility, setMaxVolatility] = useState(0.60);
  const [strategyObjective, setStrategyObjective] = useState("Growth");
  const [recommendations, setRecommendations] = useState<AssetRecommendation[]>([]);
  const [isRecLoading, setIsRecLoading] = useState(false);

  // Extraction tool state
  const [extractInput, setExtractInput] = useState(
    "BlackRock spot Bitcoin ETF registered over $850 million in daily inflows, pushing BTC above $68,000 resistance. Federal Reserve interest rate cut optimism is providing tailwinds."
  );
  const [extractedResult, setExtractedResult] = useState<ExtractedData | null>(null);
  const [isExtracting, setIsExtracting] = useState(false);

  // 1. Initial Data Fetching
  useEffect(() => {
    executeSearch();
    fetchCrawlerAndPageRank();
  }, []);

  useEffect(() => {
    executeRecommendation();
  }, [recMode, recSymbol, riskTolerance, maxVolatility, strategyObjective]);

  // Handler: LM Search
  const executeSearch = async (overrideQuery?: string) => {
    const q = overrideQuery !== undefined ? overrideQuery : searchQuery;
    if (!q.trim()) return;
    setIsSearching(true);
    try {
      const data = await api.searchIRPassages(
        q,
        rankingMethod,
        8,
        rankingMethod === "dirichlet" ? dirichletMu : undefined,
        rankingMethod === "jelinek_mercer" ? jmLambda : undefined
      );
      setSearchResults(data.results || []);
      setSearchMeta({
        totalPassages: data.total_passages_indexed || 0,
        totalTokens: data.total_corpus_tokens || 0
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsSearching(false);
    }
  };

  // Handler: Crawler & PageRank Fetch
  const fetchCrawlerAndPageRank = async () => {
    try {
      const [artRes, prRes] = await Promise.all([
        api.getCrawledArticles(),
        api.getPageRankGraph()
      ]);
      setArticles(artRes.articles || []);
      setPageRankNodes(prRes.nodes || []);
    } catch (e) {
      console.error(e);
    }
  };

  // Handler: Trigger Live Crawl
  const handleCrawlSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!crawlUrl) return;
    setIsCrawling(true);
    setCrawlMsg(null);
    try {
      const res = await api.crawlWebpage(crawlUrl, crawlSource);
      setCrawlMsg(`Crawled & Indexed: "${res.article?.title}"`);
      await fetchCrawlerAndPageRank();
      // Re-trigger search to reflect updated corpus
      executeSearch();
    } catch (err: any) {
      setCrawlMsg(`Crawl failed: ${err.message || "Network Error"}`);
    } finally {
      setIsCrawling(false);
    }
  };

  // Handler: Recommender
  const executeRecommendation = async () => {
    setIsRecLoading(true);
    try {
      const res = await api.getRecommendations({
        mode: recMode,
        symbol: recSymbol,
        risk_tolerance: riskTolerance,
        max_volatility: maxVolatility,
        strategy_objective: strategyObjective
      });
      setRecommendations(res.recommendations || []);
    } catch (e) {
      console.error(e);
    } finally {
      setIsRecLoading(false);
    }
  };

  // Handler: Information Extraction
  const handleExtract = async () => {
    if (!extractInput.trim()) return;
    setIsExtracting(true);
    try {
      const res = await api.extractFinancialInfo(extractInput);
      setExtractedResult(res.data);
    } catch (e) {
      console.error(e);
    } finally {
      setIsExtracting(false);
    }
  };

  return (
    <div className="space-y-6 font-mono pb-12">
      {/* Sub-Navigation Bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-[#232936] pb-4">
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setActiveSubTab("search")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeSubTab === "search"
                ? "bg-blue-600/20 text-blue-400 border border-blue-500/40 shadow-sm"
                : "text-[#8B949E] hover:text-white hover:bg-[#151A22]"
            }`}
          >
            <Search className="w-3.5 h-3.5" />
            <span>Unit IV: LM Passage Search</span>
          </button>

          <button
            onClick={() => setActiveSubTab("crawler_pagerank")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeSubTab === "crawler_pagerank"
                ? "bg-purple-600/20 text-purple-400 border border-purple-500/40 shadow-sm"
                : "text-[#8B949E] hover:text-white hover:bg-[#151A22]"
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            <span>Unit V: Crawler & PageRank</span>
          </button>

          <button
            onClick={() => setActiveSubTab("recommender")}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${
              activeSubTab === "recommender"
                ? "bg-emerald-600/20 text-emerald-400 border border-emerald-500/40 shadow-sm"
                : "text-[#8B949E] hover:text-white hover:bg-[#151A22]"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Unit VI: Recommender & Extraction</span>
          </button>
        </div>

        <div className="flex items-center space-x-3 text-[11px] text-[#8B949E] bg-[#0D1117] px-3 py-1.5 rounded-lg border border-[#232936]">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Corpus: <strong className="text-white">{searchMeta?.totalPassages || 6} Passages</strong>
          </span>
          <span>•</span>
          <span>Tokens: <strong className="text-white">{searchMeta?.totalTokens || 340}</strong></span>
        </div>
      </div>

      {/* ========================================================================= */}
      {/* SUB-TAB 1: LANGUAGE MODEL SEARCH & PASSAGE RETRIEVAL (UNIT IV)           */}
      {/* ========================================================================= */}
      {activeSubTab === "search" && (
        <div className="space-y-6">
          {/* Query Bar & Model Controls Card */}
          <div className="bg-[#0D1117] border border-[#232936] p-5 rounded-xl space-y-4 shadow-xl">
            <div className="flex flex-col md:flex-row gap-3">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3 top-3 text-[#8B949E]" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === "Enter" && executeSearch()}
                  placeholder="Enter financial search query (e.g., 'Bitcoin ETF inflows', 'Fed interest rates', 'NVIDIA AI architecture')..."
                  className="w-full bg-[#151A22] border border-[#232936] text-white pl-9 pr-4 py-2.5 rounded-lg text-xs focus:outline-none focus:border-blue-500"
                />
              </div>

              <button
                onClick={() => executeSearch()}
                disabled={isSearching}
                className="px-6 py-2.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold transition flex items-center justify-center space-x-2 shadow-lg shadow-blue-900/30"
              >
                {isSearching ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />}
                <span>Retrieve Passages</span>
              </button>
            </div>

            {/* Quick Presets */}
            <div className="flex flex-wrap items-center gap-2 text-[10px] text-[#8B949E]">
              <span className="font-semibold text-slate-400">Quick Queries:</span>
              {[
                "Bitcoin spot ETF institutional inflows",
                "Federal Reserve rate cut inflation",
                "Ethereum Layer 2 Dencun blobs",
                "NVIDIA Blackwell GPUs large language models",
                "Solana decentralized exchange DEX volume"
              ].map((preset) => (
                <button
                  key={preset}
                  onClick={() => {
                    setSearchQuery(preset);
                    executeSearch(preset);
                  }}
                  className="px-2.5 py-1 bg-[#151A22] hover:bg-[#1E2633] text-blue-300 rounded border border-[#232936] transition"
                >
                  {preset}
                </button>
              ))}
            </div>

            {/* Algorithm & Smoothing Configuration Bar */}
            <div className="pt-3 border-t border-[#232936] grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
              <div>
                <label className="text-[10px] text-[#8B949E] uppercase block mb-1.5 font-bold">
                  Language Model Ranking Function
                </label>
                <div className="grid grid-cols-3 gap-1 bg-[#151A22] p-1 rounded-lg border border-[#232936]">
                  {(["dirichlet", "jelinek_mercer", "dfr"] as const).map((m) => (
                    <button
                      key={m}
                      onClick={() => setRankingMethod(m)}
                      className={`py-1 text-[10px] font-bold rounded transition ${
                        rankingMethod === m
                          ? "bg-blue-600 text-white shadow"
                          : "text-[#8B949E] hover:text-white"
                      }`}
                    >
                      {m === "dirichlet" ? "Dirichlet" : m === "jelinek_mercer" ? "Jelinek-M" : "DFR (InL2)"}
                    </button>
                  ))}
                </div>
              </div>

              {rankingMethod === "dirichlet" && (
                <div>
                  <div className="flex justify-between text-[10px] text-[#8B949E] uppercase mb-1.5 font-bold">
                    <span>Dirichlet Prior (μ)</span>
                    <span className="text-blue-400 font-mono">{dirichletMu}</span>
                  </div>
                  <input
                    type="range"
                    min="100"
                    max="3000"
                    step="100"
                    value={dirichletMu}
                    onChange={(e) => setDirichletMu(Number(e.target.value))}
                    className="w-full h-1.5 bg-[#232936] rounded-lg appearance-none cursor-pointer accent-blue-500"
                  />
                  <span className="text-[9px] text-[#8B949E]">Controls pseudocount weight of collection LM</span>
                </div>
              )}

              {rankingMethod === "jelinek_mercer" && (
                <div>
                  <div className="flex justify-between text-[10px] text-[#8B949E] uppercase mb-1.5 font-bold">
                    <span>JM Interpolation (λ)</span>
                    <span className="text-purple-400 font-mono">{jmLambda.toFixed(2)}</span>
                  </div>
                  <input
                    type="range"
                    min="0.05"
                    max="0.95"
                    step="0.05"
                    value={jmLambda}
                    onChange={(e) => setJmLambda(Number(e.target.value))}
                    className="w-full h-1.5 bg-[#232936] rounded-lg appearance-none cursor-pointer accent-purple-500"
                  />
                  <span className="text-[9px] text-[#8B949E]">Linear mix: (1-λ)*Doc_MLE + λ*Collection_LM</span>
                </div>
              )}

              {rankingMethod === "dfr" && (
                <div className="flex flex-col justify-center">
                  <span className="text-[10px] text-emerald-400 font-bold uppercase mb-1">Divergence From Randomness</span>
                  <span className="text-[10px] text-[#8B949E]">
                    InL2 model: Inverse document frequency with Laplace succession normalization.
                  </span>
                </div>
              )}

              <div className="flex items-center justify-end">
                <div className="text-right text-[10px] text-[#8B949E]">
                  Formula: <span className="text-amber-400 font-mono">
                    {rankingMethod === "dirichlet"
                      ? "P(w|D) = (c(w,D) + μ P(w|C)) / (|D| + μ)"
                      : rankingMethod === "jelinek_mercer"
                      ? "P(w|D) = (1-λ)(c(w,D)/|D|) + λ P(w|C)"
                      : "DFR = Inf1 * (tfn/(tfn+1)) * log2(1+tfn)"}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Search Results List */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-xs text-[#8B949E] px-1">
              <span>Top Ranked Passages ({searchResults.length} matches)</span>
              <span>Scoring: <strong className="text-white uppercase">{rankingMethod}</strong></span>
            </div>

            {searchResults.length === 0 ? (
              <div className="bg-[#0D1117] border border-[#232936] p-8 rounded-xl text-center text-xs text-[#8B949E]">
                No matching passages found. Try a broader search term or different smoothing parameters.
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-3">
                {searchResults.map((res) => (
                  <div
                    key={`${res.doc_id}_${res.passage_id}`}
                    className="bg-[#0D1117] border border-[#232936] hover:border-blue-500/40 p-4 rounded-xl transition space-y-2.5 shadow-md"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-0.5 bg-blue-600/20 text-blue-400 border border-blue-500/30 text-[10px] font-bold rounded">
                          RANK #{res.rank}
                        </span>
                        <span className="text-xs font-bold text-white">{res.metadata.title}</span>
                        {res.metadata.symbol && (
                          <button
                            onClick={() => onSelectSymbol(res.metadata.symbol)}
                            className="px-1.5 py-0.5 bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 text-[10px] rounded border border-amber-500/30 transition"
                          >
                            {res.metadata.symbol}
                          </button>
                        )}
                      </div>

                      <div className="flex items-center space-x-3 text-[11px]">
                        <span className="text-[#8B949E]">Score:</span>
                        <span className="font-mono text-emerald-400 font-bold bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
                          {res.score}
                        </span>
                        <span className="text-[10px] text-[#8B949E] bg-[#151A22] px-2 py-0.5 rounded border border-[#232936]">
                          {res.metadata.source}
                        </span>
                      </div>
                    </div>

                    {/* Passage Snippet with Highlighted Terms */}
                    <p className="text-xs text-[#C9D1D9] leading-relaxed bg-[#151A22] p-3 rounded-lg border border-[#232936]/60">
                      {res.text}
                    </p>

                    {/* Query Terms Matched */}
                    <div className="flex flex-wrap items-center gap-2 text-[10px] text-[#8B949E]">
                      <span>Matched Terms:</span>
                      {res.matched_terms.map((term) => (
                        <span
                          key={term}
                          className="px-2 py-0.5 bg-blue-500/10 text-blue-300 rounded border border-blue-500/20"
                        >
                          {term} ({res.term_frequencies[term]}x)
                        </span>
                      ))}
                      <span className="ml-auto text-[10px] text-[#8B949E]">
                        Passage Len: {res.passage_length} words
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 2: WEB CRAWLER & PAGERANK (UNIT V)                               */}
      {/* ========================================================================= */}
      {activeSubTab === "crawler_pagerank" && (
        <div className="space-y-6">
          {/* Top Row: PageRank Authority Leaderboard & Graph */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 bg-[#0D1117] border border-[#232936] p-5 rounded-xl space-y-4 shadow-xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Share2 className="w-4 h-4 text-purple-400" />
                  <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                    PageRank Market Centrality & Influence
                  </h3>
                </div>
                <span className="text-[10px] text-[#8B949E] bg-[#151A22] px-2 py-1 rounded border border-[#232936]">
                  Damping Factor: 0.85
                </span>
              </div>

              <p className="text-[11px] text-[#8B949E]">
                Computes authority scores across crypto assets, equities, and macroeconomic catalysts based on directed co-mention citation graphs.
              </p>

              <div className="space-y-2">
                {pageRankNodes.map((node, idx) => (
                  <div
                    key={node.entity}
                    className="bg-[#151A22] border border-[#232936] p-3 rounded-lg flex items-center justify-between gap-4"
                  >
                    <div className="flex items-center space-x-3">
                      <span className="w-5 text-center text-xs font-bold text-[#8B949E]">#{idx + 1}</span>
                      <button
                        onClick={() => onSelectSymbol(node.entity)}
                        className="text-xs font-bold text-blue-400 hover:underline"
                      >
                        {node.entity}
                      </button>
                    </div>

                    <div className="flex-1 max-w-xs mx-4 hidden md:block">
                      <div className="h-1.5 w-full bg-[#232936] rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-500 to-blue-500 rounded-full"
                          style={{ width: `${Math.min(100, node.influence_percentage * 3.5)}%` }}
                        ></div>
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="text-xs font-mono font-bold text-purple-300">
                        {node.influence_percentage}%
                      </span>
                      <span className="text-[10px] text-[#8B949E] block">
                        PR: {node.pagerank.toFixed(4)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Live Crawler Form */}
            <div className="bg-[#0D1117] border border-[#232936] p-5 rounded-xl space-y-4 shadow-xl flex flex-col">
              <div className="flex items-center space-x-2">
                <Globe className="w-4 h-4 text-blue-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  Live Web Crawler (BeautifulSoup)
                </h3>
              </div>

              <p className="text-[11px] text-[#8B949E]">
                Asynchronously crawl financial URLs or SEC/Crypto headlines to ingest and update the Language Model index.
              </p>

              <form onSubmit={handleCrawlSubmit} className="space-y-3 flex-1 flex flex-col justify-between">
                <div className="space-y-3">
                  <div>
                    <label className="text-[10px] text-[#8B949E] uppercase block mb-1">Target URL</label>
                    <input
                      type="url"
                      value={crawlUrl}
                      onChange={(e) => setCrawlUrl(e.target.value)}
                      placeholder="https://..."
                      className="w-full bg-[#151A22] border border-[#232936] text-white px-3 py-2 rounded text-xs focus:outline-none focus:border-blue-500"
                    />
                  </div>

                  <div>
                    <label className="text-[10px] text-[#8B949E] uppercase block mb-1">Source Name</label>
                    <input
                      type="text"
                      value={crawlSource}
                      onChange={(e) => setCrawlSource(e.target.value)}
                      placeholder="Reuters / CoinDesk"
                      className="w-full bg-[#151A22] border border-[#232936] text-white px-3 py-2 rounded text-xs focus:outline-none focus:border-blue-500"
                    />
                  </div>

                  {crawlMsg && (
                    <div className="p-2.5 bg-[#151A22] border border-blue-500/30 rounded text-[10px] text-blue-300">
                      {crawlMsg}
                    </div>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={isCrawling}
                  className="w-full py-2.5 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold transition flex items-center justify-center space-x-2 mt-4"
                >
                  {isCrawling ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Globe className="w-3.5 h-3.5" />}
                  <span>Crawl & Ingest Webpage</span>
                </button>
              </form>
            </div>
          </div>

          {/* Crawled Corpus Stream */}
          <div className="bg-[#0D1117] border border-[#232936] p-5 rounded-xl space-y-4 shadow-xl">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                Indexed Articles Corpus ({articles.length} Documents)
              </h3>
              <button
                onClick={fetchCrawlerAndPageRank}
                className="text-xs text-[#8B949E] hover:text-white flex items-center space-x-1"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Refresh Feed</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {articles.map((art) => (
                <div
                  key={art.id}
                  className="bg-[#151A22] border border-[#232936] p-4 rounded-lg space-y-2 flex flex-col justify-between"
                >
                  <div>
                    <div className="flex items-center justify-between text-[10px] text-[#8B949E] mb-1">
                      <span className="px-1.5 py-0.5 bg-blue-500/10 text-blue-400 rounded">
                        {art.category}
                      </span>
                      <span>{art.source}</span>
                    </div>
                    <h4 className="text-xs font-bold text-white line-clamp-2">{art.title}</h4>
                    <p className="text-[11px] text-[#8B949E] mt-2 line-clamp-3 leading-relaxed">
                      {art.text}
                    </p>
                  </div>

                  <div className="pt-2 border-t border-[#232936] flex items-center justify-between text-[10px]">
                    <span className="text-amber-400 font-bold">{art.symbol}</span>
                    <span className="text-[#8B949E]">
                      {new Date(art.timestamp).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* ========================================================================= */}
      {/* SUB-TAB 3: RECOMMENDER SYSTEM & INFORMATION EXTRACTION (UNIT VI)         */}
      {/* ========================================================================= */}
      {activeSubTab === "recommender" && (
        <div className="space-y-6">
          {/* Top Section: Recommender Controls */}
          <div className="bg-[#0D1117] border border-[#232936] p-5 rounded-xl space-y-4 shadow-xl">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-emerald-400" />
                <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                  Asset & Strategy Recommender Engine
                </h3>
              </div>

              {/* Toggle Mode */}
              <div className="grid grid-cols-2 gap-1 bg-[#151A22] p-1 rounded-lg border border-[#232936]">
                <button
                  onClick={() => setRecMode("content")}
                  className={`px-3 py-1 text-xs font-bold rounded transition ${
                    recMode === "content" ? "bg-emerald-600 text-white shadow" : "text-[#8B949E] hover:text-white"
                  }`}
                >
                  Content-Based
                </button>
                <button
                  onClick={() => setRecMode("knowledge")}
                  className={`px-3 py-1 text-xs font-bold rounded transition ${
                    recMode === "knowledge" ? "bg-emerald-600 text-white shadow" : "text-[#8B949E] hover:text-white"
                  }`}
                >
                  Knowledge-Based
                </button>
              </div>
            </div>

            {/* Parameter Controls */}
            {recMode === "content" ? (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 text-xs">
                <div>
                  <label className="text-[10px] text-[#8B949E] uppercase block mb-1">Anchor Asset</label>
                  <select
                    value={recSymbol}
                    onChange={(e) => setRecSymbol(e.target.value)}
                    className="w-full bg-[#151A22] border border-[#232936] text-white px-3 py-2 rounded text-xs focus:outline-none"
                  >
                    <option value="BTCUSDT">BTCUSDT (Bitcoin)</option>
                    <option value="ETHUSDT">ETHUSDT (Ethereum)</option>
                    <option value="SOLUSDT">SOLUSDT (Solana)</option>
                    <option value="NVDA">NVDA (NVIDIA)</option>
                    <option value="SPY">SPY (S&P 500 ETF)</option>
                    <option value="TCS.NS">TCS.NS (Tata Consultancy)</option>
                  </select>
                </div>
                <div className="md:col-span-2 flex items-center text-xs text-[#8B949E]">
                  Computes high-dimensional feature cosine similarity over volatility, momentum, liquidity, and Sharpe ratio vectors.
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2 text-xs">
                <div>
                  <label className="text-[10px] text-[#8B949E] uppercase block mb-1">Risk Profile</label>
                  <select
                    value={riskTolerance}
                    onChange={(e) => setRiskTolerance(e.target.value as any)}
                    className="w-full bg-[#151A22] border border-[#232936] text-white px-3 py-2 rounded text-xs focus:outline-none"
                  >
                    <option value="Conservative">Conservative (Low Volatility)</option>
                    <option value="Moderate">Moderate (Balanced)</option>
                    <option value="Aggressive">Aggressive (High Alpha)</option>
                  </select>
                </div>

                <div>
                  <label className="text-[10px] text-[#8B949E] uppercase block mb-1">Investment Objective</label>
                  <select
                    value={strategyObjective}
                    onChange={(e) => setStrategyObjective(e.target.value)}
                    className="w-full bg-[#151A22] border border-[#232936] text-white px-3 py-2 rounded text-xs focus:outline-none"
                  >
                    <option value="Growth">Growth (Maximize Sharpe)</option>
                    <option value="Preservation">Preservation (Minimize Drawdown)</option>
                    <option value="Momentum">Momentum (Trend Following)</option>
                    <option value="Hedge">Hedge (Macro Safe Haven)</option>
                  </select>
                </div>

                <div>
                  <div className="flex justify-between text-[10px] text-[#8B949E] uppercase mb-1">
                    <span>Max Volatility Cap</span>
                    <span className="text-emerald-400 font-mono">{(maxVolatility * 100).toFixed(0)}%</span>
                  </div>
                  <input
                    type="range"
                    min="0.10"
                    max="1.0"
                    step="0.05"
                    value={maxVolatility}
                    onChange={(e) => setMaxVolatility(Number(e.target.value))}
                    className="w-full h-1.5 bg-[#232936] rounded-lg appearance-none cursor-pointer accent-emerald-500"
                  />
                </div>
              </div>
            )}
          </div>

          {/* Recommendations Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {recommendations.map((rec) => (
              <div
                key={rec.symbol}
                className="bg-[#0D1117] border border-[#232936] hover:border-emerald-500/40 p-4 rounded-xl space-y-3 transition shadow-lg flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-bold text-white">{rec.symbol}</span>
                    <span className="px-2 py-0.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[10px] font-bold rounded">
                      {rec.match_score !== undefined ? `${rec.match_score}% MATCH` : `${rec.suggested_weight_pct}% WEIGHT`}
                    </span>
                  </div>
                  <span className="text-[10px] text-[#8B949E] block">{rec.name}</span>

                  <div className="grid grid-cols-2 gap-2 my-3 text-[10px]">
                    <div className="bg-[#151A22] p-2 rounded border border-[#232936]">
                      <span className="text-[#8B949E] block">Sharpe Ratio</span>
                      <span className="font-mono text-emerald-400 font-bold">{rec.sharpe_ratio}</span>
                    </div>
                    <div className="bg-[#151A22] p-2 rounded border border-[#232936]">
                      <span className="text-[#8B949E] block">Volatility</span>
                      <span className="font-mono text-amber-400 font-bold">{(rec.volatility * 100).toFixed(0)}%</span>
                    </div>
                  </div>

                  <p className="text-[10px] text-[#8B949E] leading-relaxed">
                    {rec.rationale || rec.allocation_rationale}
                  </p>
                </div>

                <button
                  onClick={() => onSelectSymbol(rec.symbol)}
                  className="w-full py-1.5 bg-[#151A22] hover:bg-emerald-600 hover:text-white text-emerald-400 border border-emerald-500/30 rounded text-[10px] font-bold transition flex items-center justify-center space-x-1 mt-2"
                >
                  <span>Trade {rec.symbol}</span>
                  <ArrowRight className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>

          {/* Bottom Section: Information & Catalyst Extraction Sandbox */}
          <div className="bg-[#0D1117] border border-[#232936] p-5 rounded-xl space-y-4 shadow-xl">
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-blue-400" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider">
                Financial Information & Catalyst Extraction (Unit VI)
              </h3>
            </div>

            <p className="text-[11px] text-[#8B949E]">
              Extracts tickers, monetary values, percentages, catalysts, and sentiment polarity scores from unstructured financial news.
            </p>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <div className="space-y-3">
                <textarea
                  value={extractInput}
                  onChange={(e) => setExtractInput(e.target.value)}
                  rows={4}
                  className="w-full bg-[#151A22] border border-[#232936] text-white p-3 rounded-lg text-xs focus:outline-none focus:border-blue-500 leading-relaxed font-mono"
                  placeholder="Paste financial news snippet or tweet..."
                />
                <button
                  onClick={handleExtract}
                  disabled={isExtracting}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-lg text-xs font-bold transition flex items-center space-x-2"
                >
                  {isExtracting ? <RefreshCw className="w-3 h-3 animate-spin" /> : <Cpu className="w-3 h-3" />}
                  <span>Extract Market Entities</span>
                </button>
              </div>

              {/* Extraction Output */}
              <div className="bg-[#151A22] border border-[#232936] p-4 rounded-lg space-y-3 text-xs">
                {extractedResult ? (
                  <>
                    <div className="flex items-center justify-between border-b border-[#232936] pb-2">
                      <span className="text-[#8B949E] text-[10px] uppercase font-bold">Extraction Analysis</span>
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                          extractedResult.sentiment === "Bullish"
                            ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                            : extractedResult.sentiment === "Bearish"
                            ? "bg-red-500/20 text-red-400 border border-red-500/30"
                            : "bg-slate-500/20 text-slate-400"
                        }`}
                      >
                        {extractedResult.summary_tag}
                      </span>
                    </div>

                    <div className="space-y-2 text-[11px]">
                      <div>
                        <span className="text-[#8B949E] text-[10px] block">Identified Tickers:</span>
                        <div className="flex flex-wrap gap-1 mt-0.5">
                          {extractedResult.tickers.length > 0 ? (
                            extractedResult.tickers.map((t) => (
                              <span key={t} className="px-1.5 py-0.5 bg-blue-500/20 text-blue-300 rounded text-[10px]">
                                {t}
                              </span>
                            ))
                          ) : (
                            <span className="text-[#8B949E] italic text-[10px]">None</span>
                          )}
                        </div>
                      </div>

                      <div>
                        <span className="text-[#8B949E] text-[10px] block">Detected Catalysts:</span>
                        <div className="flex flex-wrap gap-1 mt-0.5">
                          {extractedResult.catalysts.length > 0 ? (
                            extractedResult.catalysts.map((c) => (
                              <span key={c} className="px-1.5 py-0.5 bg-purple-500/20 text-purple-300 rounded text-[10px]">
                                {c}
                              </span>
                            ))
                          ) : (
                            <span className="text-[#8B949E] italic text-[10px]">None</span>
                          )}
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-2 pt-1 text-[10px]">
                        <div>
                          <span className="text-[#8B949E] block">Figures / Values:</span>
                          <span className="text-white font-mono">{extractedResult.monetary_values.join(", ") || "None"}</span>
                        </div>
                        <div>
                          <span className="text-[#8B949E] block">Percentages:</span>
                          <span className="text-white font-mono">{extractedResult.percentages.join(", ") || "None"}</span>
                        </div>
                      </div>
                    </div>
                  </>
                ) : (
                  <div className="h-full flex items-center justify-center text-[#8B949E] text-[11px]">
                    Click "Extract Market Entities" to analyze text.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
