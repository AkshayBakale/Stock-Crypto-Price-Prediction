"""
Unit IV: Language Models for Information Retrieval
Implements:
- Finite Automata / Tokenizer for financial text
- Multinomial Distribution over words
- Query Likelihood Model (QLM) with Dirichlet Prior and Jelinek-Mercer Smoothing
- Divergence From Randomness (DFR) ranking model
- Passage retrieval and ranking
"""

import math
import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter


class FinancialTokenizer:
    """
    Finite-state / pattern-based tokenizer tailored for financial terms,
    tickers ($BTC, AAPL), percentages (5.2%), currency ($100M), and punctuation handling.
    """
    # Pattern matching tickers, percentages, numbers, currencies, and alphanumeric words
    TOKEN_REGEX = re.compile(r'\$?[A-Za-z0-9]+(?:[\.\,\%\-][A-Za-z0-9]+)*%?|\b[A-Za-z]+\b')
    STOPWORDS = {
        'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'in', 'to', 'for', 'of',
        'with', 'as', 'by', 'that', 'this', 'it', 'from', 'be', 'are', 'was', 'were',
        'or', 'will', 'have', 'has', 'had', 'its', 'their', 'but', 'not', 'more', 'all'
    }

    @classmethod
    def tokenize(cls, text: str, remove_stopwords: bool = False) -> List[str]:
        if not text:
            return []
        raw_tokens = cls.TOKEN_REGEX.findall(text.lower())
        tokens = []
        for t in raw_tokens:
            cleaned = t.strip(".,;:()!?'\"")
            if cleaned:
                if remove_stopwords and cleaned in cls.STOPWORDS:
                    continue
                tokens.append(cleaned)
        return tokens


class Passage:
    def __init__(self, doc_id: str, passage_id: int, text: str, tokens: List[str], metadata: Optional[Dict[str, Any]] = None):
        self.doc_id = doc_id
        self.passage_id = passage_id
        self.text = text
        self.tokens = tokens
        self.length = len(tokens)
        self.term_freqs = Counter(tokens)
        self.metadata = metadata or {}


