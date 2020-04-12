import logging
import json
import os

from uuid import uuid4
from app import app, db
from app.decorators import admin_required, is_account_owner, is_student_transaction_owner
from app.forms import AddStudentTransactionForm, LoginForm, RegistrationForm, EditUserForm, PublicEditUserForm, LandingPageEditForm, AddFeedbackForm, EncodeSubjectForm
from app.models import StudentTransaction, User, WebsiteData, Feedback, Subject
from app.dijkstras import Dijkstra

from config import Config

from flask import (Flask, flash, g, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import current_user, login_required, login_user, logout_user
from sqlalchemy import create_engine, desc, or_
from sqlalchemy.orm import sessionmaker
from werkzeug.exceptions import HTTPException
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

import boto3

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "gif"}

engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=True)
Session = sessionmaker(bind=engine)


logging.basicConfig(level=logging.DEBUG)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def before_request():
    g.user = current_user

@app.before_first_request
def create_database():
    db.create_all()
    db.session.commit()

    user = User.query.filter_by(access_level=1).first()
    if user == None:
        #Create default admin account
        user = User(
                username='admin',
                email=' ',
                firstname=' ',
                lastname=' ',
                contact=' ',
                address=' ',
                sex='0',
                access_level = '1',
            )
        user.set_password('admin')
        db.session.add(user)
        db.session.commit()
    
    website_data = WebsiteData.query.first()
    if website_data == None:
        website_data = WebsiteData(
            data = json.dumps({
                'about_ece' : 
                    '''
                  <div class="segment stripe ui vertical">
<div class="aligned container grid middle stackable ui">
<div class="row">
<div class="column eight wide">
<h3><strong>ELECTRONICS ENGINEERING</strong></h3>

<p>Electronic engineering, or electronics engineering is a form of engineering associated with electronic circuits, devices and the equipment and systems that use them.</p>

<p>Electronic engineering utilises a variety of different types of electronic components from the more traditional analogue components through to digital electronic components, microprocessors and microcontrollers as well as programmable logic devices. This means that electronic engineering can incorporate a large variety of different areas.</p>

<p>The field of electronic engineering includes a variety more specific electronic engineering fields including: analogue electronics, digital electronics, consumer electronics, embedded systems and power electronics.</p>
</div>
</div>
</div>
</div>

                    '''
                ,
                'vision_mission' : 
                    '''
                   <p>&nbsp;</p>

<div class="segment stripe ui vertical">
<div class="aligned container grid middle stackable ui">
<div class="row">
<div class="column six wide">
<h3><strong style="font-family: 'Roboto Slab'; font-size: 2em;">Lake University</strong></h3>


<h3><strong>VISION</strong></h3>
<p>Lake University as a leading university in Europe by 2040.</p>
<h3><strong>MISSION</strong></h3>
<p>
The University's mission is to provide quality and advanced education, 
higher technological, professional instruction and training technical fields of study,
promote research and development programs.
</p>

<p>&nbsp;</p>

<p>&nbsp;</p>
</div>

<div class="column ten wide">
<h3><strong>FACULTY</strong></h3>

<div class="column ten wide">

<div class="cards link ui">
    <div class="card" style="max-width:150px">
        <div class="image"><img src="https://randomuser.me/api/portraits/women/86.jpg" /></div>

        <div class="content">
            <div class="header">Esther Sanders</div>
            <div class="meta">Principal</div>
        </div>
    </div>

    <div class="card" style="max-width:150px">
        <div class="image"><img src="https://randomuser.me/api/portraits/women/24.jpg" /></div>

        <div class="content">
            <div class="header">Ann Ramos</div>
            <div class="meta">Vice-Principal</div>
        </div>
    </div>

    <div class="card" style="max-width:150px">
        <div class="image"><img src="https://randomuser.me/api/portraits/men/51.jpg" /></div>

        <div class="content">
            <div class="header">Angel Peterson</div>
            <div class="meta">Dean of Discipline</div>
        </div>
    </div>

    <div class="card" style="max-width:150px">
        <div class="image"><img src="https://randomuser.me/api/portraits/women/32.jpg" /></div>

        <div class="content">
            <div class="header">Alice Henderson</div>
            <div class="meta">Guidance Counsellor</div>
        </div>
    </div>


</div>











</div>




</div>
</div>
</div>
</div>
</div>

                    '''
                ,
            })
        )

        db.session.add(website_data)
        db.session.commit()



