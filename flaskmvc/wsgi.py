import click, pytest, sys
from flask.cli import with_appcontext, AppGroup

from App.database import db, get_migrate
from App.models import User
from App.main import create_app
from App.controllers import ( create_user, get_all_users_json, get_all_users, initialize )
from App.models.staff import Staff
from App.models.admin import Admin


# This commands file allow you to create convenient CLI commands for testing controllers

app = create_app()
migrate = get_migrate(app)

# This command creates and initializes the database
@app.cli.command("init", help="Creates and initializes the database")
def init():
    """Initialize the database with sample users, shifts, and roster entries."""
    from App.database import db
    from App.models.user import User
    from App.models.admin import Admin
    from App.models.staff import Staff
    from App.models.Shift import Shift
    from App.models.Roster import Roster
    from App.models.attendance_record import AttendanceRecord  # <-- Ensure this import is present
    import datetime

    db.drop_all()
    db.create_all()

    # Define week range
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    week_end = week_start + datetime.timedelta(days=6)

    # Use more realistic names for users
    users = [
        Admin(name="Alice Johnson", email="admin1@example.com", password="adminpass1"),
        Admin(name="Bob Smith", email="admin2@example.com", password="adminpass2"),
        Staff(name="Carol Lee", email="staff1@example.com", password="staffpass1"),
        Staff(name="David Brown", email="staff2@example.com", password="staffpass2"),
        Staff(name="Eve Davis", email="staff3@example.com", password="staffpass3"),
        Staff(name="Frank Miller", email="staff4@example.com", password="staffpass4"),
        Staff(name="Grace Wilson", email="staff5@example.com", password="staffpass5"),
    ]
    db.session.add_all(users)
    db.session.commit()

    # Remove the separate admin and staff creation since they're created above
    shifts = []
    for i, staff in enumerate(users[2:]):  # Skip first two users (admins)
        for day in range(5):
            shift = Shift(
                user_id=staff.user_id,
                changeRequest=None,
                weekStart=week_start + datetime.timedelta(days=day),
                weekEnd=week_start + datetime.timedelta(days=day)
            )
            shifts.append(shift)
    db.session.add_all(shifts)
    db.session.commit()

    # Create roster entries: assign each shift to the corresponding staff
    rosters = []
    for shift in shifts:
        roster = Roster(shiftID=shift.id, userID=shift.user_id)
        rosters.append(roster)
    db.session.add_all(rosters)
    db.session.commit()

    print("Database initialized with 2 admins, 5 staff, sample shifts, and roster entries.")

'''
User Commands
'''

# Commands can be organized using groups

# create a group, it would be the first argument of the comand
# eg : flask user <command>
user_cli = AppGroup('user', help='User object commands') 

# Then define the command and any parameters and annotate it with the group (@)
@user_cli.command("create", help="Creates a user")
@click.argument("username", default="rob")
@click.argument("password", default="robpass")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

# this command will be : flask user create bob bobpass

@user_cli.command("list", help="Lists users in the database")
@click.argument("format", default="string")
def list_user_command(format):
    if format == 'string':
        print(get_all_users())
    else:
        print(get_all_users_json())

app.cli.add_command(user_cli) # add the group to the cli

'''
Test Commands
'''

test = AppGroup('test', help='Testing commands') 

@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "App"]))
    

app.cli.add_command(test)

@app.cli.command("hello")
def hello():
    """Prints hello."""
    print("Hello from the CLI!")

@app.cli.command("view-weekly-roster")
def view_weekly_roster():
    """Display the weekly roster with shifts and assigned users."""
    from App.database import db
    from App.models.Shift import Shift
    from App.models.Roster import Roster
    from App.models.user import User
    import datetime

    # Get current week range
    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    week_end = week_start + datetime.timedelta(days=6)

    # Query all shifts in the current week
    shifts = db.session.query(Shift).filter(
        Shift.weekStart >= week_start,
        Shift.weekEnd <= week_end
    ).all()

    if not shifts:
        print("No shifts scheduled for this week.")
        return

    print(f"Weekly Roster ({week_start} to {week_end}):")
    for shift in shifts:
        roster = db.session.query(Roster).filter_by(shiftID=shift.id).first()
        user = db.session.query(User).filter_by(user_id=shift.user_id).first()
        user_info = f"{user.name} ({user.email})" if user else "Unassigned"
        print(f"Shift ID: {shift.id}, Date: {shift.weekStart}, Assigned to: {user_info}")

