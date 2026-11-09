"""repo_tools.py - save experiment outputs from Colab to GitHub."""
import datetime
import base64
import json
import shutil
import subprocess
from pathlib import Path

ALLOWED_DIRS = ("results", "notebooks", "docs", "data/synthetic", "src")
MAX_FILE_MB = 10
_state = {}


def configure(repo, repo_dir, user_name, user_email):
    from google.colab import userdata
    _state["repo"] = repo
    _state["dir"] = Path(repo_dir)
    _state["token"] = userdata.get("GITHUB_TOKEN")
    _git("config", "user.name", user_name)
    _git("config", "user.email", user_email)
    _ensure_layout()
    print("repo ready:", repo)


def _git(*args, auth=False):
    cmd = ["git"]
    if auth:
        raw = ("x-access-token:" + _state["token"]).encode()
        cmd += ["-c", "http.extraheader=AUTHORIZATION: basic " + base64.b64encode(raw).decode()]
    cmd += list(args)
    r = subprocess.run(cmd, cwd=_state["dir"], capture_output=True, text=True)
    if r.returncode != 0:
        msg = (r.stderr or r.stdout).replace(_state["token"], "***")
        raise RuntimeError("git " + args[0] + " failed: " + msg.strip()[:500])
    return r.stdout.strip()


def _ensure_layout():
    d = _state["dir"]
    for sub in ("notebooks", "results", "docs", "data/synthetic", "src"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    gi = d / ".gitignore"
    wanted = ["data/raw/", "*.zip", ".env", "__pycache__/", ".ipynb_checkpoints/"]
    current = gi.read_text().splitlines() if gi.exists() else []
    missing = [w for w in wanted if w not in current]
    if missing:
        gi.write_text("\n".join(current + missing) + "\n")


def _check_allowed(rel):
    rel = Path(rel).as_posix().strip("/")
    if not any(rel == a or rel.startswith(a + "/") for a in ALLOWED_DIRS):
        raise ValueError("folder not allowed: " + rel)


def _snapshot_notebook(name):
    # uses an undocumented Colab call; may stop working in the future
    try:
        from google.colab import _message
        nb = _message.blocking_request("get_ipynb", request="", timeout_sec=120)["ipynb"]
    except Exception as e:
        print("could not read the notebook automatically:", type(e).__name__)
        print("use File > Save a copy in GitHub for the notebook itself.")
        return None
    for cell in nb.get("cells", []):
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
    nb.get("metadata", {}).pop("widgets", None)   # breaks GitHub preview
    out = _state["dir"] / "notebooks" / name
    out.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    return out


def _append_log(title, body):
    path = _state["dir"] / "docs" / "experiment_log.md"
    if not path.exists():
        path.write_text("# Experiment Log\n", encoding="utf-8")
    header = "## " + datetime.date.today().isoformat() + " - " + title
    text = path.read_text(encoding="utf-8")
    if header in text:
        print("log entry already exists, skipped")
        return
    with path.open("a", encoding="utf-8") as f:
        f.write("\n" + header + "\n\n" + body.strip() + "\n")


def finish_step(notebook_name, files, log_title, log_body, message,
                source_dir="/content", dry_run=False):
    """files: {"file_name.csv": "results"}  (file name -> destination folder in repo)"""
    d = _state["dir"]
    _git("pull", "--rebase", "--autostash", auth=True)
    staged = []
    for fname, dest in files.items():
        _check_allowed(dest)
        src = Path(source_dir) / fname
        if not src.exists():
            raise FileNotFoundError(fname + " not found in " + source_dir)
        size_mb = src.stat().st_size / 1e6
        if size_mb > MAX_FILE_MB:
            raise ValueError(fname + " is " + str(round(size_mb, 1)) + " MB, over the limit")
        target = d / dest / fname
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(src, target)
        staged.append((Path(dest) / fname).as_posix())
    if notebook_name and _snapshot_notebook(notebook_name):
        staged.append("notebooks/" + notebook_name)
    _append_log(log_title, log_body)
    staged.append("docs/experiment_log.md")
    print("files to commit:")
    for s in staged:
        print("  ", s)
    if dry_run:
        print("dry run: nothing committed")
        return
    _git("add", *staged)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=d).returncode == 0:
        print("nothing changed, nothing to push")
        return
    _git("commit", "-m", message)
    _git("push", auth=True)
    print("pushed:", message)
