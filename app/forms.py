from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, FileField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirmpassword = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])

    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    sex = StringField('Sex', validators=[DataRequired()])

    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already taken, Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already taken, Please use a different email address.')

class PublicEditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password')
    confirmpassword = PasswordField('Repeat Password',[EqualTo('password')])

    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    sex = StringField('Sex', validators=[DataRequired()])

    submit = SubmitField('Update')

    def __init__(self, original_username, original_email, original_id, *args, **kwargs):
        super(PublicEditUserForm, self).__init__(*args, **kwargs)
        self.original_id = original_id
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if email.data == self.email:
            return
        else:
            email = User.query.filter(User.email==self.email.data, User.id != self.original_id).first()
            if email is not None:
                raise ValidationError('Please use a different email.')

class EditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password')
    confirmpassword = PasswordField('Repeat Password',[EqualTo('password')])

    firstname = StringField('Firstname', validators=[DataRequired()])
    lastname = StringField('Lastname', validators=[DataRequired()])
    contact = StringField('Contact', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    sex = StringField('Sex', validators=[DataRequired()])
    access_level = StringField('Access Level', validators=[DataRequired()])

    submit = SubmitField('Update')

    def __init__(self, original_username, original_email, original_id, *args, **kwargs):
        super(EditUserForm, self).__init__(*args, **kwargs)
        self.original_id = original_id
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        if email.data == self.email:
            return
        else:
            email = User.query.filter(User.email==self.email.data, User.id != self.original_id).first()
            if email is not None:
                raise ValidationError('Please use a different email.')


class AddStudentTransactionForm(FlaskForm):
    service_name = StringField('Service Name')
    contact_details = StringField('Contact Details')
    description = StringField('Description')
    service_type = StringField('Service Type')
    price = StringField('Price')
    submit = SubmitField('Add new transaction')

class LandingPageEditForm(FlaskForm):
    about_ece = TextAreaField('About ECE', validators=[DataRequired()])
    vision_mission = TextAreaField('Vision / Mission', validators=[DataRequired()])
    submit = SubmitField('Update landing page data')
    
class AddFeedbackForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    details = TextAreaField('Details', validators=[DataRequired()])
    submit = SubmitField('Send feedback')

class EncodeSubjectForm(FlaskForm):
    subject_name = StringField('Service Name')
    units = StringField('Units')
    year = StringField('Year')
    semester = StringField('Semester')
    final_grade = StringField('Final Grade')
    submit = SubmitField('Encode')