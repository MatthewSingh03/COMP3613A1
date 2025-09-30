from App.database import db

class AttendanceRecord(db.Model):
    __tablename__ = "attendance_records"
    attendanceID = db.Column(db.Integer, primary_key=True)
    shiftID = db.Column(db.Integer, db.ForeignKey('shifts.id'), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    timeIn = db.Column(db.DateTime, nullable=False)
    timeout = db.Column(db.DateTime)