# -*- coding: utf-8 -*-
"""A library of LaTeX templates."""
__all__ = [
    "TexTemplateLibrary",
    "TexFontTemplates",
]

from .tex import *


# This file makes TexTemplateLibrary and TexFontTemplates available for use in manim Tex and MathTex objects.


def _new_ams_template():
    """ Returns a simple Tex Template with only basic AMS packages """
    preamble = r"""
\usepackage[english]{babel}
\usepackage{amsmath}
\usepackage{amssymb}
"""
    return TexTemplate(preamble=preamble)


# TexTemplateLibrary
#
class TexTemplateLibrary(object):
    """
    A collection of basic TeX template objects

    Examples
    --------
    Normal usage as a value for the keyword argument tex_template of Tex() and MathTex() mobjects::

        ``Tex("My TeX code", tex_template=TexTemplateLibrary.ctex)``

    """

    default = TexTemplate()
    """An instance of the default TeX template in manim"""

    threeb1b = TexTemplate()
    """ An instance of the default TeX template used by 3b1b """

    ctex = TexTemplate(
        tex_compiler="xelatex",
        output_format=".xdv",
        preamble=TexTemplate.default_preamble.replace(
            r"\DisableLigatures{encoding = *, family = * }", r"\usepackage[UTF8]{ctex}"
        ),
    )
    """An instance of the TeX template used by 3b1b when using the use_ctex flag"""

    simple = _new_ams_template()
    """An instance of a simple TeX template with only basic AMS packages loaded"""


# TexFontTemplates
#
# TexFontTemplates takes a font_id and returns the appropriate TexTemplate()
# Usage:
#       my_tex_template = TexFontTemplates.font_id
#
# Note: not all of these will work out-of-the-box.
# They may require specific fonts to be installed on the local system.
# For example TexFontTemplates.comic_sans will only work if the Microsoft font 'Comic Sans'
# is installed on the local system.
#
# More information on these templates, along with example output can be found at
# http://jf.burnol.free.fr/showcase.html"
#
#
# Choices for font_id are:
#
# american_typewriter       : "American Typewriter"
# antykwa                   : "Antykwa Półtawskiego (TX Fonts for Greek and math symbols)"
# apple_chancery            : "Apple Chancery"
# auriocus_kalligraphicus   : "Auriocus Kalligraphicus (Symbol Greek)"
# baskervald_adf_fourier    : "Baskervald ADF with Fourier"
# baskerville_it            : "Baskerville (Italic)"
# biolinum                  : "Biolinum"
# brushscriptx              : "BrushScriptX-Italic (PX math and Greek)"
# chalkboard_se             : "Chalkboard SE"
# chalkduster               : "Chalkduster"
# comfortaa                 : "Comfortaa"
# comic_sans                : "Comic Sans MS"
# droid_sans                : "Droid Sans"
# droid_sans_it             : "Droid Sans (Italic)"
# droid_serif               : "Droid Serif"
# droid_serif_px_it         : "Droid Serif (PX math symbols) (Italic)"
# ecf_augie                 : "ECF Augie (Euler Greek)"
# ecf_jd                    : "ECF JD (with TX fonts)"
# ecf_skeetch               : "ECF Skeetch (CM Greek)"
# ecf_tall_paul             : "ECF Tall Paul (with Symbol font)"
# ecf_webster               : "ECF Webster (with TX fonts)"
# electrum_adf              : "Electrum ADF (CM Greek)"
# epigrafica                : Epigrafica
# fourier_utopia            : "Fourier Utopia (Fourier upright Greek)"
# french_cursive            : "French Cursive (Euler Greek)"
# gfs_bodoni                : "GFS Bodoni"
# gfs_didot                 : "GFS Didot (Italic)"
# gfs_neoHellenic           : "GFS NeoHellenic"
# gnu_freesans_tx           : "GNU FreeSerif (and TX fonts symbols)"
# gnu_freeserif_freesans    : "GNU FreeSerif and FreeSans"
# helvetica_fourier_it      : "Helvetica with Fourier (Italic)"
# latin_modern_tw_it        : "Latin Modern Typewriter Proportional (CM Greek) (Italic)"
# latin_modern_tw           : "Latin Modern Typewriter Proportional"
# libertine                 : "Libertine"
# libris_adf_fourier        : "Libris ADF with Fourier"
# minion_pro_myriad_pro     : "Minion Pro and Myriad Pro (and TX fonts symbols)"
# minion_pro_tx             : "Minion Pro (and TX fonts symbols)"
# new_century_schoolbook    : "New Century Schoolbook (Symbol Greek)"
# new_century_schoolbook_px : "New Century Schoolbook (Symbol Greek, PX math symbols)"
# noteworthy_light          : "Noteworthy Light"
# palatino                  : "Palatino (Symbol Greek)"
# papyrus                   : "Papyrus"
# romande_adf_fourier_it    : "Romande ADF with Fourier (Italic)"
# slitex                    : "SliTeX (Euler Greek)"
# times_fourier_it          : "Times with Fourier (Italic)"
# urw_avant_garde           : "URW Avant Garde (Symbol Greek)"
# urw_zapf_chancery         : "URW Zapf Chancery (CM Greek)"
# venturis_adf_fourier_it   : "Venturis ADF with Fourier (Italic)"
# verdana_it                : "Verdana (Italic)"
# vollkorn_fourier_it       : "Vollkorn with Fourier (Italic)"
# vollkorn                  : "Vollkorn (TX fonts for Greek and math symbols)"
# zapf_chancery             : "Zapf Chancery"
# -----------------------------------------------------------------------------------------
#
#
#
#
#
#
#
#
#
#

