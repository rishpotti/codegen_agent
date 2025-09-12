# codegen_workflow.py
import os
import json
import subprocess
import shlex
from dataclasses import dataclass
from typing import List, Dict, Optional

# ============== LLM BINDINGS (LangChain) ==============
# You can swap these with any LangChain chat models you prefer.
# Example with Google (Gemini) — make sure GOOGLE_API_KEY is set.
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.schema import SystemMessage, HumanMessage
except Exception:
    ChatGoogleGenerativeAI = None
    class SystemMessage:  # fallback dumb stubs so file imports cleanly
        def __init__(self, content: str): self.content = content
    class HumanMessage:
        def __init__(self, content: str): self.content = content


# ============== SANDBOX / TOOLS (safe ops) ==============
SANDBOX_DIR = os.getcwd()
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
TIMEOUT = 8  # seconds for shell calls/search

def _inside_sandbox(path: str) -> bool:
    return os.path.abspath(path).startswith(SANDBOX_DIR)

def edit_file(file_path: str, content: str, mode: str = "overwrite") -> str:
    abs_path = os.path.abspath(os.path.join(SANDBOX_DIR, file_path))
    if not _inside_sandbox(abs_path):
        return "Error: Outside sandbox."
    try:
        os.makedirs(os.path.dirname(abs_path) or ".", exist_ok=True)
        if mode == "append":
            with open(abs_path, "a", encoding="utf-8") as f:
                f.write(content)
        else:
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
        return f"OK: wrote {file_path} ({mode})"
    except Exception as e:
        return f"Error: {e}"

def read_file(file_path: str) -> str:
    abs_path = os.path.abspath(os.path.join(SANDBOX_DIR, file_path))
    if not _inside_sandbox(abs_path):
        return "Error: Outside sandbox."
    if not os.path.exists(abs_path):
        return "Error: File does not exist."
    if os.path.getsize(abs_path) > MAX_FILE_SIZE:
        return "Error: File too large."
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error: {e}"

def list_files(directory: str = ".") -> List[str]:
    abs_dir = os.path.abspath(os.path.join(SANDBOX_DIR, directory))
    if not _inside_sandbox(abs_dir):
        return ["Error: Outside sandbox."]
    out = []
    for root, _, files in os.walk(abs_dir):
        for name in files:
            out.append(os.path.relpath(os.path.join(root, name), SANDBOX_DIR))
    return out

