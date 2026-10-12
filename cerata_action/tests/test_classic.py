"""CLASSIC regression gate: host tests green before a consume must stay green."""

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

GREEN = "import { test } from 'node:test'; import assert from 'node:assert/strict';\nimport { add } from '../src/add.mjs';\ntest('add', () => assert.equal(add(2, 2), 4));\n"
RED = "import { test } from 'node:test'; import assert from 'node:assert/strict';\ntest('was always red', () => assert.equal(1, 2));\n"
OWN = "import { test } from 'node:test'; import assert from 'node:assert/strict';\nimport { ease } from '../src/ease.mjs';\ntest('ease', () => assert.equal(ease(1), 1));\n"


def reply(plan, files):
    return f"<plan>\n{json.dumps(plan)}\n</plan>\n" + "\n".join(f'<file path="{p}">\n{c}</file>' for p, c in files.items())


@unittest.skipIf(shutil.which("node") is None, "node not installed")
class TestClassicGate(unittest.TestCase):
    def test_regression_detected_and_repaired(self):
        tmp = Path(tempfile.mkdtemp())
        prey = make_repo(tmp / "prey", {"LICENSE": MIT, "ease.js": "export function ease(t) { return t; }\n"})
        host = make_repo(tmp / "host", {"src/add.mjs": "export const add = (a, b) => a + b;\n",
                                        "tests/add.test.mjs": GREEN, "tests/red.test.mjs": RED})
        os.environ["CERATA_NO_SANDBOX"] = "1"
        hunt = hunt_runner.hunt(hunt_runner.load_hunt_module(ROOT), prey, "x", None, False)
        plan = {"summary": "ease", "integration_point": "src", "nematocysts": [{"name": "ease"}]}
        llm = Scripted([
            "<read>[]</read>",
            # wires ease into add.mjs but breaks CLASSIC add
            reply(plan, {"src/ease.mjs": "export const ease = t => t;\n", "tests/ease.test.mjs": OWN,
                         "src/add.mjs": "export const add = (a, b) => a - b; // oops\n"}),
            reply({}, {"src/add.mjs": "import { ease } from './ease.mjs';\nexport const USE_EASE = false;\n"
                                      "export const add = (a, b) => a + b;\n"}),
        ])
        res = consume.metabolize(llm, host, prey, "p/ease", hunt, ["ease.js"], log=lambda *_: None)
        repair_prompt = llm.prompts[2]["messages"][-1]["content"] if len(llm.prompts) > 2 else ""
        self.assertIn("REGRESSIONS (were green, now red): tests/add.test.mjs", repair_prompt)
        self.assertIn("already red before this consume: tests/red.test.mjs", repair_prompt)
        self.assertTrue(res["tests"]["passed"], res["tests"]["output"])
        self.assertEqual(res["tests"]["regressions"], [])
        self.assertTrue(res["wired"])  # add.mjs (existing) was modified


    def test_existing_tests_are_read_only(self):
        host = Path(tempfile.mkdtemp())
        pre = {"src/a.mjs", "tests/add.test.mjs", "tests/harness.mjs", "app.py", "test_x.py"}
        prot = consume.protected_paths(pre)
        self.assertEqual(prot, {"tests/add.test.mjs", "tests/harness.mjs", "test_x.py"})
        (host / "tests").mkdir()
        w, rej = consume.apply_files(host, {"tests/harness.mjs": "hacked", "./tests/add.test.mjs": "x",
                                            "tests/new.test.mjs": "ok", "src/a.mjs": "ok"}, prot)
        self.assertEqual(sorted(w), ["src/a.mjs", "tests/new.test.mjs"])
        self.assertEqual(sorted(rej), ["./tests/add.test.mjs", "tests/harness.mjs"])


    def test_host_protect_and_guide(self):
        host = Path(tempfile.mkdtemp())
        (host / ".cerata").mkdir()
        (host / ".cerata" / "protect").write_text("src/loop.js\nsrc/core/*.js  # engine core\n\n")
        (host / ".cerata" / "guide.md").write_text("New features go in src/kit/.")
        pre = {"src/loop.js", "src/core/a.js", "src/kit/x.js", "README.md"}
        self.assertEqual(consume.protected_paths(pre, host), {"src/loop.js", "src/core/a.js"})
        self.assertEqual(consume.host_guide(host), "New features go in src/kit/.")


if __name__ == "__main__":
    unittest.main()
