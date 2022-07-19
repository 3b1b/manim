Changelog
=========

Unreleased
----------

Breaking Changes
^^^^^^^^^^^^^^^^
- Added ``InteractiveScene`` (`#1794 <https://github.com/3b1b/manim/pull/1794>`__)

Fixed bugs
^^^^^^^^^^
- Fixed ``ImageMobject`` by overriding ``set_color`` method (`#1791 <https://github.com/3b1b/manim/pull/1791>`__)
- Fixed bug with trying to close window during embed (`#1796 <https://github.com/3b1b/manim/commit/e0f5686d667152582f052021cd62bd2ef8c6b470>`__)
- Fixed animating ``Mobject.restore`` bug (`#1796 <https://github.com/3b1b/manim/commit/62289045cc8e102121cfe4d7739f3c89102046fb>`__)
- Fixed ``InteractiveScene.refresh_selection_highlight`` (`#1802 <https://github.com/3b1b/manim/commit/205116b8cec964b5619416f6e8acf0d8ac7df828>`__)
- Fixed ``VMobject.match_style`` (`#1821 <https://github.com/3b1b/manim/commit/0060a4860c9d6b073a60cd839269c213446bba7b>`__)

New Features
^^^^^^^^^^^^
- Added specific euler angle getters (`#1794 <https://github.com/3b1b/manim/commit/df2d465140e25fee265f602608aebbbaa2898c7e>`__)
- Added start angle option to ``Circle`` (`#1794 <https://github.com/3b1b/manim/commit/217c1d7bb02f23a61722bf7275c40802be808563>`__)
- Added ``Mobject.is_touching`` (`#1794 <https://github.com/3b1b/manim/commit/c1716895c0d9f36e23487322a18963991100bb95>`__)
- Added ``Mobject.get_highlight`` (`#1794 <https://github.com/3b1b/manim/commit/29816fa74c7aa6ca060b63ab4165c89987e58d8b>`__)
- Allowed for saving and loading mobjects from file (`#1794 <https://github.com/3b1b/manim/commit/50f5d20cc379947d7253d841c060dd7c55fa7787>`__)
- Added ``Mobject.get_all_corners`` (`#1794 <https://github.com/3b1b/manim/commit/f636199d9a5d1e87ab861bcb6aebae6c9d96a133>`__)
- Added ``Scene.id_to_mobject`` and ``Scene.ids_to_group`` (`#1794 <https://github.com/3b1b/manim/commit/cb768c26a0bc63e02c3035b4af31ba5cbc2e9dda>`__)
- Added ``Scene.save_mobject`` and ``Scene.load_mobject`` to allow for saving and loading mobjects from file at the Scene level (`#1794 <https://github.com/3b1b/manim/commit/777b6d37783f8592df8a8abc3d62af972bc5a0c6>`__)
- Added ``InteractiveScene`` (`#1794 <https://github.com/3b1b/manim/commit/c3afc84bfeb3a76ea8ede4ec4d9f36df0d4d9a28>`__)
- Added ``VHighlight`` (`#1794 <https://github.com/3b1b/manim/commit/9d5e2b32fa9215219d11a601829126cea40410d1>`__)
- Allowed for sweeping selection (`#1796 <https://github.com/3b1b/manim/commit/4caa03332367631d2fff15afd7e56b15fe8701ee>`__)
- Allowed stretched-resizing (`#1796 <https://github.com/3b1b/manim/commit/b4b72d1b68d0993b96a6af76c4bb6816f77f0f12>`__)
- Added cursor location label (`#1796 <https://github.com/3b1b/manim/commit/b9751e9d06068f27a327b419c52fd3c9d68db2e6>`__)
- Added ``Mobject.deserialize`` (`#1796 <https://github.com/3b1b/manim/commit/4d8698a0e88333f6481c08d1b84b6e44f9dc4543>`__)
- Added undo and redo stacks for scene (`#1796 <https://github.com/3b1b/manim/commit/cf466006faa00fc12dc22f5732dc21ccedaa5a63>`__)
- Added ``Mobject.looks_identical`` (`#1802 <https://github.com/3b1b/manim/commit/c3c5717dde543b172b928b516d80a29bbd12651f>`__)
- Added equality for ``ShaderWrapper`` (`#1802 <https://github.com/3b1b/manim/commit/3ae0a4e81b7790194bcf27142a1deb29fa548b9d>`__)
- Added ``Mobject.get_ancestors`` (`#1802 <https://github.com/3b1b/manim/commit/db884b0a67fcee1ad7009f1869c475015fa886c7>`__)
- Added smarter default radius to ``Polygon.round_corners`` (`#1802 <https://github.com/3b1b/manim/commit/4c1210b3ab1bf66b161f3d00cb859d36068c2fbb>`__)
- Added checkpoints to ``Scene`` (`#1821 <https://github.com/3b1b/manim/commit/1b589e336f8151f2914ff00e8956baea8a95abc5>`__)
- Added ``crosshair`` to ``InteractiveScene`` (`#1821 <https://github.com/3b1b/manim/commit/33ffd4863aaa7ecf950b7044181a8e8e3c643698>`__)
- Added ``SceneState`` (`#1821 <https://github.com/3b1b/manim/commit/75e1cff5792065aa1c7fb3eb02e6ee0fa0e8e18d>`__)
- Added ``time_span`` option to ``Animation`` (`#1821 <https://github.com/3b1b/manim/commit/a6fcfa3b4053b7f68f7b029eae87dbd207d97ad2>`__)
- Added ``Mobject.arrange_to_fit_dim`` (`#1821 <https://github.com/3b1b/manim/commit/a87d3b5f59a64ce5a89ce6e17310bdbf62166157>`__)
- Added ``DecimalNumber.get_tex`` (`#1821 <https://github.com/3b1b/manim/commit/48689c8c7bc0029bf5c1b540c11f647e857d419b>`__)

