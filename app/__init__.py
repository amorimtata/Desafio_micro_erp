# Este arquivo é necessário para que o Python reconheça o diretório como um pacote 

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.controllers.produto_controller import produto_bp
    from app.controllers.estoque_controller import estoque_bp
    from app.controllers.nfe_controller import nfe_bp
    from app.controllers.main_controller import main_bp

    app.register_blueprint(produto_bp)
    app.register_blueprint(estoque_bp)
    app.register_blueprint(nfe_bp)
    app.register_blueprint(main_bp)

    return app

from app import models 