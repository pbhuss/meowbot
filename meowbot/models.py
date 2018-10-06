from meowbot import db


class AccessToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    access_token = db.Column(db.String)
    scope = db.Column(db.String)
    user_id = db.Column(db.String)
    team_name = db.Column(db.String)
    team_id = db.Column(db.String)
    bot_user_id = db.Column(db.String)
    bot_access_token = db.Column(db.String)
