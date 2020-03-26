from flask import g
from app.models import User, StudentTransaction

def admin_required(f):
    def wrap(*args, **kwargs):
        if g.user.access_level == 1:
            return f(*args, **kwargs)
        else:
            return "Unauthorized Access"
    wrap.__name__ = f.__name__
    return wrap

def is_account_owner(f):
    def wrap(*args, **kwargs):
        user = User.query.filter_by(id=kwargs['user_id']).first_or_404()
        if g.user.id == user.id:
            return f(*args, **kwargs)
        else:
            return "Unauthorized Access"
    wrap.__name__ = f.__name__
    return wrap

def is_student_transaction_owner(f):
    def wrap(*args, **kwargs):
        student_transaction = StudentTransaction.query.filter_by(id=kwargs['student_transaction_id']).first_or_404()
        user = User.query.filter_by(id=kwargs['user_id']).first_or_404()
        if g.user.id == user.id and user.id == student_transaction.user_id:
            return f(*args, **kwargs)
        else:
            return "Unauthorized Access"
    wrap.__name__ = f.__name__
    return wrap