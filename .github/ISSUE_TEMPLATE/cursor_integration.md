---
name: Cursor Integration Issue
about: Report issues with Cursor IDE integration
title: '[CURSOR] '
labels: cursor, integration
assignees: ''
---

## Issue Description

Describe the problem with Cursor integration.

## Cursor Version

- **Cursor Version**: [e.g., 0.40.0]
- **OS**: [e.g., macOS 14.0]

## Integration Type

- [ ] Memory client (`.cursor/memory_client.py`)
- [ ] Slash commands (`/remember`, `/recall`)
- [ ] `.cursorrules` configuration
- [ ] Other: ___________

## What You're Trying to Do

Describe what you're attempting in Cursor.

**Example**: "I'm trying to use `/remember` to store a memory after fixing a bug."

## What Happens

Describe the actual behavior.

**Example**: "The command runs but shows 'Module not found: memory_client'"

## Steps to Reproduce

1. Open Cursor in project: `...`
2. Run command: `/remember ...`
3. See error: `...`

## Configuration

```bash
# Your .env contents (redact API keys)
GRAPHITI_PASSWORD=...
```

```python
# Relevant code from .cursor/memory_client.py
```

## Expected Behavior

What should happen?

## Logs/Screenshots

Attach Cursor console output or screenshots if applicable.

## Have You Tried

- [ ] Restarting Cursor
- [ ] Checking file paths are correct
- [ ] Verifying Neo4j is running (if using Graphiti)
- [ ] Testing the memory client directly (`python .cursor/memory_client.py`)