@app.cli.command("schedule-shift")
@click.argument("admin_email")
@click.argument("staff_email")
def schedule_shift(admin_email, staff_email):
    """
    Schedule a staff member's shifts for the current week using an admin.
    Usage: flask schedule-shift <admin_email> <staff_email>
    """
    from App.models.user import User
    from App.models.admin import Admin
    from App.models.staff import Staff
    from App.models.Shift import Shift
    from App.models.Roster import Roster
    import datetime

    admin = db.session.query(Admin).filter_by(email=admin_email).first()
    staff = db.session.query(Staff).filter_by(email=staff_email).first()
    if not admin:
        print(f"Admin with email '{admin_email}' not found.")
        return
    if not staff:
        print(f"Staff with email '{staff_email}' not found.")
        return

    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    # Schedule shifts for Monday to Friday
    shift_ids = []
    for day in range(5):
        shift_date = week_start + datetime.timedelta(days=day)
        shift = Shift(
            user_id=staff.user_id,
            changeRequest=None,
            weekStart=shift_date,
            weekEnd=shift_date
        )
        db.session.add(shift)
        db.session.flush()  # Get shift.id before commit
        shift_ids.append(shift.id)
    db.session.commit()

    # Use admin's scheduleShift method to create roster entries
    admin.scheduleShift(db.session, staff.user_id, shift_ids)
    print(f"Scheduled shifts for {staff.name} ({staff.email}) for the week.")

@app.cli.command("manual-schedule-shift")
@click.argument("staff_email")
@click.argument("date")
@click.option("--change-request", default=None, help="Optional change request for the shift")
def manual_schedule_shift(staff_email, date, change_request):
    """
    Manually schedule a shift for a staff member.
    Usage: flask manual-schedule-shift <staff_email> <date:YYYY-MM-DD> [--change-request <text>]
    """
    from App.models.staff import Staff
    from App.models.Shift import Shift
    from App.models.Roster import Roster
    import datetime

    staff = db.session.query(Staff).filter_by(email=staff_email).first()
    if not staff:
        print(f"Staff with email '{staff_email}' not found.")
        return

    try:
        shift_date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return

    # Create the shift
    shift = Shift(
        user_id=staff.user_id,
        changeRequest=change_request,
        weekStart=shift_date,
        weekEnd=shift_date
    )
    db.session.add(shift)
    db.session.flush()  # Get shift.id before commit

    # Create the roster entry
    roster = Roster(shiftID=shift.id, userID=staff.user_id)
    db.session.add(roster)
    db.session.commit()

    print(f"Shift scheduled for {staff.name} on {shift_date}.")

@app.cli.command("clock-in")
@click.argument("staff_email")
@click.argument("shift_id")
@click.argument("time_in")
def clock_in(staff_email, shift_id, time_in):
    """
    Staff clocks in for a shift.
    Usage: flask clock-in <staff_email> <shift_id> <time_in:YYYY-MM-DDTHH:MM>
    """
    from App.models.staff import Staff
    from App.models.Shift import Shift
    from App.models.attendance_record import AttendanceRecord
    import datetime

    staff = db.session.query(Staff).filter_by(email=staff_email).first()
    shift = db.session.query(Shift).filter_by(id=shift_id, user_id=staff.user_id).first() if staff else None
    if not staff:
        print(f"Staff with email '{staff_email}' not found.")
        return
    if not shift:
        print(f"Shift with ID '{shift_id}' for staff '{staff_email}' not found.")
        return

    try:
        time_in_dt = datetime.datetime.strptime(time_in, "%Y-%m-%dT%H:%M")
    except ValueError:
        print("Invalid time format. Use YYYY-MM-DDTHH:MM.")
        return

    attendance = AttendanceRecord(
        shiftID=shift.id,
        userID=staff.user_id,
        timeIn=time_in_dt,
        timeout=None
    )
    db.session.add(attendance)
    db.session.commit()
    print(f"{staff.name} clocked in for shift {shift_id} at {time_in_dt}.")

