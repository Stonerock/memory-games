# Graphiti Integration Setup

## Overview

This ReasoningBank implementation now supports **Graphiti** as an optional memory backend. Graphiti provides:
- Semantic + hybrid search (better than TF-IDF)
- Temporal knowledge graphs
- Automatic entity/relationship extraction
- Graph-based memory retrieval

## Quick Start

### Option 1: Use JSONL (Default - No Setup Required)

By default, the system uses a simple JSONL file for memory storage:

```bash
python runner.py --repo ./test_repos/buggy_add --issue ./test_repos/buggy_add/ISSUE.md --test-cmd "pytest -q" --k 2
```

### Option 2: Use Graphiti (Requires Neo4j)

#### 1. Start Neo4j Database

Make sure Docker Desktop is running, then:

```bash
# Start Neo4j container
docker-compose up -d

# Check if it's running
docker ps | grep rb-neo4j

# Wait for Neo4j to be ready (~30 seconds)
# Access Neo4j Browser at: http://localhost:7474
# Username: neo4j
# Password: reasoningbank123
```

#### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and set:
RB_STORE=graphiti
ANTHROPIC_API_KEY=your-key-here  # or OPENAI_API_KEY
```

#### 3. Run with Graphiti

```bash
source .venv/bin/activate
export $(cat .env | xargs)

python runner.py --repo ./test_repos/buggy_add --issue ./test_repos/buggy_add/ISSUE.md --test-cmd "pytest -q" --k 2
```

## How It Works

### JSONL Mode (Default)
- Memory items stored in `memory/memory.jsonl`
- Retrieval uses TF-IDF (lexical matching)
- Fast, simple, no dependencies

### Graphiti Mode
- Memory items stored as "episodes" in Neo4j graph
- Retrieval uses hybrid search (semantic + keyword + graph)
- Entities and relationships automatically extracted
- Better for complex reasoning patterns

### Memory Item Mapping

ReasoningBank MemoryItem → Graphiti Episode:
- `title` → Episode name
- `description` + `content` → Episode body
- `outcome` (success/failure) → Source description metadata
- `created_at` → Reference time

## Stopping/Cleaning Up

```bash
# Stop Neo4j
docker-compose down

# Remove data (clean slate)
docker-compose down -v
```

## Troubleshooting

**Docker not running:**
```
Cannot connect to the Docker daemon...
```
→ Start Docker Desktop application

**Connection refused:**
```
Failed to establish connection to ...
```
→ Wait longer for Neo4j to start (check `docker logs rb-neo4j`)

**GRAPHITI_PASSWORD not set:**
```
Set GRAPHITI_PASSWORD to use GraphitiClient
```
→ Make sure `.env` file exists and is loaded (`export $(cat .env | xargs)`)

## Architecture

```
MemoryStore (rb/memory_store.py)
    ├─→ JSONL Backend (default)
    │   └─→ memory/memory.jsonl
    │
    └─→ Graphiti Backend (optional)
        └─→ GraphitiClient (rb/graphiti_client.py)
            └─→ Neo4j Graph Database
                └─→ Episodes, Entities, Edges
```

## Performance Notes

- **JSONL**: Fast for <1000 items, simple lexical search
- **Graphiti**: Slower writes, better retrieval quality, scales to 100K+ items
- **Recommendation**: Start with JSONL, switch to Graphiti when you need better search

## Future Enhancements

- [ ] Support for FalkorDB (lightweight alternative to Neo4j)
- [ ] Community detection for related memory clusters
- [ ] Temporal queries (e.g., "memories from last week")
- [ ] Graph visualization of memory relationships