# Latin Modern Typewriter Proportional
lmtp = _new_ams_template()
lmtp.description = "Latin Modern Typewriter Proportional"
lmtp.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage[variablett]{lmodern}
\renewcommand{\rmdefault}{\ttdefault}
\usepackage[LGRgreek]{mathastext}
\MTgreekfont{lmtt} % no lgr lmvtt, so use lgr lmtt
\Mathastext
\let\varepsilon\epsilon % only \varsigma in LGR
"""
)


# Fourier Utopia (Fourier upright Greek)
fufug = _new_ams_template()
fufug.description = "Fourier Utopia (Fourier upright Greek)"
fufug.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage[upright]{fourier}
\usepackage{mathastext}
"""
)


# Droid Serif
droidserif = _new_ams_template()
droidserif.description = "Droid Serif"
droidserif.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage[default]{droidserif}
\usepackage[LGRgreek]{mathastext}
\let\varepsilon\epsilon
"""
)


# Droid Sans
droidsans = _new_ams_template()
droidsans.description = "Droid Sans"
droidsans.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage[default]{droidsans}
\usepackage[LGRgreek]{mathastext}
\let\varepsilon\epsilon
"""
)


# New Century Schoolbook (Symbol Greek)
ncssg = _new_ams_template()
ncssg.description = "New Century Schoolbook (Symbol Greek)"
ncssg.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{newcent}
\usepackage[symbolgreek]{mathastext}
\linespread{1.1}
"""
)


# French Cursive (Euler Greek)
fceg = _new_ams_template()
fceg.description = "French Cursive (Euler Greek)"
fceg.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage[default]{frcursive}
\usepackage[eulergreek,noplusnominus,noequal,nohbar,%
nolessnomore,noasterisk]{mathastext}
"""
)


# Auriocus Kalligraphicus (Symbol Greek)
aksg = _new_ams_template()
aksg.description = "Auriocus Kalligraphicus (Symbol Greek)"
aksg.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{aurical}
\renewcommand{\rmdefault}{AuriocusKalligraphicus}
\usepackage[symbolgreek]{mathastext}
"""
)


# Palatino (Symbol Greek)
palatinosg = _new_ams_template()
palatinosg.description = "Palatino (Symbol Greek)"
palatinosg.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{palatino}
\usepackage[symbolmax,defaultmathsizes]{mathastext}
"""
)


# Comfortaa
comfortaa = _new_ams_template()
comfortaa.description = "Comfortaa"
comfortaa.add_to_preamble(
    r"""
\usepackage[default]{comfortaa}
\usepackage[LGRgreek,defaultmathsizes,noasterisk]{mathastext}
\let\varphi\phi
\linespread{1.06}
"""
)


