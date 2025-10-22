import os, json, time, math
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@dataclass
class MemoryItem:
    title: str
    description: str
    content: str
    outcome: str  # "success" or "failure"
    created_at: float
    source: Dict[str, Any]

class MemoryStore:
    def __init__(self, path: str = "memory/memory.jsonl", use_graphiti: bool = False):
        self.use_graphiti = use_graphiti or os.getenv("RB_STORE") == "graphiti"

        if self.use_graphiti:
            from .graphiti_client import GraphitiClient
            self.graphiti = GraphitiClient()
        else:
            self.path = path
            dirname = os.path.dirname(self.path)
            if dirname:  # Only create directory if path contains a directory component
                os.makedirs(dirname, exist_ok=True)
            if not os.path.exists(self.path):
                open(self.path, "a", encoding="utf-8").close()

    def add_items(self, items: List[MemoryItem]) -> None:
        if self.use_graphiti:
            # Convert MemoryItems to dicts and store in Graphiti
            item_dicts = [asdict(it) for it in items]
            self.graphiti.upsert_memory_items(item_dicts)
        else:
            # Store in JSONL
            with open(self.path, "a", encoding="utf-8") as f:
                for it in items:
                    f.write(json.dumps(asdict(it), ensure_ascii=False) + "\n")

    def _load(self) -> List[Dict[str, Any]]:
        """Load from JSONL (only used when not using Graphiti)."""
        out = []
        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return out

    def search(self, query: str, top_k: int = 1) -> List[Dict[str, Any]]:
        """Search using Graphiti (hybrid) or TF-IDF (lexical)."""
        if self.use_graphiti:
            return self.graphiti.search(query, top_k)
        else:
            # Simple lexical retrieval using TF‑IDF over title+content
            data = self._load()
            if not data:
                return []
            docs = [d["title"] + "\n" + d["content"] for d in data]
            vect = TfidfVectorizer(stop_words="english", max_features=20000)
            X = vect.fit_transform(docs + [query])
            sims = cosine_similarity(X[:-1], X[-1])
            ranked = sorted(zip(range(len(data)), sims.flatten()), key=lambda x: x[1], reverse=True)[:top_k]
            return [data[i] for (i, _) in ranked]

    def close(self):
        """Close connections (only needed for Graphiti)."""
        if self.use_graphiti:
            self.graphiti.close()
