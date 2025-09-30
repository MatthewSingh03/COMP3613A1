from App.database import db
from datetime import date

class Shift(db.Model):
    __tablename__ = "shifts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    changeRequest = db.Column(db.String(200))
    weekStart = db.Column(db.Date, nullable=False)
    weekEnd = db.Column(db.Date, nullable=False)
    user = db.relationship("User", backref="shifts")

    def __init__(self, user_id, weekStart, weekEnd, changeRequest=None):
        self.user_id = user_id
        self.weekStart = weekStart
        self.weekEnd = weekEnd
        self.changeRequest = changeRequest
