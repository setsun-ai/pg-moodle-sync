"""
Step 2: upload DOWNLOAD_DIR to cloud storage with rclone.

rclone supports 70+ services: Google Drive, OneDrive (many universities give
students Microsoft 365 with 1 TB), Dropbox, Nextcloud, ... - the remote is
configured once with `rclone config`. Without RCLONE_REMOTE this step is
skipped, which is fine if DOWNLOAD_DIR already is a synced folder (e.g.
inside "Google Drive for desktop" or OneDrive on your PC).

We use `rclone copy`, NOT `rclone sync`:
  - copy only adds/updates files in the cloud and never deletes anything,
  - sync would mirror the local folder - clearing DOWNLOAD_DIR (e.g. to free
    space on a Raspberry Pi SD card) would wipe your materials in the cloud.
With KEEP_LOCAL=0 we use `rclone move`: a file disappears locally only after
a successful upload, and state.json remembers it was downloaded.

rclone compares size + modification time; the download step sets mtime to
the time the file was modified in Moodle, so only new or replaced files are
sent. --update also protects files you edited in the cloud (they're newer).
"""

import shutil
import subprocess

from . import config, state as state_mod
from .i18n import t

SKIPPED = 2

# Low memory use for a Raspberry Pi 3 (512 MB RAM): rclone buffers one chunk
# per parallel transfer, so 2 x 8 MB instead of the default 4 x 8 MB. With a
# few hundred files, Wi-Fi is the bottleneck anyway, not parallelism.
RCLONE_FLAGS = [
    "--transfers", "2",
    "--checkers", "4",
    "--drive-chunk-size", "8M",  # ignored by non-Google remotes
    "--fast-list",
    "--update",
    "--exclude", "*.part",
    "--exclude", "*.relocating",
    "--stats-one-line",
    "--stats", "30s",
    "--stats-log-level", "NOTICE",
]
# rclone exit codes: 3 = directory not found, 4 = file not found
RCLONE_NOT_FOUND = {3, 4}
MAX_MOVE_ATTEMPTS = 5
BACKUP_FILES = ["state.json", "courses.json", "przedmioty.json"]


def rclone(*args: str, quiet: bool = False) -> int:
    cmd = [config.rclone_bin(), *args]
    if not quiet:
        print("$", " ".join(cmd), flush=True)
    return subprocess.run(cmd).returncode


def remote_configured() -> bool:
    out = subprocess.run([config.rclone_bin(), "listremotes"], capture_output=True, text=True)
    return f"{config.rclone_remote()}:" in out.stdout.split()


def status() -> tuple[bool, str]:
    """(usable?, reason) - used by `doctor` and to decide whether to skip."""
    if not config.rclone_remote():
        return False, t("storage_disabled")
    if shutil.which(config.rclone_bin()) is None:
        return False, t("storage_no_rclone", bin=config.rclone_bin())
    if not remote_configured():
        return False, t("storage_no_remote", remote=config.rclone_remote())
    return True, f"{config.rclone_remote()}:{config.remote_dest()}"


def target(path: str = "") -> str:
    base = f"{config.rclone_remote()}:{config.remote_dest()}"
    return f"{base}/{path}" if path else base


def apply_remote_moves(dry_run: bool) -> int:
    """Files moved locally by re-categorisation -> `rclone moveto` (no re-upload)."""
    state = state_mod.load()
    moves = state.get("remote_moves", [])
    if not moves:
        return 0
    print(t("storage_moving", n=len(moves)))
    failed, remaining = 0, []
    for i, move in enumerate(moves):
        if dry_run:
            print(f"    {move['from']} -> {move['to']}")
            continue
        if i and i % 20 == 0:
            # Save progress now and then: hundreds of moves take a while on a
            # Raspberry Pi, and an interrupted run shouldn't redo the done ones.
            state["remote_moves"] = remaining + moves[i:]
            state_mod.save(state)
        code = rclone("moveto", target(move["from"]), target(move["to"]))
        if code == 0 or code in RCLONE_NOT_FOUND:
            continue  # not in the cloud (yet) - copy will upload it to the new path
        move["attempts"] = move.get("attempts", 0) + 1
        if move["attempts"] >= MAX_MOVE_ATTEMPTS:
            # Worst case of giving up: the old copy stays in the cloud next to the new one.
            print("    " + t("storage_move_gave_up", n=MAX_MOVE_ATTEMPTS, path=move["from"]))
            continue
        failed += 1
        remaining.append(move)  # e.g. no network - retry next time
    if not dry_run:
        state["remote_moves"] = remaining
        state_mod.save(state)
        rclone("rmdirs", target(), "--leave-root")  # empty folders left after moves
    return failed


def backup_state() -> None:
    """Copy state.json (+ courses config) to the cloud - no secrets (.env, tokens)."""
    for name in BACKUP_FILES:
        path = config.DATA_DIR / name
        if path.exists():
            dest = f"{config.rclone_remote()}:{config.state_backup_dest()}/{name}"
            if rclone("copyto", str(path), dest, "-q", quiet=True) != 0:
                print(t("storage_backup_failed", name=name))


def check() -> int:
    ok, reason = status()
    if not ok:
        print(reason)
        return SKIPPED
    return rclone("lsd", f"{config.rclone_remote()}:")


def run(dry_run: bool = False) -> int:
    ok, reason = status()
    if not ok:
        print(reason)
        return SKIPPED

    failed_moves = apply_remote_moves(dry_run)
    local = config.download_dir()
    code = 0
    if local.is_dir():
        verb = "copy" if config.keep_local() else "move"
        extra = ["--dry-run"] if dry_run else []
        if not config.keep_local():
            extra.append("--delete-empty-src-dirs")
        code = rclone(verb, str(local), target(), *RCLONE_FLAGS, "-v", *extra)
    else:
        print(t("storage_nothing", dir=local))
    if not dry_run:
        backup_state()
    return code or (1 if failed_moves else 0)
