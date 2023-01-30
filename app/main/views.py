from flask import abort, current_app, flash, redirect, render_template, session, url_for
from flask_login import current_user, login_required

from app import db
from app.decorators import admin_required
from app.email import send_email
from app.main.forms import ItemForm, ListForm, NameForm
from app.models import Item, List, Permission, User

from . import main


@main.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            session["known"] = False
            if current_app.config["DIBS_ADMIN"]:
                send_email(
                    current_app.config["DIBS_ADMIN"],
                    "New User",
                    "mail/newuser",
                    user=user,
                )
        else:
            session["known"] = True
        session["name"] = form.name.data
        form.name.data = ""
        return redirect(url_for(".index"))
    return render_template(
        "index.html",
        form=form,
        name=session.get("name"),
        known=session.get("known", False),
    )


@main.route("/create", methods=["GET", "POST"])
@login_required
def create():
    form = ListForm()
    if current_user.can(Permission.CREATE) and form.validate_on_submit():
        newlist = List(
            title=form.title.data,
            author=current_user._get_current_object(),
        )
        db.session.add(newlist)
        db.session.commit()
        return redirect(url_for("main.list", list_id=newlist.id))
    return render_template(
        "create.html",
        form=form,
    )


@main.route("/lists/", methods=["GET", "POST"])
@login_required
def lists():
    """
    Show lists you have created yourself
    """
    lists = List.query.filter_by(author_id=current_user.id).all()
    return render_template(
        "lists.html",
        lists=lists,
    )


@main.route("/lists/<list_id>", methods=["GET", "POST"])
@login_required
def list(list_id):
    """
    Show a single list by ID
    """
    form = ItemForm()
    if current_user.can(Permission.READ) and form.validate_on_submit():
        newitem = Item(
            name=form.name.data,
            link=form.link.data,
            description=form.description.data,
            list_id=list_id,
        )
        db.session.add(newitem)
        return redirect(url_for("main.list", list_id=list_id))
    currentlist = List.query.filter_by(id=list_id).first()
    items = Item.query.filter_by(list_id=list_id).all()
    return render_template(
        "list.html",
        currentlist=currentlist,
        items=items,
        form=form,
    )


@main.route("/lists/<list_id>/delete", methods=["GET", "POST"])
@login_required
def delete_list(list_id):
    currentlist = List.query.filter_by(id=list_id).first()
    if current_user.can(Permission.DELETE):
        db.session.delete(currentlist)
    flash(f'Your list "{currentlist.title}" has been deleted')
    return redirect(url_for("main.lists"))


@main.route("/lists/<list_id>/delete/<item_id>", methods=["GET", "POST"])
@login_required
def delete_item(list_id, item_id):
    item = Item.query.filter_by(id=item_id).first()
    if current_user.can(Permission.DELETE):
        db.session.delete(item)
    flash(f'The item "{item.name}" has been deleted')
    return redirect(url_for("main.list", list_id=list_id))


@main.route("/admin")
@login_required
@admin_required
def for_admins_only():
    """
    For demonstration only.
    Once user route has been augmented with Admin features, this can be deleted.
    """
    return "Admins only"


@main.route("/user/<username>")
def user(username):
    """
    Profile page
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template("user.html", user=user)
