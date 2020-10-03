from manim.mobject.value_tracker import ValueTracker


def test_value_tracker_set_value():
    """Test ValueTracker.set_value()"""
    tracker = ValueTracker()
    tracker.set_value(10.0)
    assert tracker.get_value() == 10.0


def test_value_tracker_get_value():
    """Test ValueTracker.get_value()"""
    tracker = ValueTracker(10.0)
    assert tracker.get_value() == 10.0


def test_value_tracker_increment_value():
    """Test ValueTracker.increment_value()"""
    tracker = ValueTracker(0.0)
    tracker.increment_value(10.0)
    assert tracker.get_value() == 10.0


def test_value_tracker_iadd():
    """Test ValueTracker.__iadd__()"""
    tracker = ValueTracker(0.0)
    tracker += 10.0
    assert tracker.get_value() == 10.0
