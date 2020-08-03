import platform
import os
import sys
import urllib.request

if "Windows" in platform.system():
    ver_num = "1.19.2"
    fork = "naveen521kk"
    # In case the python version is 3.6 and the system is 32-bit, try pycairo‑{ver_num}‑cp37‑cp37m‑win32.whl version of cairo
    if sys.version[:3] == "3.6" and platform.machine() == "x86":
        url = f"https://github.com/{fork}/pycairo/releases/download/v{ver_num}/pycairo-{ver_num}-cp36-cp36m-win32.whl"

    # In case the python version is 3.6 and the system is 64-bit, try pycairo‑{ver_num}‑cp37‑cp37m‑win32.whl version of cairo
    elif sys.version[:3] == "3.6" and platform.machine() == "AMD64":
        url = f"https://github.com/{fork}/pycairo/releases/download/v{ver_num}/pycairo-{ver_num}-cp36-cp36m-win_amd64.whl"

    # In case the python version is 3.7 and the system is 32-bit, try pycairo‑{ver_num}‑cp37‑cp37m‑win32.whl version of cairo
    elif sys.version[:3] == "3.7" and platform.machine() == "x86":
        url = f"https://github.com/{fork}/pycairo/releases/download/v{ver_num}/pycairo-{ver_num}-cp37-cp37m-win32.whl"

    # In case the python version is 3.7 and the system is AMD64, try pycairo-{ver_num}-cp37-cp37m-win_amd64.whl version of cairo
    elif sys.version[:3] == "3.7" and platform.machine() == "AMD64":
        url = f"https://github.com/{fork}/pycairo/releases/download/v{ver_num}/pycairo-{ver_num}-cp37-cp37m-win_amd64.whl"

    # In case the python version is 3.8 and the system is 32-bit, try pycairo-{ver_num}-cp38-cp38-win32.whl version of cairo
    elif sys.version[:3] == "3.8" and platform.machine() == "x86":
        url = f"https://github.com/{fork}/pycairo/releases/download/v{ver_num}/pycairo-{ver_num}-cp38-cp38-win32.whl"

    # In case the python version is 3.8 and the system is AMD64, try pycairo-{ver_num}-cp38-cp38-win_amd64.whl version of cairo
    elif sys.version[:3] == "3.8" and platform.machine() == "AMD64":
        url = f"https://github.com/{fork}/pycairo/releases/download/v{ver_num}/pycairo-{ver_num}-cp38-cp38-win_amd64.whl"
    else:
        raise Exception("Could not find a PyCairo version for your system!")

    filename = url.split("/")[-1]
    urllib.request.urlretrieve(url, filename)
    os.system(f"pip{sys.version[:3]} install {filename}")
    print("Installed PyCairo.\nCleaning up...")
    os.remove(filename)
    print("Done.")
else:
    raise Exception("This script only works if your operating system is Windows.")
