from big_ol_pile_of_manim_imports import *
import subprocess
from time import sleep
from manim import Manim

if not IS_STREAMING_TO_TWITCH:
    FNULL = open(os.devnull, 'w')
    subprocess.Popen([STREAMING_CLIENT, STREAMING_PROTOCOL + '://' + STREAMING_IP + ':' + STREAMING_PORT + '?listen'], stdout=FNULL, stderr=FNULL)
    sleep(3)

manim = Manim()

print("YOUR STREAM IS READY!")
