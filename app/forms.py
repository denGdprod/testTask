from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DecimalField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, NumberRange, Email, EqualTo, url
import sqlalchemy as sa
from app import db
from app.models import User, Key


class LoginForm(FlaskForm):
    login = StringField('Login:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    login = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    telegram_id = StringField('Telegram ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_login(self, login):
        user = db.session.scalar(sa.select(User).where(
            User.login == login.data))
        if user is not None:
            raise ValidationError('Please use a different login.')

    def validate_email(self, email):
        user = db.session.scalar(sa.select(User).where(
            User.email == email.data))
        if user is not None:
            raise ValidationError('Please use a different email address.')

    def validate_telegram_id(self, telegram_id):
        user = db.session.scalar(sa.select(User).where(
            User.telegram_id == telegram_id.data))
        if user is not None:
            raise ValidationError('Please use a different Telegram ID address.')


class AddServerForm(FlaskForm):
    name = StringField('Server name', validators=[DataRequired()])
    price = DecimalField('Price', validators=[DataRequired(), NumberRange(min=0)])
    url = StringField('URL', validators=[DataRequired(), url()])
    login_panel = StringField('Server login', validators=[DataRequired()])
    password_panel = PasswordField('Server Password', validators=[DataRequired()])
    password2_panel = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password_panel')])
    submit = SubmitField('Add server')

    def validate_price(self, field):
        if field.data and field.data.as_tuple().exponent < -2:
            raise ValidationError('The price can have no more than two decimal places.')

    def validate_login(self, login):
        user = db.session.scalar(sa.select(User).where(
            User.login == login.data))
        if user is not None:
            raise ValidationError('Please use a different login.')


class AddKeyForm(FlaskForm):
    code = TextAreaField('Key code', validators=[DataRequired()])
    payed = BooleanField("Payed", default=False)
    submit = SubmitField('Add key')

    def validate_code(self, code):

        #%validation

        code = db.session.scalar(sa.select(Key).where(
            Key.code == code.data))
        if code is not None:
            raise ValidationError('such a key is already in the system.')

