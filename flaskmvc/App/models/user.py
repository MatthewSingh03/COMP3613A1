from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class User(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    type = db.Column(db.String(50))  # Single type column for polymorphic identity

    __mapper_args__ = {
        'polymorphic_identity': 'user',
        'polymorphic_on': type
    }

    def __init__(self, name, email, password, type="user"):
        self.name = name
        self.email = email
        self.set_password(password)
        self.type = type

    def get_json(self):
        return{
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def clockIn(self, session, shift_id, timein):
        """
        Clock in the user for a shift.
        :param session: SQLAlchemy session
        :param shift_id: ID of the shift
        :param timein: datetime/date object for clock-in time
        """
        from App.models.attendance_record import AttendanceRecord
        attendance = AttendanceRecord(
            shiftID=shift_id,
            userID=self.user_id,
            timein=timein,
            timeout=None
        )
        session.add(attendance)
        session.commit()
        return attendance

    def clockOut(self, session, shift_id, timeout):
        """
        Clock out the user for a shift.
        :param session: SQLAlchemy session
        :param shift_id: ID of the shift
        :param timeout: datetime/date object for clock-out time
        """
        from App.models.attendance_record import AttendanceRecord
        attendance = session.query(AttendanceRecord).filter_by(
            shiftID=shift_id,
            userID=self.user_id,
            timeout=None
        ).first()
        if attendance:
            attendance.timeout = timeout
            session.commit()
        return attendance

    def viewRoster(self, session):
        """
        View all roster entries for this user.
        :param session: SQLAlchemy session
        :return: List of Roster objects
        """
        from App.models.Shift import Shift
        from App.models.Roster import Roster
        # Find all shifts for this user
        user_shifts = session.query(Shift).filter_by(user_id=self.user_id).all()
        shift_ids = [shift.id for shift in user_shifts]
        # Find all roster entries for these shifts
        rosters = session.query(Roster).filter(Roster.shiftID.in_(shift_ids)).all()
        return rosters



