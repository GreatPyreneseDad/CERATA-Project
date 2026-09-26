"""Model clients (stdlib only, streaming so long generations don't time out).

Two wire formats cover almost every provider:
  - Anthropic Messages API
  - OpenAI-compatible /chat/completions (OpenAI, OpenRouter, Gemini, Groq, DeepSeek,
    Mistral, Together, xAI, Azure OpenAI v1, local Ollama/vLLM/LM Studio, ...)
"""

import json
import os
import time
import urllib.error
import urllib.request
from typing import Dict, List, Optional

# provider -> (wire format, base url, default model)
PRESETS = {
    "anthropic":  ("anthropic", "https://api.anthropic.com/v1", "claude-sonnet-4-5"),
    "openai":     ("openai", "https://api.openai.com/v1", "gpt-5"),
    "openrouter": ("openai", "https://openrouter.ai/api/v1", "anthropic/claude-sonnet-4.5"),
    "gemini":     ("openai", "https://generativelanguage.googleapis.com/v1beta/openai", "gemini-2.5-pro"),
    "deepseek":   ("openai", "https://api.deepseek.com/v1", "deepseek-chat"),
    "mistral":    ("openai", "https://api.mistral.ai/v1", "mistral-large-latest"),
    "groq":       ("openai", "https://api.groq.com/openai/v1", "openai/gpt-oss-120b"),
    "together":   ("openai", "https://api.together.xyz/v1", "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8"),
    "xai":        ("openai", "https://api.x.ai/v1", "grok-4"),
    "ollama":     ("openai", "http://localhost:11434/v1", "qwen3-coder"),
}
RETRYABLE = (408, 409, 429, 500, 502, 503, 504, 529)


class LLMError(RuntimeError):
    pass


def detect_provider(api_key: str, base_url: str) -> str:
    if base_url:
        for name, (_, url, _) in PRESETS.items():
            if base_url.rstrip("/") == url:
                return name
        return "openai"  # any custom OpenAI-compatible endpoint
    if api_key.startswith("sk-ant-"):
        return "anthropic"
    if api_key.startswith("sk-or-"):
        return "openrouter"
    if api_key.startswith("gsk_"):
        return "groq"
    if api_key.startswith("xai-"):
        return "xai"
    if api_key.startswith("AIza"):
        return "gemini"
    return "openai"


class _Client:
    fmt = ""

    def __init__(self, api_key: str, model: str, base_url: str, max_tokens: int):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.max_tokens = max_tokens
        self.usage = {"input_tokens": 0, "output_tokens": 0}

    def _post(self, url: str, body: Dict, headers: Dict, retries: int = 3):
        last = None
        for attempt in range(retries):
            req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST")
            for k, v in headers.items():
                req.add_header(k, v)
            req.add_header("content-type", "application/json")
            try:
                resp = urllib.request.urlopen(req, timeout=900)
                return resp
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")[:400]
                last = LLMError(f"{self.fmt} API {e.code} ({self.model}): {detail}")
                last.status, last.detail = e.code, detail
                if e.code not in RETRYABLE:
                    raise last
            except (urllib.error.URLError, TimeoutError) as e:
                last = LLMError(f"{self.fmt} API unreachable at {url}: {e}")
            time.sleep(5 * (attempt + 1))
        raise last

    @staticmethod
    def _events(resp):
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").strip()
            if line.startswith("data:"):
                data = line[5:].strip()
                if data and data != "[DONE]":
                    yield json.loads(data)


class Anthropic(_Client):
    fmt = "Anthropic"

    def complete(self, system: str, messages: List[Dict], retries: int = 3) -> str:
        resp = self._post(f"{self.base_url}/messages", {
            "model": self.model, "max_tokens": self.max_tokens, "system": system,
            "messages": messages, "stream": True,
        }, {"x-api-key": self.api_key, "anthropic-version": "2023-06-01"}, retries)
        chunks, stop = [], None
        with resp:
            for ev in self._events(resp):
                t = ev.get("type")
                if t == "content_block_delta" and ev["delta"].get("type") == "text_delta":
                    chunks.append(ev["delta"]["text"])
                elif t == "message_start":
                    self.usage["input_tokens"] += ev["message"].get("usage", {}).get("input_tokens", 0)
                elif t == "message_delta":
                    stop = ev.get("delta", {}).get("stop_reason")
                    self.usage["output_tokens"] += ev.get("usage", {}).get("output_tokens", 0)
                elif t == "error":
                    raise LLMError(f"Anthropic stream error: {ev.get('error')}")
        text = "".join(chunks)
        return text + ("\n<!-- CERATA: output truncated at max_tokens -->" if stop == "max_tokens" else "")