# ECF Augie (Euler Greek)
ecfaugieeg = _new_ams_template()
ecfaugieeg.description = "ECF Augie (Euler Greek)"
ecfaugieeg.add_to_preamble(
    r"""
\renewcommand\familydefault{fau} % emerald package
\usepackage[defaultmathsizes,eulergreek]{mathastext}
"""
)


# Electrum ADF (CM Greek)
electrumadfcm = _new_ams_template()
electrumadfcm.description = "Electrum ADF (CM Greek)"
electrumadfcm.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage[LGRgreek,basic,defaultmathsizes]{mathastext}
\usepackage[lf]{electrum}
\Mathastext
\let\varphi\phi
"""
)


# American Typewriter
americantypewriter = _new_ams_template()
americantypewriter.description = "American Typewriter"
americantypewriter.add_to_preamble(
    r"""
\usepackage[no-math]{fontspec}
\setmainfont[Mapping=tex-text]{American Typewriter}
\usepackage[defaultmathsizes]{mathastext}
"""
)
americantypewriter.tex_compiler = "xelatex"
americantypewriter.output_format = ".xdv"

# Minion Pro and Myriad Pro (and TX fonts symbols)
mpmptx = _new_ams_template()
mpmptx.description = "Minion Pro and Myriad Pro (and TX fonts symbols)"
mpmptx.add_to_preamble(
    r"""
\usepackage{txfonts}
\usepackage[upright]{txgreeks}
\usepackage[no-math]{fontspec}
\setmainfont[Mapping=tex-text]{Minion Pro}
\setsansfont[Mapping=tex-text,Scale=MatchUppercase]{Myriad Pro}
\renewcommand\familydefault\sfdefault
\usepackage[defaultmathsizes]{mathastext}
\renewcommand\familydefault\rmdefault
"""
)
mpmptx.tex_compiler = "xelatex"
mpmptx.output_format = ".xdv"


# New Century Schoolbook (Symbol Greek, PX math symbols)
ncssgpxm = _new_ams_template()
ncssgpxm.description = "New Century Schoolbook (Symbol Greek, PX math symbols)"
ncssgpxm.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{pxfonts}
\usepackage{newcent}
\usepackage[symbolgreek,defaultmathsizes]{mathastext}
\linespread{1.06}
"""
)


# Vollkorn (TX fonts for Greek and math symbols)
vollkorntx = _new_ams_template()
vollkorntx.description = "Vollkorn (TX fonts for Greek and math symbols)"
vollkorntx.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{txfonts}
\usepackage[upright]{txgreeks}
\usepackage{vollkorn}
\usepackage[defaultmathsizes]{mathastext}
"""
)


# Libertine
libertine = _new_ams_template()
libertine.description = "Libertine"
libertine.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{libertine}
\usepackage[greek=n]{libgreek}
\usepackage[noasterisk,defaultmathsizes]{mathastext}
"""
)


# SliTeX (Euler Greek)
slitexeg = _new_ams_template()
slitexeg.description = "SliTeX (Euler Greek)"
slitexeg.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{tpslifonts}
\usepackage[eulergreek,defaultmathsizes]{mathastext}
\MTEulerScale{1.06}
\linespread{1.2}
"""
)


# ECF Webster (with TX fonts)
ecfwebstertx = _new_ams_template()
ecfwebstertx.description = "ECF Webster (with TX fonts)"
ecfwebstertx.add_to_preamble(
    r"""
\usepackage{txfonts}
\usepackage[upright]{txgreeks}
\renewcommand\familydefault{fwb} % emerald package
\usepackage{mathastext}
\renewcommand{\int}{\intop\limits}
\linespread{1.5}
"""
)
ecfwebstertx.add_to_document(
    r"""
\mathversion{bold}
"""
)


# Romande ADF with Fourier (Italic)
italicromandeadff = _new_ams_template()
italicromandeadff.description = "Romande ADF with Fourier (Italic)"
italicromandeadff.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{fourier}
\usepackage{romande}
\usepackage[italic,defaultmathsizes,noasterisk]{mathastext}
\renewcommand{\itshape}{\swashstyle}
"""
)


