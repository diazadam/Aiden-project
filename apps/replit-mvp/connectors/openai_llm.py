"""
OpenAI connector with retry, timeout, and cost estimation.
"""
from __future__ import annotations
import os
import time
from typing import Optional
from openai import OpenAI
from .base import BaseLLM, ProviderCallResult, _now_ms

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class OpenAIChat(BaseLLM):
    """OpenAI ChatGPT connector with built-in retry and error handling"""
    
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model_name = model
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable required")
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def complete(self, prompt: str, system: Optional[str] = None) -> ProviderCallResult:
        """Complete a prompt using OpenAI's chat completion API"""
        t0 = _now_ms()
        try:
            msgs = []
            if system: 
                msgs.append({"role": "system", "content": system})
            msgs.append({"role": "user", "content": prompt})
            
            resp = self.client.chat.completions.create(
                model=self.model_name, 
                messages=msgs, 
                temperature=0.2
            )
            
            text = resp.choices[0].message.content
            
            # Rough cost estimate (tokens * rate)
            # These are approximate rates, update based on current pricing
            cost_estimate = 0.0
            if hasattr(resp, 'usage') and resp.usage:
                input_tokens = resp.usage.prompt_tokens
                output_tokens = resp.usage.completion_tokens
                
                # Rough pricing estimates (update as needed)
                if "gpt-4" in self.model_name.lower():
                    cost_estimate = (input_tokens * 0.00003) + (output_tokens * 0.00006)
                else:  # gpt-3.5 or other
                    cost_estimate = (input_tokens * 0.000001) + (output_tokens * 0.000002)
            
            return ProviderCallResult(
                ok=True, 
                data=text, 
                latency_ms=_now_ms() - t0,
                cost_estimate=cost_estimate
            )
            
        except Exception as e:
            return ProviderCallResult(
                ok=False, 
                message=str(e), 
                latency_ms=_now_ms() - t0
            )