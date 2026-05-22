# ManimGL — Python 3.11 Compatibility Fixes & Setup Guide

This document describes the fixes applied to get ManimGL running on **macOS with Python 3.11**, and provides a step-by-step guide to run it from scratch.

---

## ⚙️ System Requirements

- macOS (Apple Silicon or Intel)
- [Homebrew](https://brew.sh/)
- Python 3.11 (via Homebrew)
- BasicTeX (LaTeX distribution)
- FFmpeg (optional, required for video file export)

---

## 🚀 Setup from Scratch

### 1. Install System Dependencies

```sh
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11
brew install python@3.11

# Install BasicTeX (lightweight LaTeX)
brew install --cask basictex

# (Optional) Install FFmpeg for video export
brew install ffmpeg
```

### 2. Add LaTeX to PATH

After installing BasicTeX, add it to your shell profile permanently:

```sh
echo 'export PATH="/Library/TeX/texbin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

Or run this in your current session:

```sh
eval "$(/usr/libexec/path_helper)"
```

### 3. Install Required LaTeX Packages

```sh
sudo tlmgr update --self
sudo tlmgr install \
    standalone dvisvgm preview \
    doublestroke wasysym physics \
    xcolor pifont tipa microtype \
    setspace ragged2e \
    collection-fontsrecommended
```

### 4. Create a Python Virtual Environment & Install ManimGL

```sh
# Clone the repo (if not already done)
git clone https://github.com/KarthikGangadhar/manim.git
cd manim

# Create virtual environment using Python 3.11
/opt/homebrew/bin/python3.11 -m venv .venv

# Activate it
source .venv/bin/activate

# Install manimgl in editable mode
pip install --upgrade pip
pip install -e .

# Install additional missing packages
pip install trimesh pywavefront
```

---

## ▶️ Running a Scene

```sh
# Activate the virtual environment first
source .venv/bin/activate

# Run a scene (opens an interactive window)
manimgl example_scenes.py OpeningManimExample

# Or without activating:
.venv/bin/manimgl example_scenes.py OpeningManimExample
```

### Useful CLI Flags

| Flag | Description |
|------|-------------|
| *(none)* | Opens interactive animation window |
| `-w` | Write animation to video file |
| `-o` | Write to file and open it |
| `-s` | Skip to final frame only |
| `-so` | Save final frame as image |
| `-n <N>` | Skip to the Nth animation |
| `-f` | Fullscreen playback |

---

## 🐛 Fixes Applied for Python 3.11 Compatibility

Python 3.10 introduced a [breaking change](https://docs.python.org/3/whatsnew/3.10.html) where `staticmethod` objects are **no longer directly callable**. This affected several decorator patterns in the codebase.

### `manimlib/window.py`
- Removed `@staticmethod` from `note_undrawn_event`, which was used as a class-level decorator for event handlers.

### `manimlib/shader_wrapper.py`
- Swapped decorator order on `get_fill_canvas` from `@lru_cache` / `@staticmethod` to `@staticmethod` / `@lru_cache`.
  - In Python 3.10+, `@lru_cache` on top of `@staticmethod` fails because it receives a non-callable `staticmethod` object.

### `manimlib/mobject/mobject.py`
- Removed `@staticmethod` from the following internal class decorators:
  - `affects_data`
  - `affects_family_data`
  - `stash_mobject_pointers`
  - `affects_shader_info_id`

### `manimlib/scene/scene.py`
- Removed `@staticmethod` from `affects_mobject_list` (used as a class-level decorator).

### `manimlib/tex_templates.yml`
- Removed `\usepackage{calligra}` from all templates.
  - The `calligra` font package is not available in BasicTeX and is not required for standard scenes.

---

## 📦 Additional Python Packages Required

These packages were missing from `requirements.txt` / `setup.cfg` but are required at runtime:

```sh
pip install trimesh pywavefront
```

---

## 📝 Notes

- The `pydub` warning `Couldn't find ffmpeg` is **non-fatal** — it only matters when exporting audio. Install `brew install ffmpeg` to silence it.
- The `.venv/` directory is gitignored and must be recreated locally.
- LaTeX is only required for scenes that use `Tex`, `TexText`, `MathTex`, or matrix objects.
