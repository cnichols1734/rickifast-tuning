from flask import abort
from app import db


def get_or_404(model, id):
    """
    Get an object by ID or return 404.
    Uses the new SQLAlchemy 2.0 syntax to avoid deprecation warnings.
    """
    obj = db.session.get(model, id)
    if obj is None:
        abort(404)
    return obj 