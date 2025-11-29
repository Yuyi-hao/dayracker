import functools
from flask import Blueprint 
from werkzeug.security import check_password_hash, generate_password_hash

from core.db import get_db

auth_bp = Blueprint('auth', __name__, url_prefix="/auth")

