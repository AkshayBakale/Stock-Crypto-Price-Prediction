"""
Unit V: Web Retrieval and Web Crawling
Implements:
- Asynchronous Web Crawler for market news & announcements (BeautifulSoup / HTML / RSS parser)
- Link-based ranking and PageRank algorithm on asset & source authority co-occurrence graph
- Parallel query processing / distributed search simulation
"""

import asyncio
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from datetime import datetime, timezone
import httpx
from bs4 import BeautifulSoup

from backend.ir.language_model import lm_engine


class PageRankEngine:
    """
    PageRank algorithm for determining authority and interconnected centrality
    among market assets, news sources, and macroeconomic entities.
    """
    def __init__(self, damping_factor: float = 0.85, max_iterations: int = 50, tol: float = 1e-6):
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.tol = tol

    def compute(self, nodes: List[str], edges: List[Tuple[str, str, float]]) -> Dict[str, float]:
        """
        Computes steady-state PageRank distribution.
        edges is a list of (source, target, weight)
        """
        N = len(nodes)
        if N == 0:
            return {}

        # Initialize uniform PageRank vector
        pr = {node: 1.0 / N for node in nodes}

        # Build adjacency graph
        out_links: Dict[str, Dict[str, float]] = {node: {} for node in nodes}
        in_links: Dict[str, List[str]] = {node: [] for node in nodes}

        for u, v, w in edges:
            if u in pr and v in pr:
                out_links[u][v] = w
                in_links[v].append(u)

        # Power iteration
        for _ in range(self.max_iterations):
            new_pr: Dict[str, float] = {}
            # Account for dangling nodes (nodes with 0 out-degree)
            dangling_sum = sum(pr[node] for node in nodes if len(out_links[node]) == 0)

            for u in nodes:
                # Sum PR of incoming nodes
                incoming_sum = 0.0
                for v in in_links[u]:
                    total_out_weight = sum(out_links[v].values())
                    if total_out_weight > 0:
                        incoming_sum += pr[v] * (out_links[v][u] / total_out_weight)

                # PageRank formula: (1 - d)/N + d * (incoming_sum + dangling_sum / N)
                new_pr[u] = (1.0 - self.damping_factor) / N + self.damping_factor * (
                    incoming_sum + dangling_sum / N
                )

            # Check convergence
            diff = sum(abs(new_pr[node] - pr[node]) for node in nodes)
            pr = new_pr
            if diff < self.tol:
                break

        # Normalize to sum = 1.0
        total = sum(pr.values()) or 1.0
        return {k: round(v / total, 5) for k, v in pr.items()}