class OpenAICompatible(_Client):
    fmt = "OpenAI-compatible"

    def complete(self, system: str, messages: List[Dict], retries: int = 3) -> str:
        # api.openai.com wants max_completion_tokens; most compatible servers still want max_tokens.
        key = "max_completion_tokens" if "api.openai.com" in self.base_url else "max_tokens"
        body = {"model": self.model, "stream": True, key: self.max_tokens,
                "messages": [{"role": "system", "content": system}] + messages}
        headers = {"authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        if "openrouter.ai" in self.base_url:
            headers.update({"HTTP-Referer": "https://github.com/GreatPyreneseDad/CERATA-Project",
                            "X-Title": "CERATA"})
        try:
            resp = self._post(f"{self.base_url}/chat/completions", body, headers, retries)
        except LLMError as e:
            # Model rejects the output budget: halve it once and retry.
            if getattr(e, "status", 0) == 400 and "token" in getattr(e, "detail", "").lower():
                body[key] = max(4096, self.max_tokens // 2)
                resp = self._post(f"{self.base_url}/chat/completions", body, headers, retries)
            else:
                raise
        chunks, stop = [], None
        with resp:
            for ev in self._events(resp):
                if ev.get("error"):
                    raise LLMError(f"stream error: {ev['error']}")
                for ch in ev.get("choices") or []:
                    piece = (ch.get("delta") or {}).get("content")
                    if piece:
                        chunks.append(piece)
                    stop = ch.get("finish_reason") or stop
                u = ev.get("usage") or {}
                self.usage["input_tokens"] += u.get("prompt_tokens", 0)
                self.usage["output_tokens"] += u.get("completion_tokens", 0)
        text = "".join(chunks)
        return text + ("\n<!-- CERATA: output truncated at max_tokens -->" if stop == "length" else "")


def make(provider: str, api_key: str, model: str = "", base_url: str = "",
         max_tokens: int = 32000):
    provider = (provider or "auto").lower()
    if provider == "auto":
        provider = detect_provider(api_key, base_url)
    if provider not in PRESETS:
        if not base_url:
            raise LLMError(f"Unknown provider `{provider}`. Use one of {', '.join(PRESETS)}, "
                           "or set `base-url` for any OpenAI-compatible endpoint.")
        fmt, default_url, default_model = "openai", base_url, ""
    else:
        fmt, default_url, default_model = PRESETS[provider]
    if not api_key and provider != "ollama":
        raise LLMError("No model API key. Set the `api-key` input (any provider), "
                       "or use `provider: copilot` to hand consumption to Copilot.")
    model = model or default_model
    if not model:
        raise LLMError("Set the `model` input for a custom endpoint.")
    cls = Anthropic if fmt == "anthropic" else OpenAICompatible
    client = cls(api_key, model, base_url or default_url, max_tokens)
    client.provider = provider
    return client


class Scripted:
    """Deterministic stand-in for tests: returns queued responses in order."""

    def __init__(self, responses: List[str], model: str = "scripted"):
        self.responses = list(responses)
        self.model = model
        self.provider = "scripted"
        self.prompts: List[Dict] = []
        self.usage = {"input_tokens": 0, "output_tokens": 0}

    def complete(self, system: str, messages: List[Dict], retries: int = 1) -> str:
        self.prompts.append({"system": system, "messages": messages})
        if not self.responses:
            raise LLMError("Scripted LLM ran out of responses")
        r = self.responses.pop(0)
        return r(messages) if callable(r) else r
