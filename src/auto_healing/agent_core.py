"""Cognitive LLM orchestration layer for the Auto-Healing Agent.

Implements the decision engine using LangChain for structured root
cause analysis and incremental code correction. Includes robust JSON
parsing with markdown sanitization and comprehensive error handling
for all LLM interactions.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from .models import IncrementalCorrection, RootCauseAnalysis

logger = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────────

SYSTEM_PROMPT_ROOT_CAUSE_ANALYSIS: str = """You are an expert DevOps engineer and
Python developer specializing in CI/CD pipeline failure diagnosis.

Your task is to analyze a failed GitHub Actions workflow log and provide:
1. A precise root cause summary
2. The exact file path that needs correction
3. The complete corrected file content
4. A technical explanation of the changes

You MUST respond with a valid JSON object in exactly this structure:
{{
    "root_cause_summary": "One paragraph summarizing the root cause",
    "affected_file_path": "relative/path/to/file.py",
    "corrected_code": "full corrected file content here",
    "explanation": "Technical explanation of what was changed and why"
}}

CRITICAL RULES:
- Respond ONLY with the JSON object. No markdown fences, no preamble, no trailing text.
- The corrected_code must be the COMPLETE file, not a diff or snippet.
- Ensure the corrected_code is syntactically valid Python.
- Do not add or remove dependencies unless absolutely necessary.
- Preserve all existing functionality while fixing the failure."""

SYSTEM_PROMPT_INCREMENTAL_FIX: str = """You are an expert Python developer fixing
a test failure in an auto-healing CI/CD pipeline.

A previous code correction was applied but failed during testing. You must
analyze the test failure and provide an incremental fix.

You MUST respond with a valid JSON object in exactly this structure:
{{
    "corrected_code": "full corrected file content here",
    "analysis_of_previous_failure": "Why the previous correction failed the tests",
    "changes_description": "What was changed in this iteration"
}}

