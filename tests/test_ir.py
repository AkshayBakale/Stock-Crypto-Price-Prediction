"""
Tests for Unit IV, V, and VI Information Retrieval (IR) Components
"""

import pytest
from backend.ir.language_model import FinancialTokenizer, LanguageModelIR
from backend.ir.crawler import PageRankEngine, FinancialWebCrawler
from backend.ir.recommender import FinancialRecommender
from backend.ir.extractor import FinancialInformationExtractor


def test_financial_tokenizer():
    text = "Bitcoin ($BTC) surges 12.5% to $68,000 following ETF inflows!"
    tokens = FinancialTokenizer.tokenize(text, remove_stopwords=False)
    assert "bitcoin" in tokens
    assert "$btc" in tokens or "btc" in tokens
    assert "12.5%" in tokens
    assert "$68,000" in tokens or "68,000" in tokens


def test_language_model_smoothing_and_ranking():
    lm = LanguageModelIR(dirichlet_mu=500.0, jm_lambda=0.3)
    docs = [
        {
            "id": "doc1",
            "title": "Bitcoin ETF Inflow",
            "text": "Bitcoin spot ETF registered massive institutional inflows and liquidity.",
            "symbol": "BTCUSDT"
        },
        {
            "id": "doc2",
            "title": "Federal Reserve Rates",
            "text": "The Federal Reserve indicated an upcoming interest rate cut to support economic growth.",
            "symbol": "SPY"
        }
    ]
    lm.index_documents(docs)
    assert len(lm.passages) >= 2
    assert lm.total_collection_tokens > 0

    # Search with Dirichlet smoothing
    dirichlet_results = lm.search_passages("Bitcoin ETF liquidity", method="dirichlet", top_k=2)
    assert len(dirichlet_results) > 0
    assert dirichlet_results[0]["doc_id"] == "doc1"
    assert "score" in dirichlet_results[0]

    # Search with Jelinek-Mercer smoothing
    jm_results = lm.search_passages("Federal Reserve interest rate", method="jelinek_mercer", top_k=2)
    assert len(jm_results) > 0
    assert jm_results[0]["doc_id"] == "doc2"

    # Search with DFR (Divergence From Randomness)
    dfr_results = lm.search_passages("Bitcoin", method="dfr", top_k=2)
    assert len(dfr_results) > 0


def test_pagerank_algorithm():
    pr_engine = PageRankEngine(damping_factor=0.85, max_iterations=50)
    nodes = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "NVDA"]
    edges = [
        ("BTCUSDT", "ETHUSDT", 2.0),
        ("ETHUSDT", "SOLUSDT", 1.0),
        ("SOLUSDT", "BTCUSDT", 1.0),
        ("NVDA", "BTCUSDT", 1.0)
    ]
    scores = pr_engine.compute(nodes, edges)
    assert len(scores) == 4
    # All scores must sum to approx 1.0
    total_score = sum(scores.values())
    assert abs(total_score - 1.0) < 0.05
    # BTCUSDT has multiple incoming links, so its PageRank should be high
    assert scores["BTCUSDT"] > 0.15


def test_financial_crawler_corpus():
    crawler = FinancialWebCrawler()
    assert len(crawler.crawled_articles) >= 5
    summary = crawler.get_pagerank_summary()
    assert len(summary) > 0
    assert "entity" in summary[0]
    assert "pagerank" in summary[0]


def test_recommender_system():
    recommender = FinancialRecommender()
    
    # 1. Content-based recommendation for BTCUSDT
    cb_recs = recommender.content_based_recommend("BTCUSDT", top_n=3)
    assert len(cb_recs) == 3
    assert cb_recs[0]["symbol"] != "BTCUSDT"
    assert "match_score" in cb_recs[0]
    assert "shared_traits" in cb_recs[0]

    # 2. Knowledge-based recommendation for Conservative investor
    kb_conservative = recommender.knowledge_based_recommend(
        risk_tolerance="Conservative",
        max_volatility=0.30,
        strategy_objective="Preservation"
    )
    assert len(kb_conservative) > 0
    for asset in kb_conservative:
        assert asset["volatility"] <= 0.30
        assert asset["risk_level"] in ["Conservative"]


def test_information_extraction():
    extractor = FinancialInformationExtractor()
    sample_news = "Bitcoin ($BTC) surges 8.5% as BlackRock spot ETF records $500 million in single-day volume."
    extracted = extractor.extract_from_text(sample_news)
    
    assert "BTCUSDT" in extracted["tickers"]
    assert extracted["sentiment"] == "Bullish"
    assert extracted["sentiment_score"] > 0
    assert len(extracted["catalysts"]) > 0
    assert any("ETF" in c for c in extracted["catalysts"])
    assert len(extracted["monetary_values"]) > 0
    assert len(extracted["percentages"]) > 0
