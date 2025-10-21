# Cursor Integration Guide

How to use ReasoningBank + Graphiti memory system across all your Cursor projects.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Option 1: Shared Memory Service (Recommended)](#option-1-shared-memory-service-recommended)
- [Option 2: Copy Into Each Project](#option-2-copy-into-each-project)
- [Option 3: Cursor Rules Integration](#option-3-cursor-rules-integration)
- [Option 4: MCP Server (Future)](#option-4-mcp-server-future)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

**Goal**: Store and retrieve coding memories across all your Cursor projects using a shared knowledge graph.

**Time to setup**: 5-10 minutes per project

**Prerequisites**:
- This ReasoningBank project set up and working
- Neo4j running (if using Graphiti): `docker-compose up -d`
- Python 3.10+ in your other projects

---

## Option 1: Shared Memory Service (Recommended)

Keep this `memory-games` project as a centralized memory service. All your Cursor projects connect to the same Neo4j instance.

### Architecture

```
memory-games/
  └─ Neo4j (shared knowledge graph)
      ├─ group_id: "project-a"
      ├─ group_id: "project-b"
      └─ group_id: "project-c"

Your Cursor Projects:
  ├─ project-a/ → queries Neo4j with group_id="project-a"
  ├─ project-b/ → queries Neo4j with group_id="project-b"
  └─ project-c/ → queries Neo4j with group_id="project-c"
```

### Step 1: Start Memory Service (One Time)

In this `memory-games` project:

```bash
cd ~/Local\ Sites/memory-games

# Start Neo4j
docker-compose up -d

# Verify running
docker ps | grep rb-neo4j

# Set env vars (add to ~/.bashrc or ~/.zshrc for persistence)
export GRAPHITI_URI=bolt://localhost:7687
export GRAPHITI_USER=neo4j
export GRAPHITI_PASSWORD=reasoningbank123
```

### Step 2: Add Memory Client to Your Project

In any Cursor project:

```bash
cd ~/your-cursor-project

# Install graphiti-core
pip install graphiti-core python-dotenv

# Or add to requirements.txt:
echo "graphiti-core>=0.22.0" >> requirements.txt
echo "python-dotenv>=1.0.0" >> requirements.txt
pip install -r requirements.txt
```

Create `.cursor/memory_client.py`:

```python
"""
ReasoningBank Memory Client for Cursor Projects
Connects to shared Neo4j instance to store/retrieve coding memories.
"""
import os
import asyncio
from datetime import datetime
from pathlib import Path
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType

class ProjectMemory:
    """
    Memory client for storing and retrieving coding knowledge.

    Usage:
        memory = ProjectMemory()

        # Store a memory
        memory.remember(
            title="Fixed CORS authentication bug",
            content="Added Access-Control-Allow-Origin header in middleware/auth.py",
            outcome="success"
        )

        # Retrieve memories
        results = memory.recall("CORS authentication issues")
        for r in results:
            print(r['title'], r['content'])
    """

    def __init__(self, project_name: str = None):
        self.project_name = project_name or Path.cwd().name

        # Load from env or use defaults
        self.uri = os.getenv("GRAPHITI_URI", "bolt://localhost:7687")
        self.user = os.getenv("GRAPHITI_USER", "neo4j")
        self.password = os.getenv("GRAPHITI_PASSWORD", "reasoningbank123")

        if not self.password:
            raise ValueError(
                "GRAPHITI_PASSWORD not set. "
                "Run: export GRAPHITI_PASSWORD=reasoningbank123"
            )

        # Initialize Graphiti client
        self.graphiti = Graphiti(
            uri=self.uri,
            user=self.user,
            password=self.password
        )

        print(f"✓ Connected to memory service (project: {self.project_name})")

    def remember(self, title: str, content: str, outcome: str = "success", tags: list = None):
        """
        Store a coding memory.

        Args:
            title: Brief description (e.g., "Fixed JWT token expiration bug")
            content: Detailed explanation with file paths, solutions
            outcome: "success" or "failure"
            tags: Optional list of tags (e.g., ["authentication", "backend"])
        """
        asyncio.run(self._remember_async(title, content, outcome, tags))

    async def _remember_async(self, title: str, content: str, outcome: str, tags: list):
        episode_body = content
        if tags:
            episode_body += f"\n\nTags: {', '.join(tags)}"

        await self.graphiti.add_episode(
            name=title,
            episode_body=episode_body,
            source_description=f"Project: {self.project_name} ({outcome})",
            reference_time=datetime.now(),
            source=EpisodeType.text,
            group_id=self.project_name
        )

        print(f"✓ Memory stored: {title} ({outcome})")

    def recall(self, query: str, limit: int = 3) -> list:
        """
        Search for relevant memories.

        Args:
            query: Natural language query (e.g., "authentication errors")
            limit: Max number of results

        Returns:
            List of dicts with 'title', 'content', 'outcome'
        """
        return asyncio.run(self._recall_async(query, limit))

    async def _recall_async(self, query: str, limit: int) -> list:
        edges = await self.graphiti.search(
            query=query,
            group_ids=[self.project_name],
            num_results=limit
        )

        results = []
        for edge in edges:
            results.append({
                'title': edge.name or "Memory",
                'content': edge.fact or "",
                'outcome': "success" if edge.valid_at else "unknown",
                'created_at': edge.created_at
            })

        print(f"✓ Found {len(results)} relevant memories")
        return results

    def close(self):
        """Close connection to memory service."""
        asyncio.run(self.graphiti.close())


# Convenience functions for quick use
_default_memory = None

def get_memory():
    """Get or create default memory client."""
    global _default_memory
    if _default_memory is None:
        _default_memory = ProjectMemory()
    return _default_memory

def remember(title: str, content: str, outcome: str = "success", tags: list = None):
    """Quick function to store a memory."""
    get_memory().remember(title, content, outcome, tags)

def recall(query: str, limit: int = 3) -> list:
    """Quick function to retrieve memories."""
    return get_memory().recall(query, limit)


# CLI for testing
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python memory_client.py remember 'title' 'content' [success|failure]")
        print("  python memory_client.py recall 'query' [limit]")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "remember":
        title = sys.argv[2]
        content = sys.argv[3]
        outcome = sys.argv[4] if len(sys.argv) > 4 else "success"
        remember(title, content, outcome)

    elif cmd == "recall":
        query = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 3
        results = recall(query, limit)

        print("\n" + "="*60)
        for i, r in enumerate(results, 1):
            print(f"\n[{i}] {r['title']} ({r['outcome']})")
            print(f"    {r['content'][:200]}...")
        print("="*60)

    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
```

### Step 3: Create .env File

```bash
cat > .env << 'EOF'
# Memory Service Configuration
GRAPHITI_URI=bolt://localhost:7687
GRAPHITI_USER=neo4j
GRAPHITI_PASSWORD=reasoningbank123
EOF

# Load env vars
export $(cat .env | xargs)
```

### Step 4: Test It

```bash
# Test storing a memory
python .cursor/memory_client.py remember \
  "Fixed database connection pool exhaustion" \
  "Increased max_connections from 10 to 50 in config/db.py. Also added connection timeout of 30s." \
  "success"

# Test retrieving memories
python .cursor/memory_client.py recall "database connection issues" 3
```

### Step 5: Use in Cursor

Create `.cursor/commands/remember.md`:

````markdown
Store what we just learned in project memory.

Steps:
1. Ask user for:
   - Brief title
   - What was the problem/task?
   - What was the solution?
   - Did it work? (success/failure)

2. Store using memory client:

```python
from .cursor.memory_client import remember

remember(
    title="[title from user]",
    content="[detailed description with file paths]",
    outcome="success",  # or "failure"
    tags=["relevant", "tags"]
)
```

3. Confirm saved and show what was stored.
````

Create `.cursor/commands/recall.md`:

````markdown
Search project memory for relevant past experiences.

Steps:
1. Ask user what problem they're trying to solve

2. Search memory:

```python
from .cursor.memory_client import recall

results = recall(query="[user's problem]", limit=3)

for r in results:
    print(f"**{r['title']}** ({r['outcome']})")
    print(r['content'])
    print()
```

3. Present results and suggest how to apply learnings to current task.
````

### Step 6: Use in Code

In any Python file in your project:

```python
# At top of file
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / ".cursor"))

from memory_client import remember, recall

# Before implementing
past_solutions = recall("authentication JWT tokens")
for sol in past_solutions:
    print(f"Previous: {sol['title']}")

# After fixing
remember(
    title="Fixed JWT refresh token rotation",
    content="""
    Problem: Refresh tokens weren't rotating on use
    Solution: Added rotation logic in auth/tokens.py:145
    Files: auth/tokens.py, middleware/auth.py
    """,
    outcome="success",
    tags=["auth", "jwt", "security"]
)
```

---

## Option 2: Copy Into Each Project

If you want isolated memory per project (not shared):

### Step 1: Copy Core Files

```bash
cd ~/your-cursor-project

# Copy ReasoningBank core
mkdir -p rb
cp -r ~/Local\ Sites/memory-games/rb/* ./rb/

# Copy requirements
cp ~/Local\ Sites/memory-games/requirements.txt ./rb-requirements.txt

# Install
pip install -r rb-requirements.txt
```

### Step 2: Initialize Memory

```bash
# Create memory directory
mkdir -p memory

# Create wrapper script
cat > memory_helper.py << 'EOF'
"""Simple wrapper for ReasoningBank memory."""
from rb.memory_store import MemoryStore, MemoryItem
import time
import os

PROJECT_NAME = os.path.basename(os.getcwd())

def remember(title, content, outcome="success"):
    store = MemoryStore()  # Uses memory/memory.jsonl
    store.add_items([MemoryItem(
        title=title,
        description=f"Project: {PROJECT_NAME}",
        content=content,
        outcome=outcome,
        created_at=time.time(),
        source={"project": PROJECT_NAME}
    )])
    print(f"✓ Stored: {title}")

def recall(query, top_k=3):
    store = MemoryStore()
    results = store.search(query, top_k)
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        remember("Test memory", "Testing the system", "success")
        results = recall("test")
        print(f"Found {len(results)} memories")
EOF

# Test it
python memory_helper.py test
```

### Step 3: Add to .gitignore

```bash
echo "memory/" >> .gitignore
echo "rb/__pycache__/" >> .gitignore
```

---

## Option 3: Cursor Rules Integration

Add memory guidelines to `.cursorrules` so Cursor Composer automatically uses memory:

### Create .cursorrules

```bash
cat > .cursorrules << 'EOF'
# Project Memory System

This project uses ReasoningBank for persistent coding memory.

## Memory Location
- JSONL: `memory/memory.jsonl`
- Graphiti: Neo4j at bolt://localhost:7687 (if RB_STORE=graphiti)

## Before Implementing Features

1. **Search memory first**:
   ```python
   from memory_helper import recall
   past = recall("similar feature or bug description")
   ```

2. **Review past solutions**:
   - Check if we've solved this before
   - Learn from past failures
   - Apply proven strategies

3. **Consider tradeoffs**:
   - What worked last time?
   - What didn't work?

## After Completing Work

1. **Extract learnings** (especially from failures!)
2. **Store with details**:
   ```python
   from memory_helper import remember
   remember(
       title="Descriptive title",
       content="""
       Problem: [what was wrong]
       Solution: [what fixed it]
       Files: [which files changed]
       Gotchas: [any tricky parts]
       """,
       outcome="success"  # or "failure"
   )
   ```

3. **Include specifics**:
   - Exact file paths and line numbers
   - Error messages (full stack trace)
   - Commands that worked/failed
   - Configuration values

## Memory Best Practices

### Good Memory Titles
✓ "Fixed React infinite render loop in UserProfile component"
✓ "Database migration failed: missing foreign key constraint"
✓ "API rate limiting: added exponential backoff"

✗ "Fixed bug"
✗ "Made changes"
✗ "Updated code"

### Good Memory Content
```
Problem: Users couldn't upload files >10MB
Root Cause: Nginx client_max_body_size was 10m
Solution: Increased to 100m in /etc/nginx/nginx.conf:42
Also: Updated frontend to show better error message
Files: nginx.conf, frontend/src/components/Upload.tsx
Testing: Tested with 50MB file, works now
```

### Tag Appropriately
- Component/module names
- Technology stack (react, postgres, redis)
- Category (bugfix, feature, refactor, performance)

## Cursor Composer Integration

When working on tasks:
1. Check memory before writing code
2. Reference past solutions in comments
3. Store outcome when done
4. Build knowledge base over time

## Example Workflow

```python
# 1. Before starting
from memory_helper import recall
memories = recall("authentication errors", top_k=3)
# Review what was tried before

# 2. Implement solution
# ... your code ...

# 3. After testing
from memory_helper import remember
remember(
    title="Fixed auth token expiration handling",
    content="Added refresh token logic in auth.py:234. "
            "Tokens now refresh 5min before expiry.",
    outcome="success"
)
```

## Commands

- `/remember` - Store current work in memory
- `/recall <query>` - Search for relevant past experiences
EOF
```

### Create Cursor Commands

Create `.cursor/commands/remember.md`:

````markdown
Store what we just accomplished in project memory.

Follow these steps:

1. **Ask the user**:
   - What did we just fix/build?
   - Which files were changed?
   - Did it work or fail?
   - Any gotchas or tricky parts?

2. **Store the memory**:

```python
from memory_helper import remember

remember(
    title="[descriptive title]",
    content="""
    Problem: [what was the issue]
    Solution: [how we fixed it]
    Files: [which files, with line numbers if relevant]
    Gotchas: [any tricky parts or edge cases]
    Testing: [how we verified it works]
    """,
    outcome="success"  # or "failure" if it didn't work
)
```

3. **Confirm** what was stored and suggest when this memory might be useful in the future.

Example:
```
✓ Stored: Fixed React infinite render loop in UserProfile
  This will help when debugging similar useState/useEffect issues.
```
````

Create `.cursor/commands/recall.md`:

````markdown
Search project memory for relevant past experiences before implementing.

Steps:

1. **Ask the user** what they're trying to accomplish or what problem they're facing.

2. **Search memory**:

```python
from memory_helper import recall

results = recall(query="[user's problem/task]", top_k=5)

print("Found relevant past experiences:\n")
for i, r in enumerate(results, 1):
    print(f"{i}. **{r['title']}** ({r['outcome']})")
    print(f"   {r['content'][:150]}...")
    print()
```

3. **Analyze results**:
   - Which solutions worked?
   - Which failed and why?
   - Are there patterns?

4. **Recommend approach** based on past learnings:
   - "We tried X before and it worked"
   - "Avoid Y because it caused Z"
   - "Make sure to check W based on previous gotcha"

5. **Proceed with implementation** using insights from memory.
````

---

## Option 4: MCP Server (Future)

Graphiti supports Model Context Protocol (MCP). Future integration:

```json
// In Cursor settings.json
{
  "mcpServers": {
    "reasoning-bank": {
      "command": "python",
      "args": ["/path/to/memory-games/mcp_server.py"],
      "env": {
        "GRAPHITI_PASSWORD": "reasoningbank123"
      }
    }
  }
}
```

Then Cursor could directly query/store memories without code.

**Status**: Not yet implemented, but Graphiti has MCP support. See: https://github.com/getzep/graphiti

---

## Best Practices

### 1. Be Specific in Memories

**Bad**:
```
Title: Fixed bug
Content: Updated the code and it works now
```

**Good**:
```
Title: Fixed SQL injection vulnerability in search endpoint
Content:
Problem: User input wasn't sanitized in /api/search
Solution: Added parameterized query in controllers/search.py:67
Files: controllers/search.py, tests/test_search.py
Security: Now using SQLAlchemy's text() with bindparams
Testing: Tried ' OR 1=1--, properly escaped
```

### 2. Store Failures Too

Failures are often more valuable than successes:

```python
remember(
    title="Failed: Attempted to use Redis for session storage",
    content="""
    Problem: Wanted to scale sessions across servers
    Attempted: Switched from file-based to Redis sessions
    Failure: Redis connection kept timing out under load
    Root Cause: Our Redis instance is on slow network
    Lesson: Stick with Postgres sessions, much more reliable
    Files: config/session.py (reverted changes)
    """,
    outcome="failure"
)
```

### 3. Use Consistent Naming

- Start with verb: "Fixed", "Added", "Refactored", "Failed"
- Include component/module: "in UserAuth controller"
- Be specific: "JWT token rotation" not "auth stuff"

### 4. Tag Appropriately

```python
remember(
    title="Optimized dashboard query performance",
    content="Added index on user_id column, query time 2s → 50ms",
    outcome="success",
    tags=["performance", "database", "dashboard", "postgres"]
)
```

### 5. Review Periodically

Once a month:

```bash
# View all memories (JSONL mode)
cat memory/memory.jsonl | jq -r '.title'

# Or in Neo4j Browser (Graphiti mode)
# Open http://localhost:7474
# Run: MATCH (e:Episodic) RETURN e.name, e.source_description LIMIT 50
```

### 6. Use Group IDs

When using Graphiti with multiple projects:

```python
memory = ProjectMemory(project_name="my-web-app")  # Uses group_id="my-web-app"
memory.remember(...)
```

This keeps memories isolated per project.

---

## Troubleshooting

### "Cannot connect to Neo4j"

```bash
# Check if Neo4j is running
docker ps | grep rb-neo4j

# If not running
cd ~/Local\ Sites/memory-games
docker-compose up -d

# Check logs
docker logs rb-neo4j
```

### "GRAPHITI_PASSWORD not set"

```bash
export GRAPHITI_PASSWORD=reasoningbank123

# Or add to ~/.bashrc / ~/.zshrc:
echo 'export GRAPHITI_PASSWORD=reasoningbank123' >> ~/.bashrc
source ~/.bashrc
```

### "ModuleNotFoundError: No module named 'graphiti_core'"

```bash
pip install graphiti-core python-dotenv
```

### Memory Client Not Found in Cursor

Make sure the path is correct:

```python
import sys
from pathlib import Path

# Add .cursor directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / ".cursor"))

from memory_client import remember, recall
```

### Memories Not Showing Up

```python
# Check what's stored (JSONL)
import json
with open("memory/memory.jsonl") as f:
    for line in f:
        item = json.loads(line)
        print(item['title'])

# Check what's stored (Graphiti)
from memory_client import ProjectMemory
memory = ProjectMemory()
results = memory.recall("", limit=10)  # Get recent memories
for r in results:
    print(r['title'])
```

### Search Returns Wrong Results

TF-IDF (JSONL mode) is simple. For better search:

1. Switch to Graphiti mode:
   ```bash
   export RB_STORE=graphiti
   ```

2. Use more specific queries:
   - Bad: "bug"
   - Good: "authentication JWT token expiration"

3. Use tags consistently

---

## Example: Complete Integration for New Project

Here's a full example integrating memory into a new project:

```bash
# 1. Create new project
mkdir my-awesome-app
cd my-awesome-app
git init

# 2. Set up Python
python3 -m venv .venv
source .venv/bin/activate

# 3. Install memory dependencies
pip install graphiti-core python-dotenv

# 4. Create .cursor directory
mkdir -p .cursor

# 5. Copy memory client
curl -o .cursor/memory_client.py \
  https://raw.githubusercontent.com/your-repo/memory-games/main/cursor_memory_client.py

# 6. Create .env
cat > .env << 'EOF'
GRAPHITI_URI=bolt://localhost:7687
GRAPHITI_USER=neo4j
GRAPHITI_PASSWORD=reasoningbank123
EOF

# 7. Load env
export $(cat .env | xargs)

# 8. Test memory
python .cursor/memory_client.py remember \
  "Project initialized" \
  "Set up memory system and project structure" \
  "success"

python .cursor/memory_client.py recall "initialization"

# 9. Add to .gitignore
cat >> .gitignore << 'EOF'
.env
memory/
.cursor/__pycache__/
EOF

# 10. Create .cursorrules
# (copy content from Option 3 above)

# 11. Create Cursor commands
mkdir -p .cursor/commands
# (create remember.md and recall.md as shown above)

# 12. Start coding with memory!
```

---

## Summary

**Recommended Setup**: Option 1 (Shared Memory Service)

**Why**:
- One Neo4j instance for all projects
- Better search quality (hybrid)
- Cross-project insights
- Easy to maintain

**Quick Commands**:
```bash
# In memory-games project (run once)
docker-compose up -d

# In any Cursor project (first time setup)
pip install graphiti-core python-dotenv
# Copy .cursor/memory_client.py
# Create .env with GRAPHITI_PASSWORD

# Daily usage in Cursor
/remember  # After fixing something
/recall    # Before implementing something
```

**Files to Create**:
1. `.cursor/memory_client.py` - Core memory functions
2. `.cursor/commands/remember.md` - Store memory command
3. `.cursor/commands/recall.md` - Search memory command
4. `.cursorrules` - Auto memory guidelines
5. `.env` - Configuration

Now you have a persistent memory system across all your Cursor projects! 🧠✨
EOF
