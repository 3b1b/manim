import re
import pytest


def expand_hex(markup):
    return re.sub(
        r'(?<=["\'])#([0-9a-fA-F]{3})(?=["\'])',
        lambda m: '#' + ''.join(c * 2 for c in m.group(1)),
        markup
    )


def test_expand_3digit_hex():
    assert expand_hex('foreground="#abc"') == 'foreground="#aabbcc"'
    assert expand_hex('foreground="#fff"') == 'foreground="#ffffff"'
    assert expand_hex('foreground="#aabbcc"') == 'foreground="#aabbcc"'


def test_expand_multiple_colors():
    markup = 'color="#abc" background="#def"'
    result = expand_hex(markup)
    assert result == 'color="#aabbcc" background="#ddeeff"'
