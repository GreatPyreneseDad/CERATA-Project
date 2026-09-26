"""TypeScript host + prey: JS/TS nematocyst detection and node:test validation loop."""

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from cerata_action import consume, hunt_runner  # noqa: E402
from cerata_action.llm import Scripted  # noqa: E402
from cerata_action.tests.test_action import MIT, make_repo  # noqa: E402

PREY_TS = """/** Seeded PRNG + 2D value noise. */
export function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => { a = (a + 0x6d2b79f5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}
export const lerp = (a: number, b: number, t: number): number => a + (b - a) * t;
export class ValueNoise2D { constructor(seed: number) {} }
"""

MODULE_BROKEN = "export function mulberry32(seed: number): () => number {\n  return () => 2;\n}\n"
MODULE_FIXED = ("// Consumed from prey/noise (MIT). Seeded PRNG.\n"
                "export function mulberry32(seed: number): () => number {\n  let a = seed >>> 0;\n"
                "  return () => { a = (a + 0x6d2b79f5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1);\n"
                "    t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };\n}\n")
TEST_TS = ("import { test } from 'node:test';\nimport assert from 'node:assert/strict';\n"
           "import { mulberry32 } from '../src/noise/prng.ts';\n\n"
           "test('deterministic and in [0,1)', () => {\n  const a = mulberry32(42), b = mulberry32(42);\n"
           "  for (let i = 0; i < 100; i++) { const x = a(); assert.equal(x, b()); assert.ok(x >= 0 && x < 1); }\n});\n")


def reply(plan, files):
    return f"<plan>\n{json.dumps(plan)}\n</plan>\n" + "\n".join(
        f'<file path="{p}">\n{c}</file>' for p, c in files.items())


@unittest.skipIf(shutil.which("node") is None, "node not installed")
class TestTypeScript(unittest.TestCase):
    def setUp(self):
        tmp = Path(tempfile.mkdtemp())
        self.prey = make_repo(tmp / "prey", {"LICENSE": MIT, "src/noise.ts": PREY_TS,
                                             "src/noise.test.ts": "x", "dist/noise.js": "function a(){}",
                                             "src/types.d.ts": "export declare function z(): void;"})
        self.host = make_repo(tmp / "host", {"package.json": '{"type": "module"}',
                                             "src/main.ts": "export const x = 1;\n",
                                             "src/engine/world.ts": "export class World {}\n",
                                             "tests/smoke.spec.ts": "// playwright\n"})

    def test_js_nematocysts(self):
        paths = [n["path"] for n in hunt_runner.js_nematocysts(self.prey)]
        self.assertEqual(paths, ["src/noise.ts"])
        n = hunt_runner.js_nematocysts(self.prey)[0]
        self.assertEqual((n["functions"], n["classes"]), (2, 1))

    def test_ts_consume_loop(self):
        self.assertEqual(consume.host_language(self.host), "typescript")
        hunt = hunt_runner.hunt(hunt_runner.load_hunt_module(ROOT), self.prey, "x", None, False)
        self.assertEqual(hunt["nematocyst_candidates"][0]["path"], "src/noise.ts")
        plan = {"summary": "PRNG", "integration_point": "src/noise",
                "nematocysts": [{"name": "mulberry32", "source": "src/noise.ts:mulberry32"}]}
        llm = Scripted(['<read>["src/main.ts"]</read>',
                        reply(plan, {"src/noise/prng.ts": MODULE_BROKEN, "tests/prng.test.ts": TEST_TS}),
                        reply({}, {"src/noise/prng.ts": MODULE_FIXED}),
                        "<read>[]</read>"])
        os.environ["CERATA_NO_SANDBOX"] = "1"
        res = consume.metabolize(llm, self.host, self.prey, "prey/noise", hunt, [], log=lambda *_: None)
        self.assertEqual(res["language"], "typescript")
        self.assertIn("TEST RULES (host is TypeScript)", llm.prompts[1]["messages"][2]["content"])
        self.assertTrue(res["tests"]["passed"], res["tests"]["output"])
        self.assertEqual(res["rounds"], 2)
        self.assertIn("node --", res["tests"]["output"])
        self.assertNotIn("smoke.spec.ts", res["tests"]["output"])  # host's playwright specs untouched
        self.assertFalse(res["wired"])                  # model declined to wire -> flagged, not hidden
        self.assertIn("unwired_reason", res["plan"])


if __name__ == "__main__":
    unittest.main()
