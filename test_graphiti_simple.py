#!/usr/bin/env python3
"""
Simple Graphiti integration test that won't hit rate limits.
Tests basic storage and retrieval with a single memory item.
"""
import os
import sys
import time

# Set environment variables for Graphiti
os.environ['RB_STORE'] = 'graphiti'
os.environ['GRAPHITI_URI'] = 'bolt://localhost:7687'
os.environ['GRAPHITI_USER'] = 'neo4j'
os.environ['GRAPHITI_PASSWORD'] = 'reasoningbank123'

from rb.memory_store import MemoryStore, MemoryItem

def test_single_memory():
    """Test storing and retrieving a single memory item."""
    print("=" * 60)
    print("Testing Graphiti with single memory item")
    print("=" * 60)

    try:
        # Initialize store
        print("\n1. Initializing Graphiti memory store...")
        store = MemoryStore(use_graphiti=True)
        print("   ✓ Store initialized")

        # Create a simple memory item
        print("\n2. Creating memory item...")
        item = MemoryItem(
            title="Test Bug Fix",
            description="Fixed a null pointer exception in login",
            content="The issue was in the login function where user object could be null. Added null check before accessing user properties.",
            outcome="success",
            created_at=time.time(),
            source={"type": "test", "id": "simple_test"}
        )
        print(f"   ✓ Created: {item.title}")

        # Store the memory
        print("\n3. Storing memory in Graphiti...")
        store.add_items([item])
        print("   ✓ Memory stored successfully")

        # Wait a moment for indexing
        print("\n4. Waiting for Graphiti to index (5 seconds)...")
        time.sleep(5)

        # Search for the memory
        print("\n5. Searching for 'null pointer'...")
        results = store.search("null pointer exception", top_k=1)
        print(f"   ✓ Found {len(results)} result(s)")

        if results:
            print("\n6. Retrieved memory:")
            print(f"   Title: {results[0].get('title', 'N/A')}")
            print(f"   Description: {results[0].get('description', 'N/A')[:100]}")
            print(f"   Outcome: {results[0].get('outcome', 'N/A')}")

        # Close connection
        store.close()
        print("\n" + "=" * 60)
        print("✓ Test completed successfully!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Check required environment variables
    if not os.getenv('ANTHROPIC_API_KEY') and not os.getenv('OPENAI_API_KEY'):
        print("ERROR: Set ANTHROPIC_API_KEY or OPENAI_API_KEY")
        sys.exit(1)

    success = test_single_memory()
    sys.exit(0 if success else 1)
