"""Regression tests for manimlib.mobject.types.surface.

``TexturedSurface.pointwise_become_partial`` computed the partial texture
coordinates through a bare ``im_coords`` name that was never defined -- the
array only ever exists as ``self.data["im_coords"]`` /
``tsmobject.data["im_coords"]``.  Animating the partial creation of a
``TexturedSurface`` (e.g. ``ShowCreation`` on a textured surface) therefore
raised ``NameError``.  This guards against the bare name returning.

The check is static (AST) so it needs no OpenGL context: building a real
``TexturedSurface`` requires shaders and a texture image, but the defect is a
plain undefined-name reference in the method body.
"""

import ast
from pathlib import Path

_SURFACE = (
    Path(__file__).resolve().parents[1]
    / "manimlib" / "mobject" / "types" / "surface.py"
)


def _method(class_name: str, method_name: str) -> ast.FunctionDef:
    tree = ast.parse(_SURFACE.read_text(encoding="utf-8"), filename=str(_SURFACE))
    for cls in tree.body:
        if isinstance(cls, ast.ClassDef) and cls.name == class_name:
            for node in cls.body:
                if isinstance(node, ast.FunctionDef) and node.name == method_name:
                    return node
    raise AssertionError(f"{class_name}.{method_name} not found in {_SURFACE.name}")


def test_textured_surface_partial_has_no_bare_im_coords():
    method = _method("TexturedSurface", "pointwise_become_partial")
    bare = [
        node for node in ast.walk(method)
        if isinstance(node, ast.Name) and node.id == "im_coords"
    ]
    assert not bare, (
        "TexturedSurface.pointwise_become_partial references a bare `im_coords` "
        "name; it must be accessed as self.data['im_coords'] / "
        "tsmobject.data['im_coords'] (a bare name raises NameError at runtime)"
    )
