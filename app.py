from flask import Flask, url_for, render_template, request, redirect, session, send_from_directory, abort, send_file, flash
from flask_sqlalchemy import SQLAlchemy
from flask_uploads import UploadSet, configure_uploads, DOCUMENTS
from functools import wraps
from googleSearch import searchText
from flask_admin.form import rules
from sqlalchemy.event import listens_for
from jinja2 import Markup
from flask_admin import Admin, form
from flask_admin.form import rules, SecureForm
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
from plagscan import scan
from redis import Redis
from rq import Queue
from rq.job import Job
from worker import conn
import os
import os.path as op
import mammoth
import datetime

file_path = op.join(op.dirname(__file__), 'files')
basedir = os.path.abspath(os.path.dirname(__file__))

class configClass(object):
    DATABASE_URL = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SECRET_KEY = 'aynakoputanginasukungsukonaakosapunyetangthesisnato'

    documents = UploadSet('documents', DOCUMENTS)
    UPLOADED_DOCUMENTS_DEST = 'tmp/uploads'
    QUEUES = ['default']
    CSRF_ENABLED = True
    USER_ENABLE_USERNAME = True
    USER_ENABLE_EMAIL = True
    USER_EMAIL_SENDER_EMAIL = "shazodmzyt@gmail.com"
    USER_APP_NAME = 'Plagiarism Finder'
    USER_AFTER_REGISTER_ENDPOINT = 'index'
    USER_AFTER_LOGIN_ENDPOINT = 'index'
    USER_AFTER_LOGOUT_ENDPOINT = 'index'
    SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')
    include_schemas = True
    CKEDITOR_HEIGHT = 500

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
        user = db.Column(db.Unicode(), db.ForeignKey('user.username'))
        html = db.Column(db.Unicode(), server_default='')
        links = db.Column(db.Unicode(), server_default='')
        docname = db.Column(db.Unicode(), server_default='')
        copiedlines = db.Column(db.Unicode(), server_default='')
        percentage = db.Column(db.Unicode(), server_default='0')

    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User)
    user_manager.email_adapter = SendgridEmailAdapter(app)

    db.create_all()

    class PostForm(FlaskForm):
        body = CKEditorField('Body', validators=[DataRequired()])
        submit = SubmitField('Submit')
        
    class TrialForm(FlaskForm):
        body = StringField('Body', validators=[DataRequired()])
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
    
    @app.route ('/terms', methods=['POST', 'GET'])
    def terms():
        return render_template('termsandconditions.html')

    @app.route ('/', methods=['POST', 'GET'])
    def index():
        return redirect ( url_for ( 'user.login' ) )

    @app.route ( '/homepage', methods=[ 'POST', 'GET' ] )
    @login_required
    def upload():
        return render_template ('base.html', current=current_user.roles)

    @app.route('/admin')
    def adminpage():
        return redirect(url_for('admin.index'))

    @app.route('/scan', methods=[ 'POST', 'GET' ])
    @roles_required('premium')
    def testpage():
        form = PostForm()
        if request.method == 'POST' and 'files' in request.files:
            filename = documents.save ( request.files[ 'files' ] )
            output = mammoth.convert_to_html('tmp/uploads/' + filename)
            html = output.value
            links = []
            docname = []
            copiedlines = []
            per = 0
            return render_template('scan.html', form = form, content = html, links = links, docname = docname, copiedlines = copiedlines, per = per)

        elif form.validate_on_submit():
            user_id = current_user.username
            html_data = form.body.data
            soup = BeautifulSoup(html_data, "html.parser")
            text = soup.get_text()
            search = searchText(text)
            doc_texts=scan(text)
            docname = '[-]'.join(doc_texts[0])
            copiedlines = '[-]'.join(doc_texts[1])
            percentage = doc_texts[2]
            query = Results(user=user_id, html=html_data, links=search, docname=docname, copiedlines=copiedlines, percentage=percentage)
            db.session.add(query)
            db.session.commit()
            return redirect(url_for('listahan'))
        
        else:
            links = []
            docname = []
            copiedlines = []
            return render_template('scan.html', form = form, content = 'Type something.', links = links, docname = docname, copiedlines = copiedlines)

    @app.route('/trial', methods=[ 'POST', 'GET' ])
    @login_required
    def freepage():
        form = TrialForm()
        if form.validate_on_submit():
            data = form.body.data
            search = searchText(data)
            return render_template('trialresult.html', links = search.split("[-]"), form = form)
        else:
            return render_template('freeuser.html', form = form)
    
    @app.route('/scanner/<int:pathname>')
    @login_required
    def finalized(pathname):
        form = PostForm()
        if form.validate_on_submit():
            user_id = current_user.username
            html_data = form.body.data
            soup = BeautifulSoup(html_data, "html.parser")
            text = soup.get_text()
            search = searchText(text)
            doc_texts=scan(text)
            docname = '[-]'.join(doc_texts[0])
            copiedlines = '[-]'.join(doc_texts[1])
            percentage = doc_texts[2]
            query = Results(user=user_id, html=html_data, links=search, docname=docname, copiedlines=copiedlines, percentage=percentage)
            db.session.add(query)
            db.session.commit()
            return redirect(url_for('listahan'))
        else:
            content = Results.query.filter_by(id=pathname).first()
            links = content.links.split("[-]")
            docname = content.docname.split("[-]")
            copiedlines = content.copiedlines.split("[-]")
            per = content.percentage
            return render_template('finished.html', form = form, content = content.html, links = links, docname = docname, copiedlines = copiedlines, per=per, results = Results.query.filter_by(user = current_user.username).all())
    
    @app.route ( '/list')
    @login_required
    def listahan():
        return render_template('lists.html', results = Results.query.filter_by(user = current_user.username).all())

    class UserView(sqla.ModelView):
        column_searchable_list = ('id', 'username', 'email')
        column_display_pk = True
        can_edit = False
        can_create = False
        can_delete = False
        
    class RoleView(sqla.ModelView):
        column_display_pk = True
        column_hide_backrefs = False
        column_list = ('user_id', 'role_id')

    class MyHomeView(AdminIndexView):
        @expose('/')
        @roles_required('Admin')
        def adminIndex(self):
            return self.render('admin/index.html')

    # Add views
    admin = Admin ( app, name = 'PlagFind Admin', index_view=MyHomeView(name="Plagfinder"), endpoint="admin", template_mode='bootstrap3'  )
    admin.add_views (UserView( User, db.session, name='User'), fileadmin.FileAdmin(file_path, name='Files'), RoleView(UserRoles, db.session, name='Roles'))
    admin.add_link ( MenuLink( name='Scan', url= '../../homepage' ))
    admin.add_link ( MenuLink( name='Logout', url= '../../logout', endpoint="Logout" ) )

    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

