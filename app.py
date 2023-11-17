"""Unicode display app."""

import unicodedata

import flask
import wtforms  # type: ignore
import yaml


CONFIG = "config.yaml"


## Startup.


# Creates app object.
app = flask.Flask(__name__)


# Loads configs.
with open(CONFIG, "r") as source:
    app.config.update(yaml.safe_load(source))


## Forms.


class UnicoderForm(wtforms.Form):

    string = wtforms.StringField(
        "string", [wtforms.validators.Length(max=256)]
    )
    normalization = wtforms.StringField("normalization")
    casefold = wtforms.BooleanField("casefold")
    strip = wtforms.BooleanField("strip")


## Intermediate data.


class CharInfo:
    """Helper for storing character info."""

    char: str
    code: int
    name: str
    category: str

    # After: https://en.wikipedia.org/wiki/Template:General_Category_(Unicode)
    _category_name = {
        "Lu": "Letter uppercase",
        "Ll": "Letter, lowercase",
        "Lt": "Letter, titlecase",
        "Lm": "Letter, modifier",
        "Lo": "Letter, other",
        "Mn": "Mark, nonspacing",
        "Mc": "Mark, spacing combining",
        "Me": "Mark,  enclosing",
        "Nd": "Number, decimal digit",
        "Nl": "Number, letter",
        "No": "Number, other",
        "Pc": "Punctuation, connector",
        "Pd": "Punctuation, dash",
        "Ps": "Punctuation, open",
        "Pe": "Punctuation, close",
        "Pi": "Punctuation, initial quote",
        "Pf": "Punctuation, final quote",
        "Po": "Punctuation, other",
        "Sm": "Symbol, math",
        "Sc": "Symbol, currency",
        "Sk": "Symbol, modifier",
        "So": "Symbol, other",
        "Zs": "Separator, space",
        "Zl": "Separator, line",
        "Zp": "Separator, paragraph",
        "Cc": "Other, control",
        "Cf": "Other, format",
        "Cs": "Other, surrogate",
        "Co": "Other, private use",
        "Cn": "Other, not assigned",
    }

    def __init__(self, char: str):
        assert len(char) == 1, f"expected single character, got {char}"
        self.char = char
        self.code = ord(char)
        self.name = unicodedata.name(char, "<unknown>")
        self.category = CharInfo._category_name.get(
            unicodedata.category(char), "<unknown>"
        )


class StringInfo:
    """Helper for storing character info."""

    raw_string: str
    can_string: str
    normalization_form: str
    casefold: bool
    strip: bool

    def __init__(
        self,
        raw_string: str,
        normalization_form: str,
        casefold: bool,
        strip: bool,
    ):
        self.raw_string = raw_string
        self.normalization_form = normalization_form
        self.casefold = casefold
        self.strip = strip
        self.can_string = raw_string
        if self.normalization_form != "none":
            self.can_string = unicodedata.normalize(
                normalization_form, self.can_string
            )
        if self.casefold:
            self.can_string = self.can_string.casefold()
        if self.strip:
            self.can_string = self.can_string.strip()


## Routes.


@app.route("/")
def index() -> str:
    form = UnicoderForm()
    return flask.render_template("index.html", form=form)


@app.route("/result.html", methods=["POST"])
def result() -> str:
    form = UnicoderForm(flask.request.form)
    if form.validate():
        stringinfo = StringInfo(
            form.string.data,
            form.normalization.data,
            form.casefold.data,
            form.strip.data,
        )
        charinfos = [CharInfo(char) for char in stringinfo.can_string]
        return flask.render_template(
            "result.html",
            stringinfo=stringinfo,
            charinfos=charinfos,
        )
    return "<p>Form validation failed.</p>"


if __name__ == "__main__":
    app.run()
