#!/usr/bin/env python
import manimlib.addon_helper
from threading import Timer
import sys, time



sys.stdout.write( 'Loading addons...\r' )
sys.stdout.flush()

manimlib.addon_helper.read_addons(True)
manimlib.addon_helper.print_addon_info()
