from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed


class CommentForm(FlaskForm):
    content = TextAreaField("Содержание")
    photo = FileField('Загрузка изображения', validators=[FileAllowed(['jpg', 'png'], 'Только изображения')])
    submit = SubmitField('Отправить')
