"""
Unit VI: IR Applications - Recommender System
Implements:
- Content-Based Filtering: Cosine similarity matching on multi-dimensional asset features & profiles
- Knowledge-Based Recommendation: Rule/Constraint satisfaction based on investor risk profile and constraints
- Pair & Hedge Portfolio Recommendations
"""

import math
from typing import List, Dict, Any, Optional


# Institutional Asset Profiles Matrix (Feature vectors for content-based matching)
ASSET_CATALOG: Dict[str, Dict[str, Any]] = {
    "BTCUSDT": {
        "symbol": "BTCUSDT",
        "name": "Bitcoin",
        "asset_class": "Crypto",
        "volatility": 0.55,
        "momentum": 0.72,
        "liquidity": 0.98,
        "sharpe_ratio": 1.45,
        "risk_level": "Aggressive",
        "tags": ["crypto", "layer1", "store_of_value", "etf_backed", "high_liquidity"]
    },
    "ETHUSDT": {
        "symbol": "ETHUSDT",
        "name": "Ethereum",
        "asset_class": "Crypto",
        "volatility": 0.62,
        "momentum": 0.68,
        "liquidity": 0.95,
        "sharpe_ratio": 1.32,
        "risk_level": "Aggressive",
        "tags": ["crypto", "smart_contracts", "defi", "layer1", "staking"]
    },
    "SOLUSDT": {
        "symbol": "SOLUSDT",
        "name": "Solana",
        "asset_class": "Crypto",
        "volatility": 0.78,
        "momentum": 0.85,
        "liquidity": 0.88,
        "sharpe_ratio": 1.55,
        "risk_level": "Very Aggressive",
        "tags": ["crypto", "high_tps", "defi", "layer1", "growth"]
    },
    "NVDA": {
        "symbol": "NVDA",
        "name": "NVIDIA Corporation",
        "asset_class": "Equities",
        "volatility": 0.42,
        "momentum": 0.88,
        "liquidity": 0.99,
        "sharpe_ratio": 1.85,
        "risk_level": "Moderate",
        "tags": ["equities", "tech", "semiconductors", "ai_datacenter", "growth"]
    },
    "SPY": {
        "symbol": "SPY",
        "name": "SPDR S&P 500 ETF Trust",
        "asset_class": "Equities/Index",
        "volatility": 0.16,
        "momentum": 0.52,
        "liquidity": 1.0,
        "sharpe_ratio": 1.25,
        "risk_level": "Conservative",
        "tags": ["equities", "index", "us_market", "diversified", "low_volatility"]
    },
    "TCS.NS": {
        "symbol": "TCS.NS",
        "name": "Tata Consultancy Services",
        "asset_class": "Indian Equities",
        "volatility": 0.22,
        "momentum": 0.48,
        "liquidity": 0.85,
        "sharpe_ratio": 1.15,
        "risk_level": "Conservative",
        "tags": ["equities", "indian_market", "it_services", "bluechip", "dividend"]
    },
    "RELIANCE.NS": {
        "symbol": "RELIANCE.NS",
        "name": "Reliance Industries",
        "asset_class": "Indian Equities",
        "volatility": 0.26,
        "momentum": 0.58,
        "liquidity": 0.90,
        "sharpe_ratio": 1.30,
        "risk_level": "Moderate",
        "tags": ["equities", "indian_market", "conglomerate", "telecom", "energy"]
    },
    "GLD": {
        "symbol": "GLD",
        "name": "SPDR Gold Shares",
        "asset_class": "Commodity",
        "volatility": 0.14,
        "momentum": 0.40,
        "liquidity": 0.92,
        "sharpe_ratio": 0.95,
        "risk_level": "Conservative",
        "tags": ["commodity", "gold", "hedge", "inflation_safe", "safe_haven"]
    }
}


