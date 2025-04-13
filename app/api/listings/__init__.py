# app/api/listings/__init__.py
from flask import Blueprint

bp = Blueprint('listings', __name__)

from app.api.listings import routes