@app.route("/")
@app.route("/index", methods=["GET"])
def index():
    
    website_data = WebsiteData.query.first()
    
    if website_data == None:
        website_data = {
            'about_ece' : '',
            'vision_mission' : '',
        }
    website_data = json.loads(website_data.data)
    
    return render_template('public_templates/index.html', title='Home page', about_ece=website_data['about_ece'], vision_mission=website_data['vision_mission'])

@app.route("/campus_map", methods=["GET"])
def campus_map():
    return render_template('public_templates/campus_map.html', title='Home page')


@app.route("/student_grades/<int:user_id>", methods=["GET"])
@login_required
@is_account_owner
def student_grades(user_id):
    year_filter_query = request.args.get('year_filter')
    semester_filter_query = request.args.get('semester_filter')

    subjects = None

    #filter only by semester
    if year_filter_query == "" and semester_filter_query != "" or \
       year_filter_query == "all" and semester_filter_query != "" and semester_filter_query != "all semester":
        
        subjects = Subject.query.filter(Subject.user_id==user_id, Subject.semester==semester_filter_query).all()

    #filter only by year
    elif semester_filter_query == "" and year_filter_query != "" or \
       semester_filter_query == "all semester" and year_filter_query != "" and year_filter_query != "all":
        
        subjects = Subject.query.filter(Subject.user_id==user_id, Subject.year==year_filter_query).all()

    #filter by year and semester
    elif semester_filter_query != "" and year_filter_query != "" and semester_filter_query != "all semester" and year_filter_query != "all":
        subjects = Subject.query.filter(Subject.user_id==user_id, Subject.year==year_filter_query, Subject.semester==semester_filter_query).all()

    #no filtering
    elif semester_filter_query == "" and year_filter_query == "" or \
       semester_filter_query == "all semester" and year_filter_query == "all" or \
       semester_filter_query == "" and year_filter_query == "all" or \
       semester_filter_query == "all semester" and year_filter_query == "" :
        
        subjects = Subject.query.filter_by(user_id=user_id).all()
    
    #(Grade × Unit)+(Grade × Unit)/total # of Units
    general_average = 0
    total_number_of_units = 0
    for subject in subjects:
        general_average += float(subject.final_grade) * float(subject.units)
        total_number_of_units += float(subject.units)
    try:
        general_average = general_average / total_number_of_units
    except ZeroDivisionError:
        general_average = 0

    '''
        Qualification as DL..
        1.. GPA must be greater or equal to 2.0
        2.. Individual Grades per Subject must be greater than or equal to 2.5
    '''
    is_subject_qualified = False
    subjects_qualification = Subject.query.filter_by(user_id=user_id).all()
    for subject in subjects_qualification:
        
        if float(subject.final_grade) <= 2.5:
            is_subject_qualified = True
        else:
            is_subject_qualified = False
    
    is_gpa_qualified = False
    if general_average <= 2:
        is_gpa_qualified = True

    dean_list_qualified = False
    if is_gpa_qualified and is_subject_qualified:
        dean_list_qualified = True


    user = User.query.filter_by(id=user_id).first_or_404()
    years = Subject.query.filter_by(user_id=user_id).group_by(Subject.year).distinct().all()
    
    return render_template('shared_templates/student_grades.html', title='Grades', user=user, subjects=subjects, years=years, general_average=round(general_average,2), dean_list_qualified=dean_list_qualified, is_gpa_qualified=is_gpa_qualified, is_subject_qualified=is_subject_qualified)

