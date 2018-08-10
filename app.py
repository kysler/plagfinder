from flask import Flask, url_for, render_template, request, redirect, session, send_from_directory, abort, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS
from functools import wraps
from plagscan import plagscan
from flask_admin import Admin, form
from flask_admin.form import rules
from sqlalchemy.event import listens_for
from flask_admin.contrib import sqla
from jinja2 import Markup
from flask_admin import Admin, form
from flask_admin.form import rules
from flask_admin.contrib import sqla
from flask_admin.base import MenuLink, Admin, BaseView, expose
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
import os.path as op

app = Flask ( __name__ )

file_path = op.join(op.dirname(__file__), 'files')
try:
    os.mkdir(file_path)
except OSError:
    pass
app.config['DATABASE_FILE'] = 'sample_db.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + app.config['DATABASE_FILE']
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
documents = UploadSet('documents', DOCUMENTS)
app.config['UPLOADED_DOCUMENTS_DEST'] = 'tmp/uploads'
configure_uploads(app, documents)
bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Create models
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(64))
    path = db.Column(db.Unicode(128))

    def __unicode__(self):
        return self.name

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Unicode(64))
    last_name = db.Column(db.Unicode(64))
    email = db.Column(db.Unicode(128), unique = True)
    phone = db.Column(db.Unicode(32))
    course = db.Column(db.Unicode(128))
    role = db.Column(db.Unicode(128))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=4, max=80)])

# Delete hooks for models, delete files if models are getting deleted
@listens_for(File, 'after_delete')
def del_file(mapper, connection, target):
    if target.path:
        try:
            os.remove(op.join(file_path, target.path))
        except OSError:
            # Don't care if was not deleted because it does not exist
            pass

@app.route ( '/login', methods=[ 'POST', 'GET' ] )
def login ( ):
    form = LoginForm (   )

    if form.validate_on_submit ( ):
        user = User.query.filter_by ( last_name=form.username.data ).first ( )
        if user:
            if check_password_hash ( user.id, form.password.data ):
                login_user ( user, remember=form.remember.data )
                return redirect ( url_for ( 'index' ) )

        return redirect ( url_for ( 'login' ) )
        # return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template ( 'login.html', form = form )

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_id = generate_password_hash(form.password.data, method='sha256')
        new_user = User(last_name=form.username.data, email=form.email.data, id=hashed_id)
        db.session.add(new_user)
        db.session.commit()

        return redirect ( url_for ( 'login' ) )
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route ( '/logout', methods=[ 'POST', 'GET'] )
@login_required
def logout ( ):
    logout_user( )
    return redirect ( url_for ( 'login' ) )

@app.route ( '/', methods=[ 'POST', 'GET' ] )
def startpage ( ):
    return redirect ( url_for ( 'login' ) )

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
        #output = plagscan('tmp/uploads/' + filename)
        #return render_template('output.html', output = output)
        return render_template ('index.html')
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
    column_searchable_list = ('id', 'first_name', 'last_name', 'email', 'phone', 'course', 'role')
    column_display_pk = True
    form_columns = ('id', 'first_name', 'last_name', 'email', 'phone', 'course', 'role')
    form_choices = {'course': [ ('Instructor', 'Instructor'), ('BSCS-SD', 'BSCS-SD'), ('BSCS-MGD', 'BSCS-MGD'), ('BSIT-SM', 'BSIT-SM'),
                                ('BSIT-CNS', 'BSIT-CNS')],
                    'role':[ ('Student', 'Student'), ('Admin', 'Admin'), ('Instructor', 'Instructor') ]}

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

@app.route( '/accounts/', methods=[ 'POST', 'GET' ] )
def accounts():
    return render_template('account.html')

if __name__ == "__main__":
    app_dir = op.realpath ( os.path.dirname ( __file__ ) )
    app.run(debug = True)
