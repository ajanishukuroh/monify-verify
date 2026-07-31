from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user


def merchant_required(f):
    """Decorator to require authenticated merchant for a route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
