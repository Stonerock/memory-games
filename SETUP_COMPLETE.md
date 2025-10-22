# ReasoningBank Setup Complete! ✅

Your ReasoningBank memory service with Graphiti integration is now fully operational.

## What Was Set Up

### 1. Graphiti Integration
- ✅ **GraphitiClient** (`rb/graphiti_client.py`) - Full integration with Graphiti knowledge graph
- ✅ **Neo4j Database** - Running in Docker on ports 7474 (HTTP) and 7687 (Bolt)
- ✅ **OpenAI API** - Using ChatGPT for LLM and embeddings
- ✅ **Async Event Loop Handling** - Fixed with `nest_asyncio` for smooth operation

### 2. Memory Storage
- ✅ **Dual Backend Support**:
  - **JSONL Mode**: Simple TF-IDF search (no external dependencies)
  - **Graphiti Mode**: Semantic + keyword + graph hybrid search
- ✅ **Automatic Entity Extraction** - Graphiti extracts entities and relationships
- ✅ **Temporal Knowledge Graph** - Memories are stored with timestamps and relationships

### 3. Testing
- ✅ Integration tests passing
- ✅ Memory storage working
- ✅ Semantic search working
- ✅ Entity extraction working

### 4. GitHub Repository
- ✅ Pushed to: https://github.com/Stonerock/memory-games
- ✅ Complete documentation included
- ✅ CI/CD pipeline configured
- ✅ Issue templates ready

---

## Quick Start

### Using with OpenAI (ChatGPT)

```bash
# 1. Start Neo4j
docker-compose up -d

# 2. Set environment variables
export RB_STORE=graphiti
export GRAPHITI_PASSWORD=reasoningbank123
export OPENAI_API_KEY=your-openai-key-here

# 3. Test it
python test_graphiti_simple.py
```

### Load from .env.local

```bash
# Load all environment variables
export $(cat .env.local | xargs)

# Now run your code
python runner.py --repo ./your-project --issue ./ISSUE.md
```

---

## Configuration Files

### .env.local
```bash
RB_STORE=graphiti
GRAPHITI_URI=bolt://localhost:7687
GRAPHITI_USER=neo4j
GRAPHITI_PASSWORD=reasoningbank123
OPENAI_API_KEY=sk-proj-...
```

### Docker Services
- **Neo4j Browser**: http://localhost:7474
- **Neo4j Bolt**: bolt://localhost:7687
- **Username**: neo4j
- **Password**: reasoningbank123

---

## How It Works

### 1. Storing Memories

When you store a memory:
```python
from rb.memory_store import MemoryStore, MemoryItem

store = MemoryStore(use_graphiti=True)

memory = MemoryItem(
    title="Fixed null pointer bug",
    description="Fixed crash in login function",
    content="Added null check before accessing user.email",
    outcome="success",
    created_at=time.time(),
    source={"type": "bug_fix", "issue": "#123"}
)

store.add_items([memory])
```

**What happens:**
1. GraphitiClient sends episode to Graphiti
2. Graphiti uses OpenAI to extract entities (e.g., "login function", "user.email", "null check")
3. Creates graph relationships between entities
4. Generates embeddings for semantic search
5. Stores in Neo4j with timestamps

### 2. Searching Memories

```python
results = store.search("null pointer exception", top_k=3)
```

**Hybrid search combines:**
- **Semantic**: Cosine similarity on embeddings
- **Keyword**: BM25 full-text search
- **Graph**: Relationships between entities

### 3. Retrieved Memory Format

```python
{
    "title": "FIXED",
    "description": "The login function fixed a null pointer exception.",
    "content": "The login function fixed a null pointer exception.",
    "outcome": "success",
    "created_at": 1234567890.0,
    "source": {"type": "graphiti", "uuid": "abc-123"}
}
```

---

## Cursor IDE Integration

### Option 1: Global MCP Server (Recommended)

Add to `~/.config/cursor/config/cursor-ai/config.json`:

```json
{
  "mcpServers": {
    "reasoning-bank": {
      "command": "python",
      "args": ["/Users/markus.karikivi/Local Sites/memory-games/runner.py", "--mcp"],
      "env": {
        "RB_STORE": "graphiti",
        "GRAPHITI_PASSWORD": "reasoningbank123",
        "OPENAI_API_KEY": "your-key-here"
      }
    }
  }
}
```

Now use these commands in ANY Cursor project:
- `/remember <text>` - Store a memory
- `/recall <query>` - Search memories

### Option 2: Custom Slash Commands

Create `.cursor/commands/remember.md`:
```markdown
# Remember

Store this solution in ReasoningBank:
{user_input}

Run:
python /Users/markus.karikivi/Local Sites/memory-games/runner.py \
  --remember "{user_input}" \
  --outcome success
```

