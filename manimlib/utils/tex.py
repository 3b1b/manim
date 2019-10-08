import os
from manimlib.utils.config_ops import digest_config

class TeXTemplateFromFile():
    """
    Class holding the TeX template file
    """
    CONFIG = {
        "use_ctex": False,
        "filename" : "tex_template.tex",
        "text_to_replace": "YourTextHere",
    }
    template_text = ""

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        self.rebuild_cache()
        
    def rebuild_cache(self):
        with open(self.filename, "r") as infile:
            self.template_text = infile.read()

    def get_text_for_text_mode(self,expression):
        return self.template_text.replace(
            self.text_to_replace, expression
        )

    def get_text_for_tex_mode(self,expression):
        return self.template_text.replace(
            self.text_to_replace,
            r"\begin{align*}" "\n" \
            + expression + "\n" \
            r"\end{align*}"
        )


class TeXTemplate(TeXTemplateFromFile):
    """
    Class for dynamically managing the TeX template 
    """
    CONFIG = {
        "documentclass": ["standalone",["preview"]],
        "common_packages": [
            ["babel",["english"]],
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
            "microtype"
        ],
        "tex_packages": [],
        "ctex_packages": [["ctex",["UTF8"]]],
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
        tpl = self.generate_simple_tex_command_with_options(
            "documentclass",self.documentclass
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

        self.template_text=tpl
        
    def prepend_package(self, pkg):
        self.common_packages.insert(0, pkg)
        self.rebuild_cache()

    def append_package(self, pkg):
        self.common_packages.append(pkg)
        self.rebuild_cache()

    def append_to_preamble(self,text):
        if self.use_ctex:
            self.ctex_preamble_text += text
        else:
            self.tex_preamble_text += text
        self.rebuild_cache()
        pass

    def clear_preamble(self):
        self.common_preamble_text = ""
        self.ctex_preamble_text = ""
        self.tex_preamble_text = ""
        self.rebuild_cache()
        pass

    def generate_simple_tex_command_with_options(self,command,params):
        if isinstance(params,list):
            line = "\\" \
                   + command \
                   + r"[" \
                   + ",".join(params[1]) \
                   + r"]{" \
                   + params[0] \
                   + r"}" + "\n"
        else:
            line = "\\" \
                   + command \
                   + r"{" \
                   + params \
                   + r"}" + "\n"
        return line
        
    def generate_usepackage(self,pkg):
        return self.generate_simple_tex_command_with_options("usepackage",pkg)

    def get_text_for_text_mode(self,expression):
        return self.template_text.replace(
            self.text_to_replace, expression
        )

    def get_text_for_tex_mode(self,expression):
        return self.template_text.replace(
            self.text_to_replace,
            r"\begin{align*}" "\n" \
            + expression + "\n" \
            r"\end{align*}"
        )


#tpl = TeXTemplate()
#tpl = TeXTemplateFromFile(filename="/Users/imh/test/tex_template.tex")
#tpl.append_package(["esvect",["f"]])
#tpl.clear_preamble()
#tpl.append_to_preamble(r"\newcommand{\Sp}{\operatorname{Sp}}")
#print(tpl.get_text_for_tex_mode(r"bla"))
