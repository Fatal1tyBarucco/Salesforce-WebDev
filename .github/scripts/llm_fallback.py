"""LLM fallback repair — used when deterministic repair can't fix all errors.

Handles:
- Remaining mypy/ruff/black errors after deterministic repair
- Pytest import errors (missing classes/functions in source modules)
"""

import json
import os
import re
import subprocess
import sys

MAX_ATTEMPTS = 3


def _run(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return p.returncode, p.stdout + "\n" + p.stderr
    except Exception as e:
        return 1, str(e)


def read_file(path):
    with open(path) as f:
        return f.read()


# ── Gather remaining errors ──
_, mypy_out = _run(["uv", "run", "mypy", "src/", "--ignore-missing-imports"])
_, ruff_out = _run(["uv", "run", "ruff", "check", ".", "--output-format=concise"])
_, black_out = _run(["uv", "run", "black", "--check", "."])
_, pytest_out = _run(["uv", "run", "pytest", "tests/", "-q", "--tb=short"])

# ── Collect failing files from mypy/ruff/black ──
failing = {}
for m in re.finditer(r"(?m)^(\S+\.py):\d+:\s+error:\s+(.+?)\s+\[(\S+)\]", mypy_out):
    f = m.group(1)
    failing.setdefault(f, []).append(f"mypy: {m.group(2)} [{m.group(3)}]")
for m in re.finditer(r"(?m)^(\S+\.py):\d+:\d+:\s+\S+", ruff_out):
    f = m.group(1)
    failing.setdefault(f, []).append(f"ruff: {m.group(0).strip()}")
for m in re.finditer(r"would reformat (\S+\.py)", black_out):
    failing.setdefault(m.group(1), []).append("black: needs reformatting")

# ── Collect pytest import errors ──
# Parse: ImportError: cannot import name 'X' from 'src.y' (path)
pytest_import_errors = {}  # source_module -> set of missing names
for m in re.finditer(
    r"ImportError: cannot import name '(\w+)' from '(\S+?)'",
    pytest_out,
):
    name = m.group(1)
    module = m.group(2)
    pytest_import_errors.setdefault(module, set()).add(name)

# For each missing name, find which test file imports it
test_import_context = {}  # (module, name) -> list of test files
for m in re.finditer(
    r"(tests/\S+\.py):\d+:\s+in <module>\s*\n.*\n.*from (\S+) import",
    pytest_out,
):
    test_file = m.group(1)
    module = m.group(2)
    # Find which names this test file imports from this module
    if os.path.exists(test_file):
        try:
            test_src = read_file(test_file)
        except FileNotFoundError:
            continue
        for name in pytest_import_errors.get(module, set()):
            if re.search(rf"\b{name}\b", test_src):
                test_import_context.setdefault(module, set()).add(name)

# Also scan test files directly for imports from src modules
test_files = []
for root, _dirs, files in os.walk("tests"):
    for fname in files:
        if fname.startswith("test_") and fname.endswith(".py"):
            test_files.append(os.path.join(root, fname))

for test_file in test_files:
    try:
        content = read_file(test_file)
    except FileNotFoundError:
        continue
    # Match: from src.xxx import (name1, name2, ...)
    for m in re.finditer(r"from\s+(src\.\w+)\s+import\s+\(([^)]+)\)", content, re.DOTALL):
        module = m.group(1)
        names = [n.strip().split(" as ")[0].strip() for n in m.group(2).split(",")]
        for name in names:
            if name and name[0].isalpha():
                test_import_context.setdefault(module, set()).add(name)
    # Also match: from src.xxx import name
    for m in re.finditer(r"from\s+(src\.\w+)\s+import\s+(\w+)(?:\s|$|,)", content):
        test_import_context.setdefault(m.group(1), set()).add(m.group(2))

# Check which names are actually missing from source modules
missing_stubs = {}  # source_file -> set of missing names
for module, names in test_import_context.items():
    filepath = module.replace(".", "/") + ".py"
    if not os.path.exists(filepath):
        continue
    try:
        src = read_file(filepath)
    except FileNotFoundError:
        continue
    for name in names:
        if (
            f"class {name}" not in src
            and f"def {name}" not in src
            and f"{name} =" not in src
            and not re.search(rf"(?:from\s+\S+\s+import\s+.*\b{name}\b|import\s+.*\b{name}\b)", src)
        ):
            missing_stubs.setdefault(filepath, set()).add(name)

# Add missing stubs info to failing files
for filepath, names in missing_stubs.items():
    for name in sorted(names):
        failing.setdefault(filepath, []).append(f"pytest: missing '{name}' (imported by tests)")

# ── Check if there's anything to fix ──
if not failing and not missing_stubs:
    print("No remaining errors detected.")
    with open("/tmp/llm_result.json", "w") as f:
        json.dump({"success": False, "reason": "no_errors"}, f)
    sys.exit(0)

api_key = os.environ.get("GOOGLE_API_KEY", "")
oc_key = os.environ.get("OPENCODE_API_KEY", "")

if not api_key and not oc_key:
    print("❌ No LLM API keys configured (GOOGLE_API_KEY, OPENCODE_API_KEY).")
    print("   Set these as repository secrets for LLM fallback to work.")
    with open("/tmp/llm_result.json", "w") as f:
        json.dump({"success": False, "reason": "no_api_keys"}, f)
    sys.exit(0)

# ── Read source files that need fixing ──
file_contents = {}
for filepath in failing:
    if os.path.exists(filepath):
        try:
            file_contents[filepath] = read_file(filepath)
        except FileNotFoundError:
            pass

# Also read test files that have import errors (for context)
test_file_contents = {}
for module in test_import_context:
    for test_file in test_files:
        try:
            content = read_file(test_file)
        except FileNotFoundError:
            continue
        if module in content:
            test_file_contents[test_file] = content

# ── Build prompt ──
files_section = ""
for filepath in sorted(failing):
    errors_desc = "\n".join(f"  - {e}" for e in failing[filepath])
    content = file_contents.get(filepath, "(file not found)")
    if len(content) > 15000:
        content = content[:15000] + "\n... (truncated)"
    files_section += f"\n### {filepath}\nErrors:\n{errors_desc}\n```python\n{content}\n```\n"

# Add test files as context (read-only, for understanding what's expected)
test_context = ""
for filepath in sorted(test_file_contents):
    content = test_file_contents[filepath]
    if len(content) > 8000:
        content = content[:8000] + "\n... (truncated)"
    test_context += (
        f"\n### {filepath} (test file — for reference only)\n```python\n{content}\n```\n"
    )

prompt = (
    "Fix the following Python files to pass ALL quality checks "
    "(ruff, black, mypy, pytest).\n\n"
    "RULES:\n"
    "1. Return ONLY a valid JSON object, no markdown fences, no explanation text outside JSON.\n"
    "2. For each file listed under 'FILES TO FIX', return the COMPLETE corrected file content.\n"
    "3. Preserve ALL existing functionality, classes, functions, and imports.\n"
    "4. Do NOT add self-imports (e.g. importing from the same module).\n"
    "5. For mypy errors: add proper type annotations, fix attribute access, add missing methods.\n"
    "6. For missing methods like generate_text/classify_text: add them as async wrappers "
    "around generate_completion.\n"
    "7. For missing functions/classes referenced by tests: add them to the appropriate source "
    "module. Read the test files (marked 'for reference only') to understand the expected "
    "API (method signatures, return types, behavior).\n"
    "8. For wrong import names (setup_logging vs setup_logger): fix the import.\n"
    "9. For wrong argument names (cache=): remove or fix the argument.\n"
    "10. Ensure all code is valid Python 3.13.\n"
    "11. When adding stubs for missing classes/functions, implement them with real logic "
    "when the test expectations are clear. Use minimal stubs only when behavior is ambiguous.\n\n"
    "JSON format:\n"
    "{\n"
    '    "root_cause_summary": "brief summary",\n'
    '    "explanation": "what was changed",\n'
    '    "files": [\n'
    '        {"affected_file_path": "src/file.py", "corrected_code": "complete file content"}\n'
    "    ]\n"
    "}\n\n"
    "FILES TO FIX:\n" + files_section
)

if test_context:
    prompt += (
        "\nTEST FILES (for reference — understand expected API, do NOT modify these):\n"
        + test_context
    )


def call_llm(prompt):
    """Call Gemini (primary) or OpenCode (fallback)."""
    # Primary: Google Gemini
    if api_key:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
            text = getattr(resp, "text", None) or ""
            if text:
                return text
        except Exception as e:
            print(f"Gemini failed: {e}")

    # Fallback: OpenCode
    if oc_key:
        try:
            import urllib.request

            oc_base = (
                os.environ.get("OPENCODE_BASE_URL") or "https://opencode.ai/console/zen/v1"
            ).rstrip("/")
            oc_model = os.environ.get("OPENCODE_MODEL") or "hy3-free"
            url = oc_base + "/chat/completions"
            payload = json.dumps(
                {
                    "model": oc_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2,
                    "stream": False,
                }
            ).encode()
            req = urllib.request.Request(
                url,
                data=payload,
                method="POST",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {oc_key}",
                    "Accept": "application/json",
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0 Safari/537.36",
                },
            )
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read().decode())
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if text:
                return text
        except Exception as e:
            print(f"OpenCode fallback failed: {e}")

    raise RuntimeError("All LLM providers failed")


