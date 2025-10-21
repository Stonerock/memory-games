import os
from typing import List, Dict, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

# Provider-agnostic wrapper (Anthropic first, OpenAI fallback).

class LLM:
    def __init__(self, model: Optional[str] = None, provider: Optional[str] = None, max_tokens: int = 2000):
        self.provider = provider or os.getenv("RB_LLM_PROVIDER", "anthropic")
        self.model = model or os.getenv("RB_MODEL", "")
        self.max_tokens = max_tokens

        if self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
                if not self.model:
                    # leave model unspecified so user can set; default commonly available model
                    self.model = os.getenv("RB_MODEL", "claude-3-5-sonnet-latest")
            except Exception as e:
                raise RuntimeError("Anthropic selected but anthropic package not available or API key missing.") from e
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
                if not self.model:
                    self.model = os.getenv("RB_MODEL", "gpt-4o-mini")
            except Exception as e:
                raise RuntimeError("OpenAI selected but openai package not available or API key missing.") from e
        else:
            raise ValueError("Unknown provider. Set RB_LLM_PROVIDER to 'anthropic' or 'openai'.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def complete(self, system: str, user: str) -> str:
        if self.provider == "anthropic":
            resp = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system,
                messages=[{"role": "user", "content": user}],
            )
            return "".join([c.text for c in resp.content if hasattr(c, "text")])
        else:
            # OpenAI
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                temperature=0.3,
                max_tokens=self.max_tokens,
            )
            return resp.choices[0].message.content.strip()