Refactor
^^^^^^^^
- Updated parent updater status when adding updaters (`#1794 <https://github.com/3b1b/manim/commit/3b847da9eaad7391e779c5dbce63ad9257d8c773>`__)
- Added case for zero vectors on ``angle_between_vectors`` (`#1794 <https://github.com/3b1b/manim/commit/e8ac25903e19cbb2b2c2037c988baafce4ddcbbc>`__)
- Refactored ``Mobject.clear_updaters`` (`#1794 <https://github.com/3b1b/manim/commit/95f56f5e80106443d705c68fa220850ec38daee0>`__)
- Changed the way changing-vs-static mobjects are tracked (more details see `#1794 <https://github.com/3b1b/manim/commit/50565fcd7a43ed13dc532f17515208edf97f64d0>`__)
- Refactored ``Mobject.is_point_touching`` (`#1794 <https://github.com/3b1b/manim/commit/135f68de35712be266a1a85261d6d44234fc0056>`__)
- Refactored ``Mobject.make_movable`` and ``Mobject.set_animating_status`` to recurse over family (`#1794 <https://github.com/3b1b/manim/commit/48390375037f745c9cb82b03d1cb3a1de6c530f3>`__)
- Refactored ``AnimationGroup`` (`#1794 <https://github.com/3b1b/manim/commit/fdeab8ca953b46a902b531febcf132739ca194d4>`__)
- Refactored ``Scene.save_state`` and ``Scene.restore`` (`#1794 <https://github.com/3b1b/manim/commit/97400a5cf26f33ed507ddeeb9b9a7f1a558d4f17>`__)
- Added ``MANIM_COLORS`` (`#1794 <https://github.com/3b1b/manim/commit/5a34ca1fba8b4724eda0caa11b271d74e49f468c>`__)
- Changed default transparent background codec to be prores (`#1794 <https://github.com/3b1b/manim/commit/eae7dbbe6eaf4344374713052aae694e69b62c28>`__)
- Simplified ``Mobject.copy`` (`#1794 <https://github.com/3b1b/manim/commit/1b009a4b035244bd6a0b48bc4dc945fd3b4236ef>`__)
- Refactored ``StringMobject`` and relevant classes (`#1795 <https://github.com/3b1b/manim/pull/1795>`__)
- Updates to copying based on pickle serializing (`#1796 <https://github.com/3b1b/manim/commit/fe3e10acd29a3dd6f8b485c0e36ead819f2d937b>`)
- Removed ``refresh_shader_wrapper_id`` from ``Mobject.become`` (`#1796 <https://github.com/3b1b/manim/commit/1b2460f02a694314897437b9b8755443ed290cc1>`__)
- Refactored ``Scene.embed`` to play nicely with gui interactions (`#1796 <https://github.com/3b1b/manim/commit/c96bdc243e57c17bb75bf12d73ab5bf119cf1464>`__)
- Made ``BlankScene`` inherit from ``InteractiveScene`` (`#1796 <https://github.com/3b1b/manim/commit/2737d9a736885a594dd101ffe07bb82e00069333>`__)
- Updated behavior of -e flag to take in (optional) strings as inputs (`#1796 <https://github.com/3b1b/manim/commit/bb7fa2c8aa68d7c7992517cfde3c7d0e804e13e8>`__)
- Refactor -e flag (`#1796 <https://github.com/3b1b/manim/commit/71c14969dffc8762a43f9646a0c3dc024a51b8df>`__)
- Reverted to original copying scheme (`#1796 <https://github.com/3b1b/manim/commit/59506b89cc73fff3b3736245dd72e61dcebf9a2c>`__)
- Renamed ``Mobject.is_movable`` to ``Mobject.interaction_allowed`` (`#1796 <https://github.com/3b1b/manim/commit/3961005fd708333a3e77856d10e78451faa04075>`__)
- Refreshed static mobjects on undo's and redo's (`#1796 <https://github.com/3b1b/manim/commit/04bca6cafbb1482b8f25cfb34ce83316d8a095c9>`__)
- Factored out event handling (`#1796 <https://github.com/3b1b/manim/commit/754316bf586be5a59839f8bac6fb9fcc47da0efb>`__)
- Removed ``Mobject.interaction_allowed``, in favor of using ``_is_animating`` for multiple purposes (`#1796 <https://github.com/3b1b/manim/commit/f70e91348c8241bcb96470e7881dd92d9d3386d3>`__)
- Moved Command + z and Command + shift + z behavior to Scene (`#1797 <https://github.com/3b1b/manim/commit/0fd8491c515ad23ca308099abe0f39fc38e2dd0e>`__)
- Slight copy refactor (`#1797 <https://github.com/3b1b/manim/commit/902c2c002d6ca03c8080b2bd02ca36f2b8a748b6>`__)
- When scene saves state, have it only copy mobjects which have changed (`#1802 <https://github.com/3b1b/manim/commit/bd2dce08300e5b110c6668bd6763f3918fcdc65e>`__)
- Cleaned up ``Scene.remove`` function (`#1802 <https://github.com/3b1b/manim/commit/6310e2fb6414b01b3fe4be1d4d98525e34356b5e>`__)
- Speed-ups to ``Mobject.copy`` (`#1802 <https://github.com/3b1b/manim/commit/e49e4b8373c13c7a888193aaf61955470acbe5d6>`__)
- Slight speed-up to ``InteractiveScene.gather_selection`` (`#1802 <https://github.com/3b1b/manim/commit/f2b4245c134da577a2854732ec0331768d93ffbe>`__)
- Only leave wait notes in presenter mode (`#1802 <https://github.com/3b1b/manim/commit/42d1f48c60d11caa043d5458e64bfceb31ea203f>`__)
- Refactored ``remove_list_redundancies`` and ``list_update`` (`#1821 <https://github.com/3b1b/manim/commit/b920e7be7b85bc0bb0577e2f71c4320bb97b42d4>`__)
- Match updaters in ``Mobject.become`` (`#1821 <https://github.com/3b1b/manim/commit/0e45b41fea5f22d136f62f4af2e0d892e61a12ce>`__)
- Don't show animation progress bar by default (`#1821 <https://github.com/3b1b/manim/commit/52259af5df619d3f44fbaff4c43402b93d01be2f>`__)
- Handle quitting during scene more gracefully (`#1821 <https://github.com/3b1b/manim/commit/e83ad785caaa1a1456e07b23f207469d335bbc0d>`__)
- Made ``selection_highlight`` refresh with an updater (`#1821 <https://github.com/3b1b/manim/commit/ac08963feff24a1dd2e57f604b44ea0a18ab01f3>`__)
- Refactored ``anims_from_play_args`` to ``prepare_animations`` which deprecating old style ``self.play(mob.method, ...)`` (`#1821 <https://github.com/3b1b/manim/commit/feab79c260498fd7757a304e24c617a4e51ba1df>`__)
- Made presenter mode hold before first play call (`#1821 <https://github.com/3b1b/manim/commit/a9a151d4eff80cc37b9db0fe7117727aac45ba09>`__)
- Update frame on all play calls when skipping animations, so as to provide a rapid preview during scene loading (`#1821 <https://github.com/3b1b/manim/commit/41b811a5e7c03f528d41555217106e62b287ca3b>`__)
- Renamed frame_rate to fps (`#1821 <https://github.com/3b1b/manim/commit/6decb0c32aec21c09007f9a2b91aaa8e642ca848>`__)
- Let default text alignment be decided in default_config (`#1821 <https://github.com/3b1b/manim/commit/83b4aa6b88b6c3defb19f204189681f5afbb219e>`__)

