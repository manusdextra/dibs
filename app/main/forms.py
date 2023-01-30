from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])


class ListForm(FlaskForm):
    title = StringField("Title:", validators=[DataRequired()])
    submit = SubmitField("Create List")


class ItemForm(FlaskForm):
    name = StringField("Name: ", validators=[DataRequired()])
    link = StringField("URL: (optional)")
    description = TextAreaField("Description: (optional)")
    submit = SubmitField("Add to List")
