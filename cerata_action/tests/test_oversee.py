"""The overseer's argument handling, the regression that kept it from running: --all-goals needs no --goal."""

import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

from cerata_action import oversee


class OverseeArgs(unittest.TestCase):
    def test_all_goals_does_not_demand_goal(self):
        calls = []
        with mock.patch.dict("os.environ", {"OVERSEER_GITHUB_TOKEN": "t"}), \
             mock.patch.object(oversee, "discover_goals", return_value=[("goals/a/goal.json", 4), ("goals/b/goal.json", None)]), \
             mock.patch.object(oversee, "tick", side_effect=lambda *a, **k: calls.append(a[1:5])):
            rc = oversee.main(["--repo", "https://github.com/o/r.git", "--all-goals"])
        self.assertEqual(rc, 0)
        self.assertEqual([c[0] for c in calls], ["goals/a/goal.json", "goals/b/goal.json"])
        self.assertEqual([c[3] for c in calls], [4, None])

    def test_single_goal_still_requires_goal(self):
        with mock.patch.dict("os.environ", {"OVERSEER_GITHUB_TOKEN": "t"}), redirect_stdout(io.StringIO()):
            self.assertEqual(oversee.main(["--repo", "https://github.com/o/r.git"]), 2)


class OverseeNetwork(unittest.TestCase):
    def test_all_goals_walks_listed_repos(self):
        calls = []
        goals = {"https://github.com/o/home.git": [("goals/a/goal.json", 4)], "https://github.com/o/other.git": [("goals/r/goal.json", 9)]}
        with mock.patch.dict("os.environ", {"OVERSEER_GITHUB_TOKEN": "t"}), \
             mock.patch.object(oversee, "network_repos", return_value=["https://github.com/o/other.git"]), \
             mock.patch.object(oversee, "discover_goals", side_effect=lambda r, t: goals[r]), \
             mock.patch.object(oversee, "tick", side_effect=lambda *a, **k: calls.append((a[0], a[1], a[4]))):
            self.assertEqual(oversee.main(["--repo", "https://github.com/o/home.git", "--all-goals"]), 0)
        self.assertEqual(calls, [("https://github.com/o/home.git", "goals/a/goal.json", 4), ("https://github.com/o/other.git", "goals/r/goal.json", 9)])


class OverseeDry(unittest.TestCase):
    def test_dry_run_never_comments(self):
        with mock.patch.dict("os.environ", {"OVERSEER_DRY": "1"}), mock.patch.object(oversee, "gh") as gh, redirect_stdout(io.StringIO()):
            oversee.say("t", "https://github.com/o/r.git", 10, {"said": ""}, "Done.")
        gh.assert_not_called()


if __name__ == "__main__":
    unittest.main()
