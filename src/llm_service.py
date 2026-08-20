"""LLM Service module for interacting with OpenAI and Google Gemini models."""

import os
import logging
from typing import Any, Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class LLMService:
    """Service class for handling interactions with Large Language Models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gpt-4o",
        provider: str = "openai",
    ) -> None:
        """Initialize the LLM Service.

        Args:
            api_key: Optional API key for the model provider.
            model_name: Name of the model to use.
            provider: Provider name ('openai' or 'gemini').
        """
        self.api_key = (
            api_key or os.getenv("OPENAI_API_KEY") or os.getenv("GEMINI_API_KEY")
        )
        self.model_name = model_name
        self.provider = provider.lower()

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def generate_completion(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = 1000,
    ) -> str:
        """Generate text completion using the configured LLM provider.

        Args:
            prompt: The input user prompt.
            system_instruction: Optional system prompt to guide behavior.
            temperature: Sampling temperature for output generation.
            max_tokens: Maximum number of tokens to generate.

        Returns:
            The generated string response from the model.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        logger.info(
            "Generating completion using provider=%s, model=%s",
            self.provider,
            self.model_name,
        )

        try:
            if self.provider == "openai":
                return self._generate_openai(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            elif self.provider in ("gemini", "google"):
                return self._generate_gemini(
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            else:
                raise ValueError(f"Unsupported LLM provider: {self.provider}")
        except Exception as err:
            logger.error("Failed to generate completion from LLM: %s", err)
            raise

    def _generate_openai(
        self,
        prompt: str,
        system_instruction: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
    ) -> str:
        """Generate response via OpenAI API."""
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            messages: List[Dict[str, str]] = []

            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})

            messages.append({"role": "user", "content": prompt})

            response = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            content = response.choices[0].message.content
            return content.strip() if content else ""
        except ImportError:
            logger.warning("OpenAI package not available, returning mock response.")
            return f"[Mock OpenAI Response] Prompt: {prompt[:50]}..."

    def _generate_gemini(
        self,
        prompt: str,
        system_instruction: Optional[str],
        temperature: float,
        max_tokens: Optional[int],
    ) -> str:
        """Generate response via Google Gemini API."""
        try:
            from google import genai

            client = genai.Client(api_key=self.api_key)
            full_prompt = (
                f"{system_instruction}\n\n{prompt}"
                if system_instruction
                else prompt
            )

            response = client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
            )

            return response.text.strip() if response.text else ""
        except ImportError:
            logger.warning("Google GenAI package not available, returning mock response.")
            return f"[Mock Gemini Response] Prompt: {prompt[:50]}..."

    def summarize(self, text: str, max_length: int = 200) -> str:
        """Summarize given text content using LLM.

        Args:
            text: The text content to summarize.
            max_length: Target word/token length for summary.

        Returns:
            Summarized string output.
        """
        system_prompt = (
            f"You are a concise summarizer. Summarize the text in under {max_length} words."
        )
        return self.generate_completion(prompt=text, system_instruction=system_prompt)
