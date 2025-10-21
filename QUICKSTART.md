# Quick Start Guide

## Choose Your Backend

### Option A: JSONL (Recommended for Getting Started)

**Pros**: No setup, fast, simple
**Cons**: Basic search quality

```bash
# 1. Create venv and install
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# 3. Run
python runner.py \
  --repo ./test_repos/buggy_add \
  --issue ./test_repos/buggy_add/ISSUE.md \
  --test-cmd "pytest -q" \
  --k 2
```

Memory will be stored in `memory/memory.jsonl`.

---

### Option B: Graphiti (Advanced - Better Search)

**Pros**: Hybrid search, entity extraction, graph relationships
**Cons**: Requires Neo4j, slower writes, uses more LLM tokens

#### Step 1: Start Neo4j

Make sure Docker Desktop is running:

```bash
docker-compose up -d

# Verify it's running
docker ps | grep rb-neo4j

# Wait ~30 seconds for startup
```

Access Neo4j Browser at http://localhost:7474 (neo4j/reasoningbank123)

#### Step 2: Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Step 3: Configure Environment

```bash
cp .env.example .env

# Edit .env and set:
# RB_STORE=graphiti
# ANTHROPIC_API_KEY=your-key-here
# GRAPHITI_PASSWORD=reasoningbank123

# Load env vars
export $(cat .env | xargs)
```

#### Step 4: Run

```bash
python runner.py \
  --repo ./test_repos/buggy_add \
  --issue ./test_repos/buggy_add/ISSUE.md \
  --test-cmd "pytest -q" \
  --k 2
```

Memory will be stored in Neo4j graph database.

---

## Testing the Integration

Run integration tests to verify everything works:

```bash
# Test JSONL mode
.venv/bin/python3 test_integration.py

# Test Graphiti mode (requires Neo4j running)
export RB_STORE=graphiti
export GRAPHITI_PASSWORD=reasoningbank123
.venv/bin/python3 test_integration.py
```

---

## Next Steps

- **Customize**: Edit `rb/prompts.py` to change extraction/refinement prompts
- **Extend**: Add new memory extraction logic in `rb/agent.py`
- **Scale**: Switch to Graphiti when you have >100 memory items
- **Visualize**: Use Neo4j Browser to explore memory graph relationships

---

## Troubleshooting

**"Cannot connect to Docker daemon"**
→ Start Docker Desktop app

**"GRAPHITI_PASSWORD not set"**
→ Run `export GRAPHITI_PASSWORD=reasoningbank123`

**"Connection refused to localhost:7687"**
→ Wait for Neo4j to fully start (30-60 seconds)

**Tests failing on search quality**
→ Normal - TF-IDF search is simple, switch to Graphiti for better results

See [GRAPHITI_SETUP.md](GRAPHITI_SETUP.md) for detailed troubleshooting.

---

## File Overview

```
├── runner.py              # Main CLI entrypoint
├── rb/
│   ├── agent.py           # Core logic (apply patches, run tests)
│   ├── memory_store.py    # Memory backend (JSONL or Graphiti)
│   ├── graphiti_client.py # Graphiti integration
│   ├── llm.py             # LLM wrapper (Anthropic/OpenAI)
│   └── prompts.py         # Extraction/refinement prompts
├── memory/memory.jsonl    # JSONL storage (default)
├── docker-compose.yml     # Neo4j setup
├── .env.example           # Environment template
└── test_integration.py    # Integration tests
```
