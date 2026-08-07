"""Code snippet generator for Salesforce features.

Generates Apex, LWC, Flow, and SOQL code examples
for new release features using LLM-powered templates.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Literal

logger = logging.getLogger(__name__)


@dataclass
class CodeSnippet:
    """A generated code snippet."""

    feature_name: str
    language: Literal["apex", "lwc", "soql", "flow", "javascript", "html"]
    title: str
    code: str
    description: str = ""
    prerequisites: list[str] | None = None


# ---------------------------------------------------------------------------
# Prompt templates for code generation
# ---------------------------------------------------------------------------

_CODE_SYSTEM_PROMPT = """You are a senior Salesforce developer and architect with deep expertise in:
- Apex (triggers, batch, queueable, invocable, REST/SOAP integrations)
- Lightning Web Components (wire service, imperative Apex, Lightning Data Service)
- SOQL/SOSL with advanced features
- Flow Builder (record-triggered, screen flows, subflows)
- Salesforce DX and development best practices

Generate production-ready, well-commented code examples that:
1. Follow Salesforce coding standards and best practices
2. Include proper error handling
3. Use meaningful variable/method names
4. Include inline comments explaining key decisions
5. Are compatible with the specified API version

Always respond with valid code, no markdown fences or explanations outside the code."""


def build_code_generation_prompt(
    feature_name: str,
    feature_description: str,
    language: str,
    context: str = "",
) -> tuple[str, str]:
    """Build prompts for code snippet generation.

    Args:
        feature_name: Name of the Salesforce feature.
        feature_description: Description of what the feature does.
        language: Target language (apex, lwc, soql, flow).
        context: Additional context (org type, API version, etc.).

    Returns:
        Tuple of (system_prompt, user_prompt).
    """
    user_prompt = f"""Generate a practical code example for the following Salesforce feature:

**Feature:** {feature_name}
**Description:** {feature_description}
**Language:** {language}
{f'**Context:** {context}' if context else ''}

Requirements:
- Include a clear title/comment at the top
- Add inline comments explaining the logic
- Handle common edge cases
- Follow Salesforce naming conventions
- Make it copy-paste ready"""

    return _CODE_SYSTEM_PROMPT, user_prompt


def parse_code_response(response: str, feature_name: str, language: str) -> CodeSnippet:
    """Parse LLM response into a CodeSnippet.

    Args:
        response: Raw LLM response.
        feature_name: Feature name for context.
        language: Target language.

    Returns:
        CodeSnippet instance.
    """
    # Clean up response
    code = response.strip()
    if code.startswith("```"):
        # Remove code fences
        lines = code.split("\n")
        code = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    # Extract title from first comment if present
    title = feature_name
    for line in code.split("\n")[:3]:
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("/**") or stripped.startswith("<!--"):
            title = stripped.lstrip("/ *<!-").strip()
            break

    return CodeSnippet(
        feature_name=feature_name,
        language=language,  # type: ignore[arg-type]
        title=title,
        code=code,
    )


# ---------------------------------------------------------------------------
# Template-based code generation (fallback)
# ---------------------------------------------------------------------------

_APEX_TEMPLATES: dict[str, str] = {
    "trigger": """// Trigger for {feature_name}
// {description}

trigger {object}Trigger on {object} (before insert, before update, after insert, after update) {{
    if (Trigger.isBefore) {{
        if (Trigger.isInsert || Trigger.isUpdate) {{
            // Process before insert/update logic
            for ({object} record : Trigger.new) {{
                // Add your logic here
            }}
        }}
    }}

    if (Trigger.isAfter) {{
        if (Trigger.isInsert) {{
            // Process after insert logic
        }}
    }}
}}""",
    "batch": """// Batch Apex for {feature_name}
// {description}

public class {className} implements Database.Batchable<sObject>, Database.Stateful {{
    public Integer recordsProcessed = 0;

    public Database.QueryLocator start(Database.BatchableContext bc) {{
        return Database.getQueryLocator([
            SELECT Id, Name FROM {object} WHERE CreatedDate = TODAY
        ]);
    }}

    public void execute(Database.BatchableContext bc, List<{object}> scope) {{
        for ({object} record : scope) {{
            // Process each record
            recordsProcessed++;
        }}
    }}

    public void finish(Database.BatchableContext bc) {{
        System.debug('Records processed: ' + recordsProcessed);
    }}
}}""",
    "invocable": """// Invocable Method for {feature_name}