def parse_response(raw):
    """Parse LLM response, handling markdown fences and malformed JSON."""
    raw = re.sub(r"^```(?:json)?\s*\n?", "", raw, flags=re.MULTILINE)
    raw = re.sub(r"\n?```\s*$", "", raw, flags=re.MULTILINE).strip()
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start >= 0 and end > start:
        raw = raw[start:end]
    result = json.loads(raw)
    files = result.get("files", [])
    if not isinstance(files, list):
        files = []
    return result.get("root_cause_summary", ""), result.get("explanation", ""), files


def validate_syntax(files):
    """Check that all returned code is valid Python."""
    for entry in files:
        path = entry.get("affected_file_path", "")
        code = entry.get("corrected_code", "")
        if not path or not code:
            return False, "Missing path or code for entry"
        try:
            compile(code, path, "exec")
        except SyntaxError as e:
            return False, f"SyntaxError in {path}: {e}"
    return True, ""


def apply_and_verify(files):
    """Write files, format, then verify ALL gates."""
    for entry in files:
        path = entry["affected_file_path"]
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as fh:
            fh.write(entry["corrected_code"])

    # Format (ruff first, black last for final say)
    _run(["uv", "run", "ruff", "check", ".", "--fix"])
    _run(["uv", "run", "ruff", "format", "."])
    _run(["uv", "run", "black", "."])

    # Verify ALL gates
    errors = []
    rc, out = _run(["uv", "run", "ruff", "check", "."])
    if rc != 0:
        errors.append(f"RUFF:\n{out[-1500:]}")
    rc, out = _run(["uv", "run", "black", "--check", "."])
    if rc != 0:
        errors.append(f"BLACK:\n{out[-800:]}")
    rc, out = _run(["uv", "run", "mypy", "src/", "--ignore-missing-imports"])
    if rc != 0:
        errors.append(f"MYPY:\n{out[-2000:]}")
    rc, out = _run(["uv", "run", "pytest", "tests/", "-q", "--tb=short"])
    if rc != 0:
        errors.append(f"PYTEST:\n{out[-3000:]}")
    return len(errors) == 0, "\n".join(errors)


