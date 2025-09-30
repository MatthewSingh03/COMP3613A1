from App.database import db
from App.models.user import User

class Staff(User):
    __tablename__ = "staff"
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), primary_key=True)
    role = db.Column(db.String(100), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'staff'
    }

    def __init__(self, name, email, password):
        super().__init__(name=name, email=email, password=password, type="staff")
        self.role = "staff"

    def requestShiftChange(self, session, shift_id, request_text):
        """
        Request a shift change by updating the changeRequest field in Shift.
        :param session: SQLAlchemy session
        :param shift_id: ID of the shift to request change for
        :param request_text: The change request details
        """
        from App.models.Shift import Shift
        shift = session.query(Shift).filter_by(id=shift_id, user_id=self.user_id).first()
        if shift:
            shift.changeRequest = request_text
            session.commit()
            return shift
        return None




