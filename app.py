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


## Routes.


@app.route("/")
def index() -> str:
    form = UnicoderForm()
    return flask.render_template("index.html", form=form)


@app.route("/result.html", methods=["POST"])
def result() -> str:
    form = UnicoderForm(flask.request.form)
    if form.validate():
        # Prepares the string.
        string = form.string.data
        if form.normalization.data != "none":
            string = unicodedata.normalize(form.normalization.data, string)
        if form.casefold.data:
            string = string.casefold()
        if form.strip.data:
            string = string.strip()
        return flask.render_template(
            "result.html",
            string=string,
            infos=[CharInfo(char) for char in string],
        )
    return "<p>Form validation failed.</p>"


if __name__ == "__main__":
    app.run()
