from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager, login_manager
from flask_mail import Mail, Message
from os import environ

db = SQLAlchemy()
mail_address = 'xandeeservices@gmail.com'
error_msg = "<h1 align='center'>404 not found</h1>"
db_url = "sqlite:///database.db"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8c4ef5b2a1ec103756163ab0494dffc2'
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = mail_address
app.config['MAIL_PASSWORD'] = '(ENTERpassword1234)'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
mail = Mail(app)

def create_app():
    db.init_app(app)

    from .views import views
    from .auth import auth
    
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User
    create_db(app)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app
def create_db(app):
    db.create_all(app=app)

app = create_app()

if __name__ == "__main__":
    app.run()