class FinancialWebCrawler:
    """
    Asynchronous Web Crawler and Parser for financial news, SEC/Crypto feeds, and press releases.
    """
    def __init__(self):
        self.crawled_articles: List[Dict[str, Any]] = []
        self.pagerank_engine = PageRankEngine(damping_factor=0.85)
        self.co_occurrence_graph: List[Tuple[str, str, float]] = []
        self.pagerank_scores: Dict[str, float] = {}
        
        # Pre-seed default financial articles to ensure immediate instant searchability
        self._seed_default_corpus()

    def _seed_default_corpus(self):
        default_articles = [
            {
                "id": "c1",
                "title": "Bitcoin Surges as Spot ETF Inflows Reach Historic Highs",
                "source": "CoinDesk",
                "url": "https://coindesk.com/markets/bitcoin-etf-inflows",
                "symbol": "BTCUSDT",
                "category": "Crypto",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "text": "Bitcoin pushed past key resistance levels this week as institutional spot Bitcoin ETF products registered over $1.2 billion in net weekly inflows. BlackRock and Fidelity reported surging trading volumes. Market analysts predict sustained liquidity and bullish momentum heading into the quarterly options expiry."
            },
            {
                "id": "c2",
                "title": "Federal Reserve Signals Potential Interest Rate Cut Amid Cooling Inflation",
                "source": "Bloomberg",
                "url": "https://bloomberg.com/news/fed-rate-signals",
                "symbol": "SPY",
                "category": "Macro",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "text": "Federal Reserve Chair indicated that the central bank is closely monitoring labor market conditions and headline inflation metrics. Bond yields fell sharply across the 2-year and 10-year Treasury curve, providing strong tailwinds for high-growth tech equities including Apple, Nvidia, and Microsoft."
            },
            {
                "id": "c3",
                "title": "Ethereum Layer-2 Network Activity Hits All-Time Record High",
                "source": "Decrypt",
                "url": "https://decrypt.co/eth-l2-scaling",
                "symbol": "ETHUSDT",
                "category": "Crypto",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "text": "Ethereum scaling solutions Arbitrum, Optimism, and Base processed a record 45 million daily transactions. Gas fees on Ethereum mainnet have dropped by 80% following the Dencun upgrade blobs integration. Analysts highlight growing DeFi TVL and decentralized exchange liquidity."
            },
            {
                "id": "c4",
                "title": "NVIDIA Unveils Next-Generation AI Superchip Architecture",
                "source": "Reuters",
                "url": "https://reuters.com/tech/nvidia-ai-chips",
                "symbol": "NVDA",
                "category": "Tech/AI",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "text": "NVIDIA announced its newest generation Blackwell architecture GPUs designed for large language models and enterprise AI data centers. Cloud hyperscalers Microsoft, Alphabet, and Amazon confirmed multibillion-dollar procurement orders, sparking a rally across semiconductor and hardware suppliers."
            },
            {
                "id": "c5",
                "title": "Solana Ecosystem DEX Volume Overtakes Competitors",
                "source": "CoinTelegraph",
                "url": "https://cointelegraph.com/solana-dex-volume",
                "symbol": "SOLUSDT",
                "category": "Crypto",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "text": "Solana decentralized exchange trading volume flipped major competitor chains for the third consecutive week. High throughput, sub-cent transaction fees, and thriving meme coin liquidity have attracted retail traders and institutional market makers to SOL."
            },
            {
                "id": "c6",
                "title": "Indian IT Giants Post Robust Cloud Migration Earnings",
                "source": "Economic Times",
                "url": "https://economictimes.indiatimes.com/tech/tcs-infy",
                "symbol": "TCS.NS",
                "category": "Equities",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "text": "Tata Consultancy Services (TCS) and Infosys reported strong quarterly margin expansion driven by European enterprise digital transformation and cloud modernization mandates. Domestic mutual funds increased their allocations to Nifty IT index constituents."
            }
        ]
        self.crawled_articles.extend(default_articles)
        self.rebuild_index_and_graph()

    def parse_html_content(self, html: str, url: str, source: str) -> Dict[str, Any]:
        """
        Uses BeautifulSoup to extract clean headline, body text, and links.
        """
        soup = BeautifulSoup(html, "html.parser")
        
        # Remove scripts, styles, navigations
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript"]):
            tag.decompose()

        # Extract title
        title = ""
        if soup.title and soup.title.string:
            title = soup.title.string.strip()
        elif soup.find("h1"):
            title = soup.find("h1").get_text().strip()

        # Extract article body
        paragraphs = soup.find_all("p")
        body_text = " ".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])

        # Detect primary ticker
        symbol = "MACRO"
        text_upper = f"{title} {body_text}".upper()
        if "BTC" in text_upper or "BITCOIN" in text_upper:
            symbol = "BTCUSDT"
        elif "ETH" in text_upper or "ETHEREUM" in text_upper:
            symbol = "ETHUSDT"
        elif "SOL" in text_upper or "SOLANA" in text_upper:
            symbol = "SOLUSDT"
        elif "NVDA" in text_upper or "NVIDIA" in text_upper:
            symbol = "NVDA"
        elif "SPY" in text_upper or "S&P" in text_upper or "FED" in text_upper:
            symbol = "SPY"
        elif "TCS" in text_upper or "INFY" in text_upper or "NIFTY" in text_upper:
            symbol = "TCS.NS"

        return {
            "id": f"c_{len(self.crawled_articles) + 1}",
            "title": title or "Market Update",
            "source": source,
            "url": url,
            "symbol": symbol,
            "category": "Crawled Live",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "text": body_text[:2000] if body_text else title
        }

    async def crawl_url(self, url: str, source_name: str = "Web") -> Dict[str, Any]:
        """
        Asynchronously fetches and crawls a webpage using httpx and parses via BeautifulSoup.
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MarketAI/1.0 IR Crawler"
        }
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            article = self.parse_html_content(resp.text, url, source_name)
            self.crawled_articles.insert(0, article)
            self.rebuild_index_and_graph()
            return article

    def rebuild_index_and_graph(self):
        """
        Re-indexes the document corpus in the Language Model Engine
        and builds the entity / asset co-occurrence graph to recalculate PageRank.
        """
        # 1. Update Language Model Index
        lm_engine.index_documents(self.crawled_articles)

        # 2. Build Asset Co-occurrence Graph for PageRank
        # Defined known assets and macroeconomic entities
        entities = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "NVDA", "SPY", "TCS.NS", "FED", "AI_SECTOR", "DEFI"]
        
        edges: List[Tuple[str, str, float]] = []
        # Co-occurrence tracking
        co_counts: Dict[Tuple[str, str], float] = {}

        for art in self.crawled_articles:
            txt = (art.get("title", "") + " " + art.get("text", "")).upper()
            found = [e for e in entities if e in txt or (e == "BTCUSDT" and "BITCOIN" in txt) or (e == "ETHUSDT" and "ETHEREUM" in txt) or (e == "SOLUSDT" and "SOLANA" in txt) or (e == "NVDA" and "NVIDIA" in txt)]
            
            for i in range(len(found)):
                for j in range(len(found)):
                    if i != j:
                        pair = (found[i], found[j])
                        co_counts[pair] = co_counts.get(pair, 0.0) + 1.0

        for (u, v), count in co_counts.items():
            edges.append((u, v, count))

        # Add fallback bidirectional edges if sparse
        if not edges:
            edges = [
                ("BTCUSDT", "ETHUSDT", 2.0),
                ("ETHUSDT", "SOLUSDT", 1.5),
                ("ETHUSDT", "DEFI", 2.0),
                ("NVDA", "AI_SECTOR", 3.0),
                ("SPY", "FED", 2.5),
                ("BTCUSDT", "FED", 1.0),
                ("TCS.NS", "SPY", 1.0)
            ]

        self.co_occurrence_graph = edges
        self.pagerank_scores = self.pagerank_engine.compute(entities, edges)

    def get_pagerank_summary(self) -> List[Dict[str, Any]]:
        """
        Returns sorted PageRank node authority scores and graph connections.
        """
        sorted_ranks = sorted(self.pagerank_scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {
                "entity": entity,
                "pagerank": round(score, 5),
                "influence_percentage": round(score * 100, 2),
                "connections": [
                    {"target": v, "weight": w}
                    for u, v, w in self.co_occurrence_graph if u == entity
                ]
            }
            for entity, score in sorted_ranks
        ]


# Global singleton crawler instance
crawler_engine = FinancialWebCrawler()