Dependencies
^^^^^^^^^^^^
- Added dependency on ``pyperclip`` (`#1794 <https://github.com/3b1b/manim/commit/e579f4c955844fba415b976c313f64d1bb0376d0>`__)


v1.6.1
------

Fixed bugs
^^^^^^^^^^
- Fixed the bug of ``MTex`` with multi-line tex string (`#1785 <https://github.com/3b1b/manim/pull/1785>`__)
- Fixed ``interpolate`` (`#1788 <https://github.com/3b1b/manim/pull/1788>`__)
- Fixed ``ImageMobject`` (`#1791 <https://github.com/3b1b/manim/pull/1791>`__)

Refactor
^^^^^^^^
- Added ``\overset`` as a special string in ``Tex`` (`#1783 <https://github.com/3b1b/manim/pull/1783>`__)
- Added ``outer_interpolate`` to perform interpolation using ``np.outer`` on arrays (`#1788 <https://github.com/3b1b/manim/pull/1788>`__)

v1.6.0
------

Breaking changes
^^^^^^^^^^^^^^^^
- **Python 3.6 is no longer supported** (`#1736 <https://github.com/3b1b/manim/pull/1736>`__)

Fixed bugs
^^^^^^^^^^
- Fixed the width of riemann rectangles (`#1762 <https://github.com/3b1b/manim/pull/1762>`__)
- Bug fixed in cases where empty array is passed to shader (`#1764 <https://github.com/3b1b/manim/pull/1764/commits/fa38b56fd87f713657c7f778f39dca7faf15baa8>`__)
- Fixed ``AddTextWordByWord`` (`#1772 <https://github.com/3b1b/manim/pull/1772>`__)
- Fixed ``ControlsExample`` (`#1781 <https://github.com/3b1b/manim/pull/1781>`__)


New features
^^^^^^^^^^^^
- Added more functions to ``Text`` (details: `#1751 <https://github.com/3b1b/manim/pull/1751>`__)
- Allowed ``interpolate`` to work on an array of alpha values (`#1764 <https://github.com/3b1b/manim/pull/1764/commits/bf2d9edfe67c7e63ac0107d1d713df7ae7c3fb8f>`__)
- Allowed ``Numberline.number_to_point`` and ``CoordinateSystem.coords_to_point`` to work on an array of inputs (`#1764 <https://github.com/3b1b/manim/pull/1764/commits/c3e13fff0587d3bb007e71923af7eaf9e4926560>`__)
- Added a basic ``Prismify`` to turn a flat ``VMobject`` into something with depth (`#1764 <https://github.com/3b1b/manim/pull/1764/commits/f249da95fb65ed5495cd1db1f12ece7e90061af6>`__)
- Added ``GlowDots``, analogous to ``GlowDot`` (`#1764 <https://github.com/3b1b/manim/pull/1764/commits/e19f35585d817e74b40bc30b1ab7cee84b24da05>`__)
- Added ``TransformMatchingStrings`` which is compatible with ``Text`` and ``MTex`` (`#1772 <https://github.com/3b1b/manim/pull/1772>`__)
- Added support for ``substring`` and ``case_sensitive`` parameters for ``LabelledString.get_parts_by_string`` (`#1780 <https://github.com/3b1b/manim/pull/1780>`__) 