// {description}

public class {className} {{
    @InvocableMethod(label='{feature_name}' description='{description}')
    public static List<Result> execute(List<Request> requests) {{
        List<Result> results = new List<Result>();

        for (Request req : requests) {{
            Result res = new Result();
            // Process request
            results.add(res);
        }}

        return results;
    }}

    public class Request {{
        @InvocableVariable(label='Input' required=true)
        public String input;
    }}

    public class Result {{
        @InvocableVariable(label='Output')
        public String output;
    }}
}}""",
}

_LWC_TEMPLATES: dict[str, str] = {
    "component": """// {feature_name} - Lightning Web Component
// {description}

import {{ LightningElement, api, wire, track }} from 'lwc';
import {{ getRecord }} from 'lightning/uiRecordApi';

export default class {className} extends LightningElement {{
    @api recordId;
    @track data;
    @track error;

    @wire(getRecord, {{ recordId: '$recordId', fields: [] }})
    wiredRecord({{ error, data }}) {{
        if (data) {{
            this.data = data;
            this.error = undefined;
        }} else if (error) {{
            this.error = error;
            this.data = undefined;
        }}
    }}

    handleClick() {{
        // Handle user interaction
    }}
}}""",
    "apex_controller": """// Apex Controller for {feature_name} LWC
// {description}

public with sharing class {className}Controller {{
    @AuraEnabled(cacheable=true)
    public static List<{object}> getData(String recordId) {{
        try {{
            return [
                SELECT Id, Name
                FROM {object}
                WHERE Id = :recordId
            ];
        }} catch (Exception e) {{
            throw new AuraHandledException(e.getMessage());
        }}
    }}
}}""",
}

_SOQL_TEMPLATES: dict[str, str] = {
    "query": """-- SOQL Query for {feature_name}
-- {description}

SELECT Id, Name, CreatedDate, LastModifiedDate
FROM {object}
WHERE CreatedDate = LAST_N_DAYS:30
ORDER BY CreatedDate DESC
LIMIT 200""",
}


def generate_template_snippet(
    feature_name: str,
    description: str,
    language: str,
    template_key: str,
    **kwargs: str,
) -> CodeSnippet:
    """Generate a code snippet from a template.

    Args:
        feature_name: Feature name.
        description: Feature description.
        language: Target language (apex, lwc, soql).
        template_key: Template key within the language.
        **kwargs: Template variables.

    Returns:
        CodeSnippet instance.
    """
    templates = {
        "apex": _APEX_TEMPLATES,
        "lwc": _LWC_TEMPLATES,
        "soql": _SOQL_TEMPLATES,
    }

    lang_templates = templates.get(language, {})
    template = lang_templates.get(template_key, f"// {feature_name}\n// TODO: Implement")

    # Fill template variables
    defaults = {
        "feature_name": feature_name,
        "description": description,
        "object": "Account",
        "className": feature_name.replace(" ", ""),
    }
    defaults.update(kwargs)

    try:
        code = template.format(**defaults)
    except KeyError:
        code = template

    return CodeSnippet(
        feature_name=feature_name,
        language=language,  # type: ignore[arg-type]
        title=f"{feature_name} - {language.upper()}",
        code=code,
        description=description,
    )


def generate_code_section(snippets: list[CodeSnippet]) -> str:
    """Generate a Markdown section with code snippets.

    Args:
        snippets: List of CodeSnippet instances.

    Returns:
        Markdown string with code examples.
    """
    if not snippets:
        return ""

    lines = ["## 💻 Exemplos de Código\n"]

    for snippet in snippets:
        lang_map = {
            "apex": "java",
            "lwc": "javascript",
            "soql": "sql",
            "flow": "text",
            "javascript": "javascript",
            "html": "html",
        }
        md_lang = lang_map.get(snippet.language, snippet.language)

        lines.append(f"### {snippet.title}\n")
        if snippet.description:
            lines.append(f"_{snippet.description}_\n")
        lines.append(f"```{md_lang}")
        lines.append(snippet.code)
        lines.append("```\n")

        if snippet.prerequisites:
            lines.append("**Pré-requisitos:**")
            for prereq in snippet.prerequisites:
                lines.append(f"- {prereq}")
            lines.append("")

    return "\n".join(lines)