---

## Next Steps

### 1. Test on Real Project

```bash
cd ~/your-real-project

# Create an issue file
echo "Bug: Users can't log in" > ISSUE.md

# Run ReasoningBank
python ~/Local\ Sites/memory-games/runner.py \
  --repo . \
  --issue ISSUE.md \
  --test-cmd "pytest"
```

### 2. Integrate with Cursor

Follow the Cursor integration guide:
- See [CURSOR_INTEGRATION_GUIDE.md](CURSOR_INTEGRATION_GUIDE.md)

### 3. Share with Team

Your repo is ready at: https://github.com/Stonerock/memory-games

Team members can:
1. Clone the repo
2. Start Neo4j: `docker-compose up -d`
3. Set their own `OPENAI_API_KEY`
4. Use across all their projects

---

## Troubleshooting

### Neo4j Not Running

```bash
# Check status
docker ps

# Start if stopped
docker-compose up -d

# Check logs
docker logs rb-neo4j
```

### "Rate limit exceeded"

OpenAI has much higher rate limits than Anthropic. If you still hit limits:
- Wait a minute between operations
- Upgrade your OpenAI tier
- Use batch operations sparingly

### Event Loop Errors

Already fixed with `nest_asyncio` package. If you see them:
```bash
pip install nest-asyncio
```

### Search Returns No Results

Graphiti needs time to index:
```python
store.add_items([memory])
time.sleep(5)  # Wait for indexing
results = store.search("query")
```

---

## Architecture

```
┌─────────────────────────────────────────────────┐
│  Your Application (Cursor, CLI, Scripts)       │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
        ┌─────────────────┐
        │  MemoryStore    │
        │  (rb/memory_store.py)
        └────────┬────────┘
                 │
         ┌───────┴────────┐
         │                │
         ▼                ▼
    ┌────────┐     ┌──────────────┐
    │ JSONL  │     │ GraphitiClient│
    │(simple)│     │   (semantic)  │
    └────────┘     └───────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   Graphiti   │
                    │  (graphiti_core)
                    └──────┬───────┘
                           │
                  ┌────────┴────────┐
                  │                 │
                  ▼                 ▼
            ┌─────────┐      ┌──────────┐
            │  Neo4j  │      │  OpenAI  │
            │(storage)│      │(LLM+embed)│
            └─────────┘      └──────────┘
```

---

## What's Different from Standard RAG

Traditional RAG (Retrieval-Augmented Generation):
- Stores text chunks with embeddings
- Retrieves similar chunks
- No understanding of relationships

ReasoningBank with Graphiti:
- ✅ **Extracts entities** (functions, variables, concepts)
- ✅ **Maps relationships** (A calls B, X fixes Y)
- ✅ **Tracks time** (when was this learned?)
- ✅ **Learns outcomes** (success/failure)
- ✅ **Hybrid search** (semantic + keyword + graph)

Example:
```
Query: "null pointer in login"

Standard RAG finds:
- Text chunks mentioning "null pointer" and "login"

Graphiti finds:
- The specific bug fix
- Related functions that call login()
- Other null pointer fixes (graph pattern)
- Temporal context (recent similar issues)
```

---

## Key Files

- `rb/graphiti_client.py` - Graphiti integration layer
- `rb/memory_store.py` - Unified storage interface
- `rb/agent.py` - AI agent with memory
- `rb/prompts.py` - Agent prompts
- `runner.py` - CLI entry point
- `test_graphiti_simple.py` - Simple test
- `test_integration.py` - Full integration tests
- `.env.local` - Your configuration (not in git)
- `docker-compose.yml` - Neo4j setup

---

## Success! 🎉

Your ReasoningBank is ready to use. It will:
- ✅ Remember successful solutions across projects
- ✅ Learn from failures
- ✅ Retrieve relevant memories semantically
- ✅ Extract entities and relationships automatically
- ✅ Work with ChatGPT (OpenAI)
- ✅ Run in Cursor IDE

**Try it out:**
```bash
# Load environment
export $(cat .env.local | xargs)

# Test search
python test_graphiti_simple.py
```

---

## Questions?

- 📖 See [README.md](README.md) for full documentation
- 🚀 See [QUICKSTART.md](QUICKSTART.md) for 5-minute setup
- 🔧 See [GRAPHITI_SETUP.md](GRAPHITI_SETUP.md) for Neo4j details
- 💡 See [CURSOR_INTEGRATION_GUIDE.md](CURSOR_INTEGRATION_GUIDE.md) for Cursor setup
- 🐛 Open an issue on GitHub

**Happy coding with ReasoningBank! 🚀**