Refactor
^^^^^^^^
- Added type hints (`#1736 <https://github.com/3b1b/manim/pull/1736>`__)
- Specifid UTF-8 encoding for tex files (`#1748 <https://github.com/3b1b/manim/pull/1748>`__)
- Refactored ``Text`` with the latest manimpango (`#1751 <https://github.com/3b1b/manim/pull/1751>`__)
- Reorganized getters for ``ParametricCurve`` (`#1757 <https://github.com/3b1b/manim/pull/1757>`__)
- Refactored ``CameraFrame`` to use ``scipy.spatial.transform.Rotation`` (`#1764 <https://github.com/3b1b/manim/pull/1764/commits/625460467fdc01fc1b6621cbb3d2612195daedb9>`__)
- Refactored rotation methods to use ``scipy.spatial.transform.Rotation`` (`#1764 <https://github.com/3b1b/manim/pull/1764/commits/7bf3615bb15cc6d15506d48ac800a23313054c8e>`__)
- Used ``stroke_color`` to init ``Arrow`` (`#1764 <https://github.com/3b1b/manim/pull/1764/commits/c0b7b55e49f06b75ae133b5a810bebc28c212cd6>`__)
- Refactored ``Mobject.set_rgba_array_by_color`` (`#1764 <https://github.com/3b1b/manim/pull/1764/commits/8b1f0a8749d91eeda4b674ed156cbc7f8e1e48a8>`__)
- Made panning more sensitive to mouse movements (`#1764 <https://github.com/3b1b/manim/pull/1764/commits/9d0cc810c5fcb4252990e706c6bf880d571cb1a2>`__)
- Added loading progress for large SVGs (`#1766 <https://github.com/3b1b/manim/pull/1766>`__)
- Added getter/setter of ``field_of_view`` for ``CameraFrame`` (`#1770 <https://github.com/3b1b/manim/pull/1770/commits/0610f331a4f7a126a3aae34f8a2a86eabcb692f4>`__)
- Renamed ``focal_distance`` to ``focal_dist_to_height`` and added getter/setter (`#1770 <https://github.com/3b1b/manim/pull/1770/commits/0610f331a4f7a126a3aae34f8a2a86eabcb692f4>`__)
- Added getter and setter for ``VMobject.joint_type`` (`#1770 <https://github.com/3b1b/manim/pull/1770/commits/2a7a7ac5189a14170f883533137e8a2ae09aac41>`__)
- Refactored ``VCube`` (`#1770 <https://github.com/3b1b/manim/pull/1770/commits/0f8d7ed59751d42d5011813ba5694ecb506082f7>`__)
- Refactored ``Prism`` to receive ``width height depth`` instead of ``dimensions`` (`#1770 <https://github.com/3b1b/manim/pull/1770/commits/0f8d7ed59751d42d5011813ba5694ecb506082f7>`__)
- Refactored ``Text``, ``MarkupText`` and ``MTex`` based on ``LabelledString`` (`#1772 <https://github.com/3b1b/manim/pull/1772>`__)
- Refactored ``LabelledString`` and relevant classes (`#1779 <https://github.com/3b1b/manim/pull/1779>`__)


v1.5.0
------

Fixed bugs
^^^^^^^^^^
- Bug fix for the case of calling ``Write`` on a null object (`#1740 <https://github.com/3b1b/manim/pull/1740>`__)


New features
^^^^^^^^^^^^
- Added ``TransformMatchingMTex`` (`#1725 <https://github.com/3b1b/manim/pull/1725>`__)
- Added ``ImplicitFunction`` (`#1727 <https://github.com/3b1b/manim/pull/1727>`__)
- Added ``Polyline`` (`#1731 <https://github.com/3b1b/manim/pull/1731>`__)
- Allowed ``Mobject.set_points`` to take in an empty list, and added ``Mobject.add_point`` (`#1739 <https://github.com/3b1b/manim/pull/1739/commits/a64259158538eae6043566aaf3d3329ff4ac394b>`__)
- Added ``Scene.refresh_locked_data`` (`#1739 <https://github.com/3b1b/manim/pull/1739/commits/33d2894c167c577a15fdadbaf26488ff1f5bff87>`__)
- Added presenter mode to scenes with ``-p`` option (`#1739 <https://github.com/3b1b/manim/pull/1739/commits/9a9cc8bdacb7541b7cd4a52ad705abc21f3e27fe>`__ and `#1742 <https://github.com/3b1b/manim/pull/1742>`__)
- Allowed for an embed by hitting ``ctrl+shift+e`` during interaction (`#1739 <https://github.com/3b1b/manim/pull/1739/commits/9df12fcb7d8360e51cd7021d6877ca1a5c31835e>`__ and `#1746 <https://github.com/3b1b/manim/pull/1746>`__)
- Added ``Mobject.set_min_width/height/depth`` (`#1739 <https://github.com/3b1b/manim/pull/1739/commits/2798d15591a0375ae6bb9135473e6f5328267323>`__)
- Allowed ``Mobject.match_coord/x/y/z`` to take in a point (`#1739 <https://github.com/3b1b/manim/pull/1739/commits/29a4d3e82ba94c007c996b2d1d0f923941452698>`__)
- Added ``text_config`` to ``DecimalNumber`` (`#1744 <https://github.com/3b1b/manim/pull/1744>`__)


Refactor
^^^^^^^^
- Refactored ``MTex`` (`#1725 <https://github.com/3b1b/manim/pull/1725>`__)
- Refactored ``SVGMobject`` with svgelements (`#1731 <https://github.com/3b1b/manim/pull/1731>`__)
- Made sure ``ParametricCurve`` has at least one point (`#1739 <https://github.com/3b1b/manim/pull/1739/commits/2488b9e866fb1ecb842a27dd9f4956ec167e3dee>`__)
- Set default to no tips on ``Axes`` (`#1739 <https://github.com/3b1b/manim/pull/1739/commits/6c6d387a210756c38feca7d34838aa9ac99bb58a>`__)
- Stopped displaying when writing tex string is happening (`#1739 <https://github.com/3b1b/manim/pull/1739/commits/58e06e8f6b7c5059ff315d51fd0018fec5cfbb05>`__)
- Reorganize inheriting order and refactor SVGMobject (`#1745 <https://github.com/3b1b/manim/pull/1745>`__)