# Apple Chancery
applechancery = _new_ams_template()
applechancery.description = "Apple Chancery"
applechancery.add_to_preamble(
    r"""
\usepackage[no-math]{fontspec}
\setmainfont[Mapping=tex-text]{Apple Chancery}
\usepackage[defaultmathsizes]{mathastext}
"""
)
applechancery.tex_compiler = "xelatex"
applechancery.output_format = ".xdv"


# Zapf Chancery
zapfchancery = _new_ams_template()
zapfchancery.description = "Zapf Chancery"
zapfchancery.add_to_preamble(
    r"""
\DeclareFontFamily{T1}{pzc}{}
\DeclareFontShape{T1}{pzc}{mb}{it}{<->s*[1.2] pzcmi8t}{}
\DeclareFontShape{T1}{pzc}{m}{it}{<->ssub * pzc/mb/it}{}
\usepackage{chancery} % = \renewcommand{\rmdefault}{pzc}
\renewcommand\shapedefault\itdefault
\renewcommand\bfdefault\mddefault
\usepackage[defaultmathsizes]{mathastext}
\linespread{1.05}
"""
)


# Verdana (Italic)
italicverdana = _new_ams_template()
italicverdana.description = "Verdana (Italic)"
italicverdana.add_to_preamble(
    r"""
\usepackage[no-math]{fontspec}
\setmainfont[Mapping=tex-text]{Verdana}
\usepackage[defaultmathsizes,italic]{mathastext}
"""
)
italicverdana.tex_compiler = "xelatex"
italicverdana.output_format = ".xdv"


# URW Zapf Chancery (CM Greek)
urwzccmg = _new_ams_template()
urwzccmg.description = "URW Zapf Chancery (CM Greek)"
urwzccmg.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\DeclareFontFamily{T1}{pzc}{}
\DeclareFontShape{T1}{pzc}{mb}{it}{<->s*[1.2] pzcmi8t}{}
\DeclareFontShape{T1}{pzc}{m}{it}{<->ssub * pzc/mb/it}{}
\DeclareFontShape{T1}{pzc}{mb}{sl}{<->ssub * pzc/mb/it}{}
\DeclareFontShape{T1}{pzc}{m}{sl}{<->ssub * pzc/mb/sl}{}
\DeclareFontShape{T1}{pzc}{m}{n}{<->ssub * pzc/mb/it}{}
\usepackage{chancery}
\usepackage{mathastext}
\linespread{1.05}"""
)
urwzccmg.add_to_document(
    r"""
\boldmath
"""
)


# Comic Sans MS
comicsansms = _new_ams_template()
comicsansms.description = "Comic Sans MS"
comicsansms.add_to_preamble(
    r"""
\usepackage[no-math]{fontspec}
\setmainfont[Mapping=tex-text]{Comic Sans MS}
\usepackage[defaultmathsizes]{mathastext}
"""
)
comicsansms.tex_compiler = "xelatex"
comicsansms.output_format = ".xdv"


# GFS Didot (Italic)
italicgfsdidot = _new_ams_template()
italicgfsdidot.description = "GFS Didot (Italic)"
italicgfsdidot.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\renewcommand\rmdefault{udidot}
\usepackage[LGRgreek,defaultmathsizes,italic]{mathastext}
\let\varphi\phi
"""
)


# Chalkduster
chalkduster = _new_ams_template()
chalkduster.description = "Chalkduster"
chalkduster.add_to_preamble(
    r"""
\usepackage[no-math]{fontspec}
\setmainfont[Mapping=tex-text]{Chalkduster}
\usepackage[defaultmathsizes]{mathastext}
"""
)
chalkduster.tex_compiler = "lualatex"
chalkduster.output_format = ".pdf"


# Minion Pro (and TX fonts symbols)
mptx = _new_ams_template()
mptx.description = "Minion Pro (and TX fonts symbols)"
mptx.add_to_preamble(
    r"""
\usepackage{txfonts}
\usepackage[no-math]{fontspec}
\setmainfont[Mapping=tex-text]{Minion Pro}
\usepackage[defaultmathsizes]{mathastext}
"""
)
mptx.tex_compiler = "xelatex"
mptx.output_format = ".xdv"


