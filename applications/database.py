from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

from applications import app
from applications.config import settings





# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:8thNov2022@localhost/trading_journal'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{settings.database_username}:{settings.database_password}@{settings.database_hostname}/{settings.database_name}'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view="login_page"
login_manager.login_message_category="info"

app.app_context().push()
db.create_all()
