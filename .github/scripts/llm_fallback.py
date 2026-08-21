"""LLM fallback repair — used when deterministic repair can't fix all errors."""

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


# ── Gather remaining errors ──
_, mypy_out = _run(["uv", "run", "mypy", "src/", "--ignore-missing-imports"])
_, ruff_out = _run(["uv", "run", "ruff", "check", ".", "--output-format=concise"])
_, black_out = _run(["uv", "run", "black", "--check", "."])
_, pytest_out = _run(["uv", "run", "pytest", "tests/", "-q", "--tb=short"])

# Collect failing files with their specific errors
failing = {}
for m in re.finditer(r"(?m)^(\S+\.py):\d+:\s+error:\s+(.+?)\s+\[(\S+)\]", mypy_out):
    f = m.group(1)
    failing.setdefault(f, []).append(f"mypy: {m.group(2)} [{m.group(3)}]")
for m in re.finditer(r"(?m)^(\S+\.py):\d+:\d+:\s+\S+", ruff_out):
    f = m.group(1)
    failing.setdefault(f, []).append(f"ruff: {m.group(0).strip()}")
for m in re.finditer(r"would reformat (\S+\.py)", black_out):
    failing.setdefault(m.group(1), []).append("black: needs reformatting")

if not failing:
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

# Read the source files that need fixing
file_contents = {}
for filepath in failing:
    if os.path.exists(filepath):
        with open(filepath) as fh:
            file_contents[filepath] = fh.read()

# Build a focused prompt — only the specific files with errors
files_section = ""
for filepath in sorted(failing):
    errors_desc = "\n".join(f"  - {e}" for e in failing[filepath])
    content = file_contents.get(filepath, "(file not found)")
    if len(content) > 15000:
        content = content[:15000] + "\n... (truncated)"
    files_section += f"\n### {filepath}\nErrors:\n{errors_desc}\n```python\n{content}\n```\n"

prompt = (
    "Fix the following Python files to pass ALL quality checks "
    "(ruff, black, mypy, pytest).\n\n"
    "RULES:\n"
    "1. Return ONLY a valid JSON object, no markdown fences, no explanation text outside JSON.\n"
    "2. For each file, return the COMPLETE corrected file content.\n"
    "3. Preserve ALL existing functionality, classes, functions, and imports.\n"
    "4. Do NOT add self-imports (e.g. importing from the same module).\n"
    "5. For mypy errors: add proper type annotations, fix attribute access, add missing methods.\n"
    "6. For missing methods like generate_text/classify_text: add them as async wrappers "
    "around generate_completion.\n"
    "7. For missing functions like new_correlation_id: add them to the appropriate module.\n"
    "8. For wrong import names (setup_logging vs setup_logger): fix the import.\n"
    "9. For wrong argument names (cache=): remove or fix the argument.\n"
    "10. Ensure all code is valid Python 3.13.\n\n"
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

    # Format
    _run(["uv", "run", "black", "."])
    _run(["uv", "run", "ruff", "check", ".", "--fix"])
    _run(["uv", "run", "ruff", "format", "."])

    # Verify ALL gates (not per-file for mypy — cross-file checking matters)
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
