#!/usr/bin/env python
import argparse, os, json, time
from rb.llm import LLM
from rb.memory_store import MemoryStore
from rb.agent import attempt_once, run, new_branch, ensure_git

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="Path to git repo")
    ap.add_argument("--issue", required=True, help="Path to issue.md or inline string")
    ap.add_argument("--test-cmd", default="pytest -q", help="Command to run tests")
    ap.add_argument("--k", type=int, default=1, help="Parallel attempts (Best-of-N)")
    ap.add_argument("--refine", type=int, default=0, help="Sequential self-refine rounds per attempt")
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    ensure_git(repo)

    # read issue text
    issue_text = args.issue
    if os.path.exists(issue_text):
        with open(issue_text, "r", encoding="utf-8") as f:
            issue_text = f.read()

    llm = LLM()
    store = MemoryStore()

    results = []
    base_branch_name = "rb-attempt"
    for i in range(1, args.k + 1):
        branch = f"{base_branch_name}-{i}"
        res = attempt_once(repo, issue_text, args.test_cmd, llm, store, branch, self_refine_rounds=args.refine)
        results.append(res)
        print(f"[attempt {i}] success={res['success']} branch={res['branch']}")

    # pick best: prefer any success; else keep attempt 1
    best = None
    for r in results:
        if r["success"]:
            best = r
            break
    if not best:
        best = results[0]

    # switch to best branch for convenience
    os.system(f"cd {repo} && git checkout {best['branch']}")

    # write run report
    os.makedirs("runs", exist_ok=True)
    ts = int(time.time())
    with open(f"runs/run_{ts}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nBest attempt: {best['branch']} (success={best['success']})")
    print(f"Full run saved to runs/run_{ts}.json")
    print("Memory appended to memory/memory.jsonl")

if __name__ == "__main__":
    main()
