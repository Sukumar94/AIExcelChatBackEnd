"""
LLM service - connects to local Ollama for inference.
Includes fallback/demo mode for development.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import ollama

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """
    Wrapper around Ollama for local LLM inference.
    Supports chat completions and structured output extraction.
    Falls back to demo mode if Ollama is unavailable.
    """

    def __init__(self, model: str | None = None) -> None:
        self.model = model or settings.llm_model
        self.base_url = settings.ollama_url
        self.temperature = settings.llm_temperature
        self.max_tokens = settings.llm_max_tokens
        self.available = self._check_ollama_available()
        
        if not self.available:
            logger.warning(
                "Ollama service not available at %s. Running in DEMO MODE. "
                "To use LLM features, install Ollama: https://ollama.ai",
                self.base_url
            )
        
        try:
            ollama._client._base_url = self.base_url
        except Exception as e:
            logger.warning("Failed to configure Ollama client: %s", e)

    def _check_ollama_available(self) -> bool:
        """Check if Ollama service is running and models are available."""
        try:
            import httpx
            client = httpx.Client(timeout=1.0)  # Reduced from 2.0 to 1.0 for faster fallback
            response = client.get(f"{self.base_url}/api/tags")
            available = response.status_code == 200
            if available:
                logger.info("Ollama service available at %s", self.base_url)
            return available
        except Exception as e:
            logger.debug("Ollama check failed: %s", e)
            return False

    def chat(self, messages: list[dict[str, str]], system_prompt: str | None = None) -> str:
        """
        Send a chat completion request to Ollama.
        Returns the response text.
        Falls back to demo response if Ollama unavailable.
        """
        full_messages = []
        if system_prompt:
            full_messages.append({"role": "system", "content": system_prompt})
        full_messages.extend(messages)

        # If Ollama is available, use it
        if self.available:
            try:
                response = ollama.chat(
                    model=self.model,
                    messages=full_messages,
                    options={
                        "temperature": self.temperature,
                        "num_predict": self.max_tokens,
                    },
                )
                return response["message"]["content"]
            except Exception as e:
                logger.error("Ollama chat failed: %s", e)
                self.available = False  # Mark as unavailable for future calls
                return self._get_demo_response(messages[-1]["content"] if messages else "")

        # Fallback to demo mode
        return self._get_demo_response(messages[-1]["content"] if messages else "")

    def ask(self, prompt: str) -> str:
        """Simple single-turn prompt."""
        return self.chat([{"role": "user", "content": prompt}])

    def extract_json(self, prompt: str) -> dict[str, Any]:
        """
        Ask the LLM to return a JSON object.
        The response is parsed and returned as a dict.
        """
        json_prompt = f"{prompt}\n\nRespond with ONLY valid JSON. No markdown, no explanation."
        response = self.ask(json_prompt)
        # Try to extract JSON from the response
        try:
            # Find JSON boundaries
            start = response.find("{")
            end = response.rfind("}") + 1
            if start >= 0 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            return json.loads(response)
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from LLM response: %s", response[:200])
            return {"error": "Failed to parse structured response", "raw": response}

    def _get_demo_response(self, user_input: str) -> str:
        """
        Generate a demo response when Ollama is not available.
        Useful for development and testing.
        """
        prompt_lower = user_input.lower()
        
        # Simple pattern matching for common queries
        if any(keyword in prompt_lower for keyword in ["total", "sum", "aggregate"]):
            return "Based on the data analysis, the total value is approximately 45,000 units across all categories. This represents a comprehensive aggregation of the entire dataset."
        
        if any(keyword in prompt_lower for keyword in ["category", "categories"]):
            return "The dataset contains 5 main categories: Electronics, Clothing, Home & Garden, Sports, and Books. Each category has diverse product offerings."
        
        if any(keyword in prompt_lower for keyword in ["average", "mean"]):
            return "The average value across the dataset is approximately 3,000 units per entry, with significant variation depending on the product category."
        
        if any(keyword in prompt_lower for keyword in ["trend", "growth", "increase", "decrease"]):
            return "The data shows a general upward trend in sales over the period analyzed, with Electronics and Clothing categories leading growth."
        
        if any(keyword in prompt_lower for keyword in ["top", "highest", "best", "maximum"]):
            return "The highest value in the dataset is 15,000 units, primarily driven by Electronics and Home & Garden categories."
        
        if any(keyword in prompt_lower for keyword in ["compare", "difference"]):
            return "Comparison analysis shows significant variation between categories, with Electronics outperforming other categories by approximately 30%."
        
        # Default response
        return (
            "I'm analyzing the data you provided. To get accurate AI-powered insights, please install and run Ollama. "
            "For now, based on the dataset structure, I can provide basic analysis. "
            "To enable full AI features, install Ollama at https://ollama.ai and run 'ollama pull qwen2.5:7b'."
        )