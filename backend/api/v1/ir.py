"""
FastAPI Router for Information Retrieval (IR) Endpoints
Encompasses:
- Language Model Passage Search & Ranking (Dirichlet / JM / DFR)
- Web Crawler & Live Feed Management
- PageRank Asset Centrality & Co-occurrence Network
- Content-Based & Knowledge-Based Asset Recommender
- Financial Information & Entity Extraction
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Query, HTTPException

from backend.ir.language_model import lm_engine
from backend.ir.crawler import crawler_engine
from backend.ir.recommender import recommender_engine
from backend.ir.extractor import extractor_engine

router = APIRouter(prefix="/ir", tags=["Information Retrieval"])


class CrawlRequest(BaseModel):
    url: str = Field(..., description="Target webpage URL to crawl")
    source: Optional[str] = Field("Web", description="Publisher / source name")


class RecommendationRequest(BaseModel):
    mode: str = Field("content", description="'content' for content-based matching or 'knowledge' for rule-based matching")
    symbol: Optional[str] = Field("BTCUSDT", description="Target symbol for content-based matching")
    risk_tolerance: Optional[str] = Field("Moderate", description="Conservative, Moderate, Aggressive")
    max_volatility: Optional[float] = Field(0.60, description="Maximum acceptable volatility (0.0 to 1.0)")
    preferred_classes: Optional[List[str]] = Field(default_factory=lambda: ["Crypto", "Equities", "Commodity"])
    strategy_objective: Optional[str] = Field("Growth", description="Growth, Preservation, Hedge, Momentum")


class ExtractRequest(BaseModel):
    text: str = Field(..., description="Unstructured financial news or research text to parse")


@router.get("/search")
async def search_passages(
    q: str = Query(..., description="Search query string"),
    method: str = Query("dirichlet", description="Ranking method: 'dirichlet', 'jelinek_mercer', or 'dfr'"),
    top_k: int = Query(6, ge=1, le=50, description="Max passages to return"),
    mu: Optional[float] = Query(None, description="Dirichlet prior smoothing parameter (default: 1000)"),
    lambd: Optional[float] = Query(None, description="Jelinek-Mercer smoothing lambda parameter (0.0 to 1.0)")
):
    """
    Unit IV: Searches and ranks passages from the financial news corpus using Language Models.
    Supports Dirichlet Prior smoothing, Jelinek-Mercer linear interpolation, and Divergence From Randomness (DFR).
    """
    results = lm_engine.search_passages(
        query=q,
        method=method,
        top_k=top_k,
        mu=mu,
        lambd=lambd
    )
    return {
        "query": q,
        "method": method,
        "total_passages_indexed": len(lm_engine.passages),
        "total_corpus_tokens": lm_engine.total_collection_tokens,
        "results_count": len(results),
        "results": results
    }


@router.get("/articles")
async def get_crawled_articles():
    """
    Returns all currently crawled and indexed financial articles.
    """
    return {
        "count": len(crawler_engine.crawled_articles),
        "articles": crawler_engine.crawled_articles
    }


@router.post("/crawl")
async def crawl_webpage(request: CrawlRequest):
    """
    Unit V: Crawls a web URL, parses HTML using BeautifulSoup, extracts content,
    updates the LM passage index, and recalculates PageRank.
    """
    try:
        article = await crawler_engine.crawl_url(request.url, request.source)
        return {
            "status": "SUCCESS",
            "message": "Page successfully crawled and indexed into Language Model corpus.",
            "article": article
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to crawl URL: {str(e)}")


@router.get("/pagerank")
async def get_pagerank_graph():
    """
    Unit V: Returns PageRank influence scores and the asset/macroeconomic co-occurrence graph.
    """
    summary = crawler_engine.get_pagerank_summary()
    return {
        "damping_factor": crawler_engine.pagerank_engine.damping_factor,
        "nodes": summary,
        "edges": [
            {"source": u, "target": v, "weight": w}
            for u, v, w in crawler_engine.co_occurrence_graph
        ]
    }


@router.post("/recommend")
async def get_recommendations(request: RecommendationRequest):
    """
    Unit VI: Recommender System.
    - Content-Based: Feature cosine similarity with target asset.
    - Knowledge-Based: Risk-tolerance & volatility constraint filtering.
    """
    if request.mode == "content":
        recs = recommender_engine.content_based_recommend(
            target_symbol=request.symbol or "BTCUSDT",
            top_n=5
        )
        return {
            "mode": "content_based",
            "target_symbol": request.symbol,
            "recommendations": recs
        }
    else:
        recs = recommender_engine.knowledge_based_recommend(
            risk_tolerance=request.risk_tolerance or "Moderate",
            max_volatility=request.max_volatility or 0.60,
            preferred_classes=request.preferred_classes,
            strategy_objective=request.strategy_objective or "Growth"
        )
        return {
            "mode": "knowledge_based",
            "risk_tolerance": request.risk_tolerance,
            "strategy_objective": request.strategy_objective,
            "max_volatility_cap": request.max_volatility,
            "recommendations": recs
        }


@router.post("/extract")
async def extract_information(request: ExtractRequest):
    """
    Unit VI: Extracts tickers, dollar amounts, percentages, catalysts, and sentiment scores from text.
    """
    extracted = extractor_engine.extract_from_text(request.text)
    return {
        "status": "SUCCESS",
        "data": extracted
    }
