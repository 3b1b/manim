#This script install pycairo.
import platform
import os
import sys
import urllib.request

#python 3.7 32-bit
#pycairo‑1.19.1‑cp37‑cp37m‑win32.whl
if 'Windows' in platform.system():
    if sys.version[:3]=='3.7' and platform.machine()=='x86':
        urllib.request.urlretrieve("https://download.lfd.uci.edu/pythonlibs/s2jqpv5t/pycairo-1.19.1-cp37-cp37m-win32.whl", "pycairo-1.19.1-cp37-cp37m-win32.whl")
        print("Sucessfully downloaded Cairo for your system")
        print("Installing Cairo")
        os.system("pip install pycairo-1.19.1-cp37-cp37m-win32.whl")
        os.remove("pycairo-1.19.1-cp37-cp37m-win32.whl")
        print("Succesfully installed Cairo")

    #python 3.7 AMD64(64-bit)
    #pycairo-1.19.1-cp37-cp37m-win_amd64.whl
    elif sys.version[:3]=='3.7' and platform.machine()=='AMD64':
        urllib.request.urlretrieve("https://download.lfd.uci.edu/pythonlibs/s2jqpv5t/pycairo-1.19.1-cp37-cp37m-win_amd64.whl", "pycairo-1.19.1-cp37-cp37m-win_amd64.whl")
        print("Sucessfully downloaded Cairo for your system")
        print("Installing Cairo")
        os.system("pip3 install pycairo-1.19.1-cp37-cp37m-win_amd64.whl")
        os.remove("pycairo-1.19.1-cp37-cp37m-win_amd64.whl")
        print("Succesfully installed Cairo")
        
    #python 3.8 32-bit
    #pycairo-1.19.1-cp38-cp38-win32.whl
    elif sys.version[:3]=='3.8' and platform.machine()=='x86':
        urllib.request.urlretrieve("https://download.lfd.uci.edu/pythonlibs/s2jqpv5t/pycairo-1.19.1-cp38-cp38-win32.whl", "pycairo-1.19.1-cp38-cp38-win32.whl")
        print("Sucessfully downloaded Cairo for your system")
        print("Installing Cairo")
        os.system("pip3 install pycairo-1.19.1-cp38-cp38-win32.whl")
        os.remove("pycairo-1.19.1-cp38-cp38-win32.whl")
        print("Succesfully installed Cairo")   
    #python 3.8 AMD64
    #pycairo-1.19.1-cp38-cp38-win_amd64.whl
    elif sys.version[:3]=='3.8' and platform.machine()=='AMD64':
        urllib.request.urlretrieve("https://download.lfd.uci.edu/pythonlibs/s2jqpv5t/pycairo-1.19.1-cp38-cp38-win_amd64.whl", "pycairo-1.19.1-cp38-cp38-win_amd64.whl")
        print("Sucessfully downloaded Cairo for your system")
        print("Installing Cairo")
        os.system("pip install pycairo-1.19.1-cp38-cp38-win_amd64.whl")
        os.remove("pycairo-1.19.1-cp38-cp38-win_amd64.whl")
        print("Succesfully installed Cairo")       
