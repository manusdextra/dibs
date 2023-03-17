from flask import abort, current_app, flash, redirect, render_template, session, url_for
from flask.typing import ResponseReturnValue
from flask_login import current_user, login_required

from app import db
from app.decorators import admin_required
from app.email import send_email
from app.main.forms import ItemForm, ListForm, NameForm, UserEditForm
from app.models import Category, Item, List, Permission, Role, User

from . import main


@main.route("/", methods=["GET", "POST"])
def index() -> ResponseReturnValue:
    if current_user is None:
        return render_template("index.html")
    else:
        user = User.query.filter_by(username=current_user.username).first()
        lists = List.query.filter(List.author_id != user.id).all()

        # TODO Is this best practice? It works but it feels wrong
        for l in lists:
            author = User.query.filter_by(id=l.author_id).first()
            l.author = author

        return render_template(
            "index.html",
            lists=lists,
        )


@main.route("/lists/create", methods=["GET", "POST"])
@login_required
def create() -> ResponseReturnValue:
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


@main.route("/lists/<list_id>", methods=["GET", "POST"])
@login_required
def list(list_id) -> ResponseReturnValue:
    """
    Show a single list by ID
    """
    form = ItemForm(list_id=list_id)
    if current_user.can(Permission.READ) and form.validate_on_submit():
        newitem = Item(
            name=form.name.data,
            link=form.link.data,
            description=form.description.data,
            category_id=form.category_id.data,
            list_id=list_id,
        )
        db.session.add(newitem)
        return redirect(url_for("main.list", list_id=list_id))
    currentlist = List.query.filter_by(id=list_id).first()
    user = User.query.filter_by(id=currentlist.author_id).first()
    items = Item.query.filter_by(list_id=list_id).all()
    # show only those categories that have items in them
    # TODO: this seems hacky, and potentially means a lot of
    # individual db queries, which I'm sure is not a good idea
    categories = [
        Category.query.filter_by(id=item.category_id).first() for item in items
    ]

    return render_template(
        "list.html",
        currentlist=currentlist,
        user=user,
        items=items,
        categories=categories,
        form=form,
    )


@main.route("/lists/<list_id>/delete", methods=["GET", "POST"])
@login_required
def delete_list(list_id) -> ResponseReturnValue:
    currentlist = List.query.filter_by(id=list_id).first()
    if current_user.can(Permission.DELETE):
        db.session.delete(currentlist)
        flash(f'Your list "{currentlist.title}" has been deleted')
    else:
        flash("Sorry, you're not allowed to do that.")
    return redirect(url_for("main.profile", username=current_user.username))


@main.route("/lists/<list_id>/delete/<item_id>", methods=["GET", "POST"])
@login_required
def delete_item(list_id, item_id) -> ResponseReturnValue:
    item = Item.query.filter_by(id=item_id).first()
    if current_user.can(Permission.DELETE):
        db.session.delete(item)
    flash(f'The item "{item.name}" has been deleted')
    return redirect(url_for("main.list", list_id=list_id))


@main.route("/user/<username>")
def profile(username) -> ResponseReturnValue:
    """
    User profile, shows their lists
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    lists = List.query.filter_by(author_id=user.id).all()
    return render_template("profile.html", user=user, lists=lists)


@main.route("/user/<username>/settings")
@login_required
def settings(username) -> ResponseReturnValue:
    """
    Settings page
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    return render_template("settings.html", user=user)


@main.route("/user/<username>/edit", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user(username) -> ResponseReturnValue:
    """
    Admin interface for each user
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    form = UserEditForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        db.session.add(user)
        db.session.commit()
        flash("The profile has been updated.")
        return redirect(url_for("main.user", username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    return render_template(
        "edituser.html", form=form, user=user, username=user.username
    )
