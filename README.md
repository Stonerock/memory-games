# ReasoningBank for Code — Cursor Edition 🧠✨

> A local-first AI coding agent with persistent memory. Learn from successes AND failures. Use JSONL for simplicity or Graphiti for semantic knowledge graphs.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tested with Cursor](https://img.shields.io/badge/tested%20with-Cursor-purple.svg)](https://cursor.com)

---

## 🎯 What Is This?

A **minimal, hackable implementation** of ReasoningBank + MaTTS for coding tasks. Think of it as giving your AI coding assistant a **persistent memory** that learns from every bug fix, successful feature, and failed attempt.

### Key Features

✅ **Persistent Memory**: Store coding knowledge across sessions
✅ **Dual Backend**: Simple JSONL or semantic Graphiti
✅ **Learn from Failures**: Distills anti-patterns from failed attempts
✅ **Best-of-N**: Run parallel attempts, pick the best
✅ **Self-Refine**: Iteratively improve solutions
✅ **Cursor Integration**: Ready-to-use commands for Cursor IDE
✅ **Local-First**: All data stays on your machine

---

## 🚀 Quick Start (3 minutes)

### Prerequisites

- Python 3.10+
- Git
- Docker (optional, for Graphiti/Neo4j)
- API Key: Anthropic (recommended) or OpenAI

### Option A: JSONL Mode (No Setup)

```bash
# 1. Clone
git clone https://github.com/your-org/reasoning-bank-cursor.git
cd reasoning-bank-cursor

# 2. Install
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure
export ANTHROPIC_API_KEY=sk-ant-...

# 4. Run on test repo
python runner.py \
  --repo ./test_repos/buggy_add \
  --issue ./test_repos/buggy_add/ISSUE.md \
  --test-cmd "pytest -q" \
  --k 2

# 5. Check memory
cat memory/memory.jsonl | jq -r '.title'
```

**Memory stored in**: `memory/memory.jsonl`
**Search method**: TF-IDF (lexical)

### Option B: Graphiti Mode (Better Search)

```bash
# 1. Start Neo4j
docker-compose up -d

# 2. Configure
cp .env.example .env
# Edit .env: set ANTHROPIC_API_KEY and RB_STORE=graphiti

# 3. Load env
export $(cat .env | xargs)

# 4. Run
python runner.py \
  --repo ./test_repos/buggy_add \
  --issue ./test_repos/buggy_add/ISSUE.md \
  --test-cmd "pytest -q" \
  --k 2

# 5. View memory in Neo4j Browser
open http://localhost:7474  # neo4j / reasoningbank123
```

**Memory stored in**: Neo4j graph at `bolt://localhost:7687`
**Search method**: Hybrid (semantic + keyword + graph)

---

## 📖 How It Works

```
┌─────────────────────────────────────────────────────┐
│  1. Issue: "Fix add() function for negative numbers" │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  2. Search Memory: "negative number handling bugs"  │
│     → Found: "Always check sign bit edge cases"     │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  3. Generate Patch (with memory context)            │
│     → Apply patch via git                           │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  4. Run Tests: pytest -q                            │
│     → Success or Failure                            │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  5. Extract & Store Memory                          │
│     Success: "Pattern for handling negative inputs" │
│     Failure: "Avoid: casting before sign check"     │
└─────────────────────────────────────────────────────┘
```

---

## 🎮 Usage Examples

### Basic: Fix a Bug

```bash
python runner.py \
  --repo ./my-project \
  --issue "Fix null pointer in UserAuth.login()" \
  --test-cmd "npm test"
```

### Advanced: Best-of-N with Self-Refine

```bash
python runner.py \
  --repo ./my-project \
  --issue ./issues/bug-123.md \
  --test-cmd "pytest tests/auth/" \
  --k 5 \           # Try 5 parallel solutions
  --refine 2        # Refine each solution twice
```

### With Custom Model

```bash
export RB_MODEL=claude-3-opus-20240229
python runner.py --repo ./my-project --issue "..." --test-cmd "..."
```

---

## 🔌 Cursor Integration

Turn this into a **persistent memory system** for ALL your Cursor projects!

### Step 1: Set Up Memory Service

```bash
# In this repo
docker-compose up -d
export RB_STORE=graphiti
export GRAPHITI_PASSWORD=reasoningbank123
```

### Step 2: Add to Your Cursor Projects

In any Cursor project:

```bash
# Install client
pip install graphiti-core python-dotenv

# Copy memory client
curl -o .cursor/memory_client.py \
  https://raw.githubusercontent.com/your-org/reasoning-bank-cursor/main/.cursor/memory_client.py

# Configure
echo "GRAPHITI_PASSWORD=reasoningbank123" > .env
```

### Step 3: Use in Cursor

Create `.cursor/commands/remember.md`:

````markdown
Store what we just learned.

```python
from .cursor.memory_client import remember

remember(
    title="Fixed JWT token refresh bug",
    content="Added rotation logic in auth/tokens.py:145",
    outcome="success",
    tags=["auth", "jwt"]
)
```
````

Create `.cursor/commands/recall.md`:

````markdown
Search project memory before implementing.

```python
from .cursor.memory_client import recall

results = recall("authentication errors", limit=3)
for r in results:
    print(f"{r['title']}: {r['content']}")
```
````

**Full guide**: [CURSOR_INTEGRATION_GUIDE.md](CURSOR_INTEGRATION_GUIDE.md)

---

## 📂 Project Structure

```
reasoning-bank-cursor/
├── rb/                          # Core logic
│   ├── agent.py                 # Patch generation, test execution
│   ├── memory_store.py          # Memory backend (JSONL/Graphiti)
│   ├── graphiti_client.py       # Graphiti integration
│   ├── llm.py                   # LLM wrapper (Anthropic/OpenAI)
│   └── prompts.py               # Extraction/refinement prompts
├── runner.py                    # CLI entrypoint
├── docker-compose.yml           # Neo4j for Graphiti
├── test_integration.py          # Integration tests
├── .cursor/                     # Cursor IDE integration
│   └── memory_client.py         # Reusable memory client
├── test_repos/                  # Example repos
│   └── buggy_add/               # Sample buggy code
└── memory/                      # JSONL memory storage (default)
```

---

## 🛠️ Configuration

### Environment Variables

```bash
# LLM Provider (choose one)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...

# Model (optional)
RB_MODEL=claude-3-5-sonnet-latest  # or gpt-4o

# Memory Backend (optional)
RB_STORE=graphiti  # or leave unset for JSONL

# Graphiti (only if RB_STORE=graphiti)
GRAPHITI_URI=bolt://localhost:7687
GRAPHITI_USER=neo4j
GRAPHITI_PASSWORD=reasoningbank123
```

### CLI Options

```bash
python runner.py --help

Options:
  --repo PATH          Path to git repository
  --issue PATH         Issue description (file or string)
  --test-cmd CMD       Command to run tests (e.g., "pytest -q")
  --k INT              Parallel attempts (best-of-N) [default: 1]
  --refine INT         Self-refine rounds per attempt [default: 0]
```

---

## 🧪 Testing

Run integration tests:

```bash
# Test both JSONL and Graphiti modes
python -m pytest test_integration.py -v

# Or run directly
python test_integration.py
```

Expected output:
```
============================================================
ReasoningBank Memory Integration Tests
============================================================
Testing JSONL mode...
✓ JSONL mode: Added 2 items, search returned 1 results

⊘ Graphiti mode: Skipped (RB_STORE != graphiti)

============================================================
Test Summary:
  JSONL           ✓ PASSED
  Graphiti        ✓ PASSED
============================================================
```

---

## 📊 JSONL vs Graphiti Comparison

| Feature | JSONL | Graphiti |
|---------|-------|----------|
| **Setup** | None | Docker + Neo4j |
| **Search Quality** | Basic (TF-IDF) | Advanced (hybrid) |
| **Entity Extraction** | None | Automatic |
| **Relationships** | None | Graph-based |
| **Scalability** | <1K items | 100K+ items |
| **Speed** | Fast writes | Slower (LLM calls) |
| **Cost** | Free | LLM tokens for extraction |
| **Best For** | Getting started | Production use |

**Recommendation**: Start with JSONL, switch to Graphiti when you have >100 memories.

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Quick ways to contribute:
- 🐛 Report bugs via [Issues](../../issues)
- 💡 Suggest features via [Discussions](../../discussions)
- 📖 Improve documentation
- 🧪 Add tests
- 🔌 Create integrations (VS Code, other IDEs)

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** — Fast setup guide
- **[GRAPHITI_SETUP.md](GRAPHITI_SETUP.md)** — Detailed Graphiti setup
- **[CURSOR_INTEGRATION_GUIDE.md](CURSOR_INTEGRATION_GUIDE.md)** — Use across Cursor projects
- **[INTEGRATION_SUMMARY.md](INTEGRATION_SUMMARY.md)** — Technical implementation details

---

## 🔧 Troubleshooting

### "Cannot connect to Docker daemon"

→ Start Docker Desktop

### "GRAPHITI_PASSWORD not set"

→ `export GRAPHITI_PASSWORD=reasoningbank123`

### "Tests failing"

→ Make sure pytest is installed: `pip install pytest`

### "Search returns poor results"

→ Switch to Graphiti mode for better search: `export RB_STORE=graphiti`

**Full troubleshooting**: [GRAPHITI_SETUP.md#troubleshooting](GRAPHITI_SETUP.md#troubleshooting)

---

## 🎓 Learn More

### Research Background

This implementation is inspired by:
- **ReasoningBank**: Distilling reasoning strategies into reusable memory
- **MaTTS**: Multi-attempt Tree Search for code generation

**Key differences from paper**:
- Simplified for practicality (TF-IDF instead of dense retrieval by default)
- Added Graphiti for production-grade semantic search
- Cursor IDE integration for daily development workflow
- Git-based patch application (safer than direct file edits)

### Use Cases

✅ **Bug Fixing**: Learn from past bugs, avoid repeat mistakes
✅ **Refactoring**: Remember successful refactoring patterns
✅ **Code Reviews**: Store common review comments as memory
✅ **Onboarding**: Build institutional knowledge base
✅ **Feature Development**: Reuse proven implementation strategies

---

## 📜 License

Apache 2.0 — see [LICENSE](LICENSE)

---

## 🙏 Acknowledgments

- **ReasoningBank Paper** — Original research
- **Graphiti** — Temporal knowledge graph by [Zep Software](https://github.com/getzep/graphiti)
- **Cursor** — AI-first code editor
- **Neo4j** — Graph database platform

---

## 🌟 Star History

If you find this useful, consider giving it a star! ⭐

---

## 💬 Community

- **Issues**: [Report bugs or request features](../../issues)
- **Discussions**: [Ask questions or share ideas](../../discussions)
- **Twitter**: Share your use cases with `#ReasoningBank`

---

## 🚦 Status

- ✅ Core implementation complete
- ✅ JSONL backend stable
- ✅ Graphiti integration production-ready
- ✅ Cursor commands tested
- 🚧 MCP server integration (planned)
- 🚧 VS Code extension (planned)
- 🚧 Web UI for memory exploration (planned)

---

## 📸 Screenshots

### Memory Stored in Neo4j Browser
<img width="800" alt="Neo4j memory graph" src="https://via.placeholder.com/800x400?text=Add+Screenshot+Here">

### Cursor Commands in Action
<img width="800" alt="Cursor /remember command" src="https://via.placeholder.com/800x400?text=Add+Screenshot+Here">

---

Made with ❤️ for developers who value learning from experience.

**Quick Links**: [Install](#-quick-start-3-minutes) | [Cursor Integration](#-cursor-integration) | [Docs](QUICKSTART.md) | [Contribute](CONTRIBUTING.md)
