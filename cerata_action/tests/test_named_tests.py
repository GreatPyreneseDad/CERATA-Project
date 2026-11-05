from pathlib import Path
from cerata_action import consume as C


def test_named_tests_unprotected_others_stay(tmp_path: Path):
    pre = {"pkg/test_a.py", "pkg/test_b.py", "pkg/mod.py"}
    assert C.protected_paths(pre, None, allow={"pkg/test_a.py"}) == {"pkg/test_b.py"}


def test_maintainer_listing_still_wins(tmp_path: Path):
    (tmp_path / ".cerata").mkdir()
    (tmp_path / ".cerata" / "protect").write_text("pkg/test_a.py\n")
    pre = {"pkg/test_a.py", "pkg/mod.py"}
    assert C.protected_paths(pre, tmp_path, allow={"pkg/test_a.py"}) == {"pkg/test_a.py"}