Dependencies
^^^^^^^^^^^^
- Added dependency on ``isosurfaces`` (`#1727 <https://github.com/3b1b/manim/pull/1727>`__)
- Removed dependency on ``argparse`` since it's a built-in module (`#1728 <https://github.com/3b1b/manim/pull/1728>`__)
- Removed dependency on ``pyreadline`` (`#1728 <https://github.com/3b1b/manim/pull/1728>`__)
- Removed dependency on ``cssselect2`` (`#1731 <https://github.com/3b1b/manim/pull/1731>`__)
- Added dependency on ``svgelements`` (`#1731 <https://github.com/3b1b/manim/pull/1731>`__)


v1.4.1
------

Fixed bugs 
^^^^^^^^^^
- Temporarily fixed boolean operations' bug  (`#1724 <https://github.com/3b1b/manim/pull/1724>`__)
- Import ``Iterable`` from ``collections.abc`` instead of ``collections`` which is deprecated since python 3.9 (`d2e0811 <https://github.com/3b1b/manim/commit/d2e0811285f7908e71a65e664fec88b1af1c6144>`__)

v1.4.0
------

Fixed bugs
^^^^^^^^^^
- Temporarily fixed ``Lightbulb`` (`f1996f8 <https://github.com/3b1b/manim/pull/1697/commits/f1996f8479f9e33d626b3b66e9eb6995ce231d86>`__)
- Fixed some bugs of ``SVGMobject`` (`#1712 <https://github.com/3b1b/manim/pull/1712>`__)
- Fixed some bugs of SVG path string parser (`#1717 <https://github.com/3b1b/manim/pull/1717>`__)
- Fixed some bugs of ``MTex`` (`#1720 <https://github.com/3b1b/manim/pull/1720>`__)

New features
^^^^^^^^^^^^
- Added option to add ticks on x-axis in ``BarChart`` (`#1694 <https://github.com/3b1b/manim/pull/1694>`__)
- Added ``lable_buff`` config parameter for ``Brace`` (`#1704 <https://github.com/3b1b/manim/pull/1704>`__)
- Added support for ``rotate skewX skewY`` transform in SVG  (`#1712 <https://github.com/3b1b/manim/pull/1712>`__)
- Added style support to ``SVGMobject`` (`#1717 <https://github.com/3b1b/manim/pull/1717>`__)
- Added parser to <style> element of SVG  (`#1719 <https://github.com/3b1b/manim/pull/1719>`__)
- Added support for <line> element in ``SVGMobject`` (`#1719 <https://github.com/3b1b/manim/pull/1719>`__)

Refactor 
^^^^^^^^
- Used ``FFMPEG_BIN`` instead of ``"ffmpeg"`` for sound incorporation (`5aa8d15 <https://github.com/3b1b/manim/pull/1697/commits/5aa8d15d85797f68a8f169ca69fd90d441a3abbe>`__)
- Decorated ``CoordinateSystem.get_axes`` and ``.get_all_ranges`` as abstract method  (`#1709 <https://github.com/3b1b/manim/pull/1709>`__)
- Refactored SVG path string parser (`#1712 <https://github.com/3b1b/manim/pull/1712>`__)
- Allowed ``Mobject.scale`` to receive iterable ``scale_factor`` (`#1712 <https://github.com/3b1b/manim/pull/1712>`__)
- Refactored ``MTex`` (`#1716 <https://github.com/3b1b/manim/pull/1716>`__)
- Improved config helper (``manimgl --config``) (`#1721 <https://github.com/3b1b/manim/pull/1721>`__)
- Refactored ``MTex`` (`#1723 <https://github.com/3b1b/manim/pull/1723>`__)

Dependencies
^^^^^^^^^^^^
- Added dependency on python package `cssselect2 <https://github.com/Kozea/cssselect2>`__ (`#1719 <https://github.com/3b1b/manim/pull/1719>`__)


v1.3.0
------

Fixed bugs 
^^^^^^^^^^

- Fixed ``Mobject.stretch_to_fit_depth`` (`#1653 <https://github.com/3b1b/manim/pull/1653>`__)
- Fixed the bug of rotating camera (`#1655 <https://github.com/3b1b/manim/pull/1655>`__)
- Fixed ``SurfaceMesh`` to be evenly spaced (`c73d507 <https://github.com/3b1b/manim/pull/1688/commits/c73d507c76af5c8602d4118bc7538ba04c03ebae>`__)
- Fixed ``angle_between_vectors`` add ``rotation_between_vectors`` (`82bd02d <https://github.com/3b1b/manim/pull/1688/commits/82bd02d21fbd89b71baa21e077e143f440df9014>`__)
- Fixed ``VMobject.fade`` (`a717314 <https://github.com/3b1b/manim/pull/1688/commits/a7173142bf93fd309def0cc10f3c56f5e6972332>`__)
- Fixed ``angle_between_vectors`` (`fbc329d <https://github.com/3b1b/manim/pull/1688/commits/fbc329d7ce3b11821d47adf6052d932f7eff724a>`__)
- Fixed bug in ``ShowSubmobjectsOneByOne`` (`bcd0990 <https://github.com/3b1b/manim/pull/1688/commits/bcd09906bea5eaaa5352e7bee8f3153f434cf606>`__)
- Fixed bug in ``TransformMatchingParts`` (`7023548 <https://github.com/3b1b/manim/pull/1691/commits/7023548ec62c4adb2f371aab6a8c7f62deb7c33c>`__)

