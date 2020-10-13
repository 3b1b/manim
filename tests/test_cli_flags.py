from manim import constants
from manim.config.main_utils import _determine_quality, parse_args


def test_quality_flags():
    # Assert that quality is the default when not specifying it
    parsed = parse_args("manim dummy_filename".split())

    assert parsed.quality == constants.DEFAULT_QUALITY_SHORT
    assert _determine_quality(parsed) == constants.DEFAULT_QUALITY

    for quality in constants.QUALITIES.keys():
        # Assert that quality is properly set when using -q*
        arguments = f"manim -q{constants.QUALITIES[quality]} dummy_filename".split()
        parsed = parse_args(arguments)

        assert parsed.quality == constants.QUALITIES[quality]
        assert quality == _determine_quality(parsed)

        # Assert that quality is properly set when using -q *
        arguments = f"manim -q {constants.QUALITIES[quality]} dummy_filename".split()
        parsed = parse_args(arguments)

        assert parsed.quality == constants.QUALITIES[quality]
        assert quality == _determine_quality(parsed)

        # Assert that quality is properly set when using --quality *
        arguments = (
            f"manim --quality {constants.QUALITIES[quality]} dummy_filename".split()
        )
        parsed = parse_args(arguments)

        assert parsed.quality == constants.QUALITIES[quality]
        assert quality == _determine_quality(parsed)

        # Assert that quality is properly set when using -*_quality
        arguments = f"manim --{quality} dummy_filename".split()
        parsed = parse_args(arguments)

        assert getattr(parsed, quality)
        assert quality == _determine_quality(parsed)

        # Assert that *_quality is False when not specifying it
        parsed = parse_args("manim dummy_filename".split())

        assert not getattr(parsed, quality)
        assert _determine_quality(parsed) == constants.DEFAULT_QUALITY
