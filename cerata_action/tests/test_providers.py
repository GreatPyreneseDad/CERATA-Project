"""Provider layer + Copilot handoff tests. Local HTTP server, no network."""

import http.server
import json
import os
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cerata_action import copilot, llm  # noqa: E402
from cerata_action.github_api import GitHub  # noqa: E402

SEEN = []


class FakeModel(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["content-length"])))
        SEEN.append((self.path, {k.lower(): v for k, v in self.headers.items()}, body))
        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.end_headers()
        if self.path.endswith("/messages"):
            events = [{"type": "message_start", "message": {"usage": {"input_tokens": 11}}},
                      {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "hel"}},
                      {"type": "content_block_delta", "delta": {"type": "text_delta", "text": "lo"}},
                      {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": 2}}]
        else:
            events = [{"choices": [{"delta": {"role": "assistant"}}]},
                      {"choices": [{"delta": {"content": "hel"}}]},
                      {"choices": [{"delta": {"content": "lo"}, "finish_reason": "stop"}]},
                      {"choices": [], "usage": {"prompt_tokens": 11, "completion_tokens": 2}}]
        for ev in events:
            self.wfile.write(f"data: {json.dumps(ev)}\n\n".encode())
        if not self.path.endswith("/messages"):
            self.wfile.write(b"data: [DONE]\n\n")


class TestProviders(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), FakeModel)
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.url = f"http://127.0.0.1:{cls.srv.server_port}/v1"

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()

    def test_detect(self):
        d = llm.detect_provider
        self.assertEqual(d("sk-ant-x", ""), "anthropic")
        self.assertEqual(d("sk-or-v1-x", ""), "openrouter")
        self.assertEqual(d("gsk_x", ""), "groq")
        self.assertEqual(d("AIzaX", ""), "gemini")
        self.assertEqual(d("sk-proj-x", ""), "openai")
        self.assertEqual(d("anything", "https://my.proxy/v1"), "openai")
        self.assertEqual(d("x", "https://api.deepseek.com/v1"), "deepseek")

    def test_openai_compatible_stream(self):
        c = llm.make("auto", "k", "some-model", self.url, 1000)
        self.assertEqual(c.complete("SYS", [{"role": "user", "content": "hi"}]), "hello")
        path, headers, body = SEEN[-1]
        self.assertEqual(path, "/v1/chat/completions")
        self.assertEqual(body["messages"][0], {"role": "system", "content": "SYS"})
        self.assertEqual(body["max_tokens"], 1000)
        self.assertEqual(headers["authorization"], "Bearer k")
        self.assertEqual(c.usage, {"input_tokens": 11, "output_tokens": 2})

    def test_anthropic_stream(self):
        c = llm.Anthropic("sk-ant-k", "m", self.url, 1000)
        self.assertEqual(c.complete("SYS", [{"role": "user", "content": "hi"}]), "hello")
        path, headers, body = SEEN[-1]
        self.assertEqual(path, "/v1/messages")
        self.assertEqual(body["system"], "SYS")
        self.assertEqual(headers["x-api-key"], "sk-ant-k")

    def test_errors_are_actionable(self):
        with self.assertRaises(llm.LLMError) as e:
            llm.make("auto", "", "", "")
        self.assertIn("copilot", str(e.exception))
        with self.assertRaises(llm.LLMError):
            llm.make("madeup", "k")
        self.assertEqual(llm.make("gemini", "AIza").model, llm.PRESETS["gemini"][2])


class TestCopilotHandoff(unittest.TestCase):
    HUNT = {"commit": "a" * 40, "coherence": {"coherence": 3.1, "psi": 1, "rho": .8, "q": .5, "f": .9},
            "viability": {"viability": "PRIME_PREY"},
            "license": {"note": "MIT: permissive", "file": "LICENSE", "spdx": "MIT"},
            "nematocyst_candidates": [{"path": "a.py", "functions": 2, "classes": 1, "lines": 40}]}

    def test_payload(self):
        host = Path(tempfile.mkdtemp())
        gh = GitHub("pat", "me/host", dry_run=True)
        copilot.handoff(gh, host, "me/host", "main", "x/y", self.HUNT, ["a.py"], "only parsing")
        method, url, body = gh.calls[-1]
        self.assertEqual((method, url.endswith("/repos/me/host/issues")), ("POST", True))
        self.assertEqual(body["assignees"], ["copilot-swe-agent[bot]"])
        self.assertEqual(body["agent_assignment"]["target_repo"], "me/host")
        self.assertEqual(body["agent_assignment"]["custom_agent"], "")
        self.assertIn("`a.py`", body["body"])
        self.assertIn("only parsing", body["body"])
        self.assertIn("aaaaaaa", body["body"])
        (host / ".github/agents").mkdir(parents=True)
        (host / ".github/agents/cerata.agent.md").write_text("---\ndescription: x\n---\n")
        copilot.handoff(gh, host, "me/host", "main", "x/y", self.HUNT, ["a.py"], "")
        self.assertEqual(gh.calls[-1][2]["agent_assignment"]["custom_agent"], "cerata")

    def test_agent_profile_template_is_valid(self):
        text = (ROOT / "templates/agents/cerata.agent.md").read_text()
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("description:", text.split("---")[1])
        self.assertLess(len(text), 30000)


class TestProviderResolution(unittest.TestCase):
    def test_copilot_auto(self):
        from cerata_action import main
        with mock.patch.dict(os.environ, {"CERATA_PROVIDER": "auto", "CERATA_API_KEY": "",
                                          "CERATA_ANTHROPIC_API_KEY": "", "CERATA_BASE_URL": "",
                                          "CERATA_COPILOT_TOKEN": "pat"}):
            self.assertEqual(main.resolve_provider(), "copilot")
        with mock.patch.dict(os.environ, {"CERATA_PROVIDER": "auto", "CERATA_API_KEY": "sk-ant-x",
                                          "CERATA_COPILOT_TOKEN": "pat"}):
            self.assertEqual(main.resolve_provider(), "auto")


if __name__ == "__main__":
    unittest.main()
