"""LLM fallback repair — used when deterministic repair can't fix all errors.

Strategy: fix files ONE AT A TIME (incremental) instead of all at once.
This prevents the LLM from generating incomplete/incorrect code for
multiple files simultaneously.

Handles:
- Remaining mypy/ruff/black errors after deterministic repair
- Pytest import errors (missing classes/functions in source modules)
- Complex patterns that require LLM understanding
"""

import concurrent.futures
import json
import os
import re
import subprocess
import sys

MAX_ATTEMPTS = 3
MAX_FILE_ATTEMPTS = 2


def _run(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return p.returncode, p.stdout + "\n" + p.stderr
    except Exception as e:
        return 1, str(e)


def read_file(path):
    with open(path) as f:
        return f.read()


# ── Gather current errors ──


def gather_errors():
    """Run all quality checks and return categorized errors."""
    _, mypy_out = _run(["uv", "run", "mypy", "src/", "--ignore-missing-imports"])
    _, ruff_out = _run(["uv", "run", "ruff", "check", ".", "--output-format=concise"])
    _, black_out = _run(["uv", "run", "black", "--check", "."])
    _, pytest_out = _run(["uv", "run", "pytest", "tests/", "-q", "--tb=short"])

    # Collect failing files from mypy
    mypy_failing = {}
    for m in re.finditer(r"(?m)^(\S+\.py):(\d+):\s+error:\s+(.+?)\s+\[(\S+)\]", mypy_out):
        f = m.group(1)
        mypy_failing.setdefault(f, []).append(f"mypy: {m.group(3)} [{m.group(4)}]")

    # Collect failing files from ruff
    ruff_failing = {}
    for m in re.finditer(r"(?m)^(\S+\.py):\d+:\d+:\s+\S+", ruff_out):
        f = m.group(1)
        ruff_failing.setdefault(f, []).append(f"ruff: {m.group(0).strip()}")

    # Collect failing files from black
    black_failing = {}
    for m in re.finditer(r"would reformat (\S+\.py)", black_out):
        black_failing.setdefault(m.group(1), []).append("black: needs reformatting")

    # Collect pytest import errors
    pytest_import_errors = {}
    for m in re.finditer(
        r"ImportError: cannot import name '(\w+)' from '(\S+?)'",
        pytest_out,
    ):
        name = m.group(1)
        module = m.group(2)
        filepath = module.replace(".", "/") + ".py"
        pytest_import_errors.setdefault(filepath, set()).add(name)

    # Collect runtime test FAILURES (not just collection errors) and map each
    # failing test module to the source modules it imports, so the LLM is asked
    # to implement the real behavior that makes those tests pass.
    pytest_failing = {}
    failing_test_files = set()
    for m in re.finditer(r"FAILED\s+(tests/[^\s:]+)", pytest_out):
        failing_test_files.add(m.group(1))
    for m in re.finditer(r"(?m)^tests/[^\s:]+\s+(FAILED|ERROR)", pytest_out):
        failing_test_files.add(m.group(0).split()[0])
    for tf in failing_test_files:
        try:
            content = read_file(tf)
        except FileNotFoundError:
            continue
        for m in re.finditer(r"from\s+(src\.\w+)\s+import", content):
            module = m.group(1)
            filepath = module.replace(".", "/") + ".py"
            if os.path.exists(filepath):
                pytest_failing.setdefault(filepath, []).append(f"pytest: tests failing in {tf}")

    # Also scan test files for missing imports
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
            filepath = module.replace(".", "/") + ".py"
            if not os.path.exists(filepath):
                continue
            try:
                src = read_file(filepath)
            except FileNotFoundError:
                continue
            for name in names:
                if name and name[0].isalpha():
                    if (
                        f"class {name}" not in src
                        and f"def {name}" not in src
                        and f"{name} =" not in src
                        and not re.search(
                            rf"(?:from\s+\S+\s+import\s+.*\b{name}\b|import\s+.*\b{name}\b)", src
                        )
                    ):
                        pytest_import_errors.setdefault(filepath, set()).add(name)
        # Match: from src.xxx import name
        for m in re.finditer(r"from\s+(src\.\w+)\s+import\s+(\w+)(?:\s|$|,)", content):
            module = m.group(1)
            name = m.group(2)
            filepath = module.replace(".", "/") + ".py"
            if not os.path.exists(filepath):
                continue
            try:
                src = read_file(filepath)
            except FileNotFoundError:
                continue
            if (
                f"class {name}" not in src
                and f"def {name}" not in src
                and f"{name} =" not in src
                and not re.search(
                    rf"(?:from\s+\S+\s+import\s+.*\b{name}\b|import\s+.*\b{name}\b)", src
                )
            ):
                pytest_import_errors.setdefault(filepath, set()).add(name)

    return {
        "mypy": mypy_failing,
        "ruff": ruff_failing,
        "black": black_failing,
        "pytest_imports": pytest_import_errors,
        "pytest_failing": pytest_failing,
        "raw": {"mypy": mypy_out, "ruff": ruff_out, "black": black_out, "pytest": pytest_out},
    }


def get_test_context(filepath):
    """Find test files that import from the given source module."""
    module = filepath.replace("/", ".").replace(".py", "")
    test_context = ""
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
        if module in content:
            if len(content) > 5000:
                content = content[:5000] + "\n... (truncated)"
            test_context += f"\n### {test_file} (reference)\n```python\n{content}\n```\n"

    return test_context


def build_single_file_prompt(filepath, errors, test_context):
    """Build a focused prompt for fixing a single file."""
    src = read_file(filepath) if os.path.exists(filepath) else "(file not found)"
    if len(src) > 15000:
        src = src[:15000] + "\n... (truncated)"

    errors_desc = "\n".join(f"  - {e}" for e in errors)

    prompt = (
        f"Fix the file `{filepath}` to resolve these errors:\n\n"
        f"ERRORS:\n{errors_desc}\n\n"
        f"CURRENT FILE CONTENT:\n```python\n{src}\n```\n\n"
    )

    if test_context:
        prompt += (
            "TEST FILES (reference only — understand expected API, do NOT modify):\n"
            f"{test_context}\n\n"
        )

    prompt += (
        "RULES:\n"
        "1. Return ONLY a valid JSON object, no markdown fences.\n"
        "2. Return the COMPLETE corrected file content (not just changes).\n"
        "3. Preserve ALL existing functionality, classes, functions, and imports.\n"
        "4. Add missing classes/functions that tests expect, with real logic when clear.\n"
        "5. Use minimal stubs only when behavior is ambiguous.\n"
        "6. Ensure valid Python 3.13.\n\n"
        "JSON format:\n"
        '{"corrected_code": "complete file content here"}\n'
    )
    return prompt


def build_import_fix_prompt(filepath, missing_names, test_context):
    """Build a focused prompt for adding missing imports to a file."""
    src = read_file(filepath) if os.path.exists(filepath) else "(file not found)"
    if len(src) > 15000:
        src = src[:15000] + "\n... (truncated)"

    names_list = ", ".join(missing_names)

    prompt = (
        f"The file `{filepath}` is missing these classes/functions: {names_list}\n\n"
        f"Tests import them but they don't exist in the source file.\n\n"
        f"CURRENT FILE CONTENT:\n```python\n{src}\n```\n\n"
    )

    if test_context:
        prompt += (
            f"TEST FILES (reference — understand expected signatures/behavior):\n{test_context}\n\n"
        )

    prompt += (
        "RULES:\n"
        "1. Return ONLY a valid JSON object, no markdown fences.\n"
        "2. Return the COMPLETE file content with missing items ADDED.\n"
        "3. Keep ALL existing code intact — only ADD what's missing.\n"
        "4. Implement with real logic when test expectations are clear.\n"
        "5. Use minimal stubs for ambiguous cases.\n"
        "6. Add necessary imports (dataclass, typing, etc.) at the top.\n"
        "7. Ensure valid Python 3.13.\n\n"
        "JSON format:\n"
        '{"corrected_code": "complete file content here"}\n'
    )
    return prompt


def call_llm(prompt):
    """Call Gemini (primary) or OpenCode (fallback)."""
    api_key = os.environ.get("GOOGLE_API_KEY", "")
    oc_key = os.environ.get("OPENCODE_API_KEY", "")

    if api_key:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)

            # CRITICAL: the Gemini SDK call has no built-in timeout. A stalled
            # stream/hang would block the whole workflow until the job limit
            # (this is what caused the multi-hour runs). Run it on a worker
            # thread and cap it at 180s so we always make progress.
            def _gen():
                return client.models.generate_content(model="gemini-3.6-flash", contents=prompt)

            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(_gen)
                try:
                    resp = future.result(timeout=180)
                except concurrent.futures.TimeoutError:
                    future.cancel()
                    raise RuntimeError("Gemini call timed out after 180s")

            text = getattr(resp, "text", None) or ""
            if text:
                return text
        except Exception as e:
            print(f"  Gemini failed: {e}")

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
            print(f"  OpenCode fallback failed: {e}")

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
    code = result.get("corrected_code", "")
    if not code:
        # Try alternate format with files array
        files = result.get("files", [])
        if files and isinstance(files, list):
            code = files[0].get("corrected_code", "")
    return code