@app.route("/student_grades/admin/<int:user_id>", methods=["GET","POST"])
@login_required
@admin_required
def admin_student_grades(user_id):
    year_filter_query = request.args.get('year_filter')
    semester_filter_query = request.args.get('semester_filter')

    subjects = None

    #filter only by semester
    if year_filter_query == "" and semester_filter_query != "" or \
       year_filter_query == "all" and semester_filter_query != "" and semester_filter_query != "all semester":
        
        subjects = Subject.query.filter(Subject.user_id==user_id, Subject.semester==semester_filter_query).all()

    #filter only by year
    elif semester_filter_query == "" and year_filter_query != "" or \
       semester_filter_query == "all semester" and year_filter_query != "" and year_filter_query != "all":
        
        subjects = Subject.query.filter(Subject.user_id==user_id, Subject.year==year_filter_query).all()

    #filter by year and semester
    elif semester_filter_query != "" and year_filter_query != "" and semester_filter_query != "all semester" and year_filter_query != "all":
        subjects = Subject.query.filter(Subject.user_id==user_id, Subject.year==year_filter_query, Subject.semester==semester_filter_query).all()

    #no filtering
    elif semester_filter_query == "" and year_filter_query == "" or \
       semester_filter_query == "all semester" and year_filter_query == "all" or \
       semester_filter_query == "" and year_filter_query == "all" or \
       semester_filter_query == "all semester" and year_filter_query == "" :
        
        subjects = Subject.query.filter_by(user_id=user_id).all()
    
    #(Grade × Unit)+(Grade × Unit)/total # of Units
    general_average = 0
    total_number_of_units = 0
    for subject in subjects:
        general_average += float(subject.final_grade) * float(subject.units)
        total_number_of_units += float(subject.units)
    try:
        general_average = general_average / total_number_of_units
    except ZeroDivisionError:
        general_average = 0

    '''
        Qualification as DL..
        1.. GPA must be greater or equal to 2.0
        2.. Individual Grades per Subject must be greater than or equal to 2.5
    '''
    is_subject_qualified = False
    subjects_qualification = Subject.query.filter_by(user_id=user_id).all()
    for subject in subjects_qualification:
        if float(subject.final_grade) <= 2.5:
            is_subject_qualified = True
        else:
            is_subject_qualified = False
            break
    
    
    is_gpa_qualified = False
    if general_average <= 2 and general_average != 0:
        is_gpa_qualified = True

    dean_list_qualified = False
    if is_gpa_qualified and is_subject_qualified:
        dean_list_qualified = True


    user = User.query.filter_by(id=user_id).first_or_404()
    years = Subject.query.filter_by(user_id=user_id).group_by(Subject.year).distinct().all()
    
    return render_template('shared_templates/student_grades.html', title='Grades', user=user, subjects=subjects, years=years, general_average=round(general_average,2), dean_list_qualified=dean_list_qualified, is_gpa_qualified=is_gpa_qualified, is_subject_qualified=is_subject_qualified)

@app.route("/student_grades/admin/encode/<int:user_id>", methods=["GET", "POST"])
@login_required
def admin_encode_student_grades(user_id):
    form = EncodeSubjectForm()
    user = User.query.filter_by(id=user_id).first_or_404()
    if form.validate_on_submit():
        subject = Subject(
            subject_name=form.subject_name.data, 
            units=form.units.data,
            year=form.year.data,
            semester=form.semester.data,
            final_grade=form.final_grade.data,
            user=user
        )
        
        db.session.add(subject)
        db.session.commit()
        flash('Added subject')
        return redirect(url_for('admin_student_grades', user_id=user.id))

    return render_template('admin_templates/encode_subject.html', title='Grades', user=user, form=form)


