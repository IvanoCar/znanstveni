from flask import Flask
from flask_pymongo import PyMongo
from zapp.essentials import Essentials
from flask_session import Session
from datetime import timedelta

app = Flask(__name__)
essents = Essentials()

app.config['MONGO_DBNAME'] = 'DB NAME'
app.config['MONGO_URI'] = 'MONGO URI'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)

app.secret_key = 'KEY'
mongo = PyMongo(app)
Session(app)

from zapp.modules.user.routes import userapp
from zapp.modules.moderator.routes import moderatorapp
from zapp.modules.admin.routes import adminapp
from zapp.modules.mainapp.routes import mainapp

app.register_blueprint(userapp)
app.register_blueprint(moderatorapp)
app.register_blueprint(adminapp)
app.register_blueprint(mainapp)

if __name__ == '__main__':
    app.run()
