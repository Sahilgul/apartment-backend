# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.api.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from app.api.listings import bp as listings_bp
    app.register_blueprint(listings_bp, url_prefix='/api/listings')
    
    from app.api.reviews import bp as reviews_bp
    app.register_blueprint(reviews_bp, url_prefix='/api/reviews')
    
    from app.api.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/api/users')
    
    from app.api.search import bp as search_bp
    app.register_blueprint(search_bp, url_prefix='/api/search')
    
    @app.route('/api/health')
    def health_check():
        return {"status": "healthy"}
    
    return app