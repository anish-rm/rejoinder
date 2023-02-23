from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, FileField, TextAreaField, DateTimeLocalField


class SignUpForm(FlaskForm):
    username = StringField('username')
    password = PasswordField('password')
    email = EmailField('email')
    signup = SubmitField('Sign Up')
    
class LoginForm(FlaskForm):
    email = EmailField('email')
    password = PasswordField('password')
    login = SubmitField('Log In')
    
class OTPForm(FlaskForm):
    recieved_otp = StringField('otp')
    submit = SubmitField('Validate')
    
class DocForm(FlaskForm):
    email = EmailField('email')
    upfile = FileField('upfile')
    datetime = DateTimeLocalField('datetime')
    textarea = TextAreaField('message')
    sendotp = SubmitField('Send with OTP')
    
class InboxForm(FlaskForm):
    download = SubmitField('Download')