CRITICAL RULES:
- Respond ONLY with the JSON object. No markdown fences, no preamble, no trailing text.
- The corrected_code must be the COMPLETE file, not a diff or snippet.
- Focus on making the test pass while preserving the intended fix.
- If the test itself is wrong, still fix the source code to satisfy it."""

# ── JSON Parser Utilities ───────────────────────────────────────────


def _sanitize_llm_json_output(raw_output: str) -> str:
    """Remove markdown code fences and extraneous formatting from LLM output.

    LLMs often wrap JSON responses in `````json ... ````` fences. This function
    strips those fences and any leading/trailing whitespace to produce clean
    JSON for parsing.

    Args:
        raw_output: Raw string output from the LLM.

    Returns:
        Cleaned JSON string ready for ``json.loads()``.
    """
    if not raw_output:
        return "{}"

    sanitized: str = raw_output.strip()

    # Remove markdown code fences (```json ... ``` or ``` ... ```)
    sanitized = re.sub(
        r"^```(?:json)?\s*\n?",
        "",
        sanitized,
        flags=re.MULTILINE,
    )
    sanitized = re.sub(
        r"\n?```\s*$",
        "",
        sanitized,
        flags=re.MULTILINE,
    )

    return sanitized.strip()


def _parse_json_safely(raw_output: str) -> dict[str, Any] | None:
    """Parse JSON from LLM output with multiple fallback strategies.

    Attempts direct parsing first, then tries to find JSON within
    the raw text using pattern matching.

    Args:
        raw_output: Raw string output from the LLM.

    Returns:
        Parsed dictionary if successful, None on failure.
    """
    if not raw_output:
        logger.warning("Received empty LLM output for JSON parsing.")
        return None

    sanitized = _sanitize_llm_json_output(raw_output)

    # Strategy 1: Direct parse
    try:
        parsed: dict[str, Any] = json.loads(sanitized)
        return parsed
    except json.JSONDecodeError:
        pass

    # Strategy 2: Find the first { ... } block
    brace_match = re.search(r"\{.*\}", sanitized, re.DOTALL)
    if brace_match:
        try:
            parsed = json.loads(brace_match.group(0))
            return parsed
        except json.JSONDecodeError:
            pass

    logger.error(
        "Failed to parse JSON from LLM output. First 200 chars: %s",
        sanitized[:200],
    )
    return None


# ── Agent Core ──────────────────────────────────────────────────────


class AgentCore:
    """LLM-powered decision engine for the auto-healing workflow.

    Uses LangChain with Google Generative AI to perform root cause
    analysis on pipeline failures and generate corrected code.

    Attributes:
        _llm: The LangChain LLM instance.
    """

    def __init__(
        self,
        google_api_key: str,
        model_name: str = "gemini-2.0-flash",
        temperature: float = 0.1,
    ) -> None:
        """Initialize the agent core with LLM configuration.

        Args:
            google_api_key: Google AI API key for Gemini access.
            model_name: The model to use for analysis.
            temperature: LLM temperature (low for deterministic output).

        Raises:
            ValueError: If the API key is empty or None.
        """
        if not google_api_key:
            raise ValueError("Google API key must not be empty.")

        self._llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=google_api_key,
            temperature=temperature,
            max_output_tokens=8192,
        )

    # ── Root Cause Analysis ─────────────────────────────────────────

    def analyze_pipeline_failure(
        self,
        workflow_log_text: str,
        repository_context: str = "",
    ) -> RootCauseAnalysis | None:
        """Analyze a failed pipeline log and generate a corrective code fix.

        Sends the workflow log to the LLM with a system prompt that forces
        structured JSON output, then parses and validates the response.

        Args:
            workflow_log_text: Raw concatenated log text from the failed run.
            repository_context: Optional context about the repository structure.

        Returns:
            RootCauseAnalysis if successful, None on any failure.
        """
        if not workflow_log_text:
            logger.error("Cannot analyze empty workflow log.")
            return None

        # Truncate extremely long logs to fit context window
        max_log_length: int = 30000
        truncated_log: str = workflow_log_text[:max_log_length]
        if len(workflow_log_text) > max_log_length:
            logger.warning(
                "Workflow log truncated from %d to %d characters.",
                len(workflow_log_text),
                max_log_length,
            )

        messages = [
            SystemMessage(content=SYSTEM_PROMPT_ROOT_CAUSE_ANALYSIS),
            HumanMessage(
                content=(
                    f"## Repository Context\n{repository_context}\n\n"
                    f"## Failed Workflow Log\n```\n{truncated_log}\n```"
                )
            ),
        ]

        raw_response = self._invoke_llm(messages)
        if raw_response is None:
            return None

        parsed_response = _parse_json_safely(raw_response)
        if parsed_response is None:
            return None

        return self._build_root_cause_analysis(parsed_response)

    def _build_root_cause_analysis(
        self,
        parsed_data: dict[str, Any],
    ) -> RootCauseAnalysis | None:
        """Construct a RootCauseAnalysis from parsed LLM output.

        Args:
            parsed_data: Dictionary parsed from LLM JSON output.

        Returns:
            Validated RootCauseAnalysis, or None if required fields are missing.
        """
        root_cause_summary = parsed_data.get("root_cause_summary", "")
        affected_file_path = parsed_data.get("affected_file_path", "")
        corrected_code = parsed_data.get("corrected_code", "")
        explanation = parsed_data.get("explanation", "")

        if not corrected_code:
            logger.error("LLM response missing 'corrected_code' field.")
            return None

        if not affected_file_path:
            logger.error("LLM response missing 'affected_file_path' field.")
            return None

        return RootCauseAnalysis(
            root_cause_summary=str(root_cause_summary),
            affected_file_path=str(affected_file_path),
            corrected_code=str(corrected_code),
            explanation=str(explanation),
        )

    # ── Incremental Fix Processing ──────────────────────────────────

    def process_subsequent_correction(
        self,
        current_file_content: str,
        test_failure_log: str,
        file_path: str,
        previous_analysis: str = "",
    ) -> IncrementalCorrection | None:
        """Generate an incremental code fix based on test failure analysis.

        Used when a previous auto-healing correction failed its tests.
        Analyzes the pytest output and generates a refined correction.

        Args:
            current_file_content: The current (failing) file content.
            test_failure_log: Pytest output showing the test failure.
            file_path: Path to the file being corrected.
            previous_analysis: Context about the previous correction attempt.

        Returns:
            IncrementalCorrection if successful, None on any failure.
        """
        if not current_file_content:
            logger.error("Cannot process correction for empty file content.")
            return None

        if not test_failure_log:
            logger.error("Cannot process correction with empty test log.")
            return None

        messages = [
            SystemMessage(content=SYSTEM_PROMPT_INCREMENTAL_FIX),
            HumanMessage(
                content=(
                    f"## File Being Corrected\n`{file_path}`\n\n"
                    f"## Current File Content\n```python\n{current_file_content}\n```\n\n"
                    f"## Test Failure Log\n```\n{test_failure_log[:15000]}\n```\n\n"
                    f"## Previous Analysis\n{previous_analysis}"
                )
            ),
        ]

        raw_response = self._invoke_llm(messages)
        if raw_response is None:
            return None

        parsed_response = _parse_json_safely(raw_response)
        if parsed_response is None:
            return None

        return self._build_incremental_correction(parsed_response)

    def _build_incremental_correction(
        self,
        parsed_data: dict[str, Any],
    ) -> IncrementalCorrection | None:
        """Construct an IncrementalCorrection from parsed LLM output.

        Args:
            parsed_data: Dictionary parsed from LLM JSON output.

        Returns:
            Validated IncrementalCorrection, or None if required fields are missing.
        """
        corrected_code = parsed_data.get("corrected_code", "")
        analysis_of_previous_failure = parsed_data.get("analysis_of_previous_failure", "")
        changes_description = parsed_data.get("changes_description", "")

        if not corrected_code:
            logger.error("LLM incremental response missing 'corrected_code' field.")
            return None

        return IncrementalCorrection(
            corrected_code=str(corrected_code),
            analysis_of_previous_failure=str(analysis_of_previous_failure),
            changes_description=str(changes_description),
        )

    # ── LLM Invocation ──────────────────────────────────────────────

    def _invoke_llm(self, messages: list[Any]) -> str | None:
        """Invoke the LLM with error handling and response extraction.

        Args:
            messages: List of LangChain message objects.

        Returns:
            Response content string if successful, None on failure.
        """
        try:
            response = self._llm.invoke(messages)
        except (ValueError, RuntimeError, ConnectionError, TimeoutError) as error:
            logger.error("LLM invocation failed: %s", error)
            return None

        if response is None:
            logger.error("LLM returned None response.")
            return None

        content = getattr(response, "content", None)
        if not content:
            logger.error("LLM response has empty content.")
            return None

        return str(content)
