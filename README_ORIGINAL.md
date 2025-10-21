# ReasoningBank for Code — Starter Kit

A tiny, local-first implementation of the paper's **ReasoningBank + MaTTS** ideas, adapted for coding tasks.
You can run it inside **Cursor** or **Claude Code** with any LLM that has an API key (Anthropic Claude recommended).

## What it does

- Runs a *simple code-fixing loop* on a local repo with tests (e.g., `pytest -q`).
- Stores distilled **memory items** (title, description, content, outcome) in `memory/memory.jsonl`.
- Retrieves the top-1 relevant memory item for the next task (BM25/Tf‑idf lexical; simple and local).
- Labels each attempt **success/failure** via the test command; if no tests, uses an LLM judge.
- Extracts **new memory items** from successes *and* failures via prompts adapted from the paper.
- Optional: **MaTTS-lite**
  - **Parallel (k)**: run N short attempts on branches and pick the best patch (best-of-N).
  - **Sequential (r)**: run r self-refine passes on a single attempt.

> Note: This is minimal on purpose so you can read the code and tinker.

## Quickstart

```bash
# 1) Create a fresh virtualenv
python -m venv .venv && source .venv/bin/activate

# 2) Install deps
pip install -r requirements.txt

# 3) Set your API (choose one)
export ANTHROPIC_API_KEY=sk-ant-...   # recommended
# or
export OPENAI_API_KEY=sk-proj-...

# 4) Try the included tiny buggy repo
python runner.py --repo ./test_repos/buggy_add --issue ./test_repos/buggy_add/ISSUE.md --test-cmd "pytest -q" --k 2
```

- The script will create branches `rb-attempt-1`, `rb-attempt-2`, apply suggested patches, run tests, pick the best, and write memory.
- Re‑run with different issues; the agent will reuse **memory** automatically.

## Use in Cursor or Claude Code

- Open this folder as a workspace.
- Open a terminal inside the editor and run the *Quickstart* commands.
- Memory is persisted under `memory/`. You can inspect and edit items while you iterate.

## Swap in Graphiti (optional, advanced)

This kit uses a JSONL store by default. **Graphiti integration is now fully implemented!**

To use Graphiti instead:
1. Start Neo4j: `docker-compose up -d`
2. Set environment variables:
   ```bash
   export RB_STORE=graphiti
   export GRAPHITI_PASSWORD=reasoningbank123
   ```
3. Run as normal - memory will be stored in Neo4j with hybrid search

See [GRAPHITI_SETUP.md](GRAPHITI_SETUP.md) for detailed instructions.

## Project layout

```
rb/                     # core logic
  agent.py              # run attempts, apply patches, run tests
  llm.py                # provider-agnostic LLM wrapper (Anthropic/OpenAI)
  memory_store.py       # JSONL store + lexical retrieval (top-1)
  prompts.py            # judge / extract / parallel-contrast / sequential-refine prompts
  graphiti_client.py    # optional Graphiti integration stub

runner.py               # CLI
requirements.txt
memory/memory.jsonl     # append-only memory
test_repos/buggy_add    # tiny sample repo with a failing test
```

## Safety & notes

- Running arbitrary patch suggestions on your machine can be risky. Use a throwaway repo and read the patch before applying.
- The patch application uses `git apply` and creates attempt branches. You can inspect diffs with normal Git tooling.
- Retrieval is purposely simple (tf‑idf). For better results, replace with embeddings or Graphiti later.

Have fun, and PRs welcome!