# GNU FreeSerif and FreeSans
gnufsfs = _new_ams_template()
gnufsfs.description = "GNU FreeSerif and FreeSans"
gnufsfs.add_to_preamble(
    r"""
\usepackage[no-math]{fontspec}
\setmainfont[ExternalLocation,
                Mapping=tex-text,
                BoldFont=FreeSerifBold,
                ItalicFont=FreeSerifItalic,
                BoldItalicFont=FreeSerifBoldItalic]{FreeSerif}
\setsansfont[ExternalLocation,
                Mapping=tex-text,
                BoldFont=FreeSansBold,
                ItalicFont=FreeSansOblique,
                BoldItalicFont=FreeSansBoldOblique,
                Scale=MatchLowercase]{FreeSans}
\renewcommand{\familydefault}{lmss}
\usepackage[LGRgreek,defaultmathsizes,noasterisk]{mathastext}
\renewcommand{\familydefault}{\sfdefault}
\Mathastext
\let\varphi\phi % no `var' phi in LGR encoding
\renewcommand{\familydefault}{\rmdefault}
"""
)
gnufsfs.tex_compiler = "xelatex"
gnufsfs.output_format = ".xdv"

# GFS NeoHellenic
gfsneohellenic = _new_ams_template()
gfsneohellenic.description = "GFS NeoHellenic"
gfsneohellenic.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\renewcommand{\rmdefault}{neohellenic}
\usepackage[LGRgreek]{mathastext}
\let\varphi\phi
\linespread{1.06}
"""
)


# ECF Tall Paul (with Symbol font)
ecftallpaul = _new_ams_template()
ecftallpaul.description = "ECF Tall Paul (with Symbol font)"
ecftallpaul.add_to_preamble(
    r"""
\DeclareFontFamily{T1}{ftp}{}
\DeclareFontShape{T1}{ftp}{m}{n}{
    <->s*[1.4] ftpmw8t
}{} % increase size by factor 1.4
\renewcommand\familydefault{ftp} % emerald package
\usepackage[symbol]{mathastext}
\let\infty\inftypsy
"""
)


# Droid Sans (Italic)
italicdroidsans = _new_ams_template()
italicdroidsans.description = "Droid Sans (Italic)"
italicdroidsans.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage[default]{droidsans}
\usepackage[LGRgreek,defaultmathsizes,italic]{mathastext}
\let\varphi\phi
"""
)


# Baskerville (Italic)
italicbaskerville = _new_ams_template()
italicbaskerville.description = "Baskerville (Italic)"
italicbaskerville.add_to_preamble(
    r"""
\usepackage[no-math]{fontspec}
\setmainfont[Mapping=tex-text]{Baskerville}
\usepackage[defaultmathsizes,italic]{mathastext}
"""
)
italicbaskerville.tex_compiler = "xelatex"
italicbaskerville.output_format = ".xdv"


# ECF JD (with TX fonts)
ecfjdtx = _new_ams_template()
ecfjdtx.description = "ECF JD (with TX fonts)"
ecfjdtx.add_to_preamble(
    r"""
\usepackage{txfonts}
\usepackage[upright]{txgreeks}
\renewcommand\familydefault{fjd} % emerald package
\usepackage{mathastext}
"""
)
ecfjdtx.add_to_document(
    r"""\mathversion{bold}
"""
)


# Antykwa Półtawskiego (TX Fonts for Greek and math symbols)
aptxgm = _new_ams_template()
aptxgm.description = "Antykwa Półtawskiego (TX Fonts for Greek and math symbols)"
aptxgm.add_to_preamble(
    r"""
\usepackage[OT4,OT1]{fontenc}
\usepackage{txfonts}
\usepackage[upright]{txgreeks}
\usepackage{antpolt}
\usepackage[defaultmathsizes,nolessnomore]{mathastext}
"""
)


# Papyrus
papyrus = _new_ams_template()
papyrus.description = "Papyrus"
papyrus.add_to_preamble(
    r"""
\usepackage[no-math]{fontspec}
\setmainfont[Mapping=tex-text]{Papyrus}
\usepackage[defaultmathsizes]{mathastext}
"""
)
papyrus.tex_compiler = "xelatex"
papyrus.output_format = ".xdv"


