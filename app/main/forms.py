from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
    ValidationError,
)
from wtforms.validators import DataRequired, Length, Email, Regexp

from app.models import Category, Role, User


class NameForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])


class ListForm(FlaskForm):
    title = StringField("Title:", validators=[DataRequired()])
    submit = SubmitField("Create List")


class ItemForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    link = StringField("URL: (optional)")
    description = TextAreaField("Description: (optional)")
    category_id = SelectField("Category: ", coerce=int)
    submit = SubmitField("Add to List")

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.category_id.choices = [
            (category.id, category.name)
            for category in Category.query.order_by(Category.id).all()
        ]


class UserEditForm(FlaskForm):
    email = StringField(
        "Email: ",
        validators=[
            DataRequired(),
            Length(1, 64),
            Email(),
        ],
    )
    username = StringField(
        "Username: ",
        validators=[
            DataRequired(),
            Length(0, 64),
            Regexp(
                "^[a-zA-Z][a-zA-Z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or underscores",
            ),
        ],
    )
    confirmed = BooleanField("Confirmed")
    role = SelectField("Role: ", coerce=int)
    submit = SubmitField("Submit")

    def __init__(self, user, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        self.role.choices = [
            (role.id, role.name) for role in Role.query.order_by(Role.name).all()
        ]
        self.user = user

    def validate_email(self, field):
        if (
            field.data != self.user.email
            and User.query.filter_by(email=field.data).first()
        ):
            raise ValidationError("Email already registered")

    def validate_username(self, field):
        if (
            field.data != self.user.username
            and User.query.filter_by(username=field.data).first()
        ):
            raise ValidationError("Username already in use")
