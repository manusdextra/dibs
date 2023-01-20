from flask import flash, render_template, session, redirect, url_for

from app.main.forms import NameForm
from app.models import User
from app import db
from . import main


@main.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username = form.name.data)
            db.session.add(user)
            session["known"] = False
        else:
            session["known"] = True
        session["name"] = form.name.data
        form.name.data = ""
        return redirect(url_for(".index"))
    return render_template("index.html", form=form, name=session.get("name"), known = session.get("known", False))


@main.route("/user/<name>")
def user(name):
    return render_template("user.html", user=name)