# GNU FreeSerif (and TX fonts symbols)
gnufstx = _new_ams_template()
gnufstx.description = "GNU FreeSerif (and TX fonts symbols)"
gnufstx.add_to_preamble(
    r"""
\usepackage[no-math]{fontspec}
\usepackage{txfonts}  %\let\mathbb=\varmathbb
\setmainfont[ExternalLocation,
                Mapping=tex-text,
                BoldFont=FreeSerifBold,
                ItalicFont=FreeSerifItalic,
                BoldItalicFont=FreeSerifBoldItalic]{FreeSerif}
\usepackage[defaultmathsizes]{mathastext}
"""
)
gnufstx.tex_compiler = "xelatex"
gnufstx.output_format = ".pdf"


# ECF Skeetch (CM Greek)
ecfscmg = _new_ams_template()
ecfscmg.description = "ECF Skeetch (CM Greek)"
ecfscmg.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage[T1]{fontenc}
\DeclareFontFamily{T1}{fsk}{}
\DeclareFontShape{T1}{fsk}{m}{n}{<->s*[1.315] fskmw8t}{}
\renewcommand\rmdefault{fsk}
\usepackage[noendash,defaultmathsizes,nohbar,defaultimath]{mathastext}
"""
)


# Latin Modern Typewriter Proportional (CM Greek) (Italic)
italiclmtpcm = _new_ams_template()
italiclmtpcm.description = "Latin Modern Typewriter Proportional (CM Greek) (Italic)"
italiclmtpcm.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage[variablett,nomath]{lmodern}
\renewcommand{\familydefault}{\ttdefault}
\usepackage[frenchmath]{mathastext}
\linespread{1.08}
"""
)


# Baskervald ADF with Fourier
baskervaldadff = _new_ams_template()
baskervaldadff.description = "Baskervald ADF with Fourier"
baskervaldadff.add_to_preamble(
    r"""
\usepackage[upright]{fourier}
\usepackage{baskervald}
\usepackage[defaultmathsizes,noasterisk]{mathastext}
"""
)


# Droid Serif (PX math symbols) (Italic)
italicdroidserifpx = _new_ams_template()
italicdroidserifpx.description = "Droid Serif (PX math symbols) (Italic)"
italicdroidserifpx.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{pxfonts}
\usepackage[default]{droidserif}
\usepackage[LGRgreek,defaultmathsizes,italic,basic]{mathastext}
\let\varphi\phi
"""
)


# Biolinum
biolinum = _new_ams_template()
biolinum.description = "Biolinum"
biolinum.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{libertine}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[greek=n,biolinum]{libgreek}
\usepackage[noasterisk,defaultmathsizes]{mathastext}
"""
)


# Vollkorn with Fourier (Italic)
italicvollkornf = _new_ams_template()
italicvollkornf.description = "Vollkorn with Fourier (Italic)"
italicvollkornf.add_to_preamble(
    r"""
\usepackage{fourier}
\usepackage{vollkorn}
\usepackage[italic,nohbar]{mathastext}
"""
)


# Chalkboard SE
chalkboardse = _new_ams_template()
chalkboardse.description = "Chalkboard SE"
chalkboardse.add_to_preamble(
    r"""
\usepackage[no-math]{fontspec}
\setmainfont[Mapping=tex-text]{Chalkboard SE}
\usepackage[defaultmathsizes]{mathastext}
"""
)
chalkboardse.tex_compiler = "xelatex"
chalkboardse.output_format = ".xdv"


# Noteworthy Light
noteworthylight = _new_ams_template()
noteworthylight.description = "Noteworthy Light"
noteworthylight.add_to_preamble(
    r"""
\usepackage[no-math]{fontspec}
\setmainfont[Mapping=tex-text]{Noteworthy Light}
\usepackage[defaultmathsizes]{mathastext}
"""
)


# Epigrafica
epigrafica = _new_ams_template()
epigrafica.description = "Epigrafica"
epigrafica.add_to_preamble(
    r"""
\usepackage[LGR,OT1]{fontenc}
\usepackage{epigrafica}
\usepackage[basic,LGRgreek,defaultmathsizes]{mathastext}
\let\varphi\phi
\linespread{1.2}
"""
)