New features
^^^^^^^^^^^^

- Added CLI flag ``--log-level`` to specify log level (`e10f850 <https://github.com/3b1b/manim/commit/e10f850d0d9f971931cc85d44befe67dc842af6d>`__)
- Added operations (``+`` and ``*``) for ``Mobject`` (`#1667 <https://github.com/3b1b/manim/pull/1667>`__)
- Added 4 boolean operations for ``VMobject`` in ``manimlib/mobject/boolean_ops.py`` (`#1675 <https://github.com/3b1b/manim/pull/1675>`__)

  - ``Union(*vmobjects, **kwargs)``  
  - ``Difference(subject, clip, **kwargs)`` 
  - ``Intersection(*vmobjects, **kwargs)`` 
  - ``Exclusion(*vmobjects, **kwargs)`` 
- Added reflectiveness (`81c3ae3 <https://github.com/3b1b/manim/pull/1688/commits/81c3ae30372e288dc772633dbd17def6e603753e>`__)
- Enabled ``glow_factor`` on ``DotCloud`` (`2c7689e <https://github.com/3b1b/manim/pull/1688/commits/2c7689ed9e81229ce87c648f97f26267956c0bc9>`__)
- Added option ``-e`` to insert embed line from the command line (`d065e19 <https://github.com/3b1b/manim/pull/1688/commits/d065e1973d1d6ebd2bece81ce4bdf0c2fff7c772>`__)
- Improved ``point_from_proportion`` to account for arc length (`0e78027 <https://github.com/3b1b/manim/pull/1688/commits/0e78027186a976f7e5fa8d586f586bf6e6baab8d>`__)
- Added shortcut ``set_backstroke`` for setting black background stroke (`781a993 <https://github.com/3b1b/manim/pull/1688/commits/781a9934fda6ba11f22ba32e8ccddcb3ba78592e>`__)
- Added ``Suface.always_sort_to_camera`` (`0b898a5 <https://github.com/3b1b/manim/pull/1688/commits/0b898a5594203668ed9cad38b490ab49ba233bd4>`__)
- Added getter methods for specific euler angles (`e899604 <https://github.com/3b1b/manim/pull/1688/commits/e899604a2d05f78202fcb3b9824ec34647237eae>`__)
- Hade ``rotation_between_vectors`` handle identical/similar vectors (`407c53f <https://github.com/3b1b/manim/pull/1688/commits/407c53f97c061bfd8a53beacd88af4c786f9e9ee>`__)
- Added ``Mobject.insert_submobject`` method (`49743da <https://github.com/3b1b/manim/pull/1688/commits/49743daf3244bfa11a427040bdde8e2bb79589e8>`__)
- Created single progress display for full scene render (`9dd1f47 <https://github.com/3b1b/manim/pull/1688/commits/9dd1f47dabca1580d6102e34e44574b0cba556e7>`__)
- Added ``Circle.get_radius`` (`264f7b1 <https://github.com/3b1b/manim/pull/1691/commits/264f7b11726e9e736f0fe472f66e38539f74e848>`__)
- Added ``Dodecahedron`` (`83841ae <https://github.com/3b1b/manim/pull/1691/commits/83841ae41568a9c9dff44cd163106c19a74ac281>`__)
- Added ``GlowDot`` (`a1d5147 <https://github.com/3b1b/manim/pull/1691/commits/a1d51474ea1ce3b7aa3efbe4c5e221be70ee2f5b>`__)
- Added ``MTex`` , see `#1678 <https://github.com/3b1b/manim/pull/1678>`__ for details (`#1678 <https://github.com/3b1b/manim/pull/1678>`__)

Refactor
^^^^^^^^

- Refactored support for command ``A`` in path of SVG  (`#1662 <https://github.com/3b1b/manim/pull/1662>`__)
- Refactored ``SingleStringTex.balance_braces`` (`#1662 <https://github.com/3b1b/manim/pull/1662>`__)
- Slight tweaks to how saturation_factor works on newton-fractal (`8b454fb <https://github.com/3b1b/manim/pull/1688/commits/8b454fbe9335a7011e947093230b07a74ba9c653>`__)
- Made it possible to set full screen preview as a default (`317a5d6 <https://github.com/3b1b/manim/pull/1688/commits/317a5d6226475b6b54a78db7116c373ef84ea923>`__)
- Used ``quick_point_from_proportion`` for graph points (`e764da3 <https://github.com/3b1b/manim/pull/1688/commits/e764da3c3adc5ae2a4ce877b340d2b6abcddc2fc>`__)
- Made sure ``Line.set_length`` returns self (`d2182b9 <https://github.com/3b1b/manim/pull/1688/commits/d2182b9112300558b6c074cefd685f97c10b3898>`__)
- Better align ``SurfaceMesh`` to the corresponding surface polygons (`eea3c6b <https://github.com/3b1b/manim/pull/1688/commits/eea3c6b29438f9e9325329c4355e76b9f635e97a>`__)
- Match ``fix_in_frame`` status for ``FlashAround`` mobject (`ee1594a <https://github.com/3b1b/manim/pull/1688/commits/ee1594a3cb7a79b8fc361e4c4397a88c7d20c7e3>`__)
- Made sure ``Mobject.is_fixed_in_frame`` stays updated with uniforms (`ba23fbe <https://github.com/3b1b/manim/pull/1688/commits/ba23fbe71e4a038201cd7df1d200514ed1c13bc2>`__)
- Made sure ``skip_animations`` and ``start_at_animation_number`` play well together (`98b0d26 <https://github.com/3b1b/manim/pull/1691/commits/98b0d266d2475926a606331923cca3dc1dea97ad>`__)
- Updated progress display for full scene render (`f8e6e7d <https://github.com/3b1b/manim/pull/1691/commits/f8e6e7df3ceb6f3d845ced4b690a85b35e0b8d00>`__)
- ``VectorizedPoint`` should call ``__init__`` for both super classes (`8f1dfab <https://github.com/3b1b/manim/pull/1691/commits/8f1dfabff04a8456f5c4df75b0f97d50b2755003>`__)
- Used array copy when checking need for refreshing triangulation (`758f329 <https://github.com/3b1b/manim/pull/1691/commits/758f329a06a0c198b27a48c577575d94554305bf>`__)


