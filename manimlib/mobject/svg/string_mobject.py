from __future__ import annotations

from abc import ABC, abstractmethod
import itertools as it
import re
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist

from manimlib.constants import DEFAULT_MOBJECT_COLOR
from manimlib.logger import log
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.color import color_to_hex
from manimlib.utils.color import hex_to_int
from manimlib.utils.color import int_to_hex

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable
    from manimlib.typing import ManimColor, Span, Selector


class StringMobject(SVGMobject, ABC):
    """
    Abstract base class for string-based Manim objects that converts text-like
    content into SVG geometry while preserving the relationship between
    substrings and their corresponding vector submobjects.

    ``StringMobject`` is the common base class for text-rendering classes such
    as ``Tex`` and ``MarkupText``. It extends ``SVGMobject`` with a substring
    selection system, allowing users to identify and manipulate parts of a
    rendered string using textual content, regular expressions, or index spans
    instead of relying exclusively on numerical submobject indices.

    The class parses the input string into labelled spans, reconstructs the
    string with additional commands, converts the resulting SVG into Manim
    mobjects, and associates each generated submobject with a numerical label.
    These labels allow the class to map substrings to their corresponding
    rendered geometry.

    Two SVG representations may be involved during initialization:

        1. The original SVG, which supplies the actual rendered geometry.
        2. A labelled SVG, which inserts color-based identifiers into the
           rendered content so that individual submobjects can be associated
           with their corresponding string spans.

    When ``use_labelled_svg`` is enabled, the labelled SVG is used directly
    as the source of the object's geometry.

    This class is abstract. Concrete subclasses must implement the
    format-specific methods that generate SVG content and interpret the
    commands used to identify string spans.

    Class Attributes
    ----------------
    height : None
        Overrides the default height inherited from ``SVGMobject``. Unless a
        subclass or constructor configuration specifies a target height, the
        imported geometry is not automatically resized to the default height
        of ``SVGMobject``.

    Parameters
    ----------
    string : str
        The original string to parse and render. This is the source text used
        for substring matching, span calculations, and content reconstruction.
    fill_color : ManimColor, optional
        Fill color applied to the rendered geometry. Defaults to
        ``DEFAULT_MOBJECT_COLOR``.
    fill_border_width : float, optional
        Border width passed to ``set_fill``. Defaults to ``0.5``.
    stroke_color : ManimColor, optional
        Stroke color applied to the rendered geometry. Defaults to
        ``DEFAULT_MOBJECT_COLOR``.
    stroke_width : float, optional
        Stroke width applied to the rendered geometry. Defaults to ``0``,
        meaning no visible stroke by default.
    base_color : ManimColor, optional
        Base color stored by the instance for use by concrete subclasses.
        A falsy value falls back to ``DEFAULT_MOBJECT_COLOR``.
    isolate : Selector, optional
        A selector or collection of selectors identifying substrings that
        should be treated as separate labelled spans. Supported selector
        forms include strings, compiled regular expressions, and two-element
        tuples representing index spans. Defaults to an empty tuple.
    protect : Selector, optional
        A selector or collection of selectors identifying substrings that
        should be protected from normal substring isolation during parsing.
        This is particularly useful when some portions of a formatted string
        must remain together or must not be independently labelled.
    use_labelled_svg : bool, optional
        Determines whether the labelled SVG is used directly as the geometry
        source. When ``True``, the SVG generated with label colors is parsed
        directly. When ``False``, the original SVG supplies the geometry and
        a second labelled SVG is generated to associate labels with the
        original submobjects. Defaults to ``False``.
    **kwargs
        Additional keyword arguments forwarded to ``SVGMobject.__init__``.

    Attributes
    ----------
    string : str
        The original string provided to the constructor.
    base_color : ManimColor
        The effective base color stored by the instance.
    isolate : Selector
        The selector configuration used to isolate substrings.
    protect : Selector
        The selector configuration used to protect portions of the string.
    use_labelled_svg : bool
        Whether the labelled SVG is used directly as the object's geometry.
    labels : list[int]
        Numerical labels assigned to the final submobjects. Each label
        corresponds to an entry in ``labelled_spans``.
    labelled_spans : list[Span]
        Ordered spans representing the full string and the labelled regions
        identified during parsing. The first entry represents the entire
        string; subsequent entries represent configured, isolated, or
        command-derived spans.
    labelled_submobs : list[VMobject]
        The submobjects generated from the labelled SVG when the original
        SVG is used for the actual geometry.
    unlabelled_submobs : list[VMobject]
        The submobjects generated from the original, unlabelled SVG.
    reconstruct_string : Callable
        A function created during parsing that reconstructs portions of the
        original string using selected boundary items, command replacements,
        and inserted formatting commands.

    Not every attribute is created in every execution path. For example,
    ``labelled_submobs`` and ``unlabelled_submobs`` are populated in the
    normal two-SVG labelling path, but are not assigned by that path when
    ``use_labelled_svg`` is enabled.

    Initialization Process
    ----------------------
    The constructor performs the following operations:

    1. Stores the input string, base color, isolation selectors, protection
       selectors, and labelled-SVG configuration.
    2. Calls ``parse`` to identify and organize spans in the string and
       create the string-reconstruction function.
    3. Generates the SVG markup by calling ``get_svg_string``.
    4. Passes the resulting markup to ``SVGMobject`` for SVG parsing and
       geometric construction.
    5. Applies the configured stroke color and stroke width.
    6. Applies the configured fill color and fill border width.
    7. Extracts each submobject's ``label`` attribute into ``self.labels``.
    8. Calls ``draw_fills_together`` to configure the handling of overlapping
       glyph fills.

    The final step is relevant when glyphs overlap and the fill is partly
    transparent. The typesetter generally places glyphs without overlapping
    them, so the method adjusts the default fill-drawing behavior for this
    special case.

    SVG Generation
    --------------
    ``get_svg_string(is_labelled=False)`` obtains the content to render by
    calling ``get_content`` and then delegates SVG document construction to
    the abstract method ``get_svg_string_by_content``.

    The labelled mode is enabled when either the method's ``is_labelled``
    argument or the instance's ``use_labelled_svg`` flag is true.

    This design separates two responsibilities:

        - ``get_content`` reconstructs the appropriate string content and
          inserts commands associated with labelled spans.
        - ``get_svg_string_by_content`` converts that content into complete
          SVG markup according to the concrete subclass's rendering format.

    The latter is abstract because different subclasses may use different
    string syntaxes and rendering engines.

    Label Assignment
    ----------------
    ``assign_labels_by_color`` assigns integer labels to a list of mobjects
    by interpreting each mobject's fill color as an encoded label.

    The expected color encoding is based on the numerical labels associated
    with ``self.labelled_spans``. The method first obtains the number of
    labelled spans.

    If there is exactly one labelled span, every mobject receives label
    ``0`` and no color decoding is necessary.

    Otherwise, each mobject's fill color is converted to hexadecimal form
    using ``color_to_hex`` and then decoded to an integer using
    ``hex_to_int``. If the decoded value is greater than or equal to the
    number of labelled spans, it is considered unrecognizable and replaced
    with label ``0``.

    Unrecognizable color values are collected and reported through a warning.
    The warning indicates that the resulting correspondence between
    submobjects and spans may be unexpected.

    The method stores the resulting integer directly on each mobject as
    ``mob.label``.

    SVG Conversion and Label Recovery
    ---------------------------------
    ``mobjects_from_svg_string`` overrides the corresponding method in
    ``SVGMobject`` to recover substring labels from SVG geometry.

    When ``use_labelled_svg`` is true, the method:

        1. Parses the supplied labelled SVG through the parent implementation.
        2. Assigns labels to the resulting submobjects using their fill colors.
        3. Returns those labelled submobjects directly.

    When ``use_labelled_svg`` is false, the method follows a two-SVG process:

        1. Parses the original SVG to create the actual, unlabelled geometry.
        2. Generates labelled content using ``get_content(is_labelled=True)``.
        3. Builds a second SVG using ``get_svg_string_by_content``.
        4. Parses that SVG to obtain submobjects whose colors encode labels.
        5. Stores the original and labelled submobjects separately.
        6. Assigns numerical labels to the labelled submobjects.
        7. Rearranges the labelled submobjects to correspond spatially to the
           original submobjects.
        8. Copies each label from the rearranged labelled submobject to its
           corresponding original submobject.

    If the number of original and labelled submobjects differs, a warning is
    logged and all original submobjects are assigned label ``0``. The original
    submobjects are then returned.

    This fallback avoids assigning incorrect individual labels when the two
    SVG representations cannot be aligned reliably.

    Spatial Alignment of Submobjects
    --------------------------------
    ``rearrange_submobjects_by_positions`` attempts to align the labelled SVG
    submobjects with their unlabelled counterparts.

    The labelled submobjects are first placed into a ``VGroup`` and that
    group is replaced with a group containing the unlabelled submobjects.
    This makes the labelled geometry occupy the same overall region as the
    original geometry.

    The method then calculates a distance matrix using ``scipy.spatial.distance.cdist``.
    Each matrix entry represents the Euclidean distance between the center
    of an unlabelled submobject and the center of a labelled submobject.

    The Hungarian assignment algorithm, implemented by
    ``scipy.optimize.linear_sum_assignment``, finds a minimum-cost
    assignment between these positions. The labelled list is reordered
    according to the resulting indices.

    This approach is heuristic. Inserting color commands into a string can
    change the generated SVG geometry, and matching objects by their centers
    cannot guarantee that every labelled shape corresponds to the correct
    original shape.

    If the labelled list is empty, the method returns immediately.

    Selector System
    ---------------
    A selector identifies a region of the original string. The selector
    utilities support strings, regular expressions, index spans, and
    collections of these selector forms.

    The exact behavior depends on which selector utility is used and whether
    the requested span is isolated, protected, or selected after rendering.

    find_spans_by_selector(selector)
        Converts a selector into a list of index spans.

        For a string selector, the method uses ``re.finditer`` with
        ``re.escape``. This finds literal occurrences rather than interpreting
        the selector as a regular expression.

        For a compiled ``re.Pattern``, the method uses its ``finditer``
        method to obtain matching spans.

        For a two-element tuple containing integers or ``None``, the method
        interprets the tuple as a start/end span. Negative indices are
        converted relative to the string length, and indices are clamped to
        the valid range.

        A collection of selectors is processed item by item. If an item
        has an unsupported form, a ``TypeError`` is raised.

        The final result filters out spans whose start exceeds their end.
        The method does not itself merge duplicate spans or resolve
        overlapping matches.

    span_contains(span_0, span_1)
        Static method returning ``True`` if ``span_0`` fully contains
        ``span_1``. Containment includes equality at either boundary.

    Parsing
    -------
    ``parse`` constructs the span and label structure used by the class.

    It begins by obtaining:

        - Configured spans and their associated formatting attributes through
          ``get_configured_items``.
        - Isolated spans through ``find_spans_by_selector(self.isolate)``.
        - Protected spans through ``find_spans_by_selector(self.protect)``.
        - Format-specific command matches through ``get_command_matches``.

    The method then creates boundary events for each configured span,
    isolated span, protected span, and command match. Each event records the
    category, item index, and whether it represents the beginning or end
    of that item.

    The events are sorted using a custom key that accounts for their
    positions, span lengths, category, and item order. This establishes a
    consistent order for processing nested spans and formatting commands.

    During processing, the parser maintains several pieces of state:

        - ``inserted_items``: records label boundaries and command matches
          that will be used during string reconstruction.
        - ``labelled_items``: stores spans together with their associated
          formatting attribute dictionaries.
        - ``overlapping_spans``: records isolated or configured spans that
          partially overlap another span in an unsupported way.
        - ``level_mismatched_spans``: records spans whose surrounding command
          or bracket nesting levels do not match.
        - ``protect_level``: tracks whether the current region lies inside
          a protected span.
        - ``bracket_stack`` and ``bracket_count``: track nesting levels used
          to distinguish compatible string regions.
        - ``open_command_stack``: tracks opening formatting commands awaiting
          their corresponding closing commands.
        - ``open_stack``: tracks opening boundaries of configured and isolated
          spans until their closing boundaries are processed.

    The parser uses these structures to determine which spans can safely
    receive labels and which regions should be excluded from isolation.

    Formatting commands are interpreted through subclass-provided methods
    such as ``get_command_flag`` and ``get_attr_dict_from_command_pair``.
    When a compatible opening and closing command pair is found, the parser
    records the enclosed span and its associated attributes.

    Configured spans and isolated spans are labelled when their opening
    and closing boundaries match, the region is not protected, and the
    bracket nesting level is consistent.

    After processing the events, the parser inserts a span representing the
    entire string at label index ``0``. It also inserts the corresponding
    start and end boundary items used by the reconstruction process.

    Unsupported partial overlaps and nesting mismatches generate warnings.
    The parser then stores:

        - ``self.labelled_spans``, containing the spans associated with labels.
        - ``self.reconstruct_string``, a function used to reconstruct the
          whole string or a selected region.

    String Reconstruction
    ---------------------
    The reconstruction function created by ``parse`` accepts a start item,
    an end item, a command-replacement function, and a command-insertion
    function.

    It identifies the relevant boundary items and converts them into
    zero-width insertion points or replacement spans. Text between adjacent
    items is extracted from the original string, and the generated pieces
    are interleaved to create the reconstructed content.

    This approach allows subclasses to insert format-specific commands
    around selected spans without directly changing the original string.

    The reconstructed string can represent the complete original content
    or a selected region with formatting commands removed or replaced.
    The exact replacement behavior depends on the functions supplied by
    the subclass.

    Content Construction
    --------------------
    ``get_content(is_labelled)`` calls the stored reconstruction function
    with the full-string boundary items.

    For every labelled span, it calls ``get_command_string`` to insert
    the appropriate opening or closing command. When labelled output is
    requested, the span's numerical label is converted to a hexadecimal
    color representation using ``int_to_hex`` and supplied as ``label_hex``.

    The resulting content is wrapped with the prefix and suffix returned by
    ``get_content_prefix_and_suffix``. This lets subclasses supply document
    headers, footers, or other format-specific content required by their
    rendering engine.

    Abstract Interface
    ------------------
    The following methods are intended to be implemented by concrete
    subclasses.

    get_svg_string_by_content(content)
        Convert the supplied formatted content into a complete SVG document.

    get_command_matches(string)
        Static method returning the formatting-command matches found in the
        supplied string.

    get_command_flag(match_obj)
        Static method classifying a command match, typically distinguishing
        opening commands, neutral commands, and closing commands.

    replace_for_content(match_obj)
        Static method defining how commands are replaced when constructing
        ordinary SVG content.

    replace_for_matching(match_obj)
        Static method defining how commands are replaced when reconstructing
        strings for matching or grouping purposes.

    get_attr_dict_from_command_pair(open_command, close_command)
        Static method returning the formatting attributes associated with a
        compatible pair of opening and closing commands, or ``None`` when
        no valid attribute dictionary can be obtained.

    get_configured_items()
        Return configured spans and their associated formatting attribute
        dictionaries.

    get_command_string(attr_dict, is_end, label_hex)
        Static method generating the format-specific command inserted at
        a span boundary. ``is_end`` indicates whether the command closes
        a span, while ``label_hex`` optionally specifies its encoded label
        color.

    get_content_prefix_and_suffix(is_labelled)
        Return the prefix and suffix required to wrap the reconstructed
        content in the appropriate document structure.

    These methods are decorated with ``abstractmethod``. The class therefore
    cannot be instantiated directly unless all inherited abstract methods
    have been implemented by a concrete subclass.

    Substring-to-Submobject Mapping
    -------------------------------
    get_submob_indices_list_by_span(arbitrary_span)
        Returns the indices of submobjects whose assigned labels refer to
        spans fully contained by ``arbitrary_span``.

        Each submobject's label indexes ``self.labelled_spans``. The method
        uses ``span_contains`` to determine whether the requested span
        contains the span associated with that label.

    get_specified_part_items()
        Returns a list of pairs. Each pair contains the text represented by
        a labelled span and the indices of the submobjects associated with
        that span. The first whole-string span is excluded.

    get_specified_substrings()
        Returns the distinct substrings represented by the labelled spans.
        Duplicate substrings are removed while preserving their first
        occurrence order.

    get_group_part_items()
        Groups consecutive submobjects according to their labels and
        reconstructs corresponding text fragments.

        The method first groups consecutive equal labels in ``self.labels``.
        It computes the submobject-index ranges for those groups and then
        determines suitable reconstruction boundaries using span containment.

        The selected text fragments are reconstructed using
        ``replace_for_matching`` and an empty command-insertion function.
        Whitespace is removed from each reconstructed fragment before the
        resulting substring/index-list pairs are returned.

        This method returns information about consecutive groups; it does
        not itself create the resulting ``VGroup`` objects.

    get_submob_indices_lists_by_selector(selector)
        Finds the spans represented by a selector and maps each span to
        its corresponding submobject indices. Empty index lists are removed
        from the result.

    build_parts_from_indices_lists(indices_lists)
        Creates a ``VGroup`` containing one subgroup for each supplied list
        of submobject indices. Each subgroup contains references to the
        corresponding entries in ``self.submobjects``.

    build_groups()
        Uses ``get_group_part_items`` to obtain consecutive groups and
        converts their index lists into a ``VGroup`` of subgroups.

    select_parts(selector)
        Selects and groups submobjects corresponding to a selector.

        If the selector is a string or compiled regular expression and is
        not already present in ``get_specified_substrings()``, the method
        delegates to ``select_unisolated_substring``. Otherwise, it obtains
        the relevant index lists through ``get_submob_indices_lists_by_selector``
        and constructs groups using ``build_parts_from_indices_lists``.

    __getitem__(value)
        Extends the inherited indexing behavior.

        Integer and slice arguments are passed directly to the parent
        implementation. Other values are interpreted as substring selectors
        and passed to ``select_parts``.

    select_part(selector, index=0)
        Returns the subgroup at the specified index from the result of
        ``select_parts(selector)``. The default index is ``0``.

    substr_to_path_count(substr)
        Returns the number of non-whitespace characters in ``substr``.
        This is calculated by removing whitespace using a regular expression.

    get_symbol_substrings()
        Returns the individual non-whitespace characters of the original
        string as a list. Whitespace is removed before the list is created.

    Examples
    --------
    The class is abstract, so use a concrete subclass such as ``Tex`` or
    ``MarkupText`` rather than constructing ``StringMobject`` directly.

    Render a mathematical expression with ``Tex``:

    >>> expression = Tex(r"x^2 + y^2 = z^2")
    >>> self.add(expression)

    Isolate a substring for later selection:

    >>> expression = Tex(
    ...     r"x^2 + y^2 = z^2",
    ...     isolate=["x^2", "y^2", "z^2"],
    ... )
    >>> selected = expression["x^2"]
    >>> self.add(selected)

    Use a regular expression to identify matching text:

    >>> expression = Tex(
    ...     "a + b + c",
    ...     isolate=re.compile(r"[abc]"),
    ... )
    >>> selected = expression["a"]
    >>> self.add(selected)

    Use a tuple to specify an index span:

    >>> expression = Tex("abcdef")
    >>> selected = expression[(0, 3)]
    >>> self.add(selected)

    Access a single selected part:

    >>> expression = Tex(
    ...     "x + y",
    ...     isolate=["x", "y"],
    ... )
    >>> part = expression.select_part("y")
    >>> self.add(part)

    Build groups from the current labelled submobjects:

    >>> expression = Tex(
    ...     "a + b",
    ...     isolate=["a", "b"],
    ... )
    >>> groups = expression.build_groups()
    >>> self.add(groups)

    Important Notes and Limitations
    -------------------------------
    1. **Partial overlaps**

       The selector system does not guarantee correct handling of partially
       overlapping isolated substrings. For example, selecting overlapping
       regions such as ``"abcd"`` and ``"cdef"`` may produce a warning and
       leave some regions without the expected individual labels.

    2. **Repeated substrings**

       A string selector can match multiple occurrences. The selection
       machinery works with spans and corresponding labels, while
       ``get_specified_substrings`` removes duplicate substring values.
       Therefore, the list of unique specified substrings should not be
       treated as a complete list of every occurrence.

    3. **Labelled SVG alignment**

       The original and labelled SVGs may produce different geometry because
       inserting formatting commands can affect the rendering output.
       Matching their submobjects by center positions is a heuristic and
       cannot guarantee correct correspondence for every SVG.

    4. **Color-based labels**

       The label-recovery process relies on fill colors encoding numerical
       identifiers. If an SVG renderer changes these colors or generates
       unexpected fill colors, labels may be assigned incorrectly or reset
       to zero.

    5. **Subclass-specific syntax**

       Formatting commands, configured spans, SVG document structure, and
       command replacements depend on the concrete subclass. This base class
       provides the general parsing and selection machinery rather than
       defining a single universal text syntax.

    6. **Submobject selection**

       String selection does not simply search the rendered geometry for
       visual characters. It maps string spans to labels and then maps those
       labels to submobject indices. The result therefore depends on the
       parsing, SVG conversion, and label-alignment stages.

    7. **Abstract methods**

       ``StringMobject`` is not intended to be used as a directly instantiated
       rendering class. A subclass must implement its abstract interface
       before it can be instantiated.

    8. **Geometry references**

       ``build_parts_from_indices_lists`` constructs groups from references
       to existing submobjects. Selecting or grouping parts should not
       automatically be assumed to create independent copies of the geometry.

    Raises
    ------
    TypeError
        Raised by ``find_spans_by_selector`` when a selector in a collection
        has an unsupported type or structure.
    IndexError
        May be raised when ``select_part`` is given an index outside the
        range of the groups returned by ``select_parts``.
    ValueError or other parsing exceptions
        May propagate from subclass-specific parsing, SVG generation, or
        the underlying SVG conversion implementation.
    """

    height = None

    def __init__(
        self,
        string: str,
        fill_color: ManimColor = DEFAULT_MOBJECT_COLOR,
        fill_border_width: float = 0.5,
        stroke_color: ManimColor = DEFAULT_MOBJECT_COLOR,
        stroke_width: float = 0,
        base_color: ManimColor = DEFAULT_MOBJECT_COLOR,
        isolate: Selector = (),
        protect: Selector = (),
        # When set to true, only the labelled svg is
        # rendered, and its contents are used directly
        # for the body of this String Mobject
        use_labelled_svg: bool = False,
        **kwargs
    ):
        self.string = string
        self.base_color = base_color or DEFAULT_MOBJECT_COLOR
        self.isolate = isolate
        self.protect = protect
        self.use_labelled_svg = use_labelled_svg

        self.parse()
        svg_string = self.get_svg_string()
        super().__init__(svg_string=svg_string, **kwargs)
        self.set_stroke(stroke_color, stroke_width)
        self.set_fill(fill_color, border_width=fill_border_width)
        self.labels = [submob.label for submob in self.submobjects]
        # Glyphs are placed by the typesetter, which does not lay one over another, so they
        # may share a draw. Take it back with draw_fills_together(False) for the rare string
        # whose glyphs do overlap and whose fill is partly transparent.
        self.draw_fills_together()

    def get_svg_string(self, is_labelled: bool = False) -> str:
        content = self.get_content(is_labelled or self.use_labelled_svg)
        return self.get_svg_string_by_content(content)

    @abstractmethod
    def get_svg_string_by_content(self, content: str) -> str:
        return ""

    def assign_labels_by_color(self, mobjects: list[VMobject]) -> None:
        """
        Assuming each mobject in the list `mobjects` has a fill color
        meant to represent a numerical label, this assigns those
        those numerical labels to each mobject as an attribute
        """
        labels_count = len(self.labelled_spans)
        if labels_count == 1:
            for mob in mobjects:
                mob.label = 0
            return

        unrecognizable_colors = []
        for mob in mobjects:
            label = hex_to_int(color_to_hex(mob.get_fill_color()))
            if label >= labels_count:
                unrecognizable_colors.append(label)
                label = 0
            mob.label = label

        if unrecognizable_colors:
            log.warning(
                "Unrecognizable color labels detected (%s). " + \
                "The result could be unexpected.",
                ", ".join(
                    int_to_hex(color)
                    for color in unrecognizable_colors
                )
            )

    def mobjects_from_svg_string(self, svg_string: str) -> list[VMobject]:
        submobs = super().mobjects_from_svg_string(svg_string)

        if self.use_labelled_svg:
            # This means submobjects are colored according to spans
            self.assign_labels_by_color(submobs)
            return submobs

        # Otherwise, submobs are not colored, so generate a new list
        # of submobject which are and use those for labels
        unlabelled_submobs = submobs
        labelled_content = self.get_content(is_labelled=True)
        labelled_file = self.get_svg_string_by_content(labelled_content)
        labelled_submobs = super().mobjects_from_svg_string(labelled_file)
        self.labelled_submobs = labelled_submobs
        self.unlabelled_submobs = unlabelled_submobs

        self.assign_labels_by_color(labelled_submobs)
        self.rearrange_submobjects_by_positions(labelled_submobs, unlabelled_submobs)
        for usm, lsm in zip(unlabelled_submobs, labelled_submobs):
            usm.label = lsm.label

        if len(unlabelled_submobs) != len(labelled_submobs):
            log.warning(
                "Cannot align submobjects of the labelled svg " + \
                "to the original svg. Skip the labelling process."
            )
            for usm in unlabelled_submobs:
                usm.label = 0
            return unlabelled_submobs

        return unlabelled_submobs

    def rearrange_submobjects_by_positions(
        self, labelled_submobs: list[VMobject], unlabelled_submobs: list[VMobject],
    ) -> None:
        """
        Rearrange `labeleled_submobjects` so that each submobject
        is labelled by the nearest one of `unlabelled_submobs`.
        The correctness cannot be ensured, since the svg may
        change significantly after inserting color commands.
        """
        if len(labelled_submobs) == 0:
            return

        labelled_svg = VGroup(*labelled_submobs)
        labelled_svg.replace(VGroup(*unlabelled_submobs))
        distance_matrix = cdist(
            [submob.get_center() for submob in unlabelled_submobs],
            [submob.get_center() for submob in labelled_submobs]
        )
        _, indices = linear_sum_assignment(distance_matrix)
        labelled_submobs[:] = [labelled_submobs[index] for index in indices]

    # Toolkits

    def find_spans_by_selector(self, selector: Selector) -> list[Span]:
        def find_spans_by_single_selector(sel):
            if isinstance(sel, str):
                return [
                    match_obj.span()
                    for match_obj in re.finditer(re.escape(sel), self.string)
                ]
            if isinstance(sel, re.Pattern):
                return [
                    match_obj.span()
                    for match_obj in sel.finditer(self.string)
                ]
            if isinstance(sel, tuple) and len(sel) == 2 and all(
                isinstance(index, int) or index is None
                for index in sel
            ):
                l = len(self.string)
                span = tuple(
                    default_index if index is None else
                    min(index, l) if index >= 0 else max(index + l, 0)
                    for index, default_index in zip(sel, (0, l))
                )
                return [span]
            return None

        result = find_spans_by_single_selector(selector)
        if result is None:
            result = []
            for sel in selector:
                spans = find_spans_by_single_selector(sel)
                if spans is None:
                    raise TypeError(f"Invalid selector: '{sel}'")
                result.extend(spans)
        return list(filter(lambda span: span[0] <= span[1], result))

    @staticmethod
    def span_contains(span_0: Span, span_1: Span) -> bool:
        return span_0[0] <= span_1[0] and span_0[1] >= span_1[1]

    # Parsing

    def parse(self) -> None:
        def get_substr(span: Span) -> str:
            return self.string[slice(*span)]

        configured_items = self.get_configured_items()
        isolated_spans = self.find_spans_by_selector(self.isolate)
        protected_spans = self.find_spans_by_selector(self.protect)
        command_matches = self.get_command_matches(self.string)

        def get_key(category, i, flag):
            def get_span_by_category(category, i):
                if category == 0:
                    return configured_items[i][0]
                if category == 1:
                    return isolated_spans[i]
                if category == 2:
                    return protected_spans[i]
                return command_matches[i].span()

            index, paired_index = get_span_by_category(category, i)[::flag]
            return (
                index,
                flag * (2 if index != paired_index else -1),
                -paired_index,
                flag * category,
                flag * i
            )

        index_items = sorted([
            (category, i, flag)
            for category, item_length in enumerate((
                len(configured_items),
                len(isolated_spans),
                len(protected_spans),
                len(command_matches)
            ))
            for i in range(item_length)
            for flag in (1, -1)
        ], key=lambda t: get_key(*t))

        inserted_items = []
        labelled_items = []
        overlapping_spans = []
        level_mismatched_spans = []

        label = 1
        protect_level = 0
        bracket_stack = [0]
        bracket_count = 0
        open_command_stack = []
        open_stack = []
        for category, i, flag in index_items:
            if category >= 2:
                protect_level += flag
                if flag == 1 or category == 2:
                    continue
                inserted_items.append((i, 0))
                command_match = command_matches[i]
                command_flag = self.get_command_flag(command_match)
                if command_flag == 1:
                    bracket_count += 1
                    bracket_stack.append(bracket_count)
                    open_command_stack.append((len(inserted_items), i))
                    continue
                if command_flag == 0:
                    continue
                pos, i_ = open_command_stack.pop()
                bracket_stack.pop()
                open_command_match = command_matches[i_]
                attr_dict = self.get_attr_dict_from_command_pair(
                    open_command_match, command_match
                )
                if attr_dict is None:
                    continue
                span = (open_command_match.end(), command_match.start())
                labelled_items.append((span, attr_dict))
                inserted_items.insert(pos, (label, 1))
                inserted_items.insert(-1, (label, -1))
                label += 1
                continue
            if flag == 1:
                open_stack.append((
                    len(inserted_items), category, i,
                    protect_level, bracket_stack.copy()
                ))
                continue
            span, attr_dict = configured_items[i] \
                if category == 0 else (isolated_spans[i], {})
            pos, category_, i_, protect_level_, bracket_stack_ \
                = open_stack.pop()
            if category_ != category or i_ != i:
                overlapping_spans.append(span)
                continue
            if protect_level_ or protect_level:
                continue
            if bracket_stack_ != bracket_stack:
                level_mismatched_spans.append(span)
                continue
            labelled_items.append((span, attr_dict))
            inserted_items.insert(pos, (label, 1))
            inserted_items.append((label, -1))
            label += 1
        labelled_items.insert(0, ((0, len(self.string)), {}))
        inserted_items.insert(0, (0, 1))
        inserted_items.append((0, -1))

        if overlapping_spans:
            log.warning(
                "Partly overlapping substrings detected: %s",
                ", ".join(
                    f"'{get_substr(span)}'"
                    for span in overlapping_spans
                )
            )
        if level_mismatched_spans:
            log.warning(
                "Cannot handle substrings: %s",
                ", ".join(
                    f"'{get_substr(span)}'"
                    for span in level_mismatched_spans
                )
            )

        def reconstruct_string(
            start_item: tuple[int, int],
            end_item: tuple[int, int],
            command_replace_func: Callable[[re.Match], str],
            command_insert_func: Callable[[int, int, dict[str, str]], str]
        ) -> str:
            def get_edge_item(i: int, flag: int) -> tuple[Span, str]:
                if flag == 0:
                    match_obj = command_matches[i]
                    return (
                        match_obj.span(),
                        command_replace_func(match_obj)
                    )
                span, attr_dict = labelled_items[i]
                index = span[flag < 0]
                return (
                    (index, index),
                    command_insert_func(i, flag, attr_dict)
                )

            items = [
                get_edge_item(i, flag)
                for i, flag in inserted_items[slice(
                    inserted_items.index(start_item),
                    inserted_items.index(end_item) + 1
                )]
            ]
            pieces = [
                get_substr((start, end))
                for start, end in zip(
                    [interval_end for (_, interval_end), _ in items[:-1]],
                    [interval_start for (interval_start, _), _ in items[1:]]
                )
            ]
            interval_pieces = [piece for _, piece in items[1:-1]]
            return "".join(it.chain(*zip(pieces, (*interval_pieces, ""))))

        self.labelled_spans = [span for span, _ in labelled_items]
        self.reconstruct_string = reconstruct_string

    def get_content(self, is_labelled: bool) -> str:
        content = self.reconstruct_string(
            (0, 1), (0, -1),
            self.replace_for_content,
            lambda label, flag, attr_dict: self.get_command_string(
                attr_dict,
                is_end=flag < 0,
                label_hex=int_to_hex(label) if is_labelled else None
            )
        )
        prefix, suffix = self.get_content_prefix_and_suffix(
            is_labelled=is_labelled
        )
        return "".join((prefix, content, suffix))

    @staticmethod
    @abstractmethod
    def get_command_matches(string: str) -> list[re.Match]:
        return []

    @staticmethod
    @abstractmethod
    def get_command_flag(match_obj: re.Match) -> int:
        return 0

    @staticmethod
    @abstractmethod
    def replace_for_content(match_obj: re.Match) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def replace_for_matching(match_obj: re.Match) -> str:
        return ""

    @staticmethod
    @abstractmethod
    def get_attr_dict_from_command_pair(
        open_command: re.Match, close_command: re.Match,
    ) -> dict[str, str] | None:
        return None

    @abstractmethod
    def get_configured_items(self) -> list[tuple[Span, dict[str, str]]]:
        return []

    @staticmethod
    @abstractmethod
    def get_command_string(
        attr_dict: dict[str, str], is_end: bool, label_hex: str | None
    ) -> str:
        return ""

    @abstractmethod
    def get_content_prefix_and_suffix(
        self, is_labelled: bool
    ) -> tuple[str, str]:
        return "", ""

    # Selector

    def get_submob_indices_list_by_span(
        self, arbitrary_span: Span
    ) -> list[int]:
        return [
            submob_index
            for submob_index, label in enumerate(self.labels)
            if self.span_contains(arbitrary_span, self.labelled_spans[label])
        ]

    def get_specified_part_items(self) -> list[tuple[str, list[int]]]:
        return [
            (
                self.string[slice(*span)],
                self.get_submob_indices_list_by_span(span)
            )
            for span in self.labelled_spans[1:]
        ]

    def get_specified_substrings(self) -> list[str]:
        substrs = [
            self.string[slice(*span)]
            for span in self.labelled_spans[1:]
        ]
        # Use dict.fromkeys to remove duplicates while retaining order
        return list(dict.fromkeys(substrs).keys())

    def get_group_part_items(self) -> list[tuple[str, list[int]]]:
        if not self.labels:
            return []

        def get_neighbouring_pairs(vals):
            return list(zip(vals[:-1], vals[1:]))

        range_lens, group_labels = zip(*(
            (len(list(grouper)), val)
            for val, grouper in it.groupby(self.labels)
        ))
        submob_indices_lists = [
            list(range(*submob_range))
            for submob_range in get_neighbouring_pairs(
                [0, *it.accumulate(range_lens)]
            )
        ]
        labelled_spans = self.labelled_spans
        start_items = [
            (group_labels[0], 1),
            *(
                (curr_label, 1)
                if self.span_contains(
                    labelled_spans[prev_label], labelled_spans[curr_label]
                )
                else (prev_label, -1)
                for prev_label, curr_label in get_neighbouring_pairs(
                    group_labels
                )
            )
        ]
        end_items = [
            *(
                (curr_label, -1)
                if self.span_contains(
                    labelled_spans[next_label], labelled_spans[curr_label]
                )
                else (next_label, 1)
                for curr_label, next_label in get_neighbouring_pairs(
                    group_labels
                )
            ),
            (group_labels[-1], -1)
        ]
        group_substrs = [
            re.sub(r"\s+", "", self.reconstruct_string(
                start_item, end_item,
                self.replace_for_matching,
                lambda label, flag, attr_dict: ""
            ))
            for start_item, end_item in zip(start_items, end_items)
        ]
        return list(zip(group_substrs, submob_indices_lists))

    def get_submob_indices_lists_by_selector(
        self, selector: Selector
    ) -> list[list[int]]:
        return list(filter(
            lambda indices_list: indices_list,
            [
                self.get_submob_indices_list_by_span(span)
                for span in self.find_spans_by_selector(selector)
            ]
        ))

    def build_parts_from_indices_lists(
        self, indices_lists: list[list[int]]
    ) -> VGroup:
        return VGroup(*(
            VGroup(*(
                self.submobjects[submob_index]
                for submob_index in indices_list
            ))
            for indices_list in indices_lists
        ))

    def build_groups(self) -> VGroup:
        return self.build_parts_from_indices_lists([
            indices_list
            for _, indices_list in self.get_group_part_items()
        ])

    def select_parts(self, selector: Selector) -> VGroup:
        specified_substrings = self.get_specified_substrings()
        if isinstance(selector, (str, re.Pattern)) and selector not in specified_substrings:
            return self.select_unisolated_substring(selector)
        indices_list = self.get_submob_indices_lists_by_selector(selector)
        return self.build_parts_from_indices_lists(indices_list)

    def __getitem__(self, value: int | slice | Selector) -> VMobject:
        if isinstance(value, (int, slice)):
            return super().__getitem__(value)
        return self.select_parts(value)

    def select_part(self, selector: Selector, index: int = 0) -> VMobject:
        return self.select_parts(selector)[index]

    def substr_to_path_count(self, substr: str) -> int:
        return len(re.sub(r"\s", "", substr))

    def get_symbol_substrings(self):
        return list(re.sub(r"\s", "", self.string))

    def select_unisolated_substring(self, pattern: str | re.Pattern) -> VGroup:
        if isinstance(pattern, str):
            pattern = re.compile(re.escape(pattern))
        result = []
        for match in re.finditer(pattern, self.string):
            index = match.start()
            start = self.substr_to_path_count(self.string[:index])
            substr = match.group()
            end = start + self.substr_to_path_count(substr)
            result.append(self[start:end])
        return VGroup(*result)

    def set_parts_color(self, selector: Selector, color: ManimColor):
        self.select_parts(selector).set_color(color)
        return self

    def set_parts_color_by_dict(self, color_map: dict[Selector, ManimColor]):
        for selector, color in color_map.items():
            self.set_parts_color(selector, color)
        return self

    def get_string(self) -> str:
        return self.string