# Libris ADF with Fourier
librisadff = _new_ams_template()
librisadff.description = "Libris ADF with Fourier"
librisadff.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage[upright]{fourier}
\usepackage{libris}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[noasterisk]{mathastext}
"""
)


# Venturis ADF with Fourier (Italic)
italicvanturisadff = _new_ams_template()
italicvanturisadff.description = "Venturis ADF with Fourier (Italic)"
italicvanturisadff.add_to_preamble(
    r"""
\usepackage{fourier}
\usepackage[lf]{venturis}
\usepackage[italic,defaultmathsizes,noasterisk]{mathastext}
"""
)


# GFS Bodoni
gfsbodoni = _new_ams_template()
gfsbodoni.description = "GFS Bodoni"
gfsbodoni.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\renewcommand{\rmdefault}{bodoni}
\usepackage[LGRgreek]{mathastext}
\let\varphi\phi
\linespread{1.06}
"""
)


# BrushScriptX-Italic (PX math and Greek)
brushscriptxpx = _new_ams_template()
brushscriptxpx.description = "BrushScriptX-Italic (PX math and Greek)"
brushscriptxpx.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{pxfonts}
%\usepackage{pbsi}
\renewcommand{\rmdefault}{pbsi}
\renewcommand{\mddefault}{xl}
\renewcommand{\bfdefault}{xl}
\usepackage[defaultmathsizes,noasterisk]{mathastext}
"""
)
brushscriptxpx.add_to_document(
    r"""\boldmath
"""
)
brushscriptxpx.tex_compiler = "xelatex"
brushscriptxpx.output_format = ".xdv"


# URW Avant Garde (Symbol Greek)
urwagsg = _new_ams_template()
urwagsg.description = "URW Avant Garde (Symbol Greek)"
urwagsg.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage{avant}
\renewcommand{\familydefault}{\sfdefault}
\usepackage[symbolgreek,defaultmathsizes]{mathastext}
"""
)


# Times with Fourier (Italic)
italictimesf = _new_ams_template()
italictimesf.description = "Times with Fourier (Italic)"
italictimesf.add_to_preamble(
    r"""
\usepackage{fourier}
\renewcommand{\rmdefault}{ptm}
\usepackage[italic,defaultmathsizes,noasterisk]{mathastext}
"""
)


# Helvetica with Fourier (Italic)
italichelveticaf = _new_ams_template()
italichelveticaf.description = "Helvetica with Fourier (Italic)"
italichelveticaf.add_to_preamble(
    r"""
\usepackage[T1]{fontenc}
\usepackage[scaled]{helvet}
\usepackage{fourier}
\renewcommand{\rmdefault}{phv}
\usepackage[italic,defaultmathsizes,noasterisk]{mathastext}
"""
)


