from types import ModuleType

def test_import():
    # check that the package imports without errors
    import manim

    # check that we have access to both the module and dict
    from manim import _config, config
    assert isinstance(_config, ModuleType)
    assert isinstance(config, dict)

    # check that we have access to the logger
    from manim import logger, console
