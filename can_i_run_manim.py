import platform
import subprocess
import distro
import os
import pathlib
import sys
import re


def check_ffmpeg_binary(platform, system_paths):
    print("[ffmpeg] - required: ", end="")
    error = 1

    if platform == "Windows":
        for syspath in system_paths:
            try:
                program_path = pathlib.Path(syspath) / "ffmpeg.exe"
                if program_path.is_file():
                    print(f"binary found {program_path}")
                    error = 0
                    break
            except OSError:
                pass

    elif platform in _debian_variants:
        ffmpeg_check = subprocess.run(["which", "ffmpeg"], capture_output=True)
        if ffmpeg_check.stdout:
            print(f"binary found {ffmpeg_check.stdout.strip().decode()}")
            error = 0
        else:
            print("\033[1;31;40m not found in system path\033[0;37;40m.")

    elif platform == "Darwin":
        pass

    elif platform not in _supported_distros:
        raise NotImplementedError("Your distro is not supported at the moment")

    return error


def check_latex_binary(platform, system_paths):
    print("[latex] - required: ", end="")
    error = 1

    if platform == "Windows":
        for syspath in system_paths:
            try:
                program_path = pathlib.Path(syspath) / "latex.exe"
                if program_path.is_file():
                    print(f"binary found {program_path}")
                    error = 0
                    break
            except OSError:
                pass

    elif platform in _debian_variants:
        latex_check = subprocess.run(["which", "latex"], capture_output=True)
        if latex_check.stdout:
            print(f"binary found {latex_check.stdout.strip().decode()}")
            error = 0
        else:
            print("\033[1;31;40m not found in system path\033[0;37;40m")

    elif platform == "Darwin":
        pass

    elif platform not in _supported_distros:
        raise NotImplementedError("Your distro is not supported at the moment")

    return error


def check_sox(platform, system_paths):
    print("[sox] - optional: ", end="")
    error = 1

    if platform == "Windows":
        for syspath in system_paths:
            try:
                program_path = pathlib.Path(syspath) / "sox.exe"
                if program_path.is_file():
                    print(f"binary found {program_path}")
                    error = 0
            except OSError:
                pass
        if error:
            print(f"sox not found in system path")

    elif platform in _debian_variants:
        sox_check = subprocess.run(["dpkg", "-s", "sox"], capture_output=True)
        if "install ok installed" in sox_check.stdout.decode():
            print("ok")
            error = 0
        else:
            print("sox not found in system path")

    elif platform == "Darwin":
        pass

    elif platform not in _supported_distros:
        raise NotImplementedError("Your distro is not supported at the moment")

    return error


def check_libcairo(platform):
    print("[libcairo] - optional: ", end="")
    error = 1

    if platform == "Windows":
        print("Please use gohlke pycairo binary for Windows")
        error = 0

    elif platform in _debian_variants:
        libcairo_check = subprocess.run(["dpkg", "-s", "libcairo2-dev"], capture_output=True)
        if "install ok installed" in libcairo_check.stdout.decode():
            print("libcairo2-dev ok")
            error = 0
        else:
            print("libcairo2-dev not found")

    elif platform == "Darwin":
        pass

    elif platform not in _supported_distros:
        raise NotImplementedError("Your distro is not supported at the moment")

    return error


def check_latex_packages():
    test_template = r"""\documentclass[preview]{standalone}
\usepackage{test_package}

\begin{document}
YourTextHere
\end{document}
"""
    packages = [
        "amsmath",
        "amssymb",
        "dsfont",
        "setspace",
        "tipa",
        "relsize",
        "textcomp",
        "mathrsfs",
        "calligra",
        "wasysym",
        "ragged2e",
        "physics",
        "xcolor",
        "microtype",
        "babel",
    ]

    for package in packages:
        with open("latex_package_test.tex", "w", encoding="utf8") as fout:
            test = test_template.replace("test_package", package)
            fout.write(test)
        print(f"Testing latex package {package:<15} ", end="")
        test_run = subprocess.run(
            ["latex", "-interaction=batchmode", "latex_package_test.tex"], capture_output=True
        )
        if test_run.returncode == 0:
            print("pass")
        else:
            print("failed")
            print("printing error log")
            with open("latex_package_test.log", "r") as logfile:
                log = logfile.read()
            error_regex = re.compile(r"!(.*\n){5}")
            m = error_regex.search(log)
            for line in m.group().split("\n"):
                print(line)

    print("Clean up testing artifacts...", end="")
    os.remove("latex_package_test.aux")
    os.remove("latex_package_test.dvi")
    os.remove("latex_package_test.log")
    os.remove("latex_package_test.tex")
    print("done")


