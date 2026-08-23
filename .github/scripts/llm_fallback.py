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
import time

MAX_ATTEMPTS = 3
MAX_FILE_ATTEMPTS = 2

# Wall-clock budget. Without it, file-by-file repair (each attempt costing up
# to 2 OpenCode models x 180s plus gate re-runs) blew past the workflow step's
# timeout, killing ALL progress including already-applied fixes.
# REPAIR_DEADLINE_EPOCH lets the workflow share one deadline across all
# iterations; otherwise the script gives itself 20 minutes.
_START = time.time()
_DEADLINE = int(os.environ.get("REPAIR_DEADLINE_EPOCH") or 0) or int(_START + 20 * 60)


def budget_exceeded():
    """True when the repair wall-clock budget has been exhausted."""
    return time.time() >= _DEADLINE


def budget_left():
    return _DEADLINE - time.time()


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


# Per-call cap. Free OpenCode models regularly stall past 180s; every wasted
# minute of a hung call eats the shared repair deadline, so fail fast.
_LLM_CALL_TIMEOUT_S = int(os.environ.get("LLM_CALL_TIMEOUT_S") or 60)

# Circuit breaker. In run 32619290201 the same dead providers were retried
# for every file/attempt (x-preview-f-free kept returning 503, Gemini's free
# tier was quota-exhausted), burning the whole budget on known-dead paths.
# After N consecutive failures a provider is skipped for the rest of the run.
_FAILURE_THRESHOLD = 2
_PROVIDER_FAILURES = {}
_PROVIDER_DISABLED = set()


def _opencode_models():
    primary = os.environ.get("OPENCODE_MODEL") or "x-preview-f-free"
    if os.environ.get("OPENCODE_MODEL"):
        return [primary]
    # Free-model pool. Individual free models go down regularly (503 upstream
    # one day, multi-minute stalls the next), so instead of depending on two,
    # sweep the remaining free Zen models before giving up on OpenCode.
    return [
        primary,
        "hy3-free",
        "glm-5-free",
        "deepseek-v4-flash-free",
        "kimi-k2.5-free",
        "minimax-m2.5-free",
    ]


def _openrouter_models():
    """Free OpenRouter models, best coding candidates first."""
    primary = os.environ.get("OPENROUTER_MODEL")
    pool = [
        primary,
        "z-ai/glm-5.2:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free",
        "cohere/north-mini-code:free",
        "poolside/laguna-s-2.1:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "thinkingmachines/inkling:free",
    ]
    seen = set()
    return [m for m in pool if m and not (m in seen or seen.add(m))]


def _provider_enabled(key):
    return key not in _PROVIDER_DISABLED


def _mark_failure(key, err, disable=False):
    if disable:
        _PROVIDER_DISABLED.add(key)
        print(f"  ⛔ Provider '{key}' disabled for the rest of this run: {err}")
        return
    _PROVIDER_FAILURES[key] = _PROVIDER_FAILURES.get(key, 0) + 1
    if _PROVIDER_FAILURES[key] >= _FAILURE_THRESHOLD:
        _PROVIDER_DISABLED.add(key)
        print(
            f"  ⛔ Provider '{key}' disabled for the rest of this run after "
            f"{_PROVIDER_FAILURES[key]} consecutive failures (last: {err})"
        )
    else:
        print(f"  {key} failed ({_PROVIDER_FAILURES[key]}/{_FAILURE_THRESHOLD}): {err}")


def _mark_success(key):
    _PROVIDER_FAILURES.pop(key, None)


def has_provider():
    """True when at least one LLM provider is still usable."""
    if os.environ.get("OPENCODE_API_KEY") and any(
        _provider_enabled(f"opencode:{m}") for m in _opencode_models()
    ):
        return True
    if os.environ.get("OPENROUTER_API_KEY") and any(
        _provider_enabled(f"openrouter:{m}") for m in _openrouter_models()
    ):
        return True
    if os.environ.get("GOOGLE_API_KEY") and _provider_enabled("gemini"):
        return True
    return False


