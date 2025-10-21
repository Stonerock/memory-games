# Prompts adapted for code tasks (paraphrased from the paper's Appendix A).

JUDGE_PROMPT = """You are an expert CI judge. Decide if the agent *resolved the issue*.
You receive (a) the issue text, (b) a trajectory summary (what the agent tried), and (c) the final repo state summary.

Output exactly two lines:
Thoughts: <brief reasoning>
Status: success or failure
"""

EXTRACT_SUCCESS_PROMPT = """You are an expert code maintainer. From this **successful** attempt,
distill up to 3 short **memory items** that will help with future, similar issues.

Rules:
- Focus on *generalizable strategies*, not repo-specific strings.
- Avoid redundancy; be concise and actionable.
- Each item must have Title, one-line Description, and Content (1–3 sentences).

Format strictly:

# Memory Item i
## Title <concise title>
## Description <one sentence>
## Content <1–3 sentences>
"""

EXTRACT_FAILURE_PROMPT = """You are an expert code maintainer. From this **failed** attempt,
distill up to 3 short **memory items** on *what to avoid* and *how to recover next time*.

Rules:
- Reflect on *why* it failed (bad test strategy, misreading traceback, wrong file, etc.).
- Convert mistakes into preventative heuristics.
- Avoid repo-specific strings; keep it general.
- Each item must have Title, one-line Description, and Content (1–3 sentences).

Format strictly:

# Memory Item i
## Title <concise title>
## Description <one sentence>
## Content <1–3 sentences>
"""

PARALLEL_CONTRAST_PROMPT = """You are comparing multiple code-fix trajectories that attempted the same issue.
Identify *generalizable* strategies that consistently helped and anti-patterns that hurt. Produce at most 5 memory items.
Follow the same format as extraction prompts and avoid redundancy.
"""

SEQUENTIAL_REFINE_INSTRUCTION_1 = """First-time check: carefully re-examine your previous reasoning and patch.
Verify: (1) failing tests addressed? (2) correct file/function? (3) any linting/syntax issues? If incorrect, propose a corrected patch.
Always return a *unified diff* patch if any change is needed.
"""

SEQUENTIAL_REFINE_INSTRUCTION_2 = """Follow-up check: one more sweep for consistency and side effects.
If everything is correct, say 'NO_PATCH_NEEDED'. Otherwise, output a unified diff patch that fixes the remaining issues.
"""

# System guidance used when building messages
SYSTEM_MEMORY_HEADER = """You have access to a small ReasoningBank of distilled strategies from prior attempts.
Before acting, briefly state whether each retrieved item is relevant to this issue, then continue.
"""
