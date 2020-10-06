from manim import constants
from manim.config.config_utils import _determine_quality, _parse_cli


def test_quality_flags():
    # Assert that quality is None when not specifying it
    parsed = _parse_cli([], False)

    assert not parsed.quality

    for quality in constants.QUALITIES.keys():
        # Assert that quality is properly set when using -q*
        arguments = f"-q{constants.QUALITIES[quality]}".split()
        parsed = _parse_cli(arguments, False)

        assert parsed.quality == constants.QUALITIES[quality]
        assert quality == _determine_quality(parsed)

        # Assert that quality is properly set when using -q *
        arguments = f"-q {constants.QUALITIES[quality]}".split()
        parsed = _parse_cli(arguments, False)

        assert parsed.quality == constants.QUALITIES[quality]
        assert quality == _determine_quality(parsed)

        # Assert that quality is properly set when using --quality *
        arguments = f"--quality {constants.QUALITIES[quality]}".split()
        parsed = _parse_cli(arguments, False)

        assert parsed.quality == constants.QUALITIES[quality]
        assert quality == _determine_quality(parsed)

        # Assert that quality is properly set when using -*_quality
        arguments = f"--{quality}".split()
        parsed = _parse_cli(arguments, False)

        assert getattr(parsed, quality)
        assert quality == _determine_quality(parsed)

        # Assert that *_quality is False when not specifying it
        parsed = _parse_cli([], False)

        assert not getattr(parsed, quality)
        assert "production" == _determine_quality(parsed)