def _call_chat_completions(prompt, base_url, api_key, models, provider_name):
    """Generic OpenAI-compatible chat/completions sweep with per-model breaker."""
    import urllib.error
    import urllib.request

    last_error = None

    for model in models:
        key = f"{provider_name}:{model}"
        if not _provider_enabled(key):
            continue
        url = base_url.rstrip("/") + "/chat/completions"
        payload = json.dumps(
            {
                "model": model,
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
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Chrome/124.0 Safari/537.36",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=_LLM_CALL_TIMEOUT_S) as r:
                data = json.loads(r.read().decode())
            text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if text:
                _mark_success(key)
                return text
            last_error = RuntimeError(f"empty response from {model}")
            _mark_failure(key, last_error)
        except urllib.error.HTTPError as he:
            # Surface the real server response so endpoint/quota problems are
            # diagnosable instead of just printing "failed".
            body = ""
            try:
                body = he.read().decode(errors="replace")
            except Exception:
                pass
            print(
                f"  {provider_name} HTTP {he.code} {he.reason} on POST {url} (model={model})\n"
                f"  Response body: {body[:500]}"
            )
            last_error = he
            # 401 bad key / 503 upstream / 429 quota won't recover this run.
            _mark_failure(key, f"HTTP {he.code}", disable=he.code in (401, 429, 503))
        except Exception as e:
            last_error = e
            # Timeouts are expensive (full cap burned) and rarely one-off —
            # a model that stalls once usually stalls all run. Disable now.
            timed_out = isinstance(e, TimeoutError) or "timed out" in str(e)
            _mark_failure(key, e, disable=timed_out)

    raise last_error or RuntimeError(f"{provider_name} returned no usable response")


def _call_opencode(prompt):
    """Sweep the OpenCode Zen free-model pool."""
    oc_base = os.environ.get("OPENCODE_BASE_URL") or "https://opencode.ai/zen/v1"
    return _call_chat_completions(
        prompt,
        oc_base,
        os.environ.get("OPENCODE_API_KEY", ""),
        _opencode_models(),
        "opencode",
    )


def _call_openrouter(prompt):
    """Sweep the OpenRouter free-model pool."""
    return _call_chat_completions(
        prompt,
        "https://openrouter.ai/api/v1",
        os.environ.get("OPENROUTER_API_KEY", ""),
        _openrouter_models(),
        "openrouter",
    )


def _call_gemini(prompt):
    """Call Google Gemini with a hard timeout (the SDK has no built-in one)."""
    from google import genai

    client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY", ""))

    def _gen():
        return client.models.generate_content(model="gemini-3.6-flash", contents=prompt)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
        future = ex.submit(_gen)
        try:
            resp = future.result(timeout=120)
        except concurrent.futures.TimeoutError:
            future.cancel()
            raise RuntimeError("Gemini call timed out after 120s")

    text = getattr(resp, "text", None) or ""
    if not text:
        raise RuntimeError("Gemini returned an empty response")
    return text


def call_llm(prompt):
    """Call LLM providers in order: OpenCode free pool, OpenRouter free pool, Gemini (Google).

    Gemini goes last on purpose: its free tier allows only 20 requests/day,
    so it is the scarce reserve used when every free model is down.
    """
    oc_key = os.environ.get("OPENCODE_API_KEY", "")
    or_key = os.environ.get("OPENROUTER_API_KEY", "")
    api_key = os.environ.get("GOOGLE_API_KEY", "")

    if not has_provider():
        raise RuntimeError("All LLM providers are unavailable or disabled for this run")

    if oc_key and any(_provider_enabled(f"opencode:{m}") for m in _opencode_models()):
        try:
            return _call_opencode(prompt)
        except Exception as e:
            print(f"  OpenCode failed: {e}")

    if or_key and any(_provider_enabled(f"openrouter:{m}") for m in _openrouter_models()):
        try:
            return _call_openrouter(prompt)
        except Exception as e:
            print(f"  OpenRouter failed: {e}")

    if api_key and _provider_enabled("gemini"):
        try:
            return _call_gemini(prompt)
        except Exception as e:
            msg = str(e)
            if "429" in msg and "RESOURCE_EXHAUSTED" in msg:
                # Daily quota exhausted — retrying is pointless today.
                _mark_failure("gemini", "quota exhausted (429)", disable=True)
            else:
                _mark_failure("gemini", e)

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


def select_target_test_file(errors):
    """Pick ONE failing test module as this run's scope.

    Fixing everything at once requires dozens of successful LLM calls, which
    free providers can't deliver within one run's budget. One test class per
    run, persisted across runs, converges reliably.
    """
    candidates = set()
    for reasons in errors.get("pytest_failing", {}).values():
        for reason in reasons:
            m = re.search(r"tests failing in (\S+)", reason)
            if m:
                candidates.add(m.group(1))
    return sorted(candidates)[0] if candidates else None


def scope_to_test_file(all_failing, target_test_file):
    """Restrict the repair map to source files exercised by the target test."""
    try:
        tsrc = read_file(target_test_file)
    except FileNotFoundError:
        tsrc = ""
    related = {
        m.group(1).replace(".", "/") + ".py"
        for m in re.finditer(r"(?:from|import)\s+(src\.\w+)", tsrc)
    }
    scoped = {}
    for filepath, errs in all_failing.items():
        if filepath.startswith("tests/"):
            continue
        linked = any(target_test_file in reason for reason in errs)
        if filepath in related or linked:
            scoped[filepath] = errs
    return scoped


def fix_single_file(filepath, errors, is_import_fix=False, missing_names=None):
    """Try to fix a single file using LLM. Returns True if successful."""
    test_context = get_test_context(filepath)

    for attempt in range(1, MAX_FILE_ATTEMPTS + 1):
        if budget_exceeded():
            print(f"  ⏰ Time budget exhausted — skipping {filepath}")
            return False
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
            if not has_provider():
                print("  ⛔ No LLM provider left — aborting repair of remaining files.")
                return False
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

        # Backup original so a regression can be rolled back. Keeping broken
        # LLM output poisons the tree: static gates go red and the persist
        # step refuses to save ANY progress for the next run.
        backup = read_file(filepath) if os.path.exists(filepath) else None

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
            print(f"  ⚠️  Still {len(file_errors)} errors in {filepath} — rolling back")
            for e in file_errors[:3]:
                print(f"    {e.strip()}")
            if backup is None:
                os.remove(filepath)
            else:
                with open(filepath, "w") as f:
                    f.write(backup)
            _run(["uv", "run", "ruff", "format", "."])
            _run(["uv", "run", "black", "."])

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
or_key = os.environ.get("OPENROUTER_API_KEY", "")

if not api_key and not oc_key and not or_key:
    print("❌ No LLM API keys configured.")
    with open("/tmp/llm_result.json", "w") as f:
        json.dump({"success": False, "reason": "no_api_keys"}, f)
    sys.exit(0)

if not has_provider():
    print(
        "❌ All LLM providers failed or were disabled (quota/availability). "
        "Semantic fixes are impossible right now — deterministic fixes from this run are kept."
    )
    with open("/tmp/llm_result.json", "w") as f:
        json.dump({"success": False, "reason": "no_provider_available"}, f)
    sys.exit(0)

print(f"\n{'=' * 60}")
print(f"LLM Fallback: {len(all_failing)} files to fix")
print(f"{'=' * 60}")

# Scope this run to ONE failing test class. Static gates (ruff/black/mypy)
# are still repaired deterministically every run; semantic test fixes land
# incrementally, one class at a time, persisted on the healing branch.
target_test_file = select_target_test_file(errors)
if target_test_file:
    print(f"🎯 Target test class this run: {target_test_file}")
    all_failing = scope_to_test_file(all_failing, target_test_file)
    if all_failing:
        print(f"   Source files in scope: {', '.join(sorted(all_failing))}")
    else:
        print("   No source file in scope for this test class — nothing to fix via LLM.")
else:
    print("🎯 No failing test class detected — nothing to fix via LLM this run.")
    all_failing = {}

if not all_failing:
    with open("/tmp/llm_result.json", "w") as f:
        json.dump({"success": False, "reason": f"no_scope:{target_test_file}"}, f)
    sys.exit(0)

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
fixed_set = set()

for filepath in import_files:
    if budget_exceeded():
        print(f"\n⏰ Time budget exhausted ({budget_left():.0f}s left) — stopping LLM repair.")
        break
    if not has_provider():
        print("\n⛔ All LLM providers disabled — stopping LLM repair.")
        break
    missing_names = errors["pytest_imports"][filepath]
    print(f"\n📦 Fixing imports in {filepath}: {', '.join(missing_names)}")
    if fix_single_file(
        filepath, all_failing[filepath], is_import_fix=True, missing_names=missing_names
    ):
        fixed_count += 1
        fixed_set.add(filepath)
    else:
        failed_files.append(filepath)

# Then fix remaining source files
for filepath in source_files:
    if budget_exceeded():
        print(f"\n⏰ Time budget exhausted ({budget_left():.0f}s left) — stopping LLM repair.")
        break
    if not has_provider():
        print("\n⛔ All LLM providers disabled — stopping LLM repair.")
        break
    print(f"\n🔧 Fixing {filepath}: {len(all_failing[filepath])} errors")
    if fix_single_file(filepath, all_failing[filepath]):
        fixed_count += 1
        fixed_set.add(filepath)
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

# Gather final error state for report. Reuse the pre-repair error map plus
# the files the LLM could not fix; a second full gate sweep here cost several
# minutes of the step budget for one cosmetic number.
final_failing_files = sorted(set(failed_files) | {f for f in all_failing if f not in fixed_set})

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
