from flask import flash, redirect, render_template, request, url_for
from flask.typing import ResponseReturnValue
from flask_login import current_user, login_required, login_user, logout_user

from app.auth.forms import (
    ChangePasswordForm,
    LoginForm,
    PasswordResetForm,
    PasswordResetRequestForm,
    RegistrationForm,
    ChangeEmailForm,
)

from . import auth
from .. import db
from ..email import send_email
from ..models import User


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != "auth.":
            return redirect(url_for("auth.unconfirmed"))


@auth.route("/unconfirmed")
def unconfirmed() -> ResponseReturnValue:
    if current_user.is_anonymous or current_user.confirmed:
        return redirect("main.index")
    return render_template("auth/unconfirmed.html")


@auth.route("/login", methods=["GET", "POST"])
def login() -> ResponseReturnValue:
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get("next") or url_for("main.index"))
        flash("Invalid username or password.")
    return render_template("auth/login.html", form=form)


@auth.route("/logout")
@login_required
def logout() -> ResponseReturnValue:
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register() -> ResponseReturnValue:
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            username=form.username.data,
            password=form.password.data,
        )
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(
            user.email,
            "Confirm your account",
            "auth/email/confirm",
            user=user,
            token=token,
        )
        flash("A confirmation email has just been sent to your account")
        return redirect(url_for("main.index"))
    return render_template("auth/register.html", form=form)


@auth.route("/confirm/<token>")
@login_required
def confirm(token) -> ResponseReturnValue:
    if current_user.confirmed:
        return redirect(url_for("main.index"))
    if current_user.confirm(token):
        flash("you have confirmed your account. Thanks!")
    else:
        flash("The confirmation link is invalid or has expired")
    return redirect(url_for("main.index"))


@auth.route("/confirm")
@login_required
def resend_confirmation() -> ResponseReturnValue:
    token = current_user.generate_confirmation_token()
    send_email(
        current_user.email,
        "Confirm your Account",
        "auth/email/confirm",
        user=current_user,
        token=token,
    )
    flash("A new confirmation email has been sent to you")
    return redirect(url_for("main.index"))


@auth.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password() -> ResponseReturnValue:
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash("Your password has been updated")
            return redirect(url_for("main.index"))
        else:
            flash("Invalid password")
    return render_template("auth/change_password.html", form=form)


@auth.route("/reset", methods=["GET", "POST"])
def password_reset_request() -> ResponseReturnValue:
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user:
            token = user.generate_reset_token()
            send_email(
                user.email,
                "Reset Your Password",
                "auth/email/reset_password",
                user=user,
                token=token,
            )
        flash("An email with instructions to reset your password has been sent to you.")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/reset/<token>", methods=["GET", "POST"])
def password_reset(token) -> ResponseReturnValue:
    if not current_user.is_anonymous:
        return redirect(url_for("main.index"))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash("Your password has been updated.")
            return redirect(url_for("auth.login"))
        else:
            return redirect(url_for("main.index"))
    return render_template("auth/reset_password.html", form=form)


@auth.route("/change_email", methods=["GET", "POST"])
@login_required
def change_email_request() -> ResponseReturnValue:
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email(
                new_email,
                "Confirm your email address",
                "auth/email/change_email",
                user=current_user,
                token=token,
            )
            flash(
                "An email with instructions to confirm your new email "
                "address has been sent to you."
            )
            return redirect(url_for("main.index"))
        else:
            flash("Invalid email or password.")
    return render_template("auth/change_email.html", form=form)


@auth.route("/change_email/<token>")
@login_required
def change_email(token) -> ResponseReturnValue:
    if current_user.change_email(token):
        db.session.commit()
        flash("Your email address has been updated.")
    else:
        flash("Invalid request.")
    return redirect(url_for("main.index"))
