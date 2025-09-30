from App.database import db
from App.models.user import User

class Admin(User):
    __tablename__ = "admin"
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    role = db.Column(db.String(100), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'admin'
    }

    def __init__(self, name, email, password):
        super().__init__(name=name, email=email, password=password, type="admin")
        self.role = "admin"

    def scheduleShift(self, session, user_id, shiftList):
        """
        Schedule shifts for a user by creating Roster entries.
        :param session: SQLAlchemy session
        :param user_id: ID of the user to schedule
        :param shiftList: List of shift IDs to assign
        """
        from App.models.Roster import Roster
        for shift_id in shiftList:
            roster = Roster(shiftID=shift_id, userID=user_id)
            session.add(roster)
        session.commit()

    def viewWeeklyReport(self, session, week_start, week_end):
        """
        View all shifts scheduled within a given week.
        :param session: SQLAlchemy session
        :param week_start: Start date of the week (inclusive)
        :param week_end: End date of the week (inclusive)
        :return: List of Shift objects
        """
        from App.models.Shift import Shift
        shifts = session.query(Shift).filter(
            Shift.weekStart >= week_start,
            Shift.weekEnd <= week_end
        ).all()
        return shifts

    def approveRequest(self, session, user_id, shift_id):
        """
        Approve a shift change request.
        :param session: SQLAlchemy session
        :param user_id: ID of the user who made the request
        :param shift_id: ID of the shift
        :return: String indicating approval
        """
        from App.models.Shift import Shift
        shift = session.query(Shift).filter_by(id=shift_id, user_id=user_id).first()
        if shift and shift.changeRequest:
            shift.changeRequest = "APPROVED: " + shift.changeRequest
            session.commit()
            return f"Request for shift {shift_id} by user {user_id} approved."
        return f"No pending request found for shift {shift_id} by user {user_id}."

    def denyRequest(self, session, user_id, shift_id):
        """
        Deny a shift change request.
        :param session: SQLAlchemy session
        :param user_id: ID of the user who made the request
        :param shift_id: ID of the shift
        :return: String indicating denial
        """
        from App.models.Shift import Shift
        shift = session.query(Shift).filter_by(id=shift_id, user_id=user_id).first()
        if shift and shift.changeRequest:
            shift.changeRequest = "DENIED: " + shift.changeRequest
            session.commit()
            return f"Request for shift {shift_id} by user {user_id} denied."
        return f"No pending request found for shift {shift_id} by user {user_id}."