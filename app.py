import os
import uuid
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db_connection, init_db
from ml_engine.predictor import classify_text, assign_priority, find_similar

app = Flask(__name__)
app.secret_key = "secure-college-grievance-key"

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if "user_id" not in session:
                flash("Please log in first.", "warning")
                return redirect(url_for("login"))
            if role and session.get("role") != role:
                flash("Unauthorized access.", "danger")
                return redirect(url_for("login"))
            return f(*args, **kwargs)
        return decorated
    return decorator

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("admin_dashboard" if session.get("role") == "admin" else "student_dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "")
        r = request.form.get("role", "student")

        if not u or not p:
            flash("Username and password are required.", "danger")
            return redirect(url_for("register"))

        hashed_pw = generate_password_hash(p)

        try:
            with get_db_connection() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                    (u, hashed_pw, r)
                )
                conn.commit()
            flash("Account registered successfully! You can now log in.", "success")
            return redirect(url_for("login"))
        except Exception:
            flash("This username is already taken. Please choose another one.", "danger")
            return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username", "").strip()
        p = request.form.get("password", "")
        r = request.form.get("role", "")
        with get_db_connection() as conn:
            user = conn.execute("SELECT * FROM users WHERE username = ? AND role = ?", (u, r)).fetchone()
        if user and check_password_hash(user["password_hash"], p):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect(url_for("admin_dashboard" if user["role"] == "admin" else "student_dashboard"))
        flash("Invalid username, password, or role.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/student/dashboard")
@login_required("student")
def student_dashboard():
    with get_db_connection() as conn:
        complaints = conn.execute(
            "SELECT * FROM complaints WHERE student_id = ? ORDER BY id DESC", 
            (session["user_id"],)
        ).fetchall()
        metrics = {
            "total": len(complaints),
            "pending": sum(1 for c in complaints if c["status"] == "Submitted"),
            "in_progress": sum(1 for c in complaints if c["status"] == "In Progress"),
            "resolved": sum(1 for c in complaints if c["status"] == "Resolved")
        }
    return render_template("student_dashboard.html", complaints=complaints, metrics=metrics)

@app.route("/student/submit", methods=["GET", "POST"])
@login_required("student")
def submit_complaint():
    if request.method == "POST":
        t = request.form.get("title", "").strip()
        d = request.form.get("description", "").strip()
        l = request.form.get("location", "").strip()
        if not t or not d or not l:
            flash("All fields are required.", "danger")
            return redirect(url_for("submit_complaint"))

        cat, subcat = classify_text(d)
        prio = assign_priority(d)
        cid = f"GRV-{uuid.uuid4().hex[:6].upper()}"

        with get_db_connection() as conn:
            conn.execute("""
                INSERT INTO complaints (complaint_id, student_id, title, description, location, category, subcategory, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (cid, session["user_id"], t, d, l, cat, subcat, prio))
            conn.commit()

        flash(f"Complaint {cid} submitted successfully.", "success")
        return redirect(url_for("complaint_detail", cid=cid))
    return render_template("submit_complaint.html")

@app.route("/complaint/<cid>")
@login_required()
def complaint_detail(cid):
    with get_db_connection() as conn:
        complaint = conn.execute("SELECT * FROM complaints WHERE complaint_id = ?", (cid,)).fetchone()
        if not complaint:
            flash("Complaint not found.", "danger")
            return redirect(url_for("index"))
        if session["role"] == "student" and complaint["student_id"] != session["user_id"]:
            flash("Unauthorized access.", "danger")
            return redirect(url_for("student_dashboard"))
        candidates = conn.execute(
            "SELECT complaint_id, title, description, status FROM complaints WHERE complaint_id != ?", 
            (cid,)
        ).fetchall()
        candidate_list = [dict(c) for c in candidates]

    similar = find_similar(complaint["description"], candidate_list)
    return render_template("complaint_detail.html", complaint=complaint, similar_issues=similar)

@app.route("/admin/dashboard")
@login_required("admin")
def admin_dashboard():
    with get_db_connection() as conn:
        complaints = conn.execute("SELECT * FROM complaints ORDER BY id DESC").fetchall()
    return render_template("admin_dashboard.html", complaints=complaints)

@app.route("/admin/update-status", methods=["POST"])
@login_required("admin")
def update_status():
    cid = request.form.get("complaint_id")
    st = request.form.get("status")
    dept = request.form.get("assigned_dept")
    notes = request.form.get("resolution_notes", "")

    with get_db_connection() as conn:
        conn.execute("""
            UPDATE complaints
            SET status = ?, assigned_dept = ?, resolution_notes = ?
            WHERE complaint_id = ?
        """, (st, dept, notes, cid))
        conn.commit()
    flash(f"Complaint {cid} updated.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/analytics")
@login_required("admin")
def analytics_view():
    return render_template("analytics.html")

@app.route("/api/analytics/summary")
@login_required("admin")
def analytics_data():
    with get_db_connection() as conn:
        cats = conn.execute("SELECT category, COUNT(*) as count FROM complaints GROUP BY category").fetchall()
        stats = conn.execute("SELECT status, COUNT(*) as count FROM complaints GROUP BY status").fetchall()
        prios = conn.execute("SELECT priority, COUNT(*) as count FROM complaints GROUP BY priority").fetchall()

    return jsonify({
        "categories": {r["category"]: r["count"] for r in cats},
        "statuses": {r["status"]: r["count"] for r in stats},
        "priorities": {r["priority"]: r["count"] for r in prios}
    })

if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