Dependencies
^^^^^^^^^^^^

- Added dependency on python package `skia-pathops <https://github.com/fonttools/skia-pathops>`__ (`#1675 <https://github.com/3b1b/manim/pull/1675>`__)

v1.2.0
------

Fixed bugs
^^^^^^^^^^

- Fixed ``put_start_and_end_on`` in 3D (`#1592 <https://github.com/3b1b/manim/pull/1592>`__)
- Fixed ``DecimalNumber``'s scaling issue (`#1601 <https://github.com/3b1b/manim/pull/1601>`__)
- Fixed bug with common range array used for all coordinate systems (`56df154 <https://github.com/3b1b/manim/commit/56df15453f3e3837ed731581e52a1d76d5692077>`__)
- Fixed ``CoordinateSystem`` init bug (`8645894 <https://github.com/3b1b/manim/commit/86458942550c639a241267d04d57d0e909fcf252>`__)
- Fixed bug for single-valued ``ValueTracker`` (`0dc096b <https://github.com/3b1b/manim/commit/0dc096bf576ea900b351e6f4a80c13a77676f89b>`__)
- Fixed bug with SVG rectangles (`54ad355 <https://github.com/3b1b/manim/commit/54ad3550ef0c0e2fda46b26700a43fa8cde0973f>`__)
- Fixed ``DotCloud.set_radii`` (`d45ea28 <https://github.com/3b1b/manim/commit/d45ea28dc1d92ab9c639a047c00c151382eb0131>`__)
- Temporarily fixed bug for ``PMobject`` array resizing (`b543cc0 <https://github.com/3b1b/manim/commit/b543cc0e32d45399ee81638b6d4fb631437664cd>`__)
- Fixed ``match_style`` (`5f878a2 <https://github.com/3b1b/manim/commit/5f878a2c1aa531b7682bd048468c72d2835c7fe5>`__)
- Fixed negative ``path_arc`` case (`719c81d <https://github.com/3b1b/manim/commit/719c81d72b00dcf49f148d7c146774b22e0fe348>`__)
- Fixed bug with ``CoordinateSystem.get_lines_parallel_to_axis`` (`c726eb7 <https://github.com/3b1b/manim/commit/c726eb7a180b669ee81a18555112de26a8aff6d6>`__)
- Fixed ``ComplexPlane`` -i display bug (`7732d2f <https://github.com/3b1b/manim/commit/7732d2f0ee10449c5731499396d4911c03e89648>`__)

New features 
^^^^^^^^^^^^

- Supported the elliptical arc command ``A`` for ``SVGMobject`` (`#1598 <https://github.com/3b1b/manim/pull/1598>`__)
- Added ``FlashyFadeIn`` (`#1607 <https://github.com/3b1b/manim/pull/1607>`__)
- Save triangulation  (`#1607 <https://github.com/3b1b/manim/pull/1607>`__)
- Added new ``Code`` mobject (`#1625 <https://github.com/3b1b/manim/pull/1625>`__)
- Add warnings and use rich to display log (`#1637 <https://github.com/3b1b/manim/pull/1637>`__)
- Added ``VCube`` (`bd356da <https://github.com/3b1b/manim/commit/bd356daa99bfe3134fcb192a5f72e0d76d853801>`__)
- Supported ``ValueTracker`` to track vectors (`6d72893 <https://github.com/3b1b/manim/commit/6d7289338234acc6658b9377c0f0084aa1fa7119>`__)
- Added ``set_max_width``, ``set_max_height``, ``set_max_depth`` to ``Mobject`` (`3bb8f3f <https://github.com/3b1b/manim/commit/3bb8f3f0422a5dfba0da6ef122dc0c01f31aff03>`__)
- Added ``TracgTail`` (`a35dd5a <https://github.com/3b1b/manim/commit/a35dd5a3cbdeffa3891d5aa5f80287c18dba2f7f>`__)
- Added ``Scene.point_to_mobject`` (`acba13f <https://github.com/3b1b/manim/commit/acba13f4991b78d54c0bf93cce7ca3b351c25476>`__)
- Added poly_fractal shader (`f84b8a6 <https://github.com/3b1b/manim/commit/f84b8a66fe9e8b3872e5c716c5c240c14bb555ee>`__)
- Added kwargs to ``TipableVMobject.set_length`` (`b24ba19 <https://github.com/3b1b/manim/commit/b24ba19dec48ba4e38acbde8eec6d3a308b6ab83>`__)
- Added ``Mobject.replicate`` (`17c2772 <https://github.com/3b1b/manim/commit/17c2772b84abf6392a4170030e36e981de4737d0>`__)
- Added mandelbrot_fractal shader (`33fa76d <https://github.com/3b1b/manim/commit/33fa76dfac36e70bb5fad69dc6a336800c6dacce>`__)
- Saved state before each embed (`f22a341 <https://github.com/3b1b/manim/commit/f22a341e8411eae9331d4dd976b5e15bc6db08d9>`__)
- Allowed releasing of Textures (`e10a752 <https://github.com/3b1b/manim/commit/e10a752c0001e8981038faa03be4de2603d3565f>`__)
- Consolidated and renamed newton_fractal shader (`14fbed7 <https://github.com/3b1b/manim/commit/14fbed76da4b493191136caebb8a955e2d41265b>`__)
- Hade ``ImageMoject`` remember the filepath to the Image (`6cdbe0d <https://github.com/3b1b/manim/commit/6cdbe0d67a11ab14a6d84840a114ae6d3af10168>`__)

