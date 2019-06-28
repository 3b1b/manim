#!/usr/bin/env python
import manimlib.addon_helper
from threading import Timer
import sys, time


def animation ( i = 0 ):
    sys.stdout.write( 'Loading addons\r' + ( '.' * i ) + '   ' )
    sys.stdout.flush()
    Timer( 0.5, animation, ( 0 if i == 3 else i + 1, ) ).start()

animation()
manimlib.addon_helper.read_addons()
manimlib.addon_helper.print_addon_info()