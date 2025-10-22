from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField


class ChangeForm(FlaskForm):
    name = StringField("Имя")
    email = EmailField("Почта")
    about = TextAreaField('О себе')
    new_password = PasswordField("Новый пароль")
    old_password = PasswordField("Старый пароль", validators=[DataRequired()])
    submit = SubmitField('Изменить')

