#!/usr/bin/env python3
"""Install the verified SearchMyFiles 3.36 x64 archive for the current user."""

import argparse
import hashlib
import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ARCHIVE_SHA256 = "2090e93a52d2c66a9417fb7426b77832806f0029ba9adfbf99107ee152ddad89"


def desktop_arg(value):
    """Quote one Exec argument, then escape it for the desktop-entry file."""
    quoted = "".join("\\" + c if c in ('"', "\\", "$", chr(96)) else c for c in str(value))
    return '"' + quoted.replace("\\", "\\\\").replace("%", "%%") + '"'


def install(archive):
    if os.geteuid() == 0:
        sys.exit("Run this as your normal desktop user.")
    data = Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local/share")
    if not data.is_absolute():
        sys.exit("XDG_DATA_HOME must be an absolute path.")
    if any(c in str(data) for c in "\r\n"):
        sys.exit("The desktop entry requires a single-line data directory path.")
    app = data / "searchmyfiles"
    entry = data / "applications/searchmyfiles.desktop"
    for path in (app, entry):
        if os.path.lexists(path):
            sys.exit(f"Already exists: {path}. Keeping the existing installation.")

    wine = shutil.which("wine")
    if not wine or not all(shutil.which(cmd) for cmd in ("wineboot", "wineserver")):
        sys.exit("Install Wine with x64 support and put wine, wineboot and wineserver on PATH.")
    icd_dir = Path("/usr/share/vulkan/icd.d")
    icd = next((icd_dir / name for name in ("lvp_icd.x86_64.json", "lvp_icd.json")
                if (icd_dir / name).is_file()), None)
    if icd is None:
        sys.exit(f"Mesa lavapipe driver missing in {icd_dir}. On Debian, install mesa-vulkan-drivers:amd64.")

    payload = archive.read_bytes()
    if hashlib.sha256(payload).hexdigest() != ARCHIVE_SHA256:
        sys.exit("Archive checksum mismatch. This installer expects the original 3.36 x64 ZIP.")

    prefix = app / "prefix"
    args = ["/usr/bin/env", f"WINEPREFIX={prefix}", "WINEDLLOVERRIDES=winemenubuilder.exe=d",
            "__GLX_VENDOR_LIBRARY_NAME=mesa", "LIBGL_ALWAYS_SOFTWARE=1",
            f"VK_DRIVER_FILES={icd}", wine, app / "SearchMyFiles.exe"]
    desktop = "\n".join((
        "[Desktop Entry]", "Type=Application", "Name=SearchMyFiles",
        "Comment=Search files and find duplicates with NirSoft SearchMyFiles",
        "Exec=" + " ".join(desktop_arg(arg) for arg in args),
        "Icon=system-search", "Terminal=false", "Categories=Utility;FileTools;", "",
    ))

    entry.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=entry.parent) as staging:
        staged_entry = Path(staging) / entry.name
        staged_entry.write_text(desktop, encoding="utf-8")
        app.mkdir(mode=0o700)
        try:
            with zipfile.ZipFile(io.BytesIO(payload)) as package:
                for name in ("SearchMyFiles.exe", "SearchMyFiles.chm", "readme.txt"):
                    (app / name).write_bytes(package.read(name))
            env = dict(os.environ, WINEPREFIX=str(prefix), WINEARCH="win64",
                       WINEDLLOVERRIDES="winemenubuilder.exe=d;mscoree,mshtml=")
            env.pop("DISPLAY", None)
            env.pop("WAYLAND_DISPLAY", None)
            subprocess.run(["wineboot", "--init"], env=env, check=True)
            subprocess.run(["wineserver", "-w"], env=env, check=True)
            if not (prefix / "drive_c/windows/explorer.exe").is_file():
                raise RuntimeError("Wine did not populate the prefix.")
            os.link(staged_entry, entry)
        except (OSError, RuntimeError, subprocess.CalledProcessError, KeyboardInterrupt):
            print(f"Setup stopped. Files from this attempt are in {app}.", file=sys.stderr)
            raise
    print(f"Installed {entry}. Open SearchMyFiles from Applications → Utilities.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="path to NirSoft's searchmyfiles-x64.zip")
    try:
        install(parser.parse_args().archive)
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        sys.exit(str(error))