Refactor
^^^^^^^^

- Changed back to simpler ``Mobject.scale`` implementation (`#1601 <https://github.com/3b1b/manim/pull/1601>`__)
- Simplified ``Square`` (`b667db2 <https://github.com/3b1b/manim/commit/b667db2d311a11cbbca2a6ff511d2c3cf1675486>`__)
- Removed unused parameter ``triangulation_locked`` (`40290ad <https://github.com/3b1b/manim/commit/40290ada8343f10901fa9151cbdf84689667786d>`__)
- Reimplemented ``Arrow`` (`8647a64 <https://github.com/3b1b/manim/commit/8647a6429dd0c52cba14e971b8c09194a93cfd87>`__)
- Used ``make_approximately_smooth`` for ``set_points_smoothly`` by default (`d8378d8 <https://github.com/3b1b/manim/commit/d8378d8157040cd797cc47ef9576beffd8607863>`__)
- Refactored to call ``_handle_scale_side_effects`` after scaling takes place (`7b4199c <https://github.com/3b1b/manim/commit/7b4199c674e291f1b84678828b63b6bd4fcc6b17>`__)
- Refactored to only call ``throw_error_if_no_points`` once for ``get_start_and_end`` (`7356a36 <https://github.com/3b1b/manim/commit/7356a36fa70a8279b43ae74e247cbd43b2bfd411>`__)
- Made sure framerate is 30 for previewed scenes (`0787c4f <https://github.com/3b1b/manim/commit/0787c4f36270a6560b50ce3e07b30b0ec5f2ba3e>`__)
- Pushed ``pixel_coords_to_space_coords`` to ``Window`` (`c635f19 <https://github.com/3b1b/manim/commit/c635f19f2a33e916509e53ded46f55e2afa8f5f2>`__)
- Refactored to pass tuples and not arrays to uniforms (`d5a88d0 <https://github.com/3b1b/manim/commit/d5a88d0fa457cfcf4cb9db417a098c37c95c7051>`__)
- Refactored to copy uniform arrays in ``Mobject.copy`` (`9483f26 <https://github.com/3b1b/manim/commit/9483f26a3b056de0e34f27acabd1a946f1adbdf9>`__)
- Added ``bounding_box`` as exceptional key to point_cloud mobject (`ed1fc4d <https://github.com/3b1b/manim/commit/ed1fc4d5f94467d602a568466281ca2d0368b506>`__)
- Made sure stroke width is always a float (`329d2c6 <https://github.com/3b1b/manim/commit/329d2c6eaec3d88bfb754b555575a3ea7c97a7e0>`__)


v1.1.0
-------

Fixed bugs
^^^^^^^^^^

- Fixed the bug of :func:`~manimlib.utils.iterables.resize_with_interpolation` in the case of ``length=0``
- Fixed the bug of ``__init__`` in :class:`~manimlib.mobject.geometry.Elbow`
- If chosen monitor is not available, choose one that does exist
- Make sure mobject data gets unlocked after animations
- Fixed a bug for off-center vector fields
- Had ``Mobject.match_points`` return self
- Fixed chaining animation in example scenes
- Fixed the default color of tip
- Fixed a typo in ``ShowPassingFlashWithThinningStrokeWidth``
- Fixed the default size of ``Text``
- Fixed a missing import line in ``mobject.py``
- Fixed the bug in ControlsExample
- Make sure frame is added to the scene when initialization
- Fixed zooming directions
- Rewrote ``earclip_triangulation`` to fix triangulation
- Allowed sound_file_name to be taken in without extensions

New features
^^^^^^^^^^^^

- Added :class:`~manimlib.animation.indication.VShowPassingFlash`
- Added ``COLORMAP_3B1B``
- Added some methods to coordinate system to access all axes ranges
  
  - :meth:`~manimlib.mobject.coordinate_systems.CoordinateSystem.get_origin`
  - :meth:`~manimlib.mobject.coordinate_systems.CoordinateSystem.get_all_ranges`
- Added :meth:`~manimlib.mobject.mobject.Mobject.set_color_by_rgba_func`
- Updated :class:`~manimlib.mobject.vector_field.VectorField` and :class:`~manimlib.mobject.vector_field.StreamLines`
- Allow ``3b1b_colormap`` as an option for :func:`~manimlib.utils.color.get_colormap_list`
- Return ``stroke_width`` as 1d array
- Added :meth:`~manimlib.mobject.svg.text_mobject.Text.get_parts_by_text`
- Use Text not TexText for Brace
- Update to Cross to make it default to variable stroke width
- Added :class:`~manimlib.animation.indication.FlashAround` and :class:`~manimlib.animation.indication.FlashUnder`
- Allowed configuration in ``Brace.get_text``
- Added :meth:`~manimlib.camera.camera.CameraFrame.reorient` for quicker changes to frame angle
- Added ``units`` to :meth:`~manimlib.camera.camera.CameraFrame.set_euler_angles`
- Allowed any ``VMobject`` to be passed into ``TransformMatchingTex``
- Removed double brace convention in ``Tex`` and ``TexText``
- Added support for debugger launch
- Added CLI flag ``--config_file`` to load configuration file manually
- Added ``tip_style`` to ``tip_config``
- Added ``MarkupText``
- Take in ``u_range`` and ``v_range`` as arguments to ``ParametricSurface``
- Added ``TrueDot``