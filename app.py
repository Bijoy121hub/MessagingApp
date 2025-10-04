from flask import Flask, render_template, redirect, url_for, session, request
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, send
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from google_auth_oauthlib.flow import Flow
import os
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)
socketio = SocketIO(app)

login_manager = LoginManager()
login_manager.init_app(app)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # for development

GOOGLE_CLIENT_ID = "YOUR_GOOGLE_CLIENT_ID"
GOOGLE_CLIENT_SECRET = "YOUR_GOOGLE_CLIENT_SECRET"
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    return render_template('login.html')


@app.route('/login')
def login():
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'openid'],
        redirect_uri=url_for('callback', _external=True)
    )
    auth_url, _ = flow.authorization_url(prompt='consent')
    session['flow'] = flow
    return redirect(auth_url)


@app.route('/callback')
def callback():
    flow = Flow.from_client_secrets_file(
        'client_secret.json',
        scopes=['https://www.googleapis.com/auth/userinfo.email', 'openid'],
        redirect_uri=url_for('callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    from googleapiclient.discovery import build
    service = build('oauth2', 'v2', credentials=credentials)
    info = service.userinfo().get().execute()
    email = info['email']

    user = User.query.filter_by(email=email).first()
    if not user:
        user = User(email=email)
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('chat'))


@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=current_user.email)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@socketio.on('message')
def handleMessage(msg):
    send(f"{current_user.email}: {msg}", broadcast=True)


if __name__ == '__main__':
    db.create_all()
    socketio.run(app, debug=True)
