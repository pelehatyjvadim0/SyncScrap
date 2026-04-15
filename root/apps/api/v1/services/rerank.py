import math


class CrossEncoderReranker:
    """MVP reranker: lexical overlap + price preference."""

    @staticmethod
    def score(query: str, title: str, price: float | None) -> float:
        q_tokens = {t.lower() for t in query.split() if len(t) > 1}
        t_tokens = {t.lower() for t in title.split() if len(t) > 1}
        overlap = len(q_tokens & t_tokens)
        lex_score = overlap / max(1, len(q_tokens))
        price_bonus = 0.0 if price is None else 1 / (1 + math.log1p(max(price, 1)))
        return float(0.8 * lex_score + 0.2 * price_bonus)
