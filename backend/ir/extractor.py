"""
Unit VI: IR Applications - Information Extraction and Integration
Implements:
- Extracting structured entities (tickers, dollar values, percentages, catalysts)
- Financial sentiment polarity analysis (bullish, bearish, neutral)
- Semantic market event categorization
"""

import re
from typing import Dict, Any, List


class FinancialInformationExtractor:
    """
    Extracts structured entities, sentiment scores, and market catalysts from unstructured financial text.
    """

    # Lexicons for financial sentiment
    BULLISH_KEYWORDS = {
        'surge', 'surges', 'surging', 'soar', 'soars', 'rally', 'rallies', 'bullish',
        'gain', 'gains', 'inflow', 'inflows', 'highs', 'breakout', 'growth', 'profit',
        'outperform', 'upgrade', 'expansion', 'all-time', 'record', 'dividend', 'rebound'
    }
    BEARISH_KEYWORDS = {
        'crash', 'crashes', 'drop', 'drops', 'fall', 'falls', 'bearish', 'selloff',
        'outflow', 'outflows', 'lows', 'loss', 'losses', 'downgrade', 'slump', 'decline',
        'plunge', 'recession', 'inflation', 'default', 'warning', 'liquidation', 'ban'
    }

    CATALYST_PATTERNS = [
        (re.compile(r'\b(ETF|spot ETF|approval|approved|filing)\b', re.IGNORECASE), "Regulatory / ETF Catalyst"),
        (re.compile(r'\b(rate cut|rate hike|Fed|Federal Reserve|FOMC|inflation|CPI)\b', re.IGNORECASE), "Macroeconomic / Central Bank Policy"),
        (re.compile(r'\b(earnings|quarterly report|revenue|margin|guidance)\b', re.IGNORECASE), "Corporate Earnings / Financial Disclosure"),
        (re.compile(r'\b(upgrade|hard fork|mainnet|halving|L2|scaling)\b', re.IGNORECASE), "Protocol / Technological Catalyst"),
        (re.compile(r'\b(acquisition|merger|partnership|procurement|deal)\b', re.IGNORECASE), "Strategic Partnership / M&A")
    ]

    TICKER_PATTERNS = [
        (re.compile(r'\b(BTC|BITCOIN|BTCUSDT)\b', re.IGNORECASE), "BTCUSDT"),
        (re.compile(r'\b(ETH|ETHEREUM|ETHUSDT)\b', re.IGNORECASE), "ETHUSDT"),
        (re.compile(r'\b(SOL|SOLANA|SOLUSDT)\b', re.IGNORECASE), "SOLUSDT"),
        (re.compile(r'\b(NVDA|NVIDIA)\b', re.IGNORECASE), "NVDA"),
        (re.compile(r'\b(SPY|S&P 500|SP500)\b', re.IGNORECASE), "SPY"),
        (re.compile(r'\b(TCS|INFY|RELIANCE|NIFTY)\b', re.IGNORECASE), "TCS.NS")
    ]

    DOLLAR_PATTERN = re.compile(r'\$[\d,]+(?:\.\d+)?(?:\s*(?:billion|million|trillion|B|M|T|k))?', re.IGNORECASE)
    PERCENT_PATTERN = re.compile(r'[\+\-]?\d+(?:\.\d+)?%')

    def extract_from_text(self, text: str) -> Dict[str, Any]:
        """
        Parses arbitrary text and returns structured market information.
        """
        if not text:
            return {
                "tickers": [],
                "sentiment": "Neutral",
                "sentiment_score": 0.0,
                "catalysts": [],
                "monetary_values": [],
                "percentages": []
            }

        # 1. Extract Tickers
        detected_tickers = set()
        for pattern, symbol in self.TICKER_PATTERNS:
            if pattern.search(text):
                detected_tickers.add(symbol)

        # 2. Extract Figures
        monetary_values = self.DOLLAR_PATTERN.findall(text)
        percentages = self.PERCENT_PATTERN.findall(text)

        # 3. Detect Catalysts
        catalysts = []
        for pattern, cat_name in self.CATALYST_PATTERNS:
            if pattern.search(text):
                catalysts.append(cat_name)

        # 4. Sentiment Analysis
        words = re.findall(r'\b[A-Za-z\-]+\b', text.lower())
        bull_count = sum(1 for w in words if w in self.BULLISH_KEYWORDS)
        bear_count = sum(1 for w in words if w in self.BEARISH_KEYWORDS)
        total_sentiment_words = bull_count + bear_count

        if total_sentiment_words > 0:
            score = (bull_count - bear_count) / total_sentiment_words
        else:
            score = 0.0

        if score >= 0.2:
            sentiment = "Bullish"
        elif score <= -0.2:
            sentiment = "Bearish"
        else:
            sentiment = "Neutral"

        return {
            "tickers": list(detected_tickers),
            "sentiment": sentiment,
            "sentiment_score": round(score, 3),
            "bullish_signals": bull_count,
            "bearish_signals": bear_count,
            "catalysts": catalysts,
            "monetary_values": monetary_values[:5],
            "percentages": percentages[:5],
            "summary_tag": f"{sentiment} ({'+' if score > 0 else ''}{round(score*100, 1)}%)"
        }


extractor_engine = FinancialInformationExtractor()
