import shutil
import subprocess
import sys
from pathlib import Path

from _utils import GREEN, RED, RESET, title, wxbasepath, iter_version_dirs, get_valid_dll_versions


def cleanup_invalid_versions(base: Path):
    removed = []
    kept = []
    for version_dir in sorted(iter_version_dirs(base), key=lambda p: tuple(int(part) for part in p.name.split(".")), reverse=True):
        dll_path = version_dir / "Weixin.dll"
        if dll_path.is_file():
            kept.append(version_dir)
            continue
        print(f"- Removing invalid version folder: {version_dir}")
        shutil.rmtree(version_dir)
        removed.append(version_dir)
    return kept, removed


def run_coexist(number: str):
    cmd = [sys.executable, "coexist.py", "-n", number, "--no-pause"]
    print(f"\n> Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def main():
    title("Auto Coexist")
    print("\n - Clean stale Weixin version folders and rebuild coexist executables.")

    base = wxbasepath()
    print(f"\n> Weixin base path: {base}")

    kept, removed = cleanup_invalid_versions(base)
    valid_versions = get_valid_dll_versions(base)
    if not valid_versions:
        print(f"{RED}[ERR] No valid Weixin.dll was found after cleanup{RESET}")
        return 1

    print("\n> Valid version folders:")
    for version_dir in valid_versions:
        print(f"  {GREEN}[keep]{RESET} {version_dir}")

    if not removed:
        print("\n> No stale version folders needed removal")

    run_coexist("0")
    run_coexist("1")

    print(f"\n{GREEN}[√] Done. Rebuilt coexist files with the latest valid Weixin.dll{RESET}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as exc:
        print(f"\n{RED}[ERR] coexist.py failed with exit code {exc.returncode}{RESET}")
        raise SystemExit(exc.returncode)
    except PermissionError as exc:
        print(f"\n{RED}[ERR] Permission denied: {exc}{RESET}")
        raise SystemExit(1)
