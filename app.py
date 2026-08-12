from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)


# ==========================================
# DATABASE
# ==========================================

def init_db():

    conn = sqlite3.connect("database.db")

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            department TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            urgency TEXT NOT NULL,
            affected_students INTEGER NOT NULL,
            score INTEGER NOT NULL,
            priority TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


# ==========================================
# CALCULATE PRIORITY
# ==========================================

def calculate_priority(affected_students, category):

    category_score = {

    "Safety": 60,

    "Infrastructure": 40,

    "Electrical": 35,

    "Plumbing": 30,

    "Academic": 30,

    "Examination": 35,

    "IT/Network": 30,

    "Library": 20,

    "Hostel": 30,

    "Transport": 25,

    "Cleanliness": 20,

    "Canteen": 25,

    "Other": 10

}


    # Students affected score

    if affected_students <= 10:

        affected_score = 5

    elif affected_students <= 30:

        affected_score = 10

    elif affected_students <= 100:

        affected_score = 20

    else:

        affected_score = 30


    # Calculate total score

    score = (
        category_score[category]
        + affected_score
    )


    # Determine priority

    if score >= 80:

        priority = "Critical"

    elif score >= 50:

        priority = "High"

    elif score >= 30:

        priority = "Medium"

    else:

        priority = "Low"


    return score, priority


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    return render_template("index.html")


# ==========================================
# SUBMIT COMPLAINT
# ==========================================

@app.route("/submit", methods=["GET", "POST"])
def submit():

    if request.method == "POST":

        student_name = request.form["student_name"]

        department = request.form["department"]

        category = request.form["category"]

        description = request.form["description"]

        affected_students = int(
            request.form["affected_students"]
        )


        # Automatically calculate priority

        score, priority = calculate_priority(
            affected_students,
            category
        )


        # Connect to database

        conn = sqlite3.connect("database.db")

        cursor = conn.cursor()


        # Insert complaint

        cursor.execute("""
            INSERT INTO complaints
            (
                student_name,
                department,
                category,
                description,
                urgency,
                affected_students,
                score,
                priority,
                status,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_name,
            department,
            category,
            description,
            "System Calculated",
            affected_students,
            score,
            priority,
            "Pending",
            datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        ))


        conn.commit()

        conn.close()


        return redirect("/admin")


    return render_template("submit.html")


# ==========================================
# ADMIN DASHBOARD
# ==========================================

# ==========================================
# ADMIN DASHBOARD
# ==========================================

@app.route("/admin")
def admin():

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row


    # Get all complaints

    complaints = conn.execute("""
        SELECT *
        FROM complaints
        ORDER BY score DESC
    """).fetchall()


    # Count priorities

    total_complaints = conn.execute("""
        SELECT COUNT(*)
        FROM complaints
    """).fetchone()[0]


    critical_count = conn.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE priority = 'Critical'
    """).fetchone()[0]


    high_count = conn.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE priority = 'High'
    """).fetchone()[0]


    medium_count = conn.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE priority = 'Medium'
    """).fetchone()[0]


    low_count = conn.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE priority = 'Low'
    """).fetchone()[0]


    # Count statuses

    pending_count = conn.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Pending'
    """).fetchone()[0]
    progress_count = conn.execute(
    "SELECT COUNT(*) FROM complaints WHERE status = 'In Progress'"
    ).fetchone()[0]

    resolved_count = conn.execute("""
        SELECT COUNT(*)
        FROM complaints
        WHERE status = 'Resolved'
    """).fetchone()[0]


    conn.close()


    return render_template(
        "admin.html",
        complaints=complaints,
        total_complaints=total_complaints,
        critical_count=critical_count,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        pending_count=pending_count,
        progress_count=progress_count,
        resolved_count=resolved_count
    )

# ==========================================
# VIEW COMPLAINT
# ==========================================

@app.route("/complaint/<int:complaint_id>")
def view_complaint(complaint_id):

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row


    complaint = conn.execute("""
        SELECT *
        FROM complaints
        WHERE id = ?
    """, (complaint_id,)).fetchone()


    conn.close()


    if complaint is None:

        return "Complaint not found", 404


    return render_template(
        "complaint.html",
        complaint=complaint
    )


# ==========================================
# UPDATE STATUS
# ==========================================

@app.route(
    "/update_status/<int:complaint_id>",
    methods=["POST"]
)
def update_status(complaint_id):

    new_status = request.form["status"]


    conn = sqlite3.connect("database.db")


    conn.execute("""
        UPDATE complaints
        SET status = ?
        WHERE id = ?
    """, (
        new_status,
        complaint_id
    ))


    conn.commit()

    conn.close()


    return redirect("/admin")
@app.route("/delete/<int:complaint_id>", methods=["POST"])
def delete_complaint(complaint_id):

    conn = sqlite3.connect("database.db")

    conn.execute("""
        DELETE FROM complaints
        WHERE id = ?
    """, (complaint_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")

# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)