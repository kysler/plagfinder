from flask import Flask, url_for, render_template, request, redirect, session, send_from_directory, abort, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS
from functools import wraps
from googleSearch import googleSearch
from flask_admin.form import rules
from sqlalchemy.event import listens_for
from jinja2 import Markup
from flask_admin import Admin, form
from flask_admin.form import rules
from flask_admin.contrib import sqla
from flask_admin.base import MenuLink, Admin, BaseView, expose
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, DataRequired
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask import Flask 
from flask_sqlalchemy import SQLAlchemy 
from flask_user import login_required, UserManager, UserMixin, SQLAlchemyAdapter, roles_required
from flask_user.forms import RegisterForm, EditUserProfileForm, LoginForm
from flask_mail import Mail
import os
import os.path as op

# Create Flask App
app = Flask ( __name__ )

file_path = op.join(op.dirname(__file__), 'files')
try:
    os.mkdir(file_path)
except OSError:
    pass

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:////flask_app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'

documents = UploadSet('documents', DOCUMENTS)
app.config['UPLOADED_DOCUMENTS_DEST'] = 'tmp/uploads'
configure_uploads(app, documents)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['CSRF_ENABLED'] = True 
app.config['USER_ENABLE_USERNAME'] = True
app.config['USER_ENABLE_EMAIL'] = False
app.config['USER_EMAIL_SENDER_EMAIL'] = "shazodmzyt@gmail.com"
app.config['USER_APP_NAME'] = 'Flask-User Demo'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'index'
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)
mail = Mail(app)

# Create models
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))
    def __unicode__(self):
        return self.name

class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    username = db.Column(db.String(255), nullable=False, unique=True)
    email = db.Column(db.String(255), unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')

	# User information
    first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')
    school = db.Column(db.String(100), nullable=False, server_default='')
    course = db.Column(db.String(100), nullable=False, server_default='')
    roles = db.Column(db.String(100), server_default='Student')

    # Setup Flask-User and specify the User data-model
user_manager = UserManager(app, db, User)

# Delete hooks for models, delete files if models are getting deleted
@listens_for(File, 'after_delete')
def del_file(mapper, connection, target):
    if target.path:
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            # Don't care if was not deleted because it does not exist
            pass

@app.route ( '/logout', methods=[ 'POST', 'GET'] )
@login_required
def logout ( ):
    logout_user( )
    return redirect ( url_for ( 'index' ) )

@app.route ( '/', methods=[ 'POST', 'GET' ] )
def startpage ( ):
    return redirect ( url_for ( 'index' ) )

@app.route ('/index', methods=['POST', 'GET'])
@login_required
def index():
    if request.method == 'GET':
        return render_template ( 'index.html' )

@app.route ( '/upload', methods=[ 'POST', 'GET' ] )
@login_required
def upload():
    if request.method == 'POST' and 'files' in request.files:
        filename = documents.save ( request.files[ 'files' ] )
        output = googleSearch('tmp/uploads/' + filename)
        return render_template('output.html', output = output)
    else:
        return render_template ( 'index.html' )

@app.route('/results/')
def return_files_tut():
	return send_file('tmp\\result.log')

# Create admin
admin = Admin ( app, 'PlagVoid Admin', endpoint="admin", template_mode='bootstrap3'  )
instructor = Admin( app, 'PlagVoid Instructor', url='/instructor', endpoint="instructor", template_mode='bootstrap3' )

# Administrative views
class FileView(sqla.ModelView):
    column_display_pk = True
    column_searchable_list = ('id','name','path')
    form_columns = ('id','name','path')
    form_overrides = {
        'path': form.FileUploadField
    }

    form_args = {
        'path': {
            'label': 'File',
            'base_path': file_path,
            'allow_overwrite': False
        }
    }

class UserView(sqla.ModelView):
    column_searchable_list = ('id', 'first_name', 'last_name', 'email', 'course', 'roles')
    column_display_pk = True
    form_columns = ('first_name', 'last_name', 'email', 'course', 'roles')
    form_choices = {'course': [ ('Instructor', 'Instructor'), ('BSCS-SD', 'BSCS-SD'), ('BSCS-MGD', 'BSCS-MGD'), ('BSIT-SM', 'BSIT-SM'),
                                ('BSIT-CNS', 'BSIT-CNS')],
                    'roles':[ ('Student', 'Student'), ('Admin', 'Admin'), ('Instructor', 'Instructor') ]}

class FilesView(sqla.ModelView):
    column_display_pk = True
    can_delete = False
    # Pass additional parameters to 'path' to FileUploadField constructor
    form_columns = ('id', 'name', 'path')
    column_searchable_list = ('id','name','path')
    form_overrides = {
        'path': form.FileUploadField
    }
    form_args = {
        'path': {
            'label': 'File',
            'base_path': file_path,
            'allow_overwrite': False
        }
    }

# Add views
admin.add_view ( FileView ( File, db.session, endpoint="File" ) )
admin.add_view ( UserView ( User, db.session, name='User', endpoint="Accounts" ) )
admin.add_link ( MenuLink( name='Scan', url= '../../upload', endpoint="Back to Index" ) )
admin.add_link ( MenuLink( name='Logout', url= '../../logout', endpoint="Logout" ) )
instructor.add_view ( FilesView ( File, db.session, endpoint="Files" ) )
instructor.add_link ( MenuLink( name='Scan', url= '../../upload', endpoint="Back to Index" ) )
instructor.add_link ( MenuLink( name='Logout', url= '../../logout', endpoint="Signout" ) )

if __name__ == "__main__":
	db.create_all()
	app_dir = op.realpath ( os.path.dirname ( __file__ ) )
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
