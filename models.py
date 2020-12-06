from app import db

class Performer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(200),nullable=False)
    name = db.Column(db.String(50), nullable=False)
    cost_per_hour = db.Column(db.Float, nullable=False)
    profile_pic_url = db.Column(db.String(100), nullable=True)
    birthday = db.Column(db.DateTime, nullable=False)
    score = db.Column(db.Float, nullable=False, default=0)
    search_city = db.Column(db.String(30), nullable=False)
    search_state = db.Column(db.String(30), nullable=False)
    # address = do we need this?
    fiscal_code = db.Column(db.String(20), nullable=False)
    money = db.Column(db.Float, nullable=False, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


class Consumer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password=db.Column(db.String(200),nullable=False)
    name = db.Column(db.String(50), nullable=False)
    profile_pic_url = db.Column(db.String(50), nullable=False)
    birthday = db.Column(db.DateTime, nullable=False)
    score = db.Column(db.Float, nullable=False, default=0)
    # address = do we need this?
    fiscal_code = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())