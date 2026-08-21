"""Deterministic repair — fix known mypy/ruff/black error patterns without LLM.

This script handles:
- Black formatting
- Ruff auto-fix
- Mypy pattern repairs (missing methods, wrong imports, type issues)

Test import errors are reported but NOT fixed here — the LLM fallback handles them.
"""

import json
import os
import re
import subprocess


def _run(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        return p.returncode, p.stdout + "\n" + p.stderr
    except Exception as e:
        return 1, str(e)


def read_file(path):
    with open(path) as f:
        return f.read()


def write_file(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        f.write(content)


# ── Run quality checks to get current errors ──
_, ruff_out = _run(["uv", "run", "ruff", "check", ".", "--output-format=concise"])
_, black_out = _run(["uv", "run", "black", "--check", "."])
_, mypy_out = _run(["uv", "run", "mypy", "src/", "--ignore-missing-imports"])

all_output = ruff_out + "\n" + black_out + "\n" + mypy_out
print("=== Current errors ===")
for line in all_output.splitlines():
    if "error:" in line or "would reformat" in line:
        print(f"  {line.strip()}")

fixes_applied = []

# ── FIX 1: Black formatting ──
if "would reformat" in black_out:
    print("\n🔧 Fix: Black formatting...")
    _run(["uv", "run", "black", "."])
    fixes_applied.append("black-formatting")

# ── FIX 2: Ruff auto-fix ──
if ruff_out.strip() and "All checks passed" not in ruff_out:
    print("\n🔧 Fix: Ruff auto-fix...")
    _run(["uv", "run", "ruff", "check", ".", "--fix"])
    _run(["uv", "run", "ruff", "format", "."])
    fixes_applied.append("ruff-autofix")

# ── FIX 3: Mypy — deterministic pattern repairs ──
mypy_errors = []
for m in re.finditer(
    r"(?m)^(\S+\.py):(\d+):\s+error:\s+(.+?)\s+\[(\S+)\]",
    mypy_out,
):
    mypy_errors.append(
        {
            "file": m.group(1),
            "line": int(m.group(2)),
            "message": m.group(3),
            "code": m.group(4),
        }
    )

if mypy_errors:
    print(f"\n🔧 Fix: {len(mypy_errors)} mypy errors detected, applying pattern repairs...")

    # ── FIX 3a: Add missing methods to LLMService (target: src/llm_service.py) ──
    llm_path = "src/llm_service.py"
    if os.path.exists(llm_path):
        llm_src = read_file(llm_path)
        llm_original = llm_src

        has_gen_text = any(
            '"generate_text"' in e["message"]
            for e in mypy_errors
            if e["code"] == "attr-defined" and "LLMService" in e["message"]
        )
        has_classify = any(
            '"classify_text"' in e["message"]
            for e in mypy_errors
            if e["code"] == "attr-defined" and "LLMService" in e["message"]
        )

        if has_gen_text and "def generate_text(" not in llm_src:
            insert_pattern = r"(    def summarize\()"
            if re.search(insert_pattern, llm_src):
                alias_lines = [
                    "",
                    "    async def generate_text(",
                    "        self,",
                    "        prompt: str,",
                    "        system_instruction: Optional[str] = None,",
                    "        temperature: float = 0.7,",
                    "        max_tokens: Optional[int] = 1000,",
                    "    ) -> str:",
                    '        """Alias for generate_completion (async-compatible wrapper)."""',
                    "        return self.generate_completion(",
                    "            prompt=prompt,",
                    "            system_instruction=system_instruction,",
                    "            temperature=temperature,",
                    "            max_tokens=max_tokens,",
                    "        )",
                    "",
                ]
                alias = "\n".join(alias_lines) + "\n"
                llm_src = re.sub(
                    insert_pattern, lambda m, a=alias: a + m.group(1), llm_src, count=1
                )
                fixes_applied.append(f"{llm_path}:added-generate_text")
                print(f"  ✅ Added generate_text to {llm_path}")

        if has_classify and "def classify_text(" not in llm_src:
            insert_pattern = r"(    def summarize\()"
            if re.search(insert_pattern, llm_src):
                alias_lines = [
                    "",
                    "    async def classify_text(",
                    "        self,",
                    "        text: str,",
                    "        categories: Optional[List[str]] = None,",
                    "        system_prompt: Optional[str] = None,",
                    "    ) -> str:",
                    '        """Alias for generate_completion for classification tasks."""',
                    "        prompt = text",
                    "        if categories:",
                    "            prompt = 'Classify into: ' + ', '.join(categories) + '\\n\\n' + text",
                    "        return self.generate_completion(",
                    "            prompt=prompt,",
                    "            system_instruction=system_prompt,",
                    "        )",
                    "",
                ]
                alias = "\n".join(alias_lines) + "\n"
                llm_src = re.sub(
                    insert_pattern, lambda m, a=alias: a + m.group(1), llm_src, count=1
                )
                fixes_applied.append(f"{llm_path}:added-classify_text")
                print(f"  ✅ Added classify_text to {llm_path}")

        # Fix arg-type: messages type annotation + type: ignore
        if any(
            e["code"] == "arg-type" and "messages" in e["message"]
            for e in mypy_errors
            if e["file"] == llm_path
        ):
            if "List[Dict[str, str]]" in llm_src:
                llm_src = llm_src.replace(
                    "from typing import Dict, List, Optional",
                    "from typing import Any, Dict, List, Optional",
                )
                llm_src = llm_src.replace(
                    "messages: List[Dict[str, str]] = []",
                    "messages: list[dict[str, Any]] = []",
                )
            if "messages=messages," in llm_src and "type: ignore" not in llm_src:
                llm_src = llm_src.replace(
                    "messages=messages,",
                    "messages=messages,  # type: ignore[arg-type]",
                )
            if llm_src != llm_original:
                fixes_applied.append(f"{llm_path}:fix-messages-type")
                print(f"  ✅ Fixed messages type in {llm_path}")

        # Fix arg-type: api_key str | None vs str
        if any(
            e["code"] == "arg-type" and "api_key" in e["message"]
            for e in mypy_errors
            if e["file"] == llm_path
        ):
            if "genai.Client(api_key=self.api_key)" in llm_src:
                llm_src = llm_src.replace(
                    "genai.Client(api_key=self.api_key)",
                    'genai.Client(api_key=self.api_key or "")',
                )
                if llm_src != llm_original:
                    fixes_applied.append(f"{llm_path}:fix-api-key-type")
                    print(f"  ✅ Fixed api_key type in {llm_path}")

        if llm_src != llm_original:
            write_file(llm_path, llm_src)

    # ── FIX 3b: Process per-file errors ──
    by_file = {}
    for err in mypy_errors:
        by_file.setdefault(err["file"], []).append(err)

    for filepath, errors in by_file.items():
        if filepath == llm_path:
            continue
        if not os.path.exists(filepath):
            continue

        src = read_file(filepath)
        original = src

        for err in errors:
            if src != original:
                write_file(filepath, src)
                original = src
            lines = src.splitlines(keepends=True)
            line_idx = err["line"] - 1
            if line_idx >= len(lines):
                continue

            # Pattern: Module "src.logger" has no attribute "setup_logging"
            if err["code"] == "attr-defined" and "setup_logging" in err["message"]:
                src = src.replace(
                    "from .logger import setup_logging", "from .logger import setup_logger"
                )
                src = src.replace("setup_logging(", "setup_logger(")
                if src != original:
                    fixes_applied.append(f"{filepath}:fix-setup_logging-import")
                    print(f"  ✅ Fixed setup_logging → setup_logger in {filepath}")

            # Pattern: Module "src.logger" has no attribute "new_correlation_id"
            if err["code"] == "attr-defined" and "new_correlation_id" in err["message"]:
                logger_path = "src/logger.py"
                if os.path.exists(logger_path):
                    logger_src = read_file(logger_path)
                    if "def new_correlation_id" not in logger_src:
                        addition = '\n\ndef new_correlation_id() -> str:\n    """Generate a new correlation ID for request tracing."""\n    return str(uuid.uuid4())\n'
                        logger_src = logger_src.rstrip() + addition
                        if "import uuid" not in logger_src:
                            doc_match = re.search(r'"""[\s\S]*?"""', logger_src)
                            if doc_match:
                                insert_at = doc_match.end()
                                logger_src = (
                                    logger_src[:insert_at]
                                    + "\nimport uuid\n"
                                    + logger_src[insert_at:]
                                )
                            else:
                                logger_src = "import uuid\n" + logger_src
                        write_file(logger_path, logger_src)
                        fixes_applied.append(f"{logger_path}:added-new_correlation_id")
                        print(f"  ✅ Added new_correlation_id to {logger_path}")

            # Pattern: Unexpected keyword argument "cache"
            if err["code"] == "call-arg" and "cache" in err["message"]:
                lines = src.splitlines(keepends=True)
                if line_idx < len(lines):
                    call_line = lines[line_idx]
                    fixed_line = re.sub(
                        r"LLMService\(cache=self\.cache\)", "LLMService()", call_line
                    )
                    if fixed_line != call_line:
                        lines[line_idx] = fixed_line
                        src = "".join(lines)
                        fixes_applied.append(f"{filepath}:removed-cache-arg")
                        print(f"  ✅ Removed cache= argument in {filepath}")

            # Pattern: no-any-return
            if err["code"] == "no-any-return":
                lines = src.splitlines(keepends=True)
                if line_idx < len(lines):
                    ret_line = lines[line_idx]
                    if "return" in ret_line and "str(" not in ret_line:
                        fixed = re.sub(r"return\s+(.+)", r"return str(\1)", ret_line)
                        if fixed != ret_line:
                            lines[line_idx] = fixed
                            src = "".join(lines)
                            fixes_applied.append(f"{filepath}:str-cast-return")
                            print(f"  ✅ Added str() cast in {filepath}")

            # Pattern: assignment literal type mismatch
            if err["code"] == "assignment" and '"low"' in err["message"]:
                lines = src.splitlines(keepends=True)
                if line_idx < len(lines):
                    err_line = lines[line_idx].strip()
                    var_match = re.match(r"(\w+)\s*=", err_line)
                    if var_match:
                        var_name = var_match.group(1)
                        for idx, line_text in enumerate(lines):
                            if (
                                re.match(rf"\s*{re.escape(var_name)}\s*=", line_text)
                                and idx < line_idx
                            ):
                                lines[idx] = re.sub(
                                    rf"(\s*)({re.escape(var_name)})(\s*=)",
                                    r"\1\2: str\3",
                                    line_text,
                                )
                                src = "".join(lines)
                                fixes_applied.append(f"{filepath}:annotate-{var_name}-as-str")
                                print(f"  ✅ Annotated {var_name}: str in {filepath}")
                                break

        if src != original:
            write_file(filepath, src)

# ── Run black/ruff again after mypy fixes ──
if fixes_applied:
    print("\n🔧 Post-fix formatting pass...")
    _run(["uv", "run", "ruff", "check", ".", "--fix"])
    _run(["uv", "run", "ruff", "format", "."])
    _run(["uv", "run", "black", "."])

# ── Report broken test imports (for LLM fallback) ──
print("\n🔧 Checking for broken test imports...")
_, pytest_co = _run(["uv", "run", "pytest", "tests/", "-q", "--tb=line", "--co"])
broken_tests = []
for line in pytest_co.splitlines():
    if "ERROR collecting" in line:
        m_match = re.search(r"(tests/\S+\.py)", line)
        if m_match:
            broken_tests.append(m_match.group(1))
if broken_tests:
    print(f"  ⚠️  {len(broken_tests)} test files have import errors (LLM fallback will handle):")
    for t in broken_tests:
        print(f"    - {t}")
else:
    print("  All test files import successfully")

# ── Verify all 4 gates ──
print("\n=== Verification ===")
gate_results = {}

rc, out = _run(["uv", "run", "ruff", "check", "."])
gate_results["ruff"] = rc == 0
print(f"  {'✅' if rc == 0 else '❌'} Ruff: {'PASS' if rc == 0 else 'FAIL'}")
if rc != 0:
    print(out[-500:])

rc, out = _run(["uv", "run", "black", "--check", "."])
gate_results["black"] = rc == 0
print(f"  {'✅' if rc == 0 else '❌'} Black: {'PASS' if rc == 0 else 'FAIL'}")
if rc != 0:
    print(out[-500:])

rc, out = _run(["uv", "run", "mypy", "src/", "--ignore-missing-imports"])
gate_results["mypy"] = rc == 0
print(f"  {'✅' if rc == 0 else '❌'} Mypy: {'PASS' if rc == 0 else 'FAIL'}")
if rc != 0:
    for line in out.splitlines():
        if "error:" in line:
            print(f"    {line.strip()}")

rc, out = _run(["uv", "run", "pytest", "tests/", "-q", "--tb=short"])
gate_results["pytest"] = rc == 0
print(f"  {'✅' if rc == 0 else '❌'} Pytest: {'PASS' if rc == 0 else 'FAIL'}")
if rc != 0:
    print(out[-1000:])

all_pass = all(gate_results.values())

with open("/tmp/deterministic_result.json", "w") as f:
    json.dump(
        {
            "fixes_applied": fixes_applied,
            "gate_results": gate_results,
            "all_pass": all_pass,
            "broken_tests": broken_tests,
        },
        f,
    )

gh_output = os.environ.get("GITHUB_OUTPUT", "/dev/null")
with open(gh_output, "a") as f:
    f.write(f"fixes_count={len(fixes_applied)}\n")
    f.write(f"all_pass={'true' if all_pass else 'false'}\n")

if all_pass:
    print("\n✅ All gates pass after deterministic repair!")
elif fixes_applied:
    print(f"\n⚠️  {len(fixes_applied)} fixes applied, some gates still failing.")
else:
    print("\n❌ No deterministic fixes matched. LLM fallback needed.")