class FinancialRecommender:
    """
    Hybrid Recommender combining Content-Based vector matching and
    Knowledge-Based constraint filtering.
    """
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        if len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def content_based_recommend(self, target_symbol: str, top_n: int = 4) -> List[Dict[str, Any]]:
        """
        Recommends assets most similar to the target_symbol based on quantitative
        feature similarity (volatility, momentum, liquidity, sharpe_ratio) and tag overlap.
        """
        if target_symbol not in ASSET_CATALOG:
            # Fallback to BTCUSDT if target not directly in catalog
            target_symbol = "BTCUSDT"

        target = ASSET_CATALOG[target_symbol]
        target_vec = [target["volatility"], target["momentum"], target["liquidity"], target["sharpe_ratio"]]
        target_tags = set(target["tags"])

        recommendations = []
        for symbol, asset in ASSET_CATALOG.items():
            if symbol == target_symbol:
                continue

            asset_vec = [asset["volatility"], asset["momentum"], asset["liquidity"], asset["sharpe_ratio"]]
            stat_sim = self._cosine_similarity(target_vec, asset_vec)
            
            # Jaccard tag similarity
            asset_tags = set(asset["tags"])
            tag_sim = len(target_tags & asset_tags) / max(1, len(target_tags | asset_tags))
            
            # Combined score: 70% statistical + 30% categorical
            final_score = 0.70 * stat_sim + 0.30 * tag_sim

            recommendations.append({
                "symbol": symbol,
                "name": asset["name"],
                "asset_class": asset["asset_class"],
                "match_score": round(final_score * 100, 1),
                "similarity": round(final_score, 4),
                "shared_traits": list(target_tags & asset_tags),
                "risk_level": asset["risk_level"],
                "volatility": asset["volatility"],
                "momentum": asset["momentum"],
                "sharpe_ratio": asset["sharpe_ratio"],
                "rationale": f"High statistical correlation with {target['name']} in {asset['asset_class']} profile."
            })

        recommendations.sort(key=lambda x: x["match_score"], reverse=True)
        return recommendations[:top_n]

    def knowledge_based_recommend(
        self,
        risk_tolerance: str = "Moderate", # "Conservative", "Moderate", "Aggressive"
        max_volatility: float = 0.60,
        preferred_classes: Optional[List[str]] = None,
        strategy_objective: str = "Growth" # "Growth", "Preservation", "Hedge", "Momentum"
    ) -> List[Dict[str, Any]]:
        """
        Knowledge-Based Recommender: Applies financial logic and explicit investor constraints
        to produce tailored asset allocation and strategy recommendations.
        """
        preferred_classes = preferred_classes or ["Crypto", "Equities", "Commodity"]
        matched_assets = []

        risk_scores = {"Conservative": 1, "Moderate": 2, "Aggressive": 3, "Very Aggressive": 4}
        user_risk_val = risk_scores.get(risk_tolerance, 2)

        for symbol, asset in ASSET_CATALOG.items():
            asset_risk_val = risk_scores.get(asset["risk_level"], 2)

            # Constraint 1: Risk level constraint
            if asset_risk_val > user_risk_val:
                continue

            # Constraint 2: Maximum volatility threshold
            if asset["volatility"] > max_volatility:
                continue

            # Constraint 3: Preferred asset class filter
            if not any(pref.lower() in asset["asset_class"].lower() for pref in preferred_classes):
                continue

            # Calculate Knowledge Score based on objective
            if strategy_objective == "Momentum":
                objective_score = asset["momentum"] * 100
            elif strategy_objective == "Preservation" or strategy_objective == "Hedge":
                objective_score = (1.0 - asset["volatility"]) * 70 + asset["sharpe_ratio"] * 15
            else: # Growth
                objective_score = asset["sharpe_ratio"] * 30 + asset["momentum"] * 50

            matched_assets.append({
                "symbol": symbol,
                "name": asset["name"],
                "asset_class": asset["asset_class"],
                "risk_level": asset["risk_level"],
                "volatility": asset["volatility"],
                "sharpe_ratio": asset["sharpe_ratio"],
                "objective_score": round(objective_score, 1),
                "tags": asset["tags"],
                "suggested_weight_pct": 0.0, # Will be normalized
                "allocation_rationale": f"Satisfies {risk_tolerance} risk constraint with volatility of {int(asset['volatility']*100)}%."
            })

        # Calculate suggested portfolio weights
        total_score = sum(a["objective_score"] for a in matched_assets) or 1.0
        for a in matched_assets:
            a["suggested_weight_pct"] = round((a["objective_score"] / total_score) * 100, 1)

        matched_assets.sort(key=lambda x: x["objective_score"], reverse=True)
        return matched_assets


recommender_engine = FinancialRecommender()
