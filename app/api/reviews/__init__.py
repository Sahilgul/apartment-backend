# app/api/reviews/__init__.py
from flask import Blueprint

bp = Blueprint('reviews', __name__)

from app.api.reviews import routes