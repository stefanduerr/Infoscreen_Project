from xml.dom import ValidationErr
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField, TimeField
from flask_wtf.file import FileField, FileRequired
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
# import app

import re

file = open('C:/Users/stefan.duerr/Documents/flaskProjectTV/registration_key.txt', 'r')
read = file.readlines()
regex = r"[][']"
patn = re.sub(regex, "", str(read))


class RegistrationForm(FlaskForm):

    def validate_reg(self, registration_token):
        # print(str(registration_token.data))
        reg_token = patn
        r_t = str(registration_token.data)
        # print(reg_token)
        if not r_t == reg_token:
            # print('ti') 
            raise ValidationError('Token is incorrect.')
    
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    registration_token = StringField('Registration Token', validators=[DataRequired(), validate_reg])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        from app import User
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username is taken.')
    
    def validate_email(self, email):
        from app import User
        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('E-Mail is taken.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UploadForm(FlaskForm):

    def check_extension(form, field):
        if field.data:
            filename = field.data.filename
            # print(dir(field.data))
            if not filename.lower().endswith(('.mp4', '.wmv', '.mov')):
                raise ValidationError('Please provide a supported video file (.mp4, .wmw, .mov)!')
        else:
            raise ValidationError('Please select a file!')

    video = FileField('Choose File', validators=[check_extension])
    ifnow = BooleanField('Instant Upload', default=False)
    date = DateField('Publish Date', format='%Y-%m-%d')
    time = TimeField('Publish Time')
    submit = SubmitField('Upload Video')
    folder = 'p09'