@app.route("/student_grades/admin/edit/<int:user_id>/<int:subject_id>", methods=["GET", "POST"])
@login_required
def admin_edit_student_grades(user_id, subject_id):
    form = EncodeSubjectForm()
    user = User.query.filter_by(id=user_id).first_or_404()
    subject = Subject.query.filter_by(id=subject_id).first_or_404()

    if form.validate_on_submit():
        subject.subject_name = form.subject_name.data
        subject.units = form.units.data
        subject.year = form.year.data
        subject.semester = form.semester.data
        subject.final_grade = form.final_grade.data
        
        db.session.add(subject)
        db.session.commit()
        flash('Updated!')
        return redirect(url_for('admin_student_grades', user_id=user.id))

    return render_template('admin_templates/edit_subject.html', title='Grades', user=user, form=form, subject=subject)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == "GET":
        return render_template('./public_templates/login.html', title="Login page", form=form)
    elif request.method == "POST":
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('Invalid username or password')
                return redirect(url_for('login'))
            login_user(user, remember=form.remember_me.data)
            g.user = user
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
    
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data, 
            email=form.email.data,
            firstname=form.firstname.data,
            lastname=form.lastname.data,
            contact=form.contact.data,
            address=form.address.data,
            sex=form.sex.data,
            access_level = 0,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('./public_templates/register.html', title="Registration page", form=form)


@app.route('/user/<int:user_id>', methods=["GET", "POST"])
@login_required
@is_account_owner
def user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    form = PublicEditUserForm(user.username, user.email, user.id)

    if form.validate_on_submit():
        if form.username.data:
            user.username = form.username.data

        if form.email.data and user.email != form.email.data:
            user.email = form.email.data
        if form.firstname.data:
            user.firstname = form.firstname.data
        if form.lastname.data:
            user.lastname = form.lastname.data
        if form.contact.data:
            user.contact = form.contact.data
        if form.address.data:
            user.address = form.address.data
        if form.sex.data:
            user.sex = form.sex.data
        if form.password.data:
            user.set_password(form.password.data)
            
        db.session.commit()
        flash('Successfully saved!')
        return redirect(url_for('user', user_id=user.id))

    return render_template('./shared_templates/profile.html', title=user.username, form=form, user=user)

