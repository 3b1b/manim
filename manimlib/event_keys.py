"""
manim's own names for what a key event carries, so that nothing above the window has to
know what the window is built on.

A key which types something is named by what it types, so that ord("s") and Keys of it come
to the same number and a binding may be written either way. Every other key takes a
codepoint from Unicode's private use area, which is what it is for, so that chr() of one is
harmless and can never come out equal to a key which does type something.

A window translates from whatever vocabulary it is given into this one before handing an
event up, and takes these back from is_key_pressed, see window.py. Mouse buttons are left
alone: nothing compares one against anything, so they need no names.
"""
from __future__ import annotations


class Keys:
    # Keys which type a control character, named by the character
    BACKSPACE = 0x08
    TAB = 0x09
    ENTER = 0x0D
    ESCAPE = 0x1B
    SPACE = 0x20
    DELETE = 0x7F

    # Keys which type nothing. Left and right hand modifiers come to the same key, since
    # nothing manim binds cares which of the pair was pressed.
    LEFT = 0xE000
    RIGHT = 0xE001
    UP = 0xE002
    DOWN = 0xE003
    SHIFT = 0xE004
    CTRL = 0xE005
    ALT = 0xE006
    CMD = 0xE007


class Mods:
    """Which modifiers were held while an event happened, as the bits of one number"""

    SHIFT = 1 << 0
    CTRL = 1 << 1
    ALT = 1 << 2
    CMD = 1 << 3

    # A mac says command where everything else says control, and every shortcut manim
    # binds means either of them
    CTRL_OR_CMD = CTRL | CMD
    # The modifiers anything is bound to, for a shortcut which asks that none be held.
    # Alt is left out because nothing is bound to it.
    ANY = SHIFT | CTRL | CMD