def validate_syntax(code, filepath):
    """Check that code is valid Python."""
    try:
        compile(code, filepath, "exec")
        return True, ""
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"


def verify_all_gates():
    """Run all quality checks and return True if all pass."""
    rc, _ = _run(["uv", "run", "ruff", "check", "."])
    if rc != 0:
        return False
    rc, _ = _run(["uv", "run", "black", "--check", "."])
    if rc != 0:
        return False
    rc, _ = _run(["uv", "run", "mypy", "src/", "--ignore-missing-imports"])
    if rc != 0:
        return False
    rc, _ = _run(["uv", "run", "pytest", "tests/", "-q", "--tb=short"])
    if rc != 0:
        return False
    return True


def format_and_verify():
    """Format code then verify all gates."""
    _run(["uv", "run", "ruff", "check", ".", "--fix"])
    _run(["uv", "run", "ruff", "format", "."])
    _run(["uv", "run", "black", "."])
    return verify_all_gates()


# ── Main: incremental file-by-file repair ──


def fix_single_file(filepath, errors, is_import_fix=False, missing_names=None):
    """Try to fix a single file using LLM. Returns True if successful."""
    test_context = get_test_context(filepath)

    for attempt in range(1, MAX_FILE_ATTEMPTS + 1):
        print(f"\n  --- {filepath} attempt {attempt}/{MAX_FILE_ATTEMPTS} ---")

        if is_import_fix and missing_names:
            prompt = build_import_fix_prompt(filepath, missing_names, test_context)
        else:
            prompt = build_single_file_prompt(filepath, errors, test_context)

        if attempt > 1:
            # Add previous error context
            _, verification_errors = _run(["uv", "run", "pytest", "tests/", "-q", "--tb=short"])
            prompt += f"\n\nPREVIOUS ERRORS:\n{verification_errors[:3000]}"

        try:
            raw = call_llm(prompt)
        except Exception as e:
            print(f"  LLM call failed: {e}")
            continue

        try:
            code = parse_response(raw)
        except Exception as e:
            print(f"  Parse failed: {e}")
            continue

        if not code:
            print("  Empty response from LLM.")
            continue

        ok, verr = validate_syntax(code, filepath)
        if not ok:
            print(f"  Syntax validation failed: {verr}")
            continue

        # Backup original
        read_file(filepath) if os.path.exists(filepath) else ""

        # Write the fix
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w") as f:
            f.write(code)

        # Format and verify
        _run(["uv", "run", "ruff", "check", ".", "--fix"])
        _run(["uv", "run", "ruff", "format", "."])
        _run(["uv", "run", "black", "."])

        # Check if this specific file still has errors
        _, mypy_out = _run(["uv", "run", "mypy", "src/", "--ignore-missing-imports"])
        file_errors = [
            line for line in mypy_out.splitlines() if filepath in line and "error:" in line
        ]

        if not file_errors:
            print(f"  ✅ {filepath} fixed successfully!")
            return True
        else:
            print(f"  ⚠️  Still {len(file_errors)} errors in {filepath}")
            for e in file_errors[:3]:
                print(f"    {e.strip()}")

    return False


