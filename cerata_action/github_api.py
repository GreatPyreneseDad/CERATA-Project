"""Minimal GitHub REST client (stdlib only)."""

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

API = os.environ.get("GITHUB_API_URL", "https://api.github.com")


class GitHubError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(f"GitHub API {status}: {message}")
        self.status = status


class GitHub:
    def __init__(self, token: str, repo: str, dry_run: bool = False):
        self.token = token
        self.repo = repo  # "owner/name"
        self.dry_run = dry_run
        self.calls = []  # recorded in dry-run for tests

    def request(self, method: str, path: str, body: Optional[Dict] = None,
                auth: bool = True) -> Any:
        url = path if path.startswith("http") else f"{API}{path}"
        if self.dry_run and method != "GET":
            self.calls.append((method, url, body))
            return {"html_url": f"https://github.com/{self.repo}/dry-run", "number": 0, "id": 0}
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(url, data=data, method=method)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        req.add_header("User-Agent", "cerata-action")
        if auth and self.token:
            req.add_header("Authorization", f"Bearer {self.token}")
        if data is not None:
            req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="replace")[:500]
            raise GitHubError(e.code, detail) from None

    # --- helpers -------------------------------------------------------
    def comment(self, issue_number: int, body: str) -> Dict:
        return self.request("POST", f"/repos/{self.repo}/issues/{issue_number}/comments",
                            {"body": body})

    def react(self, comment_id: int, content: str) -> None:
        try:
            self.request("POST", f"/repos/{self.repo}/issues/comments/{comment_id}/reactions",
                         {"content": content})
        except GitHubError:
            pass  # reactions are cosmetic

    def repo_info(self, full_name: str) -> Optional[Dict]:
        """Public metadata for any repo. Unauthenticated fallback for foreign prey."""
        for auth in (True, False):
            try:
                return self.request("GET", f"/repos/{full_name}", auth=auth)
            except GitHubError:
                continue
        return None

    def default_branch(self) -> str:
        info = self.request("GET", f"/repos/{self.repo}")
        return info.get("default_branch", "main")

    def open_pr(self, head: str, base: str, title: str, body: str) -> Dict:
        return self.request("POST", f"/repos/{self.repo}/pulls",
                            {"head": head, "base": base, "title": title, "body": body,
                             "maintainer_can_modify": True})

    def add_labels(self, issue_number: int, labels) -> None:
        try:
            self.request("POST", f"/repos/{self.repo}/issues/{issue_number}/labels",
                         {"labels": list(labels)})
        except GitHubError:
            pass
