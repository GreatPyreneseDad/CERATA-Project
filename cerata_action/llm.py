"""Anthropic Messages client (stdlib only, streaming so long generations don't time out)."""

import json
import os
import time
import urllib.error
import urllib.request
from typing import Callable, Dict, List, Optional

ANTHROPIC_URL = os.environ.get("CERATA_ANTHROPIC_URL", "https://api.anthropic.com/v1/messages")


class LLMError(RuntimeError):
    pass


class Anthropic:
    def __init__(self, api_key: str, model: str, max_tokens: int = 32000):
        if not api_key:
            raise LLMError("No Anthropic API key. Add an ANTHROPIC_API_KEY secret and pass it as `anthropic-api-key`.")
        self.api_key = api_key
        self.model = model
        self.max_tokens = max_tokens
        self.usage = {"input_tokens": 0, "output_tokens": 0}

    def complete(self, system: str, messages: List[Dict], retries: int = 3) -> str:
        body = json.dumps({
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": messages,
            "stream": True,
        }).encode()
        last = None
        for attempt in range(retries):
            req = urllib.request.Request(ANTHROPIC_URL, data=body, method="POST")
            req.add_header("x-api-key", self.api_key)
            req.add_header("anthropic-version", "2023-06-01")
            req.add_header("content-type", "application/json")
            try:
                with urllib.request.urlopen(req, timeout=900) as resp:
                    return self._read_stream(resp)
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")[:400]
                last = LLMError(f"Anthropic API {e.code}: {detail}")
                if e.code not in (429, 500, 502, 503, 529):
                    raise last
            except (urllib.error.URLError, TimeoutError) as e:
                last = LLMError(f"Anthropic API unreachable: {e}")
            time.sleep(5 * (attempt + 1))
        raise last

    def _read_stream(self, resp) -> str:
        chunks, stop = [], None
        for raw in resp:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            ev = json.loads(line[5:].strip() or "{}")
            t = ev.get("type")
            if t == "content_block_delta" and ev["delta"].get("type") == "text_delta":
                chunks.append(ev["delta"]["text"])
            elif t == "message_start":
                u = ev["message"].get("usage", {})
                self.usage["input_tokens"] += u.get("input_tokens", 0)
            elif t == "message_delta":
                stop = ev.get("delta", {}).get("stop_reason")
                self.usage["output_tokens"] += ev.get("usage", {}).get("output_tokens", 0)
            elif t == "error":
                raise LLMError(f"Anthropic stream error: {ev.get('error')}")
        text = "".join(chunks)
        if stop == "max_tokens":
            text += "\n<!-- CERATA: output truncated at max_tokens -->"
        return text


class Scripted:
    """Deterministic stand-in for tests: returns queued responses in order."""

    def __init__(self, responses: List[str], model: str = "scripted"):
        self.responses = list(responses)
        self.model = model
        self.prompts: List[Dict] = []
        self.usage = {"input_tokens": 0, "output_tokens": 0}

    def complete(self, system: str, messages: List[Dict], retries: int = 1) -> str:
        self.prompts.append({"system": system, "messages": messages})
        if not self.responses:
            raise LLMError("Scripted LLM ran out of responses")
        r = self.responses.pop(0)
        return r(messages) if callable(r) else r