def check_python_dep():
    from importlib import import_module

    error = 0
    python_modules = [
        "argparse",
        "colour",
        "numpy",
        "PIL",
        "progressbar",
        "scipy",
        "tqdm",
        # "cv2",  # optional
        "cairo",
        "pydub",
        "scipy.linalg",
    ]
    for module in python_modules:
        try:
            import_module(module)
            print(f"{module:<15} ok")
        except ImportError as e:
            print(f"importing {module:<15} failed")
            print(e)
            error = 1
        except ModuleNotFoundError as e2:
            print(f"{module:<15} not found")
            print(e2)
            error = 1

    return error


def try_squaretocircle():
    cmd = ["python3", "-m", "manim", "example_scenes.py", "SquareToCircle", "-pl"]
    print("Running command: ", " ".join(cmd))
    try:
        stc_test = subprocess.run(cmd, capture_output=True)
    except Exception as e:
        print("fail")
        print(stc_test.stderr)
        print(e)
    return stc_test.returncode


def try_writestuff():
    cmd = ["python3", "-m", "manim", "example_scenes.py", "WriteStuff", "-pl"]
    print("Running command: ", " ".join(cmd))
    try:
        ws_test = subprocess.run(cmd, capture_output=True)
    except Exception as e:
        print("fail")
        print(ws_test.stderr)
        print(e)
    return ws_test.returncode


if __name__ == "__main__":
    import time

    _platform = platform.system()

    _debian_variants = ["ubuntu", "debian", "kubuntu", "xubuntu"]
    _redhat_variants = ["fedora", "centos", "redhat"]
    _suse_variants = ["suse", "opensuse"]
    _arch_variants = ["arch", "manjaro", "antegro"]
    _supported_distros = [
        "Windows"
    ] + _debian_variants  # add distro list to this list when implemented

    if _platform == "Linux":
        syspaths = os.environ["PATH"].split(":")
    elif _platform == "Windows":
        syspaths = os.environ["Path"].split(";")
    elif _platform == "Darwin":
        syspaths = os.environ["PATH"].split(":")
        raise NotImplementedError(
            "Dependency check for MacOS not implemented at the moment\nPatches are welcome."
        )
        sys.exit(0)

    print("\n===Manim dependency Check===\n")
    print(f"Minimal python version 3.6 is required")
    print(f"Current python version {platform.python_version()}")
    print(f"OS {_platform}")
    if _platform == "Linux":
        print(" ".join(distro.linux_distribution(full_distribution_name=False)))
        _platform = distro.linux_distribution(full_distribution_name=False)[0]

    try:
        repo_ver = subprocess.check_output(["git", "describe", "--always"]).strip()
    except FileNotFoundError:
        repo_ver = "Unknown"

    print(f"Repository version {repo_ver.decode()}")
    print("\n===Checking for required system libraries===\n")
    ffmpeg_fail = check_ffmpeg_binary(_platform, syspaths)
    latex_fail = check_latex_binary(_platform, syspaths)
    sox_fail = check_sox(_platform, syspaths)
    libcairo_fail = check_libcairo(_platform)
    print("\n===Checking for python package dependencies===\n")
    python_dep_fail = check_python_dep()
    print("\n===Checking for latex package dependencies===\n")
    latex_package_fail = check_latex_packages()

    print("\n===Running example scenes===\n")
    try_squaretocircle()
    time.sleep(3)
    try_writestuff()

    print("\n===Possible diagnosis===\n")
    if ffmpeg_fail:
        if platform == "Windows":
            print("ffmpeg not found, please install it via https://ffmpeg.org/download.html")
            print(
                "and make sure the bin directory which ffmpeg.exe resides is included in your system variable path"
            )
        if platform == _debian_variants:
            print("ffmpeg not found, please install it: apt install ffmpeg")
    if latex_fail:
        if platform == "Windows":
            print("latex on Windows is distributed via latex distribution")
            print("You can choose use MikTex or TexLive")
            print("A full installation is recommended")
            print(
                "make sure the bin/x64 directory which latex.exe resides is included in your system variable path"
            )
        if platform == _debian_variants:
            print("latex not found, please install it via: apt install texlive-full")
    if sox_fail:
        print("sox is optional, only needed when using --sound with manim")
        if platform == "Windows":
            print(
                "sox binary not found in system path, you can install it via http://sox.sourceforge.net/"
            )
        if platform == _debian_variants:
            print("sox binary not found, you can install it: apt install sox")
    if libcairo_fail:
        if platform == _debian_variants:
            print("libcairo missing, please install it: apt install libcairo libcairo2-dev")
        print("libcairo is only needed when the precompiled pycairo wheel fails to install")
    if python_dep_fail:
        print("Some or all of the required python packages are missing")
        print("Please install the required package: pip3 install -r requirement.txt")
        print(
            "For pycairo on Windows use the gohlke binary: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pycairo"
        )
    if latex_package_fail:
        if platform == "Windows":
            print(
                "Some latex packages are missing, please check the latex package manager for missing packages"
            )
        if platform == _debian_variants:
            print(
                "Some latex packages are missing, a full latex install is recommended: apt install texlive-full"
            )

# TODO add support for macos
# TODO add support distros other than debian variants
