from flask import render_template
from . import main

@main.route("/")
def index() -> str:
    return render_template("index.html")

@main.route("/user/<name>")
def user(name) -> str:
    return render_template("user.html", user=name)