@app.cli.command("clock-out")
@click.argument("staff_email")
@click.argument("shift_id")
@click.argument("time_out")
def clock_out(staff_email, shift_id, time_out):
    """
    Staff clocks out for a shift.
    Usage: flask clock-out <staff_email> <shift_id> <time_out:YYYY-MM-DDTHH:MM>
    """
    from App.models.staff import Staff
    from App.models.Shift import Shift
    from App.models.attendance_record import AttendanceRecord
    import datetime

    staff = db.session.query(Staff).filter_by(email=staff_email).first()
    shift = db.session.query(Shift).filter_by(id=shift_id, user_id=staff.user_id).first() if staff else None
    if not staff:
        print(f"Staff with email '{staff_email}' not found.")
        return
    if not shift:
        print(f"Shift with ID '{shift_id}' for staff '{staff_email}' not found.")
        return

    try:
        time_out_dt = datetime.datetime.strptime(time_out, "%Y-%m-%dT%H:%M")
    except ValueError:
        print("Invalid time format. Use YYYY-MM-DDTHH:MM.")
        return

    attendance = db.session.query(AttendanceRecord).filter_by(
        shiftID=shift.id,
        userID=staff.user_id,
        timeout=None
    ).first()
    if not attendance:
        print(f"No active attendance record found for shift {shift_id} and staff {staff_email}.")
        return

    attendance.timeout = time_out_dt
    db.session.commit()
    print(f"{staff.name} clocked out for shift {shift_id} at {time_out_dt}.")

@app.cli.command("generate-shift-report")
@click.argument("week_start")
@click.argument("week_end")
def generate_shift_report(week_start, week_end):
    """
    Generate a weekly shift report for all staff.
    Usage: flask generate-shift-report <week_start:YYYY-MM-DD> <week_end:YYYY-MM-DD>
    """
    from App.models.staff import Staff
    from App.models.Shift import Shift
    from App.models.attendance_record import AttendanceRecord
    import datetime

    try:
        week_start_date = datetime.datetime.strptime(week_start, "%Y-%m-%d").date()
        week_end_date = datetime.datetime.strptime(week_end, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.")
        return

    staff_members = db.session.query(Staff).all()
    print(f"Shift Report ({week_start_date} to {week_end_date}):")
    print("-" * 60)
    for staff in staff_members:
        # Scheduled shifts for the week
        scheduled_shifts = db.session.query(Shift).filter(
            Shift.user_id == staff.user_id,
            Shift.weekStart >= week_start_date,
            Shift.weekEnd <= week_end_date
        ).all()
        num_shifts = len(scheduled_shifts)

        # Attendance records for the week
        attendance_records = db.session.query(AttendanceRecord).filter(
            AttendanceRecord.userID == staff.user_id,
            AttendanceRecord.timeIn >= datetime.datetime.combine(week_start_date, datetime.time.min),
            AttendanceRecord.timeIn <= datetime.datetime.combine(week_end_date, datetime.time.max)
        ).all()

        total_hours = 0.0
        for record in attendance_records:
            if record.timeout and record.timeIn:
                duration = record.timeout - record.timeIn
                total_hours += duration.total_seconds() / 3600.0

        print(f"Staff: {staff.name} ({staff.email})")
        print(f"  Scheduled Shifts: {num_shifts}")
        print(f"  Total Hours Clocked In: {total_hours:.2f}")
        print(f"  Attendance Records: {len(attendance_records)}")
        print("-" * 60)

@app.cli.command("generate-sample-attendance")
def generate_sample_attendance():
    """
    Generate sample attendance records for all staff for the current week.
    Usage: flask generate-sample-attendance
    """
    from App.models.staff import Staff
    from App.models.Shift import Shift
    from App.models.attendance_record import AttendanceRecord
    import datetime
    import random

    today = datetime.date.today()
    week_start = today - datetime.timedelta(days=today.weekday())
    week_end = week_start + datetime.timedelta(days=6)

    staff_members = db.session.query(Staff).all()
    shifts = db.session.query(Shift).filter(
        Shift.weekStart >= week_start,
        Shift.weekEnd <= week_end
    ).all()

    # For each staff, create 2-3 attendance records for their scheduled shifts
    for staff in staff_members:
        # staff.name is already set from init
        staff_shifts = [s for s in shifts if s.user_id == staff.user_id]
        sample_shifts = random.sample(staff_shifts, min(len(staff_shifts), random.randint(2, 3)))
        for shift in sample_shifts:
            clock_in_hour = random.randint(7, 9)
            time_in = datetime.datetime.combine(shift.weekStart, datetime.time(clock_in_hour, 0))
            time_out = time_in + datetime.timedelta(hours=8)
            attendance = AttendanceRecord(
                shiftID=shift.id,
                userID=staff.user_id,
                timeIn=time_in,
                timeout=time_out
            )
            db.session.add(attendance)
    db.session.commit()
    print("Sample attendance records generated for the current week with staff names.")