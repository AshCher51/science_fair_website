from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import secrets

DB_HOST = "private-db-postgresql-nyc1-73442-do-user-12414162-0.b.db.ondigitalocean.com"
DB_PORT = 25060
DB_NAME = "defaultdb"
DB_USERNAME = "doadmin"
DB_PASSWORD = "AVNS_UrdjZGrQYJ53f8mc3u3"

db = SQLAlchemy()
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = secrets.token_hex(16)
    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?sslmode=require"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    from models import Users
    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(int(user_id))

    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
