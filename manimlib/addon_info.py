#!/usr/bin/env python
import manimlib.addon_loader
from threading import Timer
import sys, time


sys.stdout.write( 'Loading addons...\r' )
sys.stdout.flush()

manimlib.addon_loader.read_addons(True)
manimlib.addon_loader.print_addon_info()
