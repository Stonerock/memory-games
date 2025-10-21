# Contributing to ReasoningBank for Code

Thank you for your interest in contributing! This project is designed to be hackable and extensible.

## 🎯 Ways to Contribute

### 🐛 Report Bugs

Found a bug? [Open an issue](../../issues/new) with:
- Clear title describing the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment (OS, Python version, backend: JSONL/Graphiti)
- Relevant logs or error messages

### 💡 Suggest Features

Have an idea? [Start a discussion](../../discussions/new) or open an issue with:
- Problem you're trying to solve
- Proposed solution
- Alternative approaches considered
- Example use case

### 📖 Improve Documentation

Documentation improvements are always welcome:
- Fix typos or clarify confusing sections
- Add missing examples
- Improve setup instructions
- Translate to other languages

### 🧪 Add Tests

Help us maintain quality:
- Add unit tests for new features
- Add integration tests for workflows
- Improve test coverage
- Add regression tests for fixed bugs

### 🔌 Build Integrations

Extend ReasoningBank:
- VS Code extension
- GitHub Actions workflow
- CLI improvements
- Web UI for memory browsing
- Other IDE integrations

## 🚀 Development Setup

### 1. Fork & Clone

```bash
git clone https://github.com/YOUR_USERNAME/reasoning-bank-cursor.git
cd reasoning-bank-cursor
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

### 3. Run Tests

```bash
# Run integration tests
python test_integration.py

# Run with pytest (if installed)
pytest test_integration.py -v
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

## 📝 Code Style

### Python

- Follow [PEP 8](https://pep8.org/)
- Use type hints where possible
- Keep functions small and focused
- Add docstrings for public functions

**Example**:

```python
def search(self, query: str, top_k: int = 1) -> List[Dict[str, Any]]:
    """
    Search memory items using hybrid retrieval.

    Args:
        query: Natural language search query
        top_k: Maximum number of results to return

    Returns:
        List of matching memory items with title, content, outcome
    """
    # Implementation...
```

### Markdown

- Use consistent heading levels
- Add code fences with language tags
- Keep lines under 120 characters (when reasonable)
- Add blank line before/after code blocks

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding/updating tests
- `chore`: Maintenance tasks

**Examples**:

```
feat(graphiti): add community detection support

Implements graph clustering to find related memory items.
Uses Louvain algorithm for community detection.

Closes #42
```

```
fix(memory_store): handle empty directory paths

JSONL mode crashed when path had no directory component.
Now checks if dirname exists before creating.

Fixes #38
```

## 🧪 Testing Guidelines

### Unit Tests

Test individual functions in isolation:

```python
def test_memory_item_creation():
    """Test MemoryItem can be created with all fields."""
    item = MemoryItem(
        title="Test",
        description="Test desc",
        content="Test content",
        outcome="success",
        created_at=time.time(),
        source={"type": "test"}
    )
    assert item.title == "Test"
    assert item.outcome == "success"
```

### Integration Tests

Test full workflows:

```python
def test_end_to_end_jsonl():
    """Test complete workflow: store, search, retrieve."""
    store = MemoryStore(path="test.jsonl")

    # Store
    store.add_items([...])

    # Search
    results = store.search("query")

    # Verify
    assert len(results) > 0
```

### Testing Checklist

Before submitting PR:
- [ ] All existing tests pass
- [ ] New tests added for new features
- [ ] Tests cover edge cases
- [ ] Tests are documented
- [ ] Integration tests pass (both JSONL and Graphiti)

## 🔄 Pull Request Process

### 1. Update Your Fork

```bash
git remote add upstream https://github.com/original-org/reasoning-bank-cursor.git
git fetch upstream
git rebase upstream/main
```

### 2. Run Tests

```bash
python test_integration.py
# All tests should pass
```

### 3. Commit Your Changes

```bash
git add .
git commit -m "feat(scope): description"
```

### 4. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 5. Open Pull Request

Go to GitHub and click "New Pull Request"

**PR Template**:

```markdown
## Description
Brief description of changes

## Motivation
Why is this change needed?

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
How did you test this?

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Commit messages follow convention
- [ ] No breaking changes (or documented)

## Related Issues
Closes #issue_number
```

### 6. Code Review

- Address feedback from reviewers
- Make requested changes
- Push updates to the same branch
- Request re-review when ready

## 🏗️ Project Structure

Understanding the codebase:

```
rb/
├── agent.py              # Core agent logic
│   ├── attempt_once()    # Run single fix attempt
│   ├── apply_patch()     # Apply git patch
│   └── extract_memory()  # Extract learnings
├── memory_store.py       # Memory backend router
│   ├── MemoryStore       # Main class
│   ├── add_items()       # Store memories
│   └── search()          # Retrieve memories
├── graphiti_client.py    # Graphiti integration
│   ├── upsert_memory_items()
│   └── search()
├── llm.py                # LLM wrapper
│   └── LLM.complete()    # Call LLM
└── prompts.py            # Prompt templates
    ├── EXTRACT_SUCCESS_PROMPT
    └── EXTRACT_FAILURE_PROMPT
```

## 🎨 Adding New Features

### Example: Add New Memory Backend

1. **Create backend client** (`rb/new_backend_client.py`):

```python
class NewBackendClient:
    def __init__(self):
        # Initialize connection
        pass

    def upsert_memory_items(self, items: List[Dict[str, Any]]):
        # Store items
        pass

    def search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        # Search items
        pass
```

2. **Update MemoryStore** (`rb/memory_store.py`):

```python
def __init__(self, path: str = "memory/memory.jsonl", use_graphiti: bool = False):
    backend = os.getenv("RB_STORE", "jsonl")

    if backend == "new_backend":
        from .new_backend_client import NewBackendClient
        self.client = NewBackendClient()
    elif backend == "graphiti":
        # Existing Graphiti code...
    else:
        # JSONL code...
```

3. **Add tests** (`test_integration.py`):

```python
def test_new_backend_mode():
    os.environ["RB_STORE"] = "new_backend"
    store = MemoryStore()
    # Test store and retrieve...
```

4. **Document** (README.md, QUICKSTART.md):

```markdown
### Option C: New Backend

Set `RB_STORE=new_backend` to use...
```

## 🐞 Debugging Tips

### Enable Verbose Logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Graphiti Locally

```bash
# Start Neo4j
docker-compose up -d

# Connect with cypher-shell
docker exec -it rb-neo4j cypher-shell -u neo4j -p reasoningbank123

# Query episodes
MATCH (e:Episodic) RETURN e.name, e.content LIMIT 10;
```

### Test LLM Calls Without API

Mock the LLM client:

```python
class MockLLM:
    def complete(self, system: str, user: str) -> str:
        return "Mock response"

llm = MockLLM()
```

## 📚 Resources

- [ReasoningBank Paper](https://arxiv.org/abs/2305.02301) (if available)
- [Graphiti Documentation](https://help.getzep.com/graphiti)
- [Neo4j Documentation](https://neo4j.com/docs/)
- [Cursor Documentation](https://docs.cursor.com)

## ❓ Questions?

- **General questions**: [Discussions](../../discussions)
- **Bug reports**: [Issues](../../issues)
- **Security issues**: Email security@your-domain.com (not public issues)

## 🎉 Recognition

Contributors will be:
- Listed in README.md
- Mentioned in release notes
- Added to CONTRIBUTORS.md (coming soon)

Thank you for contributing to ReasoningBank! 🙏