def run_safe_bash(command: str, timeout: int = TIMEOUT) -> str:
    # basic safeguard — no absolute path escapes
    if command.strip().startswith("cd /") or " .." in command or "../" in command:
        return "Error: sandbox path violation."
    try:
        proc = subprocess.run(
            command,
            shell=True,
            cwd=SANDBOX_DIR,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if proc.returncode == 0:
            return proc.stdout.strip() or "(no output)"
        return f"(exit {proc.returncode})\n{proc.stdout}{proc.stderr}".strip()
    except subprocess.TimeoutExpired:
        return f"Error: Command timed out after {timeout}s."
    except Exception as e:
        return f"Error: {e}"

def code_search(pattern: str, directory: str = ".") -> str:
    abs_dir = os.path.abspath(os.path.join(SANDBOX_DIR, directory))
    if not _inside_sandbox(abs_dir):
        return "Error: Outside sandbox."
    try:
        proc = subprocess.run(
            ["rg", "--line-number", "--no-heading", pattern, abs_dir],
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
        )
        # rg returns 0 if matches, 1 if no matches, >1 on error
        if proc.returncode in (0, 1):
            return proc.stdout.strip() or "(no matches)"
        return f"(rg exit {proc.returncode})\n{proc.stderr}".strip()
    except FileNotFoundError:
        return "Error: ripgrep (rg) not installed."
    except subprocess.TimeoutExpired:
        return f"Error: ripgrep timed out after {TIMEOUT}s."
    except Exception as e:
        return f"Error: {e}"


# ============== DATA STRUCTURES ==============
@dataclass
class PlannedFile:
    file_name: str
    description: str
    packages: List[str]

@dataclass
class Plan:
    files: List[PlannedFile]
    entrypoint: Optional[str]  # e.g., "app.py" or "main.py"


# ============== ORCHESTRATOR (planner LLM) ==============
def make_planner_llm() -> "ChatGoogleGenerativeAI":
    if ChatGoogleGenerativeAI is None:
        raise RuntimeError("LangChain Google Generative AI not installed.")
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

PLANNER_SYSTEM = SystemMessage(
    content=(
        "You are a project manager and senior developer. "
        "Given a project request, output STRICT JSON with this schema:\n"
        "{\n"
        '  "files": [\n'
        '    {"file_name": "path/to/file.py", "description": "what to implement", "packages": ["pkg1","pkg2"]}\n'
        "  ],\n"
        '  "entrypoint": "path/to/entry.py"  // if unknown, choose the most likely runtime entry file\n'
        "}\n"
        "No commentary. No markdown. Only JSON."
    )
)

def plan_project(planner_llm, prompt: str) -> Plan:
    resp = planner_llm.invoke([PLANNER_SYSTEM, HumanMessage(content=prompt)])
    text = getattr(resp, "content", str(resp))
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Planner did not return valid JSON. Got:\n{text}") from e

    files: List[PlannedFile] = []
    for f in data.get("files", []):
        files.append(
            PlannedFile(
                file_name=f["file_name"],
                description=f.get("description", ""),
                packages=list(f.get("packages", [])),
            )
        )
    entry = data.get("entrypoint")
    return Plan(files=files, entrypoint=entry)


# ============== CODER (file writer LLM) ==============
def make_coder_llm() -> "ChatGoogleGenerativeAI":
    if ChatGoogleGenerativeAI is None:
        raise RuntimeError("LangChain Google Generative AI not installed.")
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

CODER_SYSTEM = SystemMessage(
    content=(
        "You are a senior software engineer. "
        "Write the requested file. Output ONLY the code. No comments, no backticks."
    )
)

def generate_file(coder_llm, pf: PlannedFile) -> str:
    prompt = (
        f"File name: {pf.file_name}\n"
        f"Description: {pf.description}\n"
        f"Required packages: {', '.join(pf.packages) if pf.packages else 'none'}\n"
        "Write the complete code for this file."
    )
    resp = coder_llm.invoke([CODER_SYSTEM, HumanMessage(content=prompt)])
    return getattr(resp, "content", str(resp))


# ============== TESTER/FIXER (LLM-in-the-loop) ==============
def make_fixer_llm() -> "ChatGoogleGenerativeAI":
    if ChatGoogleGenerativeAI is None:
        raise RuntimeError("LangChain Google Generative AI not installed.")
    return ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

FIXER_SYSTEM = SystemMessage(
    content=(
        "You are a software tester and fixer. "
        "Given a file's code and the execution output (including tracebacks), "
        "return a corrected FULL FILE (entire content). "
        "Output ONLY the code. No explanations."
    )
)

def unit_test_and_fix(fixer_llm, file_path: str, max_attempts: int = 3) -> Dict:
    """Write/overwrite file already happened before calling this (by coder)."""
    logs: List[str] = []
    status = "Fail"
    code = read_file(file_path)
    if code.startswith("Error:"):
        return {"name": file_path, "content": code, "unit_status": "Fail", "unit_test_logs": code}

    for attempt in range(1, max_attempts + 1):
        run_out = run_safe_bash(f"python {shlex.quote(file_path)}")
        logs.append(f"Attempt {attempt}:\n{run_out}")
        if "Traceback" not in run_out and not run_out.startswith("Error:") and not run_out.startswith("(exit"):
            status = "Pass"
            break

        # Ask the fixer to produce a new full file
        fix_resp = fixer_llm.invoke([
            FIXER_SYSTEM,
            HumanMessage(content=f"Filename: {file_path}\n\nCurrent code:\n{code}\n\nExecution Output:\n{run_out}")
        ])
        new_code = getattr(fix_resp, "content", str(fix_resp))
        write_status = edit_file(file_path, new_code, mode="overwrite")
        code = new_code
        logs.append(f"(applied fix) {write_status}")

    return {
        "name": file_path,
        "content": code,
        "unit_status": status,
        "unit_test_logs": "\n\n".join(logs),
    }


# ============== ENTRYPOINT DISCOVERY ==============
def discover_entrypoint_from_plan(plan: Plan) -> Optional[str]:
    if plan.entrypoint:
        return plan.entrypoint

    # heuristic: prefer typical names if present
    candidates = ["app.py", "main.py", "server.py", "run.py"]
    plan_names = {pf.file_name for pf in plan.files}
    for c in candidates:
        if c in plan_names:
            return c

    # last resort: search for __main__ guard among generated files on disk
    for pf in plan.files:
        code = read_file(pf.file_name)
        if isinstance(code, str) and ("if __name__ == \"__main__\"" in code or "if __name__ == '__main__'" in code):
            return pf.file_name

    return None


# ============== INTEGRATION TEST & FIX ==============
INTEGRATION_FIXER_SYSTEM = SystemMessage(
    content=(
        "You are a software maintainer. "
        "Given project execution logs and access to current file contents, "
        "produce corrected FULL files for any files that need changes. "
        "Your output MUST be a JSON array of objects [{\"file\":\"path\",\"code\":\"full file content\"}, ...]. "
        "No commentary."
    )
)

def integration_test_and_fix(fixer_llm, entrypoint: str, all_files: List[str], max_attempts: int = 3) -> Dict:
    logs: List[str] = []
    status = "Fail"

    for attempt in range(1, max_attempts + 1):
        run_out = run_safe_bash(f"python {shlex.quote(entrypoint)}")
        logs.append(f"Integration attempt {attempt}:\n{run_out}")

        if "Traceback" not in run_out and not run_out.startswith("Error:") and not run_out.startswith("(exit"):
            status = "Pass"
            break

        # Build a compact snapshot of current files
        snapshot_parts = []
        for path in all_files:
            content = read_file(path)
            if isinstance(content, str) and not content.startswith("Error:"):
                snapshot_parts.append(f"--- {path} ---\n{content}\n")
        snapshot = "\n".join(snapshot_parts)

        # Ask the LLM to return a JSON array of file patches (full file content each)
        fix_resp = fixer_llm.invoke([
            INTEGRATION_FIXER_SYSTEM,
            HumanMessage(content=f"Entrypoint: {entrypoint}\n\nRun Output:\n{run_out}\n\nCurrent files:\n{snapshot}")
        ])
        fix_text = getattr(fix_resp, "content", str(fix_resp))

        # Try to parse and apply patches
        try:
            patches = json.loads(fix_text)
            if isinstance(patches, list):
                for p in patches:
                    target = p.get("file")
                    code = p.get("code", "")
                    if target and code is not None:
                        write_status = edit_file(target, code, mode="overwrite")
                        logs.append(f"(applied integration fix to {target}) {write_status}")
            else:
                logs.append("(integration fixer returned non-list JSON; ignored)")
        except json.JSONDecodeError:
            logs.append("(integration fixer did not return JSON; ignored)")

    return {"integration_status": status, "integration_logs": "\n\n".join(logs)}


# ============== SYNTHESIZER ==============
def synthesize_bundle(tested_files: List[Dict], integration_result: Dict) -> str:
    parts = []
    for tf in tested_files:
        parts.append(
            f"# File: {tf['name']}\n\n{tf['content']}\n\n"
            f"## Unit Status: {tf['unit_status']}\n"
            f"## Unit Logs:\n{tf['unit_test_logs']}\n"
        )
    parts.append(
        f"# Integration Status: {integration_result.get('integration_status','Unknown')}\n"
        f"## Integration Logs:\n{integration_result.get('integration_logs','')}\n"
    )
    return "\n\n---\n\n".join(parts)


# ============== MAIN PIPELINE (single prompt → project) ==============
def generate_project_from_prompt(
    prompt: str,
    planner_llm=None,
    coder_llm=None,
    fixer_llm=None,
    max_unit_attempts: int = 3,
    max_integration_attempts: int = 3,
) -> Dict:
    """
    Returns dict with keys:
      - plan (Plan object serialized)
      - tested_files (list of dict)
      - entrypoint (str or None)
      - integration (dict)
      - final_project (str)
    """
    # create default LLMs if not provided
    planner_llm = planner_llm or make_planner_llm()
    coder_llm   = coder_llm   or make_coder_llm()
    fixer_llm   = fixer_llm   or make_fixer_llm()

    # 1) Plan
    plan = plan_project(planner_llm, prompt)

    # 2) Generate files (write immediately to disk)
    tested_files: List[Dict] = []
    for pf in plan.files:
        code = generate_file(coder_llm, pf)
        edit_status = edit_file(pf.file_name, code, mode="overwrite")

        # 3) Unit test & fix each file
        unit = unit_test_and_fix(fixer_llm, pf.file_name, max_attempts=max_unit_attempts)
        tested_files.append(unit)

    # Update local disk with the latest unit-fixed versions (already written)
    all_paths = [pf.file_name for pf in plan.files]

    # 4) Integration
    entry = discover_entrypoint_from_plan(plan)
    if not entry:
        # if still unknown, pick a best guess among produced files
        guesses = ["app.py", "main.py", "server.py", "run.py"]
        existing = set(list_files("."))
        entry = next((g for g in guesses if g in existing), None)

    integration = {"integration_status": "Skipped", "integration_logs": "No entrypoint found."}
    if entry:
        integration = integration_test_and_fix(
            fixer_llm, entry, all_paths, max_attempts=max_integration_attempts
        )

    # 5) Synthesize
    final_bundle = synthesize_bundle(tested_files, integration)

    return {
        "plan": {
            "entrypoint": plan.entrypoint,
            "files": [pf.__dict__ for pf in plan.files],
            "resolved_entrypoint": entry,
        },
        "tested_files": tested_files,
        "entrypoint": entry,
        "integration": integration,
        "final_project": final_bundle,
    }


# ============== CLI Helper ==============
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Single-prompt codegen workflow")
    parser.add_argument("prompt", type=str, help="Project prompt")
    parser.add_argument("--unit-attempts", type=int, default=3, help="Max unit test fix attempts")
    parser.add_argument("--int-attempts", type=int, default=3, help="Max integration fix attempts")
    args = parser.parse_args()

    if ChatGoogleGenerativeAI is None:
        raise SystemExit("Please `pip install langchain-google-genai` and set GOOGLE_API_KEY.")

    result = generate_project_from_prompt(
        prompt=args.prompt,
        max_unit_attempts=args.unit_attempts,
        max_integration_attempts=args.int_attempts,
    )

    # Write a final bundle file for convenience
    _ = edit_file("_FINAL_PROJECT.md", result["final_project"], mode="overwrite")
    print("✅ Generation complete.")
    print(f"Entrypoint: {result['entrypoint'] or '(not found)'}")
    print("See _FINAL_PROJECT.md for the combined output.\n")
