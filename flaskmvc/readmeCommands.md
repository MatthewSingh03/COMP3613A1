# CLI Commands Reference

## Database & Sample Data
- flask init
  - Initialize the database with sample admins, staff, shifts, and rosters.
  **Example:**  
  flask init

- flask generate-sample-attendance
  - Generate sample attendance records for staff for the current week.
  **Example:**  
  flask generate-sample-attendance

## Shift & Roster Management
- flask view-weekly-roster
  - Display the weekly roster with staff names and emails for each shift.
  **Example:**  
  flask view-weekly-roster

- flask manual-schedule-shift <staff_email> <date:YYYY-MM-DD> [--change-request <text>]
  - Manually schedule a shift for a staff member on a specific date.
  **Example:**  
  flask manual-schedule-shift staff1@example.com 2025-10-05 --change-request "Swap with staff2"

## Attendance
- flask clock-in <staff_email> <shift_id> <time_in:YYYY-MM-DDTHH:MM>
  - Staff clocks in for a shift at the specified time.
  **Example:**  
  flask clock-in staff1@example.com 5 2025-10-05T08:00

- flask clock-out <staff_email> <shift_id> <time_out:YYYY-MM-DDTHH:MM>
  - Staff clocks out for a shift at the specified time.
  **Example:**  
  flask clock-out staff1@example.com 5 2025-10-05T16:00

## Reports
- flask generate-shift-report <week_start:YYYY-MM-DD> <week_end:YYYY-MM-DD>
  - Generate a weekly shift report showing scheduled shifts and total hours clocked in for each staff member.
  **Example:**  
  flask generate-shift-report 2025-10-01 2025-10-07