class TexFontTemplates(object):
    """
    A collection of TeX templates for the fonts described at http://jf.burnol.free.fr/showcase.html

    These templates are specifically designed to allow you to typeset formulae and mathematics using
    different fonts. They are based on the mathastext LaTeX package.

    Examples
    ---------
    Normal usage as a value for the keyword argument tex_template of Tex() and MathTex() mobjects::

        ``Tex("My TeX code", tex_template=TexFontTemplates.comic_sans)``

    Notes
    ------
    Many of these templates require that specific fonts
    are installed on your local machine.
    For example, choosing the template TexFontTemplates.comic_sans will
    not compile if the Comic Sans Microsoft font is not installed.

    To experiment, try to render the TexFontTemplateLibrary example scene:
         ``manim path/to/manim/example_scenes/advanced_tex_fonts.py TexFontTemplateLibrary -p -ql``
    """

    american_typewriter = americantypewriter
    """American Typewriter"""
    antykwa = aptxgm
    """Antykwa Półtawskiego (TX Fonts for Greek and math symbols)"""
    apple_chancery = applechancery
    """Apple Chancery"""
    auriocus_kalligraphicus = aksg
    """Auriocus Kalligraphicus (Symbol Greek)"""
    baskervald_adf_fourier = baskervaldadff
    """Baskervald ADF with Fourier"""
    baskerville_it = italicbaskerville
    """Baskerville (Italic)"""
    biolinum = biolinum
    """Biolinum"""
    brushscriptx = brushscriptxpx
    """BrushScriptX-Italic (PX math and Greek)"""
    chalkboard_se = chalkboardse
    """Chalkboard SE"""
    chalkduster = chalkduster
    """Chalkduster"""
    comfortaa = comfortaa
    """Comfortaa"""
    comic_sans = comicsansms
    """Comic Sans MS"""
    droid_sans = droidsans
    """Droid Sans"""
    droid_sans_it = italicdroidsans
    """Droid Sans (Italic)"""
    droid_serif = droidserif
    """Droid Serif"""
    droid_serif_px_it = italicdroidserifpx
    """Droid Serif (PX math symbols) (Italic)"""
    ecf_augie = ecfaugieeg
    """ECF Augie (Euler Greek)"""
    ecf_jd = ecfjdtx
    """ECF JD (with TX fonts)"""
    ecf_skeetch = ecfscmg
    """ECF Skeetch (CM Greek)"""
    ecf_tall_paul = ecftallpaul
    """ECF Tall Paul (with Symbol font)"""
    ecf_webster = ecfwebstertx
    """ECF Webster (with TX fonts)"""
    electrum_adf = electrumadfcm
    """Electrum ADF (CM Greek)"""
    epigrafica = epigrafica
    """ Epigrafica """
    fourier_utopia = fufug
    """Fourier Utopia (Fourier upright Greek)"""
    french_cursive = fceg
    """French Cursive (Euler Greek)"""
    gfs_bodoni = gfsbodoni
    """GFS Bodoni"""
    gfs_didot = italicgfsdidot
    """GFS Didot (Italic)"""
    gfs_neoHellenic = gfsneohellenic
    """GFS NeoHellenic"""
    gnu_freesans_tx = gnufstx
    """GNU FreeSerif (and TX fonts symbols)"""
    gnu_freeserif_freesans = gnufsfs
    """GNU FreeSerif and FreeSans"""
    helvetica_fourier_it = italichelveticaf
    """Helvetica with Fourier (Italic)"""
    latin_modern_tw_it = italiclmtpcm
    """Latin Modern Typewriter Proportional (CM Greek) (Italic)"""
    latin_modern_tw = lmtp
    """Latin Modern Typewriter Proportional"""
    libertine = libertine
    """Libertine"""
    libris_adf_fourier = librisadff
    """Libris ADF with Fourier"""
    minion_pro_myriad_pro = mpmptx
    """Minion Pro and Myriad Pro (and TX fonts symbols)"""
    minion_pro_tx = mptx
    """Minion Pro (and TX fonts symbols)"""
    new_century_schoolbook = ncssg
    """New Century Schoolbook (Symbol Greek)"""
    new_century_schoolbook_px = ncssgpxm
    """New Century Schoolbook (Symbol Greek, PX math symbols)"""
    noteworthy_light = noteworthylight
    """Noteworthy Light"""
    palatino = palatinosg
    """Palatino (Symbol Greek)"""
    papyrus = papyrus
    """Papyrus"""
    romande_adf_fourier_it = italicromandeadff
    """Romande ADF with Fourier (Italic)"""
    slitex = slitexeg
    """SliTeX (Euler Greek)"""
    times_fourier_it = italictimesf
    """Times with Fourier (Italic)"""
    urw_avant_garde = urwagsg
    """URW Avant Garde (Symbol Greek)"""
    urw_zapf_chancery = urwzccmg
    """URW Zapf Chancery (CM Greek)"""
    venturis_adf_fourier_it = italicvanturisadff
    """Venturis ADF with Fourier (Italic)"""
    verdana_it = italicverdana
    """Verdana (Italic)"""
    vollkorn_fourier_it = italicvollkornf
    """Vollkorn with Fourier (Italic)"""
    vollkorn = vollkorntx
    """Vollkorn (TX fonts for Greek and math symbols)"""
    zapf_chancery = zapfchancery
    """Zapf Chancery"""
