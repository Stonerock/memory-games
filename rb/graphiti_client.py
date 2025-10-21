"""
Optional Graphiti integration.

Uses Graphiti's temporal knowledge graph for storing and retrieving memory items.
Set env var RB_STORE=graphiti and configure GRAPHITI_URI, GRAPHITI_USER, GRAPHITI_PASSWORD.
"""
import os, asyncio
from typing import List, Dict, Any
from datetime import datetime
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

class GraphitiClient:
    def __init__(self):
        self.uri = os.getenv("GRAPHITI_URI", "bolt://localhost:7687")
        self.user = os.getenv("GRAPHITI_USER", "neo4j")
        self.password = os.getenv("GRAPHITI_PASSWORD", "")

        if not self.password:
            raise RuntimeError("Set GRAPHITI_PASSWORD to use GraphitiClient. Also optionally set GRAPHITI_URI and GRAPHITI_USER.")

        # Initialize Graphiti client
        self.graphiti = Graphiti(
            uri=self.uri,
            user=self.user,
            password=self.password
        )

        # Ensure indices are built (run once)
        asyncio.run(self._ensure_setup())

    async def _ensure_setup(self):
        """Ensure database indices and constraints are set up."""
        try:
            await self.graphiti.build_indices_and_constraints()
        except Exception:
            # May already exist, that's OK
            pass

    def upsert_memory_items(self, items: List[Dict[str, Any]]) -> None:
        """
        Store memory items as episodes in Graphiti.
        Each memory item becomes an episode with its content.
        """
        asyncio.run(self._upsert_memory_items_async(items))

    async def _upsert_memory_items_async(self, items: List[Dict[str, Any]]) -> None:
        for item in items:
            # Convert memory item to episode
            title = item.get("title", "Untitled Memory")
            description = item.get("description", "")
            content = item.get("content", "")
            outcome = item.get("outcome", "unknown")
            created_at = item.get("created_at", datetime.now().timestamp())

            # Combine description and content into episode body
            episode_body = f"{description}\n\n{content}"

            # Add metadata about outcome
            source_description = f"ReasoningBank memory ({outcome})"

            await self.graphiti.add_episode(
                name=title,
                episode_body=episode_body,
                source_description=source_description,
                reference_time=datetime.fromtimestamp(created_at),
                source=EpisodeType.text,
                group_id="reasoning_bank"
            )

    def search(self, query: str, top_k: int = 1) -> List[Dict[str, Any]]:
        """
        Search memory items using Graphiti's hybrid search.
        Returns top_k relevant memory items.
        """
        return asyncio.run(self._search_async(query, top_k))

    async def _search_async(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        # Use Graphiti's hybrid search on edges (facts)
        edges = await self.graphiti.search(
            query=query,
            group_ids=["reasoning_bank"],
            num_results=top_k
        )

        # Convert edges to memory item format
        results = []
        for edge in edges[:top_k]:
            # Extract info from the edge
            results.append({
                "title": edge.name or "Memory Item",
                "description": edge.fact[:200] if edge.fact else "",  # First 200 chars
                "content": edge.fact or "",
                "outcome": "success" if edge.valid_at else "unknown",
                "created_at": edge.created_at.timestamp() if edge.created_at else datetime.now().timestamp(),
                "source": {"type": "graphiti", "uuid": edge.uuid}
            })

        return results

    def close(self):
        """Close the Graphiti connection."""
        asyncio.run(self.graphiti.close())
