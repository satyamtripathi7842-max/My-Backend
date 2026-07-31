"""
news_agent.py
Fetches / estimates news sentiment for a supplier.

By default this runs in SIMULATED mode with a lightweight keyword-based
sentiment heuristic over a small in-memory headline pool, so the platform
is fully demoable without external API keys.

To go live: set NEWS_API_KEY in your environment and implement
`_fetch_real_headlines()` to call a provider (NewsAPI, GDELT, Bing News, etc).
"""

import os
import random

NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

POSITIVE_WORDS = {"growth", "expansion", "record", "strong", "partnership", "award", "profit"}
NEGATIVE_WORDS = {"strike", "delay", "lawsuit", "shortage", "recall", "bankruptcy", "sanction", "layoffs"}

_SIMULATED_HEADLINE_POOL = [
    "{name} announces record quarterly growth",
    "{name} faces supply shortage amid raw material delay",
    "{name} signs new partnership expanding capacity",
    "{name} hit with regulatory sanction over compliance issue",
    "{name} workers stage strike over wage dispute",
    "{name} reports strong profit despite market headwinds",
    "{name} recalls batch of products over quality concern",
    "Analysts flag bankruptcy risk for {name} amid debt load",
]


class NewsAgent:
    def _fetch_real_headlines(self, supplier_name: str):
        # Placeholder for real integration, e.g. NewsAPI:
        # resp = requests.get("https://newsapi.org/v2/everything",
        #     params={"q": supplier_name, "apiKey": NEWS_API_KEY})
        # return [a["title"] for a in resp.json().get("articles", [])]
        raise NotImplementedError

    def _score_headline(self, headline: str) -> float:
        text = headline.lower()
        pos = sum(1 for w in POSITIVE_WORDS if w in text)
        neg = sum(1 for w in NEGATIVE_WORDS if w in text)
        if pos == neg == 0:
            return 0.0
        return (pos - neg) / max(pos + neg, 1)

    def fetch_sentiment(self, supplier_name: str) -> float:
        """Returns a sentiment score in [-1, 1]. Higher = more positive coverage."""
        if NEWS_API_KEY:
            try:
                headlines = self._fetch_real_headlines(supplier_name)
            except NotImplementedError:
                headlines = self._simulated_headlines(supplier_name)
        else:
            headlines = self._simulated_headlines(supplier_name)

        if not headlines:
            return 0.0

        scores = [self._score_headline(h) for h in headlines]
        return round(sum(scores) / len(scores), 2)

    def _simulated_headlines(self, supplier_name: str):
        sample = random.sample(_SIMULATED_HEADLINE_POOL, k=min(3, len(_SIMULATED_HEADLINE_POOL)))
        return [h.format(name=supplier_name) for h in sample]


news_agent = NewsAgent()
