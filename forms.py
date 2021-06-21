from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flask_ckeditor import CKEditorField

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=40)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Hasło', validators=[DataRequired()])
    confirm_password = PasswordField('Powtórz hasło', validators=[DataRequired(), EqualTo('password')])

    submit = SubmitField('Zarejestuj się')
    # def validate_username(self, username):
    #     hello = User.query.filter_by(username=username.data).first()
    #     if hello:
    #         raise ValidationError('Ten username już jest zajęty. Proszę wybrać inny username.')
    # def validate_email(self, email):
    #     hello = User.query.filter_by(email=email.data).first()
    #     if hello:
    #         raise ValidationError('Ten email już jest zajęty. Proszę podać inny email.')



class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Hasło', validators=[DataRequired()])
    remember = BooleanField('Zapamiętaj mnie')
    submit = SubmitField('Zaloguj')

class UpdatePasswordForm(FlaskForm):
    password = PasswordField('Hasło', validators=[DataRequired()])
    confirm_password = PasswordField('Powtórz hasło', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Zatwierdź')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=40)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Zatwierdź')
    # def validate_username(self, username):
    #     if username.data != current_user.username:
    #         user = User.query.filter_by(username=username.data).first()
    #         if user:
    #             raise ValidationError('Ten username już jest zajęty. Proszę wybrać inny username.')
    #
    # def validate_email(self, email):
    #     if email.data != current_user.email:
    #         user = User.query.filter_by(email=email.data).first()
    #         if user:
    #             raise ValidationError('Ten email już jest zajęty. Proszę podać inny email.')




class DeletePictureForm(FlaskForm):
    submit = SubmitField('Usuń')

class DeleteCommentForm(FlaskForm):
    submit = SubmitField('Usuń')

class CommentForm(FlaskForm):
    content = TextAreaField('Twój komentarz:', validators=[DataRequired()])
    submit = SubmitField('Wyślij')


class PictureForm(FlaskForm):
    name = StringField('Nazwa obrazu', validators=[DataRequired()])
    description = CKEditorField('Opis', validators=[DataRequired()])
    # description = TextAreaField('Opis', validators=[DataRequired()])
    year = IntegerField('Rok powstania', validators=[DataRequired()])
    origin = StringField('Lokalizacja', validators=[DataRequired()])
    artist = SelectField('Artysta', coerce=int)
    picture = FileField('Plik obrazu', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Zatwierdź')