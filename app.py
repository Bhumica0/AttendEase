
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

# Secret key for session management
app.secret_key = "attendance_system_secret_key"

# Database Initialization
def init_db():

    conn = sqlite3.connect("attendance.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_number TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT,
            course TEXT,
            semester INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Add sample students automatically

    sample_students = [
        ("MCA001", "Aarav Sharma", "aarav@gmail.com", "MCA - Artificial Intelligence", 1),
        ("MCA002", "Ananya Verma", "ananya@gmail.com", "MCA - Artificial Intelligence", 1),
        ("MCA003", "Rohan Mehta", "rohan@gmail.com", "MCA - Artificial Intelligence", 1),
        ("MCA004", "Priya Singh", "priya@gmail.com", "MCA - Artificial Intelligence", 1),
        ("MCA005", "Arjun Kapoor", "arjun@gmail.com", "MCA - Artificial Intelligence", 1),
        ("MCA006", "Sneha Gupta", "sneha@gmail.com", "MCA - Artificial Intelligence", 1),
        ("MCA007", "Kabir Malhotra", "kabir@gmail.com", "MCA - Artificial Intelligence", 1),
        ("MCA008", "Ishita Roy", "ishita@gmail.com", "MCA - Artificial Intelligence", 1),
        ("MCA009", "Aditya Kumar", "aditya@gmail.com", "MCA - Artificial Intelligence", 1),
        ("MCA010", "Meera Joshi", "meera@gmail.com", "MCA - Artificial Intelligence", 1)
    ]

    conn.executemany("""
        INSERT OR IGNORE INTO students
        (roll_number, full_name, email, course, semester)
        VALUES (?, ?, ?, ?, ?)
    """, sample_students)
        # Create Attendance Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date DATE NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            UNIQUE(student_id, attendance_date)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            attendance_date DATE NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            UNIQUE(student_id, attendance_date)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            notification_type TEXT DEFAULT 'info',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    """)

    # Create Admin Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
        # Add Administrator Name Column
    admin_columns = [
        row[1] for row in conn.execute("PRAGMA table_info(admin)").fetchall()
    ]

    if "full_name" not in admin_columns:
        conn.execute("""
            ALTER TABLE admin
            ADD COLUMN full_name TEXT DEFAULT 'Administrator'
        """)
        # Create Default Admin Account
    conn.execute("""
        INSERT OR IGNORE INTO admin (username, password)
        VALUES (?, ?)
    """, ("admin", generate_password_hash("admin123")))
    # Create Notification Settings Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notification_settings (
            setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            notifications_enabled INTEGER DEFAULT 0
        )
    """)

    conn.execute("""
        INSERT OR IGNORE INTO notification_settings
        (username, notifications_enabled)
        VALUES ('admin', 0)
    """)
    conn.commit()
    conn.close()


# Home page - Admin Login
@app.route("/")
def home():
    return render_template("login.html")


# Teacher and Student Login
@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    password = request.form.get("password")
    role = request.form.get("role")

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    # Teacher Login
    if role == "teacher":

        teacher = conn.execute(
            "SELECT * FROM admin WHERE username = ?",
            (username,)
        ).fetchone()

        conn.close()

        if teacher and check_password_hash(teacher["password"], password):

            session.clear()
            session["admin"] = username
            session["role"] = "teacher"

            return redirect(url_for("dashboard"))

    # Student Login
    elif role == "student":

        student = conn.execute(
            "SELECT * FROM students WHERE roll_number = ?",
            (username,)
        ).fetchone()

        conn.close()

        if student and student["password"] and check_password_hash(student["password"], password):

            session.clear()
            session["student_id"] = student["student_id"]
            session["role"] = "student"

            return redirect(url_for("student_dashboard"))

    else:
        conn.close()

    return """
    <h3>Invalid username, password or role!</h3>
    <a href="/">Try Again</a>
    """

# Dashboard



@app.route("/dashboard")
def dashboard():

    if "admin" not in session:
        return redirect(url_for("home"))

    from datetime import date

    today = date.today().isoformat()

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    # Get Administrator Name
    admin = conn.execute("""
        SELECT full_name
        FROM admin
        WHERE username = ?
    """, (session["admin"],)).fetchone()

    admin_name = admin["full_name"] if admin and admin["full_name"] else session["admin"]

    total_students = conn.execute("""
        SELECT COUNT(*) FROM students
    """).fetchone()[0]

    present_today = conn.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE attendance_date = ? AND status = 'Present'
    """, (today,)).fetchone()[0]

    absent_today = conn.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE attendance_date = ? AND status = 'Absent'
    """, (today,)).fetchone()[0]

    late_today = conn.execute("""
        SELECT COUNT(*) FROM attendance
        WHERE attendance_date = ? AND status = 'Late'
    """, (today,)).fetchone()[0]

    attendance_rate = 0

    if total_students > 0:
        attendance_rate = round(
            (present_today / total_students) * 100, 1
        )

    recent_records = conn.execute("""
        SELECT
            students.roll_number,
            students.full_name,
            attendance.attendance_date,
            attendance.status
        FROM attendance
        JOIN students
        ON attendance.student_id = students.student_id
        ORDER BY attendance.attendance_date ASC,
         attendance.attendance_id ASC
        LIMIT 5
    """).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        admin_name=admin_name,
        total_students=total_students,
        present_today=present_today,
        absent_today=absent_today,
        late_today=late_today,
        attendance_rate=attendance_rate,
        recent_records=recent_records
    )

# Student Management
@app.route("/students")
def students():

    if "admin" not in session:
        return redirect(url_for("home"))

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    students = conn.execute(
        "SELECT * FROM students ORDER BY student_id ASC"
    ).fetchall()

    conn.close()

    return render_template(
        "students.html",
        students=students
    )

# Add New Student
# Add New Student
@app.route("/add_student", methods=["POST"])
def add_student():

    if session.get("role") != "teacher":
        return redirect(url_for("home"))

    roll_number = request.form.get("roll_number")
    full_name = request.form.get("full_name")
    email = request.form.get("email")
    course = request.form.get("course")
    semester = request.form.get("semester")
    password = request.form.get("password")

    if not password or len(password) < 6:
        return "Password must contain at least 6 characters."

    hashed_password = generate_password_hash(password)

    conn = sqlite3.connect("attendance.db")

    try:
        conn.execute("""
            INSERT INTO students
            (roll_number, full_name, email, course, semester, password)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            roll_number,
            full_name,
            email,
            course,
            semester,
            hashed_password
        ))

        conn.commit()

    except sqlite3.IntegrityError:
        conn.close()
        return "This roll number is already registered. <a href='/students'>Go Back</a>"

    conn.close()

    return redirect(url_for("students"))
