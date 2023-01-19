from flask import flash, render_template, session, redirect, url_for

from app.main.forms import NameForm
from . import main


@main.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        session["name"] = form.name.data
        form.name.data = ""
        return redirect(url_for(".index"))
    return render_template("index.html", form=form, name=session.get("name"))


@main.route("/user/<name>")
def user(name):
    return render_template("user.html", user=name)
