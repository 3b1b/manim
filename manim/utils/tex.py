"""Utilities for processing custom LaTeX templates."""

__all__ = ["TexTemplateFromFile", "TexTemplate"]


import os
from ..utils.config_ops import digest_config


class TexTemplateFromFile:
    """
    Class representing a TeX template file
    """  # TODO: attributes, dataclasses stuff

    CONFIG = {
        "use_ctex": False,
        "filename": "tex_template.tex",
        "text_to_replace": "YourTextHere",
    }
    body = ""

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.rebuild_cache()

    def rebuild_cache(self):
        """For faster access, the LaTeX template's code is cached.
        If the base file is modified, the cache needs to be rebuilt.
        """
        with open(self.filename, "r") as infile:
            self.body = infile.read()

    def get_text_for_text_mode(self, expression):
        """Inserting expression verbatim into TeX template.

        Parameters
        ----------
        expression : :class:`str`
            String containing the expression to be typeset, e.g. ``"foo"``

        Returns
        -------
        :class:`str`
            LaTeX code based on the template containing the given expression and ready for typesetting.
        """
        return self.body.replace(self.text_to_replace, expression)

    def get_text_for_env(self, environment, expression):
        """Inserts an expression wrapped in a given environment into the TeX template.

        Parameters
        ----------
        environment : :class:`str`
            The environment in which we should wrap the expression.
        expression : :class:`str`
            The string containing the expression to be typeset, e.g. ``$\\sqrt{2}$``

        Returns
        -------
        :class:`str`
            LaTeX code based on template, containing the given expression and ready for typesetting
        """
        begin = r"\begin{" + environment + "}"
        end = r"\end{" + environment + "}"
        return self.body.replace(
            self.text_to_replace, "{0}\n{1}\n{2}".format(begin, expression, end)
        )

    def get_text_for_tex_mode(self, expression):
        """Inserts an expression within an ``align*`` environment into the TeX template.

        Parameters
        ----------
        expression : :class:`str`
            The string containing the (math) expression to be typeset,
            e.g. ``$\\sqrt{2}$``

        Returns
        -------
        :class:`str`
            LaTeX code based on template, containing the given expression and ready for typesetting
        """
        return self.get_text_for_env("align*", expression)