# Edit Student
@app.route("/edit_student/<int:student_id>", methods=["GET", "POST"])
def edit_student(student_id):

    if "admin" not in session:
        return redirect(url_for("home"))

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    if request.method == "POST":

        roll_number = request.form.get("roll_number")
        full_name = request.form.get("full_name")
        email = request.form.get("email")
        course = request.form.get("course")
        semester = request.form.get("semester")

        try:
            conn.execute("""
                UPDATE students
                SET roll_number = ?,
                    full_name = ?,
                    email = ?,
                    course = ?,
                    semester = ?
                WHERE student_id = ?
            """, (
                roll_number,
                full_name,
                email,
                course,
                semester,
                student_id
            ))

            conn.commit()
            conn.close()

            return redirect(url_for("students"))

        except sqlite3.IntegrityError:
            conn.close()
            return "This roll number is already registered."

    student = conn.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (student_id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found.", 404

    return render_template("edit_student.html", student=student)



# Delete Student
@app.route("/delete_student/<int:student_id>")
def delete_student(student_id):

    if "admin" not in session:
        return redirect(url_for("home"))

    conn = sqlite3.connect("attendance.db")

    conn.execute(
        "DELETE FROM students WHERE student_id = ?",
        (student_id,)
    )

    conn.commit()
    conn.close()

    return redirect(url_for("students"))

@app.route("/mark_attendance")
def mark_attendance():
    if "admin" not in session:
        return redirect(url_for("home"))

    selected_subject_id = request.args.get("subject_id", "")
    selected_date = request.args.get("date", "")

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    students = conn.execute(
        "SELECT * FROM students ORDER BY roll_number ASC"
    ).fetchall()

    subjects = conn.execute(
        "SELECT * FROM subjects ORDER BY subject_name ASC"
    ).fetchall()

    conn.close()

    return render_template(
        "mark_attendance.html",
        students=students,
        subjects=subjects,
        selected_subject_id=selected_subject_id,
        selected_date=selected_date
    )

@app.route("/save_attendance", methods=["POST"])
def save_attendance():
    if "admin" not in session:
        return redirect(url_for("home"))

    attendance_date = request.form.get("attendance_date")
    subject_id = request.form.get("subject_id")

    if not attendance_date or not subject_id:
        return redirect(url_for("mark_attendance", subject_id=subject_id, date=attendance_date))
    conn = sqlite3.connect("attendance.db")

    students = conn.execute(
        "SELECT student_id FROM students"
    ).fetchall()

    for student in students:
        student_id = student[0]
        status = request.form.get(f"status_{student_id}")

        if status:
            conn.execute("""
                INSERT INTO attendance
                (student_id, attendance_date, status, subject_id)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(student_id, attendance_date, subject_id)
                DO UPDATE SET status = excluded.status
            """, (student_id, attendance_date, status, subject_id))

    conn.commit()
    conn.close()

    return redirect(url_for("mark_attendance"))
@app.route("/attendance_records")
def attendance_records():
    if "admin" not in session:
        return redirect(url_for("home"))

    selected_date = request.args.get("date", "")
    selected_subject_id = request.args.get("subject_id", "")

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row


    if selected_date:
        records = conn.execute("""
            SELECT
                attendance.attendance_id,
                students.roll_number,
                students.full_name,
                attendance.attendance_date,
                attendance.status
            FROM attendance
            JOIN students
            ON attendance.student_id = students.student_id
            WHERE attendance.attendance_date = ?
            ORDER BY students.roll_number ASC
        """, (selected_date,)).fetchall()
    else:
        records = conn.execute("""
            SELECT
                attendance.attendance_id,
                students.roll_number,
                students.full_name,
                attendance.attendance_date,
                attendance.status
            FROM attendance
            JOIN students
            ON attendance.student_id = students.student_id
            ORDER BY attendance.attendance_date DESC
        """).fetchall()

    conn.close()

    return render_template(
        "attendance_records.html",
        records=records,
        selected_date=selected_date
    )
# Reports & Analytics


@app.route("/reports")
def reports():

    if "admin" not in session:
        return redirect(url_for("home"))

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    # Total students
    total_students = conn.execute(
        "SELECT COUNT(*) FROM students"
    ).fetchone()[0]

    # Total attendance records
    total_records = conn.execute(
        "SELECT COUNT(*) FROM attendance"
    ).fetchone()[0]

    # Present + Late records
    attended_records = conn.execute("""
        SELECT COUNT(*)
        FROM attendance
        WHERE status IN ('Present', 'Late')
    """).fetchone()[0]

    # Overall attendance percentage
    overall_attendance = 0

    if total_records > 0:
        overall_attendance = round(
            (attended_records / total_records) * 100, 1
        )

    # Individual student reports
    student_reports = conn.execute("""
        SELECT
            students.roll_number,
            students.full_name,
            COUNT(attendance.attendance_id) AS total_classes,
            SUM(CASE WHEN attendance.status IN ('Present', 'Late')
                THEN 1 ELSE 0 END) AS attended,
            SUM(CASE WHEN attendance.status = 'Absent'
                THEN 1 ELSE 0 END) AS absent
        FROM students
        LEFT JOIN attendance
        ON students.student_id = attendance.student_id
        GROUP BY students.student_id
        ORDER BY students.roll_number
    """).fetchall()

    # Monthly attendance trend
    monthly_data = conn.execute("""
        SELECT
            strftime('%Y-%m', attendance_date) AS month,
            COUNT(*) AS total,
            SUM(
                CASE WHEN status IN ('Present', 'Late')
                THEN 1 ELSE 0 END
            ) AS attended
        FROM attendance
        GROUP BY month
        ORDER BY month
    """).fetchall()

    monthly_labels = [row["month"] for row in monthly_data]

    monthly_percentages = [
        round((row["attended"] / row["total"]) * 100, 1)
        if row["total"] > 0 else 0
        for row in monthly_data
    ]

    # Attendance status distribution
    status_data = conn.execute("""
        SELECT status, COUNT(*) AS total
        FROM attendance
        GROUP BY status
    """).fetchall()

    status_counts = {
        "Present": 0,
        "Absent": 0,
        "Late": 0
    }

    for row in status_data:
        if row["status"] in status_counts:
            status_counts[row["status"]] = row["total"]

    conn.close()

    return render_template(
        "reports.html",
        total_students=total_students,
        total_records=total_records,
        overall_attendance=overall_attendance,
        student_reports=student_reports,
        monthly_labels=monthly_labels,
        monthly_percentages=monthly_percentages,
        status_counts=status_counts
    )

# Admin Profile
@app.route("/admin_profile")
def admin_profile():

    if "admin" not in session:
        return redirect(url_for("home"))

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    admin = conn.execute(
        "SELECT * FROM admin WHERE username = ?",
        (session["admin"],)
    ).fetchone()

    conn.close()

    return render_template(
        "admin_profile.html",
        admin=admin
    )
# Edit Admin Profile

@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():

    if "admin" not in session:
        return redirect(url_for("home"))

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    current_username = session["admin"]

    admin = conn.execute(
        "SELECT * FROM admin WHERE username = ?",
        (current_username,)
    ).fetchone()

    if request.method == "POST":

        full_name = request.form.get("full_name", "").strip()
        new_username = request.form.get("username", "").strip()

        if not full_name or not new_username:
            conn.close()
            flash("Name and username cannot be empty.", "error")
            return redirect(url_for("edit_profile"))

        existing_user = conn.execute("""
            SELECT * FROM admin
            WHERE username = ? AND username != ?
        """, (new_username, current_username)).fetchone()

        if existing_user:
            conn.close()
            flash("This username is already taken.", "error")
            return redirect(url_for("edit_profile"))

        conn.execute("""
            UPDATE admin
            SET full_name = ?, username = ?
            WHERE username = ?
        """, (full_name, new_username, current_username))

        conn.execute("""
            UPDATE notification_settings
            SET username = ?
            WHERE username = ?
        """, (new_username, current_username))

        conn.commit()
        conn.close()

        session["admin"] = new_username

        flash("Profile updated successfully!", "success")

        return redirect(url_for("admin_profile"))

    conn.close()

    return render_template("edit_profile.html", admin=admin)
# Settings Page
@app.route("/settings")
def settings():

    if "admin" not in session:
        return redirect(url_for("home"))

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    notification = conn.execute("""
        SELECT notifications_enabled
        FROM notification_settings
        WHERE username = ?
    """, (session["admin"],)).fetchone()

    conn.close()

    notifications_enabled = notification["notifications_enabled"] if notification else 0

    return render_template(
        "settings.html",
        notifications_enabled=notifications_enabled
    )
# Update Notification Preferences
@app.route("/update_notifications", methods=["POST"])
def update_notifications():

    if "admin" not in session:
        return redirect(url_for("home"))

    notifications_enabled = 1 if request.form.get("notifications") == "on" else 0

    conn = sqlite3.connect("attendance.db")

    conn.execute("""
        UPDATE notification_settings
        SET notifications_enabled = ?
        WHERE username = ?
    """, (notifications_enabled, session["admin"]))

    conn.commit()
    conn.close()
    flash("Notification preferences saved successfully!", "success")

    return redirect(url_for("settings"))
# Change Password
@app.route("/change_password", methods=["POST"])
def change_password():

    if "admin" not in session:
        return redirect(url_for("home"))

    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    admin = conn.execute(
        "SELECT * FROM admin WHERE username = ?",
        (session["admin"],)
    ).fetchone()

    if not check_password_hash(admin["password"], current_password):
        conn.close()
        return "Current password is incorrect. <a href='/settings'>Go Back</a>"

    if new_password != confirm_password:
        conn.close()
        return "New passwords do not match. <a href='/settings'>Go Back</a>"

    if len(new_password) < 8:
        conn.close()
        return "Password must be at least 8 characters. <a href='/settings'>Go Back</a>"

    hashed_password = generate_password_hash(new_password)

    conn.execute(
        "UPDATE admin SET password = ? WHERE username = ?",
        (hashed_password, session["admin"])
    )

    conn.commit()
    conn.close()

    return redirect(url_for("settings"))
 #Student Dashboard
# Student Dashboard
@app.route("/student_dashboard")
def student_dashboard():

    if session.get("role") != "student" or "student_id" not in session:
        return redirect(url_for("home"))

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    student = conn.execute(
        "SELECT * FROM students WHERE student_id = ?",
        (session["student_id"],)
    ).fetchone()

    if student is None:
        conn.close()
        session.clear()
        return redirect(url_for("home"))

    # Attendance statistics
    records = conn.execute("""
        SELECT status, COUNT(*) AS total
        FROM attendance
        WHERE student_id = ?
        GROUP BY status
    """, (session["student_id"],)).fetchall()

    # Recent attendance history
    recent_attendance = conn.execute("""
        SELECT attendance_date, status
        FROM attendance
        WHERE student_id = ?
        ORDER BY attendance_date DESC, attendance_id DESC
        LIMIT 10
    """, (session["student_id"],)).fetchall()

    conn.close()

    counts = {
        "Present": 0,
        "Absent": 0,
        "Late": 0
    }

    for record in records:
        if record["status"] in counts:
            counts[record["status"]] = record["total"]

    total = sum(counts.values())

    percentage = (counts["Present"] / total * 100) if total else 0

    return render_template(
        "student_dashboard.html",
        student=student,
        counts=counts,
        total=total,
        percentage=round(percentage, 2),
        recent_attendance=recent_attendance
    )
# Student - My Attendance Page
@app.route("/my_attendance")
def my_attendance():

    if session.get("role") != "student" or "student_id" not in session:
        return redirect(url_for("home"))

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    records = conn.execute("""
        SELECT attendance_date, status
        FROM attendance
        WHERE student_id = ?
        ORDER BY attendance_date DESC
    """, (session["student_id"],)).fetchall()

    conn.close()

    return render_template(
        "my_attendance.html",
        records=records
    )
# Student - My Profile Page
@app.route("/student_profile")
def student_profile():

    if session.get("role") != "student" or "student_id" not in session:
        return redirect(url_for("home"))

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    student = conn.execute("""
        SELECT roll_number, full_name, email, course, semester, created_at
        FROM students
        WHERE student_id = ?
    """, (session["student_id"],)).fetchone()

    conn.close()

    return render_template(
        "student_profile.html",
        student=student
    )


@app.route("/notifications")
def notifications():
    if session.get("role") != "student" or "student_id" not in session:
        return redirect(url_for("home"))

    student_id = session["student_id"]

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    # Fetch attendance statistics
    attendance_data = conn.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present
        FROM attendance
        WHERE student_id = ?
    """, (student_id,)).fetchone()

    total = attendance_data["total"] or 0
    present = attendance_data["present"] or 0

        # Generate low attendance warning
    title = "Low Attendance Warning"

    if total > 0:
        percentage = (present / total) * 100

        if percentage < 75:
            message = (
                f"Your attendance is {percentage:.1f}%. "
                "Your attendance is below the required 75%. "
                "Please attend upcoming classes regularly."
            )

            existing = conn.execute("""
                SELECT notification_id FROM notifications
                WHERE student_id = ?
                AND title = ?
            """, (student_id, title)).fetchone()

            if existing:
                conn.execute("""
                    UPDATE notifications
                    SET message = ?, created_at = CURRENT_TIMESTAMP
                    WHERE notification_id = ?
                """, (message, existing["notification_id"]))
            else:
                conn.execute("""
                    INSERT INTO notifications
                    (student_id, title, message, notification_type)
                    VALUES (?, ?, ?, 'warning')
                """, (student_id, title, message))

        else:
            conn.execute("""
                DELETE FROM notifications
                WHERE student_id = ?
                AND title = ?
            """, (student_id, title))
    # Fetch notifications
    records = conn.execute("""
        SELECT * FROM notifications
        WHERE student_id = ?
        ORDER BY created_at DESC
    """, (student_id,)).fetchall()

    conn.commit()
    conn.close()

    return render_template("notifications.html", records=records)
@app.route("/attendance_calendar")
def attendance_calendar():
    if session.get("role") != "student" or "student_id" not in session:
        return redirect(url_for("home"))

    student_id = session["student_id"]

    conn = sqlite3.connect("attendance.db")
    conn.row_factory = sqlite3.Row

    records = conn.execute("""
        SELECT attendance_date, status
        FROM attendance
        WHERE student_id = ?
        ORDER BY attendance_date
    """, (student_id,)).fetchall()

    conn.close()

    return render_template("attendance_calendar.html", records=records)
@app.route("/student_settings")
def student_settings():
    if session.get("role") != "student" or "student_id" not in session:
        return redirect(url_for("home"))

    return render_template("student_settings.html")
@app.route("/student_change_password", methods=["GET", "POST"])
def student_change_password():
    if session.get("role") != "student" or "student_id" not in session:
        return redirect(url_for("home"))

    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")

        conn = sqlite3.connect("attendance.db")
        conn.row_factory = sqlite3.Row

        student = conn.execute(
            "SELECT password FROM students WHERE student_id = ?",
            (session["student_id"],)
        ).fetchone()

        if not student or not check_password_hash(student["password"], current_password):
            conn.close()
            flash("Current password is incorrect.")
            return redirect(url_for("student_change_password"))

        if len(new_password) < 8:
            conn.close()
            flash("New password must contain at least 8 characters.")
            return redirect(url_for("student_change_password"))

        if new_password != confirm_password:
            conn.close()
            flash("New passwords do not match.")
            return redirect(url_for("student_change_password"))

        hashed_password = generate_password_hash(new_password)

        conn.execute(
            "UPDATE students SET password = ? WHERE student_id = ?",
            (hashed_password, session["student_id"])
        )

        conn.commit()
        conn.close()

        flash("Password changed successfully!")
        return redirect(url_for("student_settings"))

    return render_template("student_change_password.html")
## Logout for Teacher and Student
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# Run Application
if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5001)