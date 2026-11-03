"""The bounty actor, end to end against a local git repo with a scripted model and a fake mandate."""

import hmac
import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from cerata_action import build
from cerata_action.llm import Scripted

MANDATE = {"jti": "jti-test", "nonce": "n0nce", "repo": "local", "scope_paths": ["src"], "expires_at": "2099-01-01"}

FIXED = "export const add = (a, b) => a + b;\n"
TEST = "import { test } from 'node:test'; import assert from 'node:assert/strict'; import { add } from './add.mjs';\n" \
       "test('adds', () => assert.equal(add(2, 3), 5));\n"


def make_host(d: Path):
    (d / "src").mkdir()
    (d / "src" / "add.mjs").write_text("export const add = (a, b) => a - b;\n")
    (d / "src" / "add.test.mjs").write_text(TEST)
    (d / "README.md").write_text("host\n")
    (d / "package.json").write_text(json.dumps({"name": "host", "type": "module", "scripts": {"test": "node --test src/*.test.mjs"}}))
    for c in (["init", "-q", "-b", "main"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "init"]):
        subprocess.run(["git", "-C", str(d)] + c, check=True)


def row_for(d: Path):
    sha = subprocess.run(["git", "-C", str(d), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    return {"id": "f1", "verified": "red", "judged": False, "f": {
        "kind": "bug", "severity": "low",
        "location": {"repo": str(d), "commit": sha, "path": "src/add.mjs", "line_start": 1},
        "defect": "add subtracts",
        "evidence": {"repro": {"workdir": ".", "cmd": "node --test src/add.test.mjs", "expect": "nonzero_exit"}}}}


class BuildTest(unittest.TestCase):
    def test_scope_gate_trailers_and_tag(self):
        with tempfile.TemporaryDirectory() as t:
            host = Path(t) / "repo"; host.mkdir(); make_host(host)
            row = row_for(host)
            llm = Scripted([
                '<read>["src/add.mjs"]</read>',
                '<plan>{"summary": "fix add to add", "reasoning": "add used minus. Changed one operator. Ran the test.", '
                '"out_of_scope_needed": [], "warnings": []}</plan>'
                f'<file path="src/add.mjs">{FIXED}</file>'
                '<file path="README.md">pwned\n</file>',
            ])
            res = build.build(llm, host, row, MANDATE)
            self.assertFalse(res["declined"])
            self.assertTrue(res["repro_pass"], res.get("repro_out"))
            self.assertEqual(res["written"], ["src/add.mjs"])
            self.assertTrue(any("README.md" in r and "scope" in r for r in res["rejected"]), res["rejected"])
            self.assertEqual((host / "README.md").read_text(), "host\n")
            sub = build.submit(host, row, MANDATE, res, token="", dry_run=True, log=lambda *_: None)
            msg = subprocess.run(["git", "-C", str(host), "log", "-1", "--format=%B"], capture_output=True, text=True).stdout
            self.assertIn("Buildup-Mandate: jti-test", msg)
            self.assertIn("Buildup-Nonce: n0nce", msg)
            body = build.pr_body(res["plan"], res, MANDATE, sub["head"], "f1")
            first = body.split("<!-- buildup-reasoning -->\n", 1)[1].splitlines()[0]
            self.assertEqual(first, hmac.new(b"n0nce", sub["head"].encode(), hashlib.sha256).hexdigest())
            self.assertNotIn("proven", body)

    def test_submit_rebases_onto_moved_default_branch(self):
        with tempfile.TemporaryDirectory() as t:
            origin = Path(t) / "origin.git"; seed = Path(t) / "seed"; seed.mkdir()
            make_host(seed)
            subprocess.run(["git", "clone", "-q", "--bare", str(seed), str(origin)], check=True)
            host = Path(t) / "host"
            subprocess.run(["git", "clone", "-q", str(origin), str(host)], check=True)
            row = row_for(host)
            # someone else lands unrelated work on main while we build
            other = Path(t) / "other"
            subprocess.run(["git", "clone", "-q", str(origin), str(other)], check=True)
            (other / "NEWS.md").write_text("moved\n")
            for c in (["add", "-A"], ["-c", "user.name=o", "-c", "user.email=o@o", "commit", "-q", "-m", "news"], ["push", "-q", "origin", "main"]):
                subprocess.run(["git", "-C", str(other)] + c, check=True)
            llm = Scripted(['<read>[]</read>', f'<plan>{{"summary": "fix", "reasoning": "r"}}</plan><file path="src/add.mjs">{FIXED}</file>'])
            res = build.build(llm, host, row, MANDATE)
            self.assertTrue(res["repro_pass"])
            sub = build.submit(host, row, MANDATE, res, token="", dry_run=True, log=lambda *_: None)
            self.assertTrue((host / "NEWS.md").exists(), "build was not rebased onto the moved branch")
            msg = subprocess.run(["git", "-C", str(host), "log", "-1", "--format=%B"], capture_output=True, text=True).stdout
            self.assertIn("Buildup-Nonce: n0nce", msg)
            parent = subprocess.run(["git", "-C", str(host), "rev-parse", "HEAD~1"], capture_output=True, text=True).stdout.strip()
            main = subprocess.run(["git", "-C", str(host), "rev-parse", "origin/main"], capture_output=True, text=True).stdout.strip()
            self.assertEqual(parent, main)

    def test_edits_apply_exactly_once_and_reject_ambiguity(self):
        with tempfile.TemporaryDirectory() as t:
            host = Path(t) / "repo"; host.mkdir(); make_host(host)
            row = row_for(host)
            llm = Scripted([
                '<read>["src/add.mjs"]</read>',
                '<plan>{"summary": "fix operator", "reasoning": "one char"}</plan>'
                '<edit path="src/add.mjs"><find>a - b</find><replace>a + b</replace></edit>'
                '<edit path="README.md"><find>host</find><replace>pwned</replace></edit>'
                '<edit path="package.json"><find>"</find><replace>x</replace></edit>',
            ])
            res = build.build(llm, host, row, MANDATE)
            self.assertTrue(res["repro_pass"], res.get("repro_out"))
            self.assertEqual(res["written"], ["src/add.mjs"])
            self.assertEqual((host / "src" / "add.mjs").read_text(), FIXED)
            self.assertTrue(any("README.md" in r and "scope" in r for r in res["rejected"]), res["rejected"])
            self.assertTrue(any("package.json" in r and "matched" in r for r in res["rejected"]), res["rejected"])
            self.assertEqual((host / "README.md").read_text(), "host\n")

    def test_finding_file_delivered_whole_and_truncation_labelled(self):
        with tempfile.TemporaryDirectory() as t:
            host = Path(t); (host / "big.txt").write_text("x" * 5000); (host / "focus.txt").write_text("y" * 5000)
            from cerata_action import consume as C
            out = C.read_host_files(host, ["big.txt", "focus.txt"], whole=("focus.txt",), budget=1000)
            self.assertIn('truncated="true"', out.split("focus.txt")[0])
            self.assertIn("y" * 5000, out)

    def test_eligible_retries_declines_from_an_older_harness(self):
        rows = [{"id": "a", "verified": "red", "judged": False}, {"id": "b", "verified": "red", "judged": False}]
        st = {"built": {"a": {"status": "declined", "build_version": build.BUILD_VERSION - 1}, "b": {"status": "declined", "build_version": build.BUILD_VERSION}}}
        self.assertEqual([r["id"] for r in build.eligible(rows, st)], ["a"])

    def test_root_scope_and_prefix_rules(self):
        self.assertTrue(build.in_scope("anything/at/all.js", ["./"]))
        self.assertTrue(build.in_scope("src/x.js", ["src"]))
        self.assertTrue(build.in_scope("src/x.js", ["./src/"]))
        self.assertFalse(build.in_scope("srcx/x.js", ["src"]))
        self.assertFalse(build.in_scope("README.md", ["src"]))

    def test_repair_round_then_pass(self):
        with tempfile.TemporaryDirectory() as t:
            host = Path(t) / "repo"; host.mkdir(); make_host(host)
            row = row_for(host)
            llm = Scripted([
                '<read>[]</read>',
                '<plan>{"summary": "try", "reasoning": "r"}</plan><file path="src/add.mjs">export const add = (a, b) => a * b;\n</file>',
                f'<plan>{{"summary": "fix", "reasoning": "r2"}}</plan><file path="src/add.mjs">{FIXED}</file>',
            ])
            res = build.build(llm, host, row, MANDATE, max_repair=2)
            self.assertTrue(res["repro_pass"])
            self.assertEqual(res["rounds"], 2)

    def test_eligible_skips_judged_unverified_built_and_blocked(self):
        rows = [
            {"id": "a", "verified": "red", "judged": False},
            {"id": "b", "verified": "red", "judged": True, "bounty": {"title": "B"}},
            {"id": "c", "verified": "green", "judged": False},
            {"id": "d", "verified": "red", "judged": False, "bounty": {"title": "D", "depends_on": ["B"]}},
            {"id": "e", "verified": "red", "judged": False, "bounty": {"title": "E", "depends_on": ["Z"]}},
            {"id": "f", "verified": "red", "judged": False},
            {"id": "g", "verified": "red", "judged": False},
        ]
        ids = [r["id"] for r in build.eligible(rows, {"built": {"f": {"status": "submitted"}, "g": {"status": "error"}}})]
        self.assertEqual(ids, ["a", "d", "g"])


if __name__ == "__main__":
    unittest.main()