class TexTemplate(TexTemplateFromFile):
    """
    Class for dynamically managing a TeX template
    """  # TODO: Add attributes (when dataclasses are implemented)

    CONFIG = {
        "documentclass": ["standalone", ["preview"]],
        "common_packages": [
            ["babel", ["english"]],
            "amsmath",
            "amssymb",
            "dsfont",
            "setspace",
            "tipa",
            "relsize",
            "textcomp",
            "mathrsfs",
            "calligra",
            "wasysym",
            "ragged2e",
            "physics",
            "xcolor",
            "microtype",
        ],
        "tex_packages": [["inputenc", ["utf8"]], ["fontenc", ["T1"]]],
        "ctex_packages": [["ctex", ["UTF8"]]],
        "common_preamble_text": r"\linespread{1}" "\n",
        "tex_preamble_text": r"\DisableLigatures{encoding = *, family = *}" "\n",
        "ctex_preamble_text": "",
        "document_prefix": "",
        "document_suffix": "",
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.rebuild_cache()

    def rebuild_cache(self):
        """For faster access, the LaTeX template's code is cached.
        If the base file is modified, the cache needs to be rebuilt."""
        tpl = self.generate_tex_command(
            "documentclass",
            required_params=[self.documentclass[0]],
            optional_params=self.documentclass[1],
        )
        for pkg in self.common_packages:
            tpl += self.generate_usepackage(pkg)

        if self.use_ctex:
            for pkg in self.ctex_packages:
                tpl += self.generate_usepackage(pkg)
        else:
            for pkg in self.tex_packages:
                tpl += self.generate_usepackage(pkg)

        tpl += self.common_preamble_text
        if self.use_ctex:
            tpl += self.ctex_preamble_text
        else:
            tpl += self.tex_preamble_text

        tpl += "\n" r"\begin{document}" "\n"
        tpl += f"\n{self.text_to_replace}\n"
        tpl += "\n" r"\end{document}"

        self.body = tpl

    def prepend_package(self, pkg):
        """Adds a new package (or several new packages)
        before all other packages. Sometimes, the order of
        the ``\\usepackage`` directives is relevant.

        Parameters
        ----------
        pkg : :class:`str`
            The package name, e.g. ``"siunitx"``
        """
        self.common_packages.insert(0, pkg)
        self.rebuild_cache()

    def append_package(self, pkg):
        """Adds a new package (or several new packages)
        after all other packages. Sometimes, the order of
        the ``\\usepackage`` directives is relevant.

        Parameters
        ----------
        pkg : :class:`str`
            The package name, e.g. ``"siunitx"``
        """
        self.common_packages.append(pkg)
        self.rebuild_cache()

    def append_to_preamble(self, text):
        """Adds commands (e.g. macro definitions) at the end of the preamble.

        Parameters
        ----------
        text : :class:`str`
            The text to be included, e.g. ``"\\newcommand{\\R}{\\mathbb{Q}}"``.
        """
        if self.use_ctex:
            self.ctex_preamble_text += text
        else:
            self.tex_preamble_text += text
        self.rebuild_cache()
        pass

    def clear_preamble(self):
        """Removes custom definitions from the LaTeX preamble.
        This does not affect the imported packages or documentclass."""
        self.common_preamble_text = ""
        self.ctex_preamble_text = ""
        self.tex_preamble_text = ""
        self.rebuild_cache()
        pass

    def generate_tex_command(self, command, *, required_params, optional_params=[]):
        """
        Function for creating LaTeX command strings with or without options.
        Internally used to generate ``\\usepackage`` commands.

        Parameters
        ----------
        command : :class:`str`
            The command, e.g. ``"usepackage"``.
        required_params : Iterable[:class:`str`]
            The required parameters of this command, each wrapped in ``{}``.
        optional_params : Iterable[:class:`str`]
             The optional parameters of this command, each separated by a comma inside one ``[]``.

        Examples
        --------
        ::

            generate_tex_command("usepackage", required_params=["packagename"], optional_params=["option1", "option2"])

        Returns
        -------
        :class:`str`
            The generated command.
        """
        optional_params = list(optional_params)  # so we can measure its length
        return r"\{0}{1}{2}".format(
            command,
            f"[{','.join(optional_params)}]" if optional_params else "",
            "".join("{" + param + "}" for param in required_params),
        )

    def generate_usepackage(self, pkg):
        if isinstance(pkg, list):
            return self.generate_tex_command(
                "usepackage", required_params=[pkg[0]], optional_params=pkg[1]
            )
        else:
            return self.generate_tex_command("usepackage", required_params=[pkg])

    def get_text_for_text_mode(self, expression):
        """Inserts an expression verbatim into the TeX template.

        Parameters
        ----------
        expression : :class:`str`
            The expression to be typeset, e.g. ``"foo"``.

        Returns
        -------
        :class:`str`
            LaTeX code based on the template, containing the given expression and ready for typesetting
        """
        return self.body.replace(self.text_to_replace, expression)

    def get_text_for_env(self, environment, expression):
        """Inserts an expression wrapped in a given environment into the TeX template.

        Parameters
        ----------
        environment : :class:`str`
            The environment in which we should wrap the expression.
        expression : :class:`str`
            The string containing the expression to be typeset, e.g. ``"$\\sqrt{2}$"``

        Returns
        -------
        :class:`str`
            LaTeX code based on template, containing the given expression and ready for typesetting
        """
        begin = r"\begin{" + environment + "}"
        end = r"\end{" + environment + "}"
        return self.body.replace(
            self.text_to_replace, "{0}\n{1}\n{2}".format(begin, expression, end)
        )

    def get_text_for_tex_mode(self, expression):
        """Inserts an expression within an ``align*`` environment into
        the TeX template.

        Parameters
        ----------
        expression : :class:`str`
            The string containing the (math) expression to be typeset,
            e.g. ``"$\\sqrt{2}$"``

        Returns
        -------
        :class:`str`
            LaTeX code based on template, containing the given expression and ready for typesetting
        """
        return self.get_text_for_env("align*", expression)