# ── Entry point ──

errors = gather_errors()

# Check if there's anything to fix
all_failing = {}
all_failing.update(errors["mypy"])
all_failing.update(errors["ruff"])
all_failing.update(errors["black"])

# Add import errors
for filepath, names in errors["pytest_imports"].items():
    for name in sorted(names):
        all_failing.setdefault(filepath, []).append(f"pytest: missing '{name}'")

# Add modules with failing tests (need real implementations)
for filepath, reasons in errors.get("pytest_failing", {}).items():
    for reason in reasons:
        all_failing.setdefault(filepath, []).append(reason)

if not all_failing:
    print("No remaining errors detected.")
    with open("/tmp/llm_result.json", "w") as f:
        json.dump({"success": False, "reason": "no_errors"}, f)
    sys.exit(0)

api_key = os.environ.get("GOOGLE_API_KEY", "")
oc_key = os.environ.get("OPENCODE_API_KEY", "")

if not api_key and not oc_key:
    print("❌ No LLM API keys configured.")
    with open("/tmp/llm_result.json", "w") as f:
        json.dump({"success": False, "reason": "no_api_keys"}, f)
    sys.exit(0)

print(f"\n{'=' * 60}")
print(f"LLM Fallback: {len(all_failing)} files to fix")
print(f"{'=' * 60}")

