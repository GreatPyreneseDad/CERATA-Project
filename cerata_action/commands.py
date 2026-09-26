"""Parse `/cerata ...` commands from comments or workflow inputs."""

import os
import re
import shlex
from dataclasses import dataclass, field
from typing import List, Optional

TRIGGER = "/cerata"
VERBS = ("hunt", "consume", "help")

_SLUG = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9._-]{1,100}$")
_GH_URL = re.compile(
    r"^https://github\.com/([A-Za-z0-9](?:[A-Za-z0-9-]{0,38})/[A-Za-z0-9._-]{1,100}?)(?:\.git)?/?$"
)
_SAFE_PATH = re.compile(r"^[A-Za-z0-9._/@+-]{1,300}$")


@dataclass
class Prey:
    slug: str  # owner/name

    @property
    def url(self) -> str:
        base = os.environ.get("CERATA_PREY_BASE", "https://github.com/")  # tests point this at local repos
        return f"{base.rstrip('/')}/{self.slug}.git" if base.startswith("http") else f"{base.rstrip('/')}/{self.slug}"

    @property
    def key(self) -> str:
        return self.slug.replace("/", "__").lower()


@dataclass
class Command:
    verb: str
    prey: Optional[Prey] = None
    paths: List[str] = field(default_factory=list)
    focus: str = ""
    error: str = ""


def parse_prey(token: str) -> Optional[Prey]:
    token = token.strip().rstrip("/")
    if token.startswith("-"):
        return None
    m = _GH_URL.match(token)
    if m:
        return Prey(m.group(1))
    if token.startswith("github.com/"):
        return parse_prey("https://" + token)
    if _SLUG.match(token):
        return Prey(token.removesuffix(".git"))
    return None


def extract(text: str) -> Optional[str]:
    """Return the first line starting with /cerata, minus the trigger."""
    for line in (text or "").splitlines():
        s = line.strip()
        if s.lower().startswith(TRIGGER):
            return s[len(TRIGGER):].strip()
    return None


def parse(text: str) -> Command:
    """Parse "hunt owner/repo" / "consume owner/repo path ... -- focus note"."""
    focus = ""
    if " -- " in f" {text} ":
        text, _, focus = f" {text} ".partition(" -- ")
        text, focus = text.strip(), focus.strip()
    try:
        parts = shlex.split(text)
    except ValueError:
        parts = text.split()
    if not parts:
        return Command("help")
    verb = parts[0].lower()
    if verb not in VERBS:
        return Command("help", error=f"Unknown command `{verb}`.")
    if verb == "help":
        return Command("help")
    if len(parts) < 2:
        return Command(verb, error=f"`/cerata {verb}` needs a repository, e.g. `/cerata {verb} owner/repo`.")
    prey = parse_prey(parts[1])
    if prey is None:
        return Command(verb, error=f"`{parts[1]}` is not a GitHub repository (use `owner/repo`).")
    paths = []
    for p in parts[2:]:
        p = p.lstrip("/")
        if not _SAFE_PATH.match(p) or ".." in p.split("/"):
            return Command(verb, error=f"Invalid path `{p}`.")
        paths.append(p)
    return Command(verb, prey=prey, paths=paths, focus=focus[:1000])
