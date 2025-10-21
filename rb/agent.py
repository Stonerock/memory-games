import os, subprocess, tempfile, time, json, re, shutil
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from unidiff import PatchSet

from .llm import LLM
from .memory_store import MemoryStore, MemoryItem
from . import prompts

def run(cmd: str, cwd: Optional[str] = None, timeout: int = 600) -> Tuple[int, str]:
    p = subprocess.Popen(cmd, cwd=cwd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        out, _ = p.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        p.kill()
        return 124, f"TIMEOUT running: {cmd}"
    return p.returncode, out

def ensure_git(repo: str):
    code, _ = run("git rev-parse --is-inside-work-tree", cwd=repo)
    if code != 0:
        raise RuntimeError(f"{repo} is not a git repository. Run 'git init && git add . && git commit -m init' first.")

def new_branch(repo: str, name: str):
    run(f"git checkout -B {name}", cwd=repo)

def get_diff(repo: str) -> str:
    code, out = run("git diff", cwd=repo)
    return out

def apply_patch(repo: str, patch_text: str) -> Tuple[bool, str]:
    if "NO_PATCH_NEEDED" in patch_text:
        return True, "No patch needed."
    # Write patch to temp and apply
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".patch") as f:
        f.write(patch_text)
        patch_path = f.name
    code, out = run(f"git apply --reject --whitespace=nowarn {patch_path}", cwd=repo)
    os.unlink(patch_path)
    return code == 0, out

def summarize_repo_state(repo: str) -> str:
    code, out = run("git status --porcelain", cwd=repo)
    status = out.strip()
    code, out = run("git log -1 --oneline", cwd=repo)
    last = out.strip()
    return f"STATUS:\n{status}\n\nLAST COMMIT:\n{last}"

def build_system(retrieved: List[Dict]) -> str:
    header = prompts.SYSTEM_MEMORY_HEADER
    mem_block = ""
    for i, m in enumerate(retrieved, 1):
        mem_block += f"\n[Memory {i}] {m.get('title','').strip()}\n{m.get('content','').strip()}\n"
    return header + ("\nRetrieved:\n" + mem_block if mem_block else "\n(No relevant memory retrieved.)")

def build_user(issue_text: str, repo_state: str, test_cmd: str) -> str:
    return f"""Issue:\n{issue_text.strip()}\n\nRepo summary:\n{repo_state}\n\nTask:\nPropose a minimal code patch (unified diff) that resolves the issue and makes tests pass.\n- Only output the patch, nothing else.\n- If the repo needs additional tests or small refactors, include them.\n- Keep changes focused.\n"""

def extract_patch(text: str) -> str:
    # Accept raw unified diff or code fence containing it.
    m = re.search(r"```(?:diff|patch)?\n(.*?)\n```", text, re.DOTALL)
    patch = m.group(1).strip() if m else text.strip()
    # Validate basic unified diff markers
    if "--- " in patch and "+++ " in patch and "@@ " in patch:
        return patch
    return patch  # let git apply validate

def label_success_from_tests(repo: str, test_cmd: str, timeout: int = 600) -> Tuple[bool, str]:
    code, out = run(test_cmd, cwd=repo, timeout=timeout)
    return code == 0, out

def judge_with_llm(llm: LLM, issue: str, traj: str, repo_summary: str) -> Tuple[bool, str]:
    user = f"Issue:\n{issue}\n\nTrajectory:\n{traj}\n\nFinal repo summary:\n{repo_summary}"
    out = llm.complete(system="You are a strict CI judge.", user=prompts.JUDGE_PROMPT + "\n\n" + user)
    status_line = [ln for ln in out.splitlines() if ln.lower().startswith("status:")]
    status = status_line[0].split(":",1)[1].strip().lower() if status_line else "failure"
    return status == "success", out

def extract_memory(llm: LLM, issue: str, traj: str, outcome: str) -> List[MemoryItem]:
    prompt = prompts.EXTRACT_SUCCESS_PROMPT if outcome == "success" else prompts.EXTRACT_FAILURE_PROMPT
    out = llm.complete(system="Distill reusable coding strategies as memory.", user=prompt + f"\n\nIssue:\n{issue}\n\nTrajectory:\n{traj}")
    items = []
    blocks = re.split(r"(?m)^# Memory Item .*?$", out)
    # naive parse: look for Title/Description/Content
    for blk in blocks:
        t = re.search(r"##\s*Title\s*(.+)", blk)
        d = re.search(r"##\s*Description\s*(.+)", blk)
        c = re.search(r"##\s*Content\s*(.+)", blk, re.DOTALL)
        if t and d and c:
            items.append(MemoryItem(
                title=t.group(1).strip(),
                description=d.group(1).strip(),
                content=c.group(1).strip(),
                outcome=outcome,
                created_at=time.time(),
                source={"type":"code", "notes":"rb-run"}
            ))
    return items[:3]

def attempt_once(repo: str, issue_text: str, test_cmd: str, llm: LLM, store: MemoryStore, branch: str, self_refine_rounds: int = 0) -> Dict:
    ensure_git(repo)
    new_branch(repo, branch)

    retrieved = store.search(issue_text, top_k=1)
    system = build_system(retrieved)
    user = build_user(issue_text, summarize_repo_state(repo), test_cmd)
    model_out = llm.complete(system=system, user=user)
    patch = extract_patch(model_out)
    ok_apply, apply_out = apply_patch(repo, patch)
    traj_log = f"SYSTEM:\n{system}\n\nUSER:\n{user}\n\nMODEL_OUT:\n{model_out}\n\nPATCH_APPLY_OK={ok_apply}\nAPPLY_LOG:\n{apply_out}\n"

    if not ok_apply:
        # try once with small refine
        if self_refine_rounds > 0:
            refine = llm.complete(system="Self-refine", user=prompts.SEQUENTIAL_REFINE_INSTRUCTION_1 + f"\n\nPrevious patch apply failed:\n{apply_out}\n\nReprint a corrected unified diff.")
            patch2 = extract_patch(refine)
            ok_apply, apply_out2 = apply_patch(repo, patch2)
            traj_log += f"\nREFINE1_OUT:\n{refine}\nPATCH_APPLY_OK={ok_apply}\nAPPLY_LOG:\n{apply_out2}\n"

    # run tests
    success, test_log = label_success_from_tests(repo, test_cmd)
    traj_log += f"\nTEST_SUCCESS={success}\nTEST_LOG:\n{test_log}\n"

    # extract memory
    outcome = "success" if success else "failure"
    items = extract_memory(llm, issue_text, traj_log, outcome)
    store.add_items(items)

    return {
        "branch": branch,
        "success": success,
        "test_log": test_log,
        "traj_log": traj_log,
        "retrieved": retrieved,
        "memory_added": [asdict(i) for i in items],
    }
