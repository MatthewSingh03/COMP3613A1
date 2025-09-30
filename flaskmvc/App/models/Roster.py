from App.database import db

class Roster(db.Model):
    __tablename__ = "rosters"
    shiftID = db.Column(db.Integer, db.ForeignKey('shifts.id'), primary_key=True)
    userID = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    shift = db.relationship("Shift", backref="roster")
    user = db.relationship("User", backref="rosters")

    def __init__(self, shiftID, userID):
        self.shiftID = shiftID
        self.userID = userID