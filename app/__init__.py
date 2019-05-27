import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask import Flask, request, redirect
from config import Config
from werkzeug.contrib.fixers import ProxyFix
from flask_admin import Admin
from flask_mail import Mail
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore, current_user
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
from geopy.geocoders import Nominatim


app = Flask(__name__)
db = SQLAlchemy()
migrate = Migrate()
security = Security()
admin = Admin()
mail = Mail()
geolocator = Nominatim(user_agent='Assignably')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.config.from_object(config_class)
    app.elasticsearch = Elasticsearch([app.config['ELASTICSEARCH_URL']]) \
        if app.config['ELASTICSEARCH_URL'] else None

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    from app.api import bp as api_bp
    from app.deals.views import bp as deals_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(deals_bp)

    from app.auth.models import User, Role
    from app.deals.models import Address, Deal, DealContact, DealContactRole, Contact

    user_datastore = SQLAlchemyUserDatastore(db, User, Role)
    security.init_app(app=app, datastore=user_datastore)

    from app.admin import create_admin
    admin = create_admin(app, db)

    if not app.debug and not app.testing:
        if app.config['LOG_TO_STDOUT']:
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(logging.INFO)
            app.logger.addHandler(stream_handler)
        else:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler('logs/assignably.log',
                                               maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s '
                '[in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)
            app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Assignably startup')

    return app
