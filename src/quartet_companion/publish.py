"""`qc publish`: build the public listening site and put it on the repository's gh-pages branch.

The code lives on `main`; the website (with the recordings whose licences allow it) lives on
the separate `gh-pages` branch of the same GitHub repository, which GitHub Pages serves.
`public_site/` is ignored by the main branch and is itself a small git checkout of gh-pages.
Each publish replaces gh-pages with a single new commit (no history, so a file that was
removed cannot be downloaded from an older version); git still uploads only new files.
"""
from __future__ import annotations

import datetime as dt
import re
import subprocess
from pathlib import Path

GITHUB_FILE_LIMIT = 100 * 1024 * 1024        # GitHub refuses files of 100 MB or more
PAGES_SITE_LIMIT = 1024 * 1024 * 1024         # GitHub Pages: sites up to 1 GB


def _git(args: list[str], cwd: Path, check: bool = True) -> subprocess.CompletedProcess:
    r = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    if check and r.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed:\n{r.stderr.strip() or r.stdout.strip()}")
    return r


def pages_url(remote: str) -> str | None:
    """https://github.com/<user>/<repo>(.git) or git@github.com:<user>/<repo>.git -> Pages address."""
    m = re.search(r"github\.com[:/]([^/]+)/([^/]+?)(?:\.git)?/?$", remote)
    return f"https://{m.group(1).lower()}.github.io/{m.group(2)}/" if m else None


def check_sizes(site: Path) -> list[str]:
    problems, total = [], 0
    for f in site.rglob("*"):
        if f.is_file() and ".git" not in f.parts:
            size = f.stat().st_size
            total += size
            if size >= GITHUB_FILE_LIMIT:
                problems.append(f"{f.relative_to(site)} is {size / 1e6:.0f} MB; GitHub accepts files under 100 MB")
    if total > PAGES_SITE_LIMIT:
        problems.append(f"the site is {total / 1e9:.2f} GB; GitHub Pages allows 1 GB")
    return problems


def publish(root: Path, build: bool = True, push: bool = True, force: bool = False) -> str:
    """Build public_site/ and commit it to the gh-pages branch; push it unless push=False.
    Returns the commit message (or a note that nothing changed). `force` is kept for older
    instructions: every push now replaces the branch."""
    if _git(["rev-parse", "--is-inside-work-tree"], root, check=False).returncode != 0:
        raise SystemExit("This folder is not a git repository yet. Run `git init` and push the code first "
                         "(README, 'Publishing').")
    remote = _git(["remote", "get-url", "origin"], root, check=False).stdout.strip()
    if push and not remote:
        raise SystemExit("No GitHub remote yet: create the repository on GitHub, then "
                         "`git remote add origin https://github.com/<you>/<repo>.git`.")
    site = root / "public_site"
    if build:
        from .site import build_site
        build_site(root, site, public=True)
    problems = check_sizes(site)
    if problems:
        raise SystemExit("Not published:\n  " + "\n  ".join(problems))
    (site / ".nojekyll").write_text("")          # serve files as they are (no Jekyll processing)

    if not (site / ".git").exists():
        _git(["init", "-q"], site)
        _git(["checkout", "-q", "-b", "gh-pages"], site)
    # the remote may have been added (or changed) after the first, local-only publish
    if remote:
        current = _git(["remote", "get-url", "origin"], site, check=False)
        if current.returncode != 0:
            _git(["remote", "add", "origin", remote], site)
        elif current.stdout.strip() != remote:
            _git(["remote", "set-url", "origin", remote], site)
    # use the same name/e-mail as the main repository
    for key in ("user.name", "user.email"):
        v = _git(["config", key], root, check=False).stdout.strip()
        if v:
            _git(["config", key, v], site)

    # The branch always holds ONE commit: the site as it is now. A recording that was
    # removed (made private, wrong licence) must not stay downloadable from older commits.
    _git(["add", "-A"], site)
    has_head = _git(["rev-parse", "--verify", "-q", "HEAD"], site, check=False).returncode == 0
    if has_head and not _git(["status", "--porcelain"], site).stdout.strip():
        msg = "nothing changed since the last publish"
    else:
        msg = f"Publish listening site {dt.date.today().isoformat()}"
        _git(["checkout", "-q", "--orphan", "qc-publish-new"], site)
        _git(["commit", "-q", "-m", msg], site)
        if _git(["rev-parse", "--verify", "-q", "gh-pages"], site, check=False).returncode == 0:
            _git(["branch", "-q", "-D", "gh-pages"], site)
        _git(["branch", "-q", "-m", "gh-pages"], site)
        # unchanged files are already on GitHub (the old commit), so only new files are uploaded
    if push:
        r = _git(["push", "-u", "--force", "origin", "gh-pages"], site, check=False)
        if r.returncode != 0:
            raise SystemExit("Push failed:\n" + (r.stderr.strip() or r.stdout.strip()))
    return msg
