# SearchMyFiles under Wine

Run Nir Sofer’s SearchMyFiles on Linux from **Applications → Utilities → SearchMyFiles**. The installer adds a per-user desktop entry and a dedicated Wine prefix. SearchMyFiles itself comes from NirSoft. [SearchMyFiles features and downloads](https://www.nirsoft.net/utils/search_my_files.html)

## 1. Requirements

The tested system was Debian 12 x86-64, WineHQ stable 11.0, and KDE Plasma on X11. It used Python 3, Wine with 64-bit Windows support, and the 64-bit Mesa software drivers (`libgl1-mesa-dri` and `mesa-vulkan-drivers` on Debian). Put `wine`, `wineboot`, and `wineserver` from the same installation on your PATH. Allow about 1.5 GiB for the Wine prefix. Compatibility with Wayland, other Wine releases, and other distributions remains unverified.

## 2. Install and search

1. Download the official **SearchMyFiles for x64** ZIP to your Downloads folder. Leave the archive intact. The installer verifies NirSoft’s published SHA-256 for version 3.36 before it writes application files. A newer upstream archive needs its own compatibility check and checksum update. [Download x64 ZIP](https://www.nirsoft.net/utils/searchmyfiles-x64.zip) · [NirSoft’s published hashes](https://www.nirsoft.net/hash_check/?software=searchmyfiles)
2. Extract this repository ZIP, or use a local checkout. In that directory, run the quoted command in a terminal as your normal desktop user.

   > `python3 ./install.py "$HOME/Downloads/searchmyfiles-x64.zip"`

3. After the installer prints the menu entry path, open **Applications → Utilities → SearchMyFiles**. In **Search Options**, choose a **Base Folders** path and a **Files Wildcard**. For example, a Linux user named `alex` can enter `Z:\home\alex\Documents` and `*.txt`. Enable **Scan Subfolders** to include nested folders. In this Wine prefix, `Z:\` maps to the Linux root.
4. For a content comparison, select **Duplicate Search** in **Search Mode**. To save results, select the rows and use **File → Save Selected Items**, then choose CSV.

## 3. What the launcher uses

The installer sets up the prefix with both display variables unset, then waits for Wine setup to finish before adding the menu entry. Wine can print display-driver messages during this headless step. The desktop entry enables the following settings for the GUI process.

| Setting | Value on the tested system |
| --- | --- |
| `__GLX_VENDOR_LIBRARY_NAME` | `mesa` |
| `LIBGL_ALWAYS_SOFTWARE` | `1` |
| `VK_DRIVER_FILES` | `/usr/share/vulkan/icd.d/lvp_icd.x86_64.json` |
| `WINEDLLOVERRIDES` | `winemenubuilder.exe=d` |

The installer also recognizes Mesa’s `lvp_icd.json` filename. With the default XDG data directory, the application, its `SearchMyFiles.cfg` preferences, and its `prefix/` live under `~/.local/share/searchmyfiles/`. The menu entry is `~/.local/share/applications/searchmyfiles.desktop`. If `XDG_DATA_HOME` is set, both locations use that directory instead.

Setup preserves an existing application directory or menu entry and reports the conflicting path. If Wine setup fails partway through a fresh install, the installer prints the incomplete directory’s path. Close any Wine process using that prefix and move that directory aside before retrying. Keep any saved preferences you want to reuse.

## 4. Compatibility results

On the test desktop, initial prefix setup stalled with the display attached. Headless initialization succeeded. The first search with the default graphics settings also timed out. Using the three Mesa settings together allowed the search to finish and the Search Options dialog to open. These tests establish a working configuration on one host. They did not isolate an individual graphics setting or establish the cause of the stall.

| Check | Observed result |
| --- | --- |
| Recursive wildcard and text search | `*.txt` with a text marker found both matching files across two directories. A text file without the marker and a different extension containing the marker were excluded. |
| Duplicate search | Found the two byte-identical copies and excluded a third file of the same size whose contents differed. |
| CSV export | Both searches exported exactly the expected two filenames. |
| Graphical launch | The menu launcher opened the main window and the Search Options dialog. |

SearchMyFiles is freeware by Nir Sofer and is subject to NirSoft’s terms. This repository contains the Linux installer and documentation. Codex assisted with the packaging and tests. [NirSoft’s license and documentation](https://www.nirsoft.net/utils/search_my_files.html)
