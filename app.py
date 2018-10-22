from flask import Flask, url_for, render_template, request, redirect, session, send_from_directory, abort, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS
from functools import wraps
from googleSearch import googleSearch, searchText
from flask_admin.form import rules
from sqlalchemy.event import listens_for
from jinja2 import Markup
from flask_admin import Admin, form
from flask_admin.form import rules
from flask_admin.contrib import sqla
from flask_admin.base import MenuLink, Admin, BaseView, expose, AdminIndexView
from flask_admin.contrib import fileadmin
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter, roles_required
from flask_user.forms import RegisterForm, EditUserProfileForm, LoginForm
from flask_mail import Mail
from flask_user.email_adapters import SendgridEmailAdapter
from flask_ckeditor import CKEditor, CKEditorField
from bs4 import BeautifulSoup
from flask_migrate import Migrate
import os
import os.path as op
import mammoth
import datetime

file_path = op.join(op.dirname(__file__), 'files')

class configClass(object):
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:////flask_app.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SECRET_KEY = 'aynakoputanginasukungsukonaakosapunyetangthesisnato'

    documents = UploadSet('documents', DOCUMENTS)
    UPLOADED_DOCUMENTS_DEST = 'tmp/uploads'

    CSRF_ENABLED = True
    USER_ENABLE_USERNAME = True
    USER_ENABLE_EMAIL = True
    USER_EMAIL_SENDER_EMAIL = "shazodmzyt@gmail.com"
    USER_APP_NAME = 'Plagiarism Finder'
    USER_AFTER_REGISTER_ENDPOINT = 'index'
    USER_AFTER_LOGIN_ENDPOINT = 'index'
    USER_AFTER_LOGOUT_ENDPOINT = 'index'
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')

def create_app(config_class=configClass):
    # Create Flask App
    app = Flask(__name__)
    app.config.from_object(__name__ + '.configClass')
    app.config.from_pyfile('config.cfg')
    migrate = Migrate()
    db = SQLAlchemy(app)
    migrate.init_app(app, db)
    ckeditor = CKEditor(app)
    bootstrap = Bootstrap(app)
    documents = UploadSet('documents', DOCUMENTS)
    configure_uploads(app, documents)

    class User(db.Model, UserMixin):
        __tablename__ = "user"
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
        username = db.Column(db.String(255, collation='NOCASE'), nullable=False, unique=True)
        email = db.Column(db.String(255), unique=True)
        email_confirmed_at = db.Column(db.DateTime())
        password = db.Column(db.String(255), nullable=False, server_default='')
        roles = db.relationship('Role', secondary='user_roles')

    class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50), unique=True)

    # Define the UserRoles association table
    class UserRoles(db.Model):
        __tablename__ = 'user_roles'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


    class Results(db.Model):
        __tablename__ = "result"
        id = db.Column(db.Integer, primary_key=True)
        user = db.Column(db.Integer, db.ForeignKey('user.username'))
        html = db.Column(db.Unicode())
        links = db.Column(db.Unicode())
        docs = db.Column(db.Unicode())

    class Log(db.Model):
        __tablename__="logs"
        id = db.Column(db.Integer, primary_key=True)
        message = db.Column(db.Unicode())

    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User)
    mail = Mail(app)

    db.create_all()

    if not User.query.filter(User.email == 'admin@example.com').first():
        user = User(username = 'admin', email='admin@example.com', email_confirmed_at=datetime.datetime.utcnow(), password=user_manager.hash_password('Password1'))
        user.roles.append(Role(name='Admin'))
        db.session.add(user)
        db.session.commit()

    class PostForm(FlaskForm):
        title = StringField('Title', validators=[DataRequired()])
        body = CKEditorField('Body', validators=[DataRequired()])
        submit = SubmitField('Submit')

    @app.errorhandler(500)
    def handle_bad_request(e):
        flash('An error has occured, you are redirected back to the homepage.', 'error')
        return redirect(url_for('index'))

    @app.route ( '/logout', methods=[ 'POST', 'GET'] )
    @login_required
    def logout ( ):
        logout_user( )
        return redirect ( url_for ( 'index' ) )

    @app.route ('/', methods=['POST', 'GET'])
    def index():
        return redirect ( url_for ( 'user.login' ) )

    @app.route ( '/homepage', methods=[ 'POST', 'GET' ] )
    @login_required
    def upload():
        form = PostForm()
        if request.method == 'POST' and 'files' in request.files:
            filename = documents.save ( request.files[ 'files' ] )
            output = mammoth.convert_to_html('tmp/uploads/' + filename)
            html = output.value
            return render_template('member.html', form=form, content=html)
        else:
            return render_template ( 'member.html', form=form, content='Type or upload.')

    @app.route('/admin')
    def adminpage():
        return redirect(url_for('admin.index'))

    @app.route('/scan', methods=[ 'POST', 'GET' ])
    @login_required
    def testpage():
        form = PostForm()
        if request.method == 'POST' and 'files' in request.files:
            filename = documents.save ( request.files[ 'files' ] )
            output = mammoth.convert_to_html('tmp/uploads/' + filename)
            html = output.value
            return render_template('scan.html', form=form, content=html)

        elif form.validate_on_submit():
            user_id = current_user.username
            html_data = form.body.data
            soup = BeautifulSoup(html_data)
            search = searchText(soup.get_text())
            query = Results(user=user_id, html=html_data, links=search)
            db.session.add(query)
            db.session.commit()
            return redirect(url_for('testpage'))

        else:
            return render_template ( 'scan.html', form=form, content='Type or upload.')

    @app.route('/scanner/<int:pathname>')
    @login_required
    def finalized(pathname):
        form = PostForm()
        if form.validate_on_submit():
            user_id = current_user.username
            html_data = form.body.data
            soup = BeautifulSoup(html_data)
            search = searchText(soup.get_text())
            query = Results(user=user_id, html=html_data, links=search)
            db.session.add(query)
            db.session.commit()
            return redirect(url_for('testpage'))
        else:
            content = Results.query.filter_by(id=pathname).first()
            links = content.links.split("[-]")
            return render_template('scan.html', form = form, content = content.html, links = links)

    @app.route ( '/list')
    @login_required
    def listahan():
        return render_template('lists.html', results = Results.query.filter_by(user = current_user.username).all())

    # Create admin
    class UserView(sqla.ModelView):
        column_searchable_list = ('id', 'username', 'email')
        column_display_pk = True
        form_choices = {'course': [ ('Instructor', 'Instructor'), ('BSCS-SD', 'BSCS-SD'), ('BSCS-MGD', 'BSCS-MGD'), ('BSIT-SM', 'BSIT-SM'),
                                        ('BSIT-CNS', 'BSIT-CNS')]}

    class MyHomeView(AdminIndexView):
        @expose('/')
        @roles_required('Admin')
        def adminIndex(self):
            return self.render('admin/index.html')

    # Add views
    admin = Admin ( app, name = 'PlagFind Admin', index_view=MyHomeView(name="Plagfinder"), endpoint="admin", template_mode='bootstrap3'  )
    admin.add_views (UserView( User, db.session, name='User'), fileadmin.FileAdmin(file_path, name='Files'))
    admin.add_link ( MenuLink( name='Scan', url= '../../homepage' ))
    admin.add_link ( MenuLink( name='Logout', url= '../../logout', endpoint="Logout" ) )

    return app

if __name__ == "__main__":
    app = create_app('app')
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
#Lol
