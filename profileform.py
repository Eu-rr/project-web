from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed


class ProfileForm(FlaskForm):
    title = StringField('Заголовок')
    content = TextAreaField("Содержание")
    photo = FileField('Загрузка изображения', validators=[FileAllowed(['jpg', 'png'], 'Только изображения')])
    tag = TextAreaField('Довавьте теги через пробел')
    is_private = BooleanField("Личное")
    submit = SubmitField('Применить')
