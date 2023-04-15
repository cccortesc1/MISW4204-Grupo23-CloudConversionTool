from flask import Flask

def create_app(config_name):
    app = Flask(__name__)
    db_url = "postgresql://postgres:postgres@localhost:5432/converter"
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url #'sqlite:///converter.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.config['JWT_SECRET_KEY'] = 'platipus'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    
    return app