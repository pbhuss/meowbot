from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class AccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String)
    scope = db.Column(db.String)
    user_id = db.Column(db.String)
    team_name = db.Column(db.String)
    team_id = db.Column(db.String)
    bot_user_id = db.Column(db.String)
    bot_access_token = db.Column(db.String)


class Cat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    url = db.Column(db.String)
