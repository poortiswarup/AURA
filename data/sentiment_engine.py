"""
AURA — Sentiment Engine
Runs all 4 models on a headline and returns scores.
Falls back gracefully if libraries not installed.
"""

def analyze(headline: str, company: str = "") -> dict:
    """
    Run VADER, TextBlob, LM Lexicon, and FinBERT on a headline.
    Returns dict with all scores and aggregate.
    """
    scores = {}

    # ── VADER ────────────────────────────────────────────────────
    try:
        from nltk.sentiment.vader import SentimentIntensityAnalyzer
        import nltk
        nltk.download("vader_lexicon", quiet=True)
        sia = SentimentIntensityAnalyzer()
        scores["vader_score"] = round(sia.polarity_scores(headline)["compound"], 4)
    except Exception:
        scores["vader_score"] = 0.0

    # ── TextBlob ─────────────────────────────────────────────────
    try:
        from textblob import TextBlob
        scores["textblob_score"] = round(TextBlob(headline).sentiment.polarity, 4)
    except Exception:
        scores["textblob_score"] = 0.0

    # ── Loughran-McDonald ────────────────────────────────────────
    try:
        LM_POS = {"achieve","profit","gain","growth","strong","record","beat","exceed",
                  "outperform","recovery","opportunity","efficient","expand","revenue",
                  "success","improvement","positive","favorable","innovation","rise","surge"}
        LM_NEG = {"loss","risk","decline","fall","drop","crash","default","liability",
                  "debt","lawsuit","fraud","bankruptcy","disappoint","concern","uncertainty",
                  "volatile","downgrade","miss","warn","penalty","weak","fail","reduce",
                  "cut","layoff","restructure","plunge","tumble","slump","worries"}
        tokens = headline.lower().split()
        pos = sum(1 for t in tokens if t in LM_POS)
        neg = sum(1 for t in tokens if t in LM_NEG)
        total = max(len(tokens), 1)
        scores["lm_score"] = round((pos - neg) / total, 4)
    except Exception:
        scores["lm_score"] = 0.0

    # ── FinBERT (optional — skip if not installed) ───────────────
    try:
        from transformers import pipeline
        pipe = pipeline("text-classification", model="ProsusAI/finbert", top_k=None)
        result = pipe(headline[:512])[0]
        label_map = {"positive": 1, "negative": -1, "neutral": 0}
        best = max(result, key=lambda x: x["score"])
        scores["finbert_score"] = round(label_map.get(best["label"], 0) * best["score"], 4)
    except Exception:
        # FinBERT not available — estimate from other scores
        scores["finbert_score"] = round(
            (scores["vader_score"] + scores["textblob_score"] + scores["lm_score"]) / 3, 4
        )

    # ── Aggregate ─────────────────────────────────────────────────
    agg = round(
        scores["vader_score"] * 0.20 +
        scores["textblob_score"] * 0.15 +
        scores["lm_score"] * 0.25 +
        scores["finbert_score"] * 0.40,
        4
    )
    scores["aggregate_score"] = agg

    # ── Label ─────────────────────────────────────────────────────
    if agg >= 0.35:   label = "very_positive"
    elif agg >= 0.05: label = "positive"
    elif agg <= -0.35: label = "very_negative"
    elif agg <= -0.05: label = "negative"
    else:             label = "neutral"
    scores["sentiment_label"] = label

    return scores
