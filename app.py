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
from flask_admin.base import MenuLink, Admin, BaseView, expose
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
import os
import os.path as op
import mammoth

# Create Flask App
app = Flask ( __name__ )

file_path = op.join(op.dirname(__file__), 'files')
try:
    os.mkdir(file_path)
except OSError:
    pass

DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:////flask_app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SECRET_KEY'] = 'aynakoputanginasukungsukonaakosapunyetangthesisnato'

documents = UploadSet('documents', DOCUMENTS)
app.config['UPLOADED_DOCUMENTS_DEST'] = 'tmp/uploads'
configure_uploads(app, documents)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

app.config['CSRF_ENABLED'] = True 
app.config['USER_ENABLE_USERNAME'] = True
app.config['USER_ENABLE_EMAIL'] = True
app.config['USER_EMAIL_SENDER_EMAIL'] = "shazodmzyt@gmail.com"
app.config['USER_APP_NAME'] = 'Plagiarism Finder'
app.config['USER_AFTER_REGISTER_ENDPOINT'] = 'index'
app.config['USER_AFTER_LOGIN_ENDPOINT'] = 'index'
app.config['USER_AFTER_LOGOUT_ENDPOINT'] = 'index'
app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY')
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)
ckeditor = CKEditor(app)

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
    roles = db.Column(db.String(100), server_default='Student')

    def __init__(self, roles):
        self.roles = roles

    def get_roles(self):
        return self.roles

'''
	first_name = db.Column(db.String(100), nullable=False, server_default='')
    last_name = db.Column(db.String(100), nullable=False, server_default='')
    school = db.Column(db.String(100), nullable=False, server_default='')
    course = db.Column(db.String(100), nullable=False, server_default='')
'''


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
user_manager.email_adapter = SendgridEmailAdapter(app)
admin = Admin ( app, 'PlagFind Admin', url='/admin', endpoint="admin", template_mode='bootstrap3'  )

def login_required(role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            if ((current_user.roles != role) and (role != "ANY")):
                return current_app.login_manager.unauthorized()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

# Delete hooks for models, delete files if models are getting deleted
@listens_for(File, 'after_delete')
def del_file(mapper, connection, target):
    if target.path:
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            # Don't care if was not deleted because it does not exist
            pass

class PostForm(FlaskForm):
    body = CKEditorField('Body', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.errorhandler(500)
def handle_bad_request(e):
    flash('An error has occured, you are redirected back to the homepage.', 'error')
    return redirect(url_for('index'))

@app.route ( '/logout', methods=[ 'POST', 'GET'] )
@login_required(role="ANY")
def logout ( ):
    logout_user( )
    return redirect ( url_for ( 'index' ) )

@app.route ('/', methods=['POST', 'GET'])
def index():
    return redirect ( url_for ( 'user.login' ) )

@app.route ( '/homepage', methods=[ 'POST', 'GET' ] )
@login_required(role="ANY")
def upload():
    form = PostForm()
    if request.method == 'POST' and 'files' in request.files:
        filename = documents.save ( request.files[ 'files' ] )
        output = mammoth.convert_to_html('tmp/uploads/' + filename)
        html = output.value
        return render_template('member.html', form=form, content=html)
    else:
        return render_template ( 'member.html', form=form, content='Type or upload.')
    
@app.route('/results')
def return_files_tut():
	return send_file('tmp\\results.log')

@app.route('/admin')
@login_required(role="Admin")
def adminpage():
	return render_template('admin/index.html')

@app.route('/scan', methods=[ 'POST', 'GET' ])
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
def finalized(pathname):
    form = PostForm()
    content = Results.query.filter_by(id=pathname).first()
    links = content.links.split("[-]")
    return render_template('scan.html', form = form, content = content.html, links = links)

@app.route ( '/list')
def listahan():
    return render_template('lists.html', results = Results.query.filter_by(user = current_user.username).all())

# Create admin

class UserView(sqla.ModelView):
    column_searchable_list = ('id', 'username', 'email', 'roles')
    column_display_pk = True
    form_choices = {'course': [ ('Instructor', 'Instructor'), ('BSCS-SD', 'BSCS-SD'), ('BSCS-MGD', 'BSCS-MGD'), ('BSIT-SM', 'BSIT-SM'),
                                    ('BSIT-CNS', 'BSIT-CNS')],
                        'roles':[ ('Student', 'Student'), ('Admin', 'Admin')]}

# Add views
admin.add_view (fileadmin.FileAdmin(file_path, name='Files'))
admin.add_view ( UserView ( User, db.session, name='User', endpoint="Accounts" ) )
admin.add_link ( MenuLink( name='Scan', url= '../../homepage', endpoint="Back to Index" ) )
admin.add_link ( MenuLink( name='Logout', url= '../../logout', endpoint="Logout" ) )

if __name__ == "__main__":
	db.create_all()
	app_dir = op.realpath ( os.path.dirname ( __file__ ) )
	port = int(os.environ.get('PORT', 5000))
	app.run(host='0.0.0.0', port=port, debug=True)