class LanguageModelIR:
    """
    Language Model for Information Retrieval Engine
    """
    def __init__(self, dirichlet_mu: float = 1000.0, jm_lambda: float = 0.4):
        self.dirichlet_mu = dirichlet_mu
        self.jm_lambda = jm_lambda
        self.passages: List[Passage] = []
        self.collection_term_freqs = Counter()
        self.total_collection_tokens = 0
        self.collection_lm: Dict[str, float] = {}
        self.doc_frequencies = Counter()

    def index_documents(self, documents: List[Dict[str, Any]], passage_size: int = 40, passage_overlap: int = 10):
        """
        Takes raw financial documents, chunks them into passages, builds multinomial collection distribution.
        """
        self.passages.clear()
        self.collection_term_freqs.clear()
        self.total_collection_tokens = 0
        self.doc_frequencies.clear()

        for doc in documents:
            doc_id = str(doc.get("id", f"doc_{len(self.passages)}"))
            text = doc.get("text", "")
            title = doc.get("title", "")
            symbol = doc.get("symbol", "")
            category = doc.get("category", "General")
            source = doc.get("source", "MarketFeed")
            timestamp = doc.get("timestamp", "")

            # Chunk document into passages
            doc_tokens = FinancialTokenizer.tokenize(text)
            if not doc_tokens:
                continue

            # If document is short, treat as 1 passage
            if len(doc_tokens) <= passage_size:
                chunks = [(0, text, doc_tokens)]
            else:
                # Sliding window
                chunks = []
                step = passage_size - passage_overlap
                words = text.split()
                for i in range(0, len(doc_tokens), step):
                    chunk_tokens = doc_tokens[i:i + passage_size]
                    if not chunk_tokens:
                        break
                    # Approximate corresponding text snippet
                    word_start = max(0, int(i * (len(words) / max(1, len(doc_tokens)))))
                    word_end = min(len(words), word_start + passage_size)
                    chunk_text = " ".join(words[word_start:word_end])
                    chunks.append((len(chunks), chunk_text, chunk_tokens))

            for pid, ptext, ptokens in chunks:
                passage = Passage(
                    doc_id=doc_id,
                    passage_id=pid,
                    text=ptext,
                    tokens=ptokens,
                    metadata={
                        "title": title,
                        "symbol": symbol,
                        "category": category,
                        "source": source,
                        "timestamp": timestamp,
                        "parent_text": text
                    }
                )
                self.passages.append(passage)
                self.collection_term_freqs.update(ptokens)
                self.total_collection_tokens += len(ptokens)
                
                # Update doc frequencies for DFR
                unique_tokens = set(ptokens)
                for t in unique_tokens:
                    self.doc_frequencies[t] += 1

        # Calculate Multinomial Collection Language Model P(w | C)
        self.collection_lm = {
            word: count / max(1, self.total_collection_tokens)
            for word, count in self.collection_term_freqs.items()
        }

    def score_dirichlet(self, query_tokens: List[str], passage: Passage, mu: Optional[float] = None) -> float:
        """
        Query Likelihood with Dirichlet Prior Smoothing:
        log P(Q | D) = sum_{w in Q} log( (c(w, D) + mu * P(w | C)) / (|D| + mu) )
        """
        mu_val = mu if mu is not None else self.dirichlet_mu
        if passage.length == 0 or not query_tokens:
            return -1e9

        log_prob = 0.0
        doc_len = passage.length

        for q in query_tokens:
            c_w_d = passage.term_freqs.get(q, 0)
            p_w_c = self.collection_lm.get(q, 1e-6) # Background smoothing floor
            prob = (c_w_d + mu_val * p_w_c) / (doc_len + mu_val)
            log_prob += math.log(max(prob, 1e-12))

        return log_prob

    def score_jelinek_mercer(self, query_tokens: List[str], passage: Passage, lambd: Optional[float] = None) -> float:
        """
        Query Likelihood with Jelinek-Mercer (JM) Smoothing:
        P(w | D) = (1 - lambda) * (c(w, D) / |D|) + lambda * P(w | C)
        """
        lam_val = lambd if lambd is not None else self.jm_lambda
        if passage.length == 0 or not query_tokens:
            return -1e9

        log_prob = 0.0
        doc_len = passage.length

        for q in query_tokens:
            c_w_d = passage.term_freqs.get(q, 0)
            p_w_c = self.collection_lm.get(q, 1e-6)
            mle_doc = c_w_d / doc_len
            prob = (1.0 - lam_val) * mle_doc + lam_val * p_w_c
            log_prob += math.log(max(prob, 1e-12))

        return log_prob

    def score_divergence_from_randomness(self, query_tokens: List[str], passage: Passage) -> float:
        """
        Divergence From Randomness (DFR) - InL2 Model:
        Measures information divergence between term distribution in passage vs random baseline.
        """
        if passage.length == 0 or not query_tokens or len(self.passages) == 0:
            return 0.0

        score = 0.0
        N = len(self.passages)
        avg_l = sum(p.length for p in self.passages) / max(1, N)
        c = 1.0  # Parameter for term frequency normalization

        for q in query_tokens:
            tf = passage.term_freqs.get(q, 0)
            if tf == 0:
                continue
            df = self.doc_frequencies.get(q, 1)

            # 1. Normalization 2: tfn = tf * log2(1 + c * avg_l / |D|)
            tfn = tf * math.log2(1.0 + c * (avg_l / max(1, passage.length)))

            # 2. First component of InL2: Information gain Inf1 = -log2(Prob1)
            # In (Inverse Document Frequency): log2((N + 1) / (df + 0.5))
            idf_dfr = math.log2((N + 1.0) / (df + 0.5))

            # 3. Second component L (Laplace succession): (tfn / (tfn + 1))
            score += idf_dfr * (tfn / (tfn + 1.0)) * math.log2(1.0 + tfn)

        return score

    def search_passages(
        self,
        query: str,
        method: str = "dirichlet", # "dirichlet", "jelinek_mercer", or "dfr"
        top_k: int = 10,
        mu: Optional[float] = None,
        lambd: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Ranks all indexed passages using the selected Language Model / DFR retrieval formula.
        """
        query_tokens = FinancialTokenizer.tokenize(query, remove_stopwords=False)
        if not query_tokens or not self.passages:
            return []

        scored_results: List[Tuple[float, Passage]] = []

        for p in self.passages:
            if method == "dirichlet":
                s = self.score_dirichlet(query_tokens, p, mu=mu)
            elif method == "jelinek_mercer":
                s = self.score_jelinek_mercer(query_tokens, p, lambd=lambd)
            elif method == "dfr":
                s = self.score_divergence_from_randomness(query_tokens, p)
            else:
                s = self.score_dirichlet(query_tokens, p)

            scored_results.append((s, p))

        # Sort descending by score
        scored_results.sort(key=lambda x: x[0], reverse=True)

        results = []
        for rank, (score, p) in enumerate(scored_results[:top_k], start=1):
            # Compute term match highlights
            matched_terms = [q for q in set(query_tokens) if q in p.term_freqs]
            results.append({
                "rank": rank,
                "doc_id": p.doc_id,
                "passage_id": p.passage_id,
                "score": round(score, 4),
                "method": method,
                "text": p.text,
                "matched_terms": matched_terms,
                "term_frequencies": {t: p.term_freqs[t] for t in matched_terms},
                "passage_length": p.length,
                "metadata": p.metadata
            })

        return results


# Global singleton instance preloaded with initial financial corpus
lm_engine = LanguageModelIR()
