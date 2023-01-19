from flask import render_template

from app.main.forms import NameForm
from . import main

@main.route("/", methods=["GET", "POST"])
def index() -> str:
    name = None
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ""
    return render_template("index.html", form=form, name=name)

@main.route("/user/<name>")
def user(name) -> str:
    return render_template("user.html", user=name)