# ── Retry loop ──
passed = False
result_files = []
summary = ""
explanation = ""
last_errors = ""

for attempt in range(1, MAX_ATTEMPTS + 1):
    print(f"\n--- LLM attempt {attempt}/{MAX_ATTEMPTS} ---")
    current_prompt = (
        prompt if attempt == 1 else prompt + f"\n\nPREVIOUS ERRORS:\n{last_errors[:5000]}"
    )

    try:
        raw = call_llm(current_prompt)
    except Exception as e:
        print(f"LLM call failed: {e}")
        last_errors = str(e)
        continue

    try:
        summary, explanation, result_files = parse_response(raw)
    except Exception as e:
        print(f"Parse failed: {e}")
        last_errors = f"Invalid JSON: {e}\nRaw: {raw[:500]}"
        continue

    if not result_files:
        print("No files returned.")
        last_errors = "No files in response."
        continue

    ok, verr = validate_syntax(result_files)
    if not ok:
        print(f"Syntax validation failed: {verr}")
        last_errors = verr
        continue

    passed, gerr = apply_and_verify(result_files)
    if passed:
        print("✅ All gates pass!")
        break
    print(f"Verification failed:\n{gerr[:2000]}")
    last_errors = gerr

with open("/tmp/llm_result.json", "w") as f:
    json.dump(
        {
            "success": passed,
            "summary": summary[:200] if summary else "",
            "explanation": explanation[:500] if explanation else "",
            "files": [e["affected_file_path"] for e in result_files],
        },
        f,
    )

if not passed:
    print("\n❌ LLM could not produce a passing fix.")
