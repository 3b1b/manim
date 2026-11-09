from diskcache_community import Cache, Disk

from manimlib.utils import cache

planted_calls = []


def planted():
    planted_calls.append(True)
    return "<svg>planted</svg>"


class Planted:
    def __reduce__(self):
        return (planted, ())


def test_pickled_entry_is_rendered_again_without_running(tmp_path, monkeypatch):
    with Cache(str(tmp_path), disk=type(cache._cache.disk)) as temp_cache:
        monkeypatch.setattr(cache, "_cache", temp_cache)
        renders = []

        @cache.cache_on_disk
        def to_svg(text):
            renders.append(text)
            return f"<svg>{text}</svg>"

        assert to_svg("x") == to_svg("x") == "<svg>x</svg>"
        assert renders == ["x"]

        (key,) = list(temp_cache)
        with Cache(str(tmp_path), disk=Disk) as other_writer:
            other_writer.set(key, Planted())

        assert to_svg("x") == "<svg>x</svg>"
        assert renders == ["x", "x"]
        assert planted_calls == []