# Sort files by priority: source files first, then by error count
# Files with import errors get special handling
source_files = []
import_files = []

for filepath in all_failing:
    if filepath in errors["pytest_imports"]:
        import_files.append(filepath)
    else:
        source_files.append(filepath)

# Fix import files first (simpler, more likely to succeed)
fixed_count = 0
failed_files = []

for filepath in import_files:
    missing_names = errors["pytest_imports"][filepath]
    print(f"\n📦 Fixing imports in {filepath}: {', '.join(missing_names)}")
    if fix_single_file(
        filepath, all_failing[filepath], is_import_fix=True, missing_names=missing_names
    ):
        fixed_count += 1
    else:
        failed_files.append(filepath)

# Then fix remaining source files
for filepath in source_files:
    print(f"\n🔧 Fixing {filepath}: {len(all_failing[filepath])} errors")
    if fix_single_file(filepath, all_failing[filepath]):
        fixed_count += 1
    else:
        failed_files.append(filepath)

# Final verification
print(f"\n{'=' * 60}")
print("Final verification...")
passed = format_and_verify()

if passed:
    print("✅ All gates pass!")
elif fixed_count > 0:
    print(f"⚠️  Fixed {fixed_count}/{len(all_failing)} files, some gates still failing.")
    if failed_files:
        print(f"   Failed files: {', '.join(failed_files)}")
else:
    print("❌ LLM could not produce any passing fix.")

# Gather final error state for report
final_errors = gather_errors()
final_failing_files = list(
    set(
        list(final_errors["mypy"].keys())
        + list(final_errors["ruff"].keys())
        + list(final_errors["black"].keys())
        + list(final_errors["pytest_imports"].keys())
    )
)

with open("/tmp/llm_result.json", "w") as f:
    json.dump(
        {
            "success": passed,
            "files_fixed": fixed_count,
            "files_failed": len(failed_files),
            "failed_files": failed_files,
            "remaining_errors": len(final_failing_files),
        },
        f,
    )

if not passed:
    print("\n❌ LLM could not produce a passing fix.")