@app.route('/student_transactions/<int:user_id>', methods=["GET", "POST"])
@login_required
@is_account_owner
def student_transaction_list(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    student_transactions = StudentTransaction.query.filter_by(user_id=user_id).all()

    return render_template('./student_templates/student_transaction_list.html', title=user.firstname +" "+ user.lastname, student_transactions=student_transactions, user=user)

@app.route('/student_transaction/delete/<int:user_id>/<int:student_transaction_id>', methods=["GET", "POST"])
@login_required
@is_student_transaction_owner
def delete_student_transaction(user_id, student_transaction_id):
    student_transaction = StudentTransaction.query.filter_by(id=student_transaction_id).first()
    db.session.delete(student_transaction)
    db.session.commit()
    return redirect(url_for('student_transaction_list', user_id=user_id))

@app.route('/admin/student_transaction/delete/<int:student_transaction_id>', methods=["GET", "POST"])
@login_required
@admin_required
def admin_delete_student_transaction(student_transaction_id):
    student_transaction = StudentTransaction.query.filter_by(id=student_transaction_id).first()
    db.session.delete(student_transaction)
    db.session.commit()
    return redirect(url_for('student_transaction', page_num='1'))


@app.route("/student_transaction_add", methods=["GET", "POST"])
@login_required
def add_student_transaction():
    form = AddStudentTransactionForm()
    folder_unique_str = "student_transaction_" + str(uuid4())

    if form.validate_on_submit():
        filename = ''
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            
            if file and allowed_file(file.filename):
                session = boto3.Session(
                    aws_access_key_id=app.config["AWS_ACCESS_KEY_ID"],
                    aws_secret_access_key=app.config["AWS_SECRET_ACCESS_KEY"],
                )
                filename = secure_filename(file.filename)
                filename = str(uuid4()) + "_" + filename

                s3_client = session.resource("s3")
                response = s3_client.Bucket(app.config["S3_BUCKET"]).put_object(
                    Key=(
                        "lakeuniversity/pictures/"
                        + app.config["IMAGE_DEPLOY_FOLDER_LOCATION"]
                        + "/"
                        + folder_unique_str
                        + "/"
                        + filename
                    ),
                    Body=file,
                    ACL="public-read",
                )
                app.logger.info("[response]:")
                app.logger.info(response)

        price = 0
        if form.price.data != '':
            price = float(form.price.data)
        
        student_transaction = StudentTransaction(
            service_name=form.service_name.data, 
            contact_details=form.contact_details.data,
            description=form.description.data,
            service_type=form.service_type.data,
            price=price,
            user=User.query.filter_by(id=g.user.id).first_or_404(),
            cover_destination=( "https://lake-uni.s3.ap-northeast-2.amazonaws.com/lakeuniversity/pictures/"
                    + app.config["IMAGE_DEPLOY_FOLDER_LOCATION"]
                    + "/"
                    + folder_unique_str
                    + "/"
                    + filename)
        )
        db.session.add(student_transaction)
        db.session.commit()
        flash('Successfully added!')
        return redirect(url_for('student_transaction', page_num=1))
    return render_template('./student_templates/add_student_transaction.html', title="Add student transaction page", form=form)


@app.route("/student_transaction/<int:page_num>", methods=["GET", "POST"])
def student_transaction(page_num=1):
    student_transactions = StudentTransaction.query.paginate(per_page=10, page=page_num, error_out=True)
    print(student_transactions)
    return render_template('./student_templates/student_transaction.html', title="Student transaction page", student_transactions=student_transactions)


@app.route("/student_transaction/search", methods=["GET", "POST"])
def search_student_transaction():
    request_query = request.args.get('query')
    filter_query = request.args.get('filter')

    service_id = 0
    if filter_query == 'book renting':
        service_id = 1
    elif filter_query == 'tutorial services':
        service_id = 2
    
    if request_query == '' and filter_query == '':
        return redirect(url_for('student_transaction', page_num=1))
    
    if filter_query == '':
        search = "%{}%".format(request_query)
        student_transactions = StudentTransaction.query.filter(
                or_(
                    StudentTransaction.service_name.like(search),
                    StudentTransaction.contact_details.like(search),
                    StudentTransaction.description.like(search),
                    StudentTransaction.price.like(search),
                    #StudentTransaction.user_id.like(search),
        )).all()
    else:
        search = "%{}%".format(request_query)
        student_transactions = StudentTransaction.query.filter(
                or_(
                    StudentTransaction.service_name.like(search),
                    StudentTransaction.contact_details.like(search),
                    StudentTransaction.description.like(search),
                    StudentTransaction.price.like(search),
                    #StudentTransaction.user_id.like(search),
                ),
                StudentTransaction.service_type == service_id
        ).all()
    print(student_transactions)
    return render_template('./student_templates/student_transaction_search.html', title="Student transaction page", student_transactions=student_transactions)


@app.route("/admin_dashboard", methods=["GET", "POST"])
@login_required
@admin_required
def admin_dashboard():
    return render_template('./admin_templates/admin_dashboard.html', title="Admin Dashboard page")

@app.route("/student_management/<int:page_num>", methods=["GET", "POST"])
@login_required
@admin_required
def student_management(page_num=1):
    students = User.query.filter_by(access_level=0).paginate(per_page=10, page=page_num, error_out=True)
    return render_template('./admin_templates/student_management.html', title="Student Management - Admin Dashboard page", students=students)

@app.route("/student_management/search/", methods=["GET", "POST"])
@login_required
@admin_required
def student_management_search():
    request_query = request.args.get('query')
    
    if request_query == '':
        return redirect(url_for('student_management', page_num=1))
    
    search = "%{}%".format(request_query)
    students = User.query.filter(
            or_(
                User.firstname.like(search),
                User.username.like(search),
                User.email.like(search),
                User.firstname.like(search),
                User.lastname.like(search),
            ),
            User.access_level==0
        ).all()
    
    return render_template('./admin_templates/student_management_search.html', title="Student Management - Admin Dashboard page", students=students)

@app.route("/landing_page_management", methods=["GET", "POST"])
@login_required
@admin_required
def landing_page_management():
    form = LandingPageEditForm()

    website_data = WebsiteData.query.first()
    
    if form.validate_on_submit():
        new_data = json.loads(website_data.data)

        if form.about_ece.data:
            new_data['about_ece'] = form.about_ece.data
        if form.vision_mission.data:
            new_data['vision_mission'] = form.vision_mission.data

        website_data.data = json.dumps(new_data)

        db.session.add(website_data)
        db.session.commit()
        flash('Successfully saved!')
        return redirect(url_for('landing_page_management'))

    if website_data == None:
        website_data = {
            'about_ece' : '',
            'vision_mission' : '',
        }
    website_data = json.loads(website_data.data)

    return render_template('./admin_templates/landing_page_management.html', title="Landing Page Management - Admin Dashboard page", form=form, about_ece=website_data['about_ece'], vision_mission=website_data['vision_mission'])

@app.route("/admin/edit_user_data/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.filter_by(id=user_id).first_or_404()
    form = EditUserForm(original_username=user.username, original_email=user.email, original_id=user.id)

    if form.validate_on_submit():
        if form.username.data:
            user.username = form.username.data
        if form.email.data and user.email != form.email.data:
            user.email = form.email.data
        if form.firstname.data:
            user.firstname = form.firstname.data
        if form.lastname.data:
            user.lastname = form.lastname.data
        if form.contact.data:
            user.contact = form.contact.data
        if form.address.data:
            user.address = form.address.data
        if form.sex.data:
            user.sex = form.sex.data
        if form.access_level.data:
            user.access_level = form.access_level.data
        if form.password.data:
            user.set_password(form.password.data)
            
        db.session.commit()
        flash('Successfully saved!')
        return redirect(url_for('student_management', page_num=1))

    return render_template('./admin_templates/admin_edit_user.html', title="Edit user- Admin Dashboard page", form=form, user=user)


@app.route('/feedback_form', methods=["GET", "POST"])
def add_feedback():
    form = AddFeedbackForm()

    if form.validate_on_submit():
        feedback = Feedback(
            name=form.name.data, 
            email=form.email.data,
            details=form.details.data,
        )
        db.session.add(feedback)
        db.session.commit()

        flash('Successfully sent feedback!')
        return redirect(url_for('index'))

    return render_template('./public_templates/feedback_form.html', title="Feedback form", form=form)


@app.route('/feedback_list', methods=["GET", "POST"])
@login_required
@admin_required
def feedback_list():
    feedbacks = Feedback.query.all()
    return render_template('./admin_templates/feedback_list.html', title="Feedback form", feedbacks=feedbacks)

@app.route('/feedback/delete/<int:feedback_id>', methods=["GET", "POST"])
@login_required
@admin_required
def delete_feedback(feedback_id):
    feedback = Feedback.query.filter_by(id=feedback_id).first_or_404()
    db.session.delete(feedback)
    db.session.commit()
    return redirect(url_for('feedback_list'))



@app.route('/get_shortest_path', methods=["GET", "POST"])
def get_shortest_path():
    start_query = str(request.args.get('start'))
    goal_query = str(request.args.get('goal'))
    
    graph =  {
    '1': { '2': 100, '5': 100, '4': 200},
    '2': { '3': 100, '1': 50},
    '3': { '2': 100, '6': 25},
    '4': { '6': 25, '5': 100, '1': 200 },
    '5': { '4': 100, '1': 100},
    '6': { '3': 25, '4': 25},
    }

    dijkstra = Dijkstra()
    return jsonify(dijkstra.get_shortest_path(graph, start_query, goal_query))

