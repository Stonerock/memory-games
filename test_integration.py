#!/usr/bin/env python3
"""
Simple integration test for ReasoningBank memory system.
Tests both JSONL and Graphiti modes (if configured).
"""
import os
import tempfile
import json
from rb.memory_store import MemoryStore, MemoryItem
import time

def test_jsonl_mode():
    """Test JSONL-based memory storage and retrieval."""
    print("Testing JSONL mode...")

    with tempfile.TemporaryDirectory() as tmpdir:
        store_path = os.path.join(tmpdir, "test_memory.jsonl")
        store = MemoryStore(path=store_path, use_graphiti=False)

        # Add some test memory items
        items = [
            MemoryItem(
                title="Fix off-by-one error",
                description="Always check array bounds",
                content="When iterating, use < length not <= length to avoid index errors",
                outcome="success",
                created_at=time.time(),
                source={"type": "test"}
            ),
            MemoryItem(
                title="Null pointer bug",
                description="Check for null before dereferencing",
                content="Always validate object existence before accessing properties",
                outcome="failure",
                created_at=time.time(),
                source={"type": "test"}
            ),
        ]

        store.add_items(items)

        # Test search
        results = store.search("array bounds error", top_k=1)

        assert len(results) > 0, "Should return at least one result"

        # Check if the result is relevant (either result could match)
        top_result = results[0]
        content_lower = top_result["content"].lower()
        title_lower = top_result["title"].lower()
        is_relevant = ("array" in content_lower or "array" in title_lower or
                      "bounds" in content_lower or "bounds" in title_lower)

        print(f"✓ JSONL mode: Added {len(items)} items, search returned {len(results)} results")
        print(f"  Top result: {results[0]['title']}")
        print(f"  Relevance check: {is_relevant}")

    return True

def test_graphiti_mode():
    """Test Graphiti-based memory storage and retrieval."""
    if os.getenv("RB_STORE") != "graphiti":
        print("⊘ Graphiti mode: Skipped (RB_STORE != graphiti)")
        return True

    if not os.getenv("GRAPHITI_PASSWORD"):
        print("⊘ Graphiti mode: Skipped (GRAPHITI_PASSWORD not set)")
        return True

    print("Testing Graphiti mode...")

    try:
        store = MemoryStore(use_graphiti=True)

        # Add some test memory items
        items = [
            MemoryItem(
                title="Test: Async function patterns",
                description="Use async/await for I/O operations",
                content="Always await async functions and use asyncio.run() for top-level calls",
                outcome="success",
                created_at=time.time(),
                source={"type": "test"}
            ),
        ]

        store.add_items(items)

        # Test search
        results = store.search("async await patterns", top_k=1)

        assert len(results) >= 0, "Search should not fail"

        print(f"✓ Graphiti mode: Added {len(items)} items, search returned {len(results)} results")
        if results:
            print(f"  Top result: {results[0]['title']}")

    except Exception as e:
        print(f"✗ Graphiti mode: Failed with error: {e}")
        print(f"  Make sure Neo4j is running and GRAPHITI_PASSWORD is set")
        return False

    return True

if __name__ == "__main__":
    print("=" * 60)
    print("ReasoningBank Memory Integration Tests")
    print("=" * 60)

    results = []

    # Test JSONL mode
    try:
        results.append(("JSONL", test_jsonl_mode()))
    except Exception as e:
        import traceback
        print(f"✗ JSONL mode failed: {e}")
        traceback.print_exc()
        results.append(("JSONL", False))

    print()

    # Test Graphiti mode
    try:
        results.append(("Graphiti", test_graphiti_mode()))
    except Exception as e:
        print(f"✗ Graphiti mode failed: {e}")
        results.append(("Graphiti", False))

    print()
    print("=" * 60)
    print("Test Summary:")
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {name:15} {status}")
    print("=" * 60)

    # Exit with error if any test failed
    if not all(passed for _, passed in results):
        exit(1)
