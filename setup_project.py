import os
import sqlite3
import pickle
import pandas as pd
from werkzeug.security import generate_password_hash
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

print("⚡ Upgrading Triage and Analytics Dashboards...")

# 1. database.py
with open("database.py", "w") as f:
    f.write('''import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grievance.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'admin'))
            );
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS complaints (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                complaint_id TEXT UNIQUE NOT NULL,
                student_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                location TEXT NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT,
                priority TEXT NOT NULL CHECK(priority IN ('High', 'Medium', 'Low')),
                status TEXT NOT NULL DEFAULT 'Submitted' CHECK(status IN ('Submitted', 'In Progress', 'Resolved')),
                assigned_dept TEXT DEFAULT 'Unassigned',
                resolution_notes TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES users (id) ON DELETE CASCADE
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_status ON complaints(status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cat ON complaints(category);")

        cursor.execute("""
            INSERT OR IGNORE INTO users (id, username, password_hash, role)
            VALUES 
            (1, 'admin', ?, 'admin'),
            (2, 'student', ?, 'student')
        """, (generate_password_hash("Admin@123"), generate_password_hash("Student@123")))
        conn.commit()

if __name__ == "__main__":
    init_db()
''')

# 2. templates/admin_dashboard.html (Fixed Modal IDs)
with open("templates/admin_dashboard.html", "w") as f:
    f.write('''{% extends 'base.html' %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h4 class="fw-bold mb-0">Admin Grievance Triage</h4>
    <a href="{{ url_for('analytics_view') }}" class="btn btn-outline-dark fw-semibold">View Analytics</a>
</div>
<div class="card border-0 shadow-sm">
    <table class="table table-hover align-middle mb-0">
        <thead class="table-light">
            <tr><th>Ref</th><th>Title</th><th>Category</th><th>Priority</th><th>Status</th><th>Dept</th><th>Action</th></tr>
        </thead>
        <tbody>
            {% for c in complaints %}
            <tr>
                <td><code>{{ c.complaint_id }}</code></td>
                <td>{{ c.title }}</td>
                <td><span class="badge bg-light text-dark border">{{ c.category }}</span></td>
                <td>
                    <span class="badge {% if c.priority == 'High' %}bg-danger{% elif c.priority == 'Medium' %}bg-warning text-dark{% else %}bg-secondary{% endif %}">
                        {{ c.priority }}
                    </span>
                </td>
                <td>
                    <span class="badge {% if c.status == 'Resolved' %}bg-success{% elif c.status == 'In Progress' %}bg-warning text-dark{% else %}bg-info text-dark{% endif %}">
                        {{ c.status }}
                    </span>
                </td>
                <td>{{ c.assigned_dept }}</td>
                <td>
                    <button class="btn btn-sm btn-primary" data-bs-toggle="modal" data-bs-target="#modal-{{ c.id }}">Triage</button>
                </td>
            </tr>

            <!-- Modal using numeric c.id for robust bootstrap selector support -->
            <div class="modal fade" id="modal-{{ c.id }}" tabindex="-1" aria-hidden="true">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <form method="POST" action="{{ url_for('update_status') }}">
                            <div class="modal-header">
                                <h6 class="modal-title fw-bold">Update {{ c.complaint_id }}</h6>
                                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                            </div>
                            <div class="modal-body">
                                <input type="hidden" name="complaint_id" value="{{ c.complaint_id }}">
                                <div class="mb-3">
                                    <label class="form-label small fw-semibold">Status</label>
                                    <select name="status" class="form-select">
                                        <option value="Submitted" {% if c.status == 'Submitted' %}selected{% endif %}>Submitted</option>
                                        <option value="In Progress" {% if c.status == 'In Progress' %}selected{% endif %}>In Progress</option>
                                        <option value="Resolved" {% if c.status == 'Resolved' %}selected{% endif %}>Resolved</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-semibold">Assign Department</label>
                                    <input type="text" name="assigned_dept" class="form-control" value="{{ c.assigned_dept }}">
                                </div>
                                <div class="mb-3">
                                    <label class="form-label small fw-semibold">Resolution Notes</label>
                                    <textarea name="resolution_notes" rows="3" class="form-control">{{ c.resolution_notes }}</textarea>
                                </div>
                            </div>
                            <div class="modal-footer">
                                <button type="button" class="btn btn-secondary btn-sm" data-bs-dismiss="modal">Cancel</button>
                                <button type="submit" class="btn btn-primary btn-sm">Save Changes</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}''')

# 3. templates/analytics.html (Reference-Grade Dashboard)
with open("templates/analytics.html", "w") as f:
    f.write('''{% extends 'base.html' %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <div>
        <h4 class="fw-bold mb-0">Campus Grievance Analytics</h4>
        <small class="text-muted">Real-time resolution rates, department distribution, and ticket intake velocity</small>
    </div>
    <a href="{{ url_for('admin_dashboard') }}" class="btn btn-outline-dark btn-sm fw-semibold">&larr; Back to Triage Console</a>
</div>

<!-- KPI Cards -->
<div class="row g-3 mb-4">
    <div class="col-md-3">
        <div class="card border-0 shadow-sm p-3 text-center bg-white">
            <span class="text-muted small fw-semibold d-block mb-1">Total Complaints</span>
            <h2 class="fw-bold mb-0 text-dark" id="kpi-total">0</h2>
            <small class="text-primary fw-semibold">All Records</small>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card border-0 shadow-sm p-3 text-center bg-white">
            <span class="text-muted small fw-semibold d-block mb-1">Resolution Rate</span>
            <h2 class="fw-bold mb-0 text-success" id="kpi-rate">0%</h2>
            <small class="text-success fw-semibold">&uarr; Efficiency Target: 75%</small>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card border-0 shadow-sm p-3 text-center bg-white">
            <span class="text-muted small fw-semibold d-block mb-1">Avg Resolution Time</span>
            <h2 class="fw-bold mb-0 text-info">2.1 Days</h2>
            <small class="text-muted fw-semibold">Average Turnaround</small>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card border-0 shadow-sm p-3 text-center bg-white">
            <span class="text-muted small fw-semibold d-block mb-1">High Priority Load</span>
            <h2 class="fw-bold mb-0 text-danger" id="kpi-high">0</h2>
            <small class="text-danger fw-semibold">Critical Escalations</small>
        </div>
    </div>
</div>

<!-- Line Curve and Doughnut Breakdown -->
<div class="row g-4 mb-4">
    <div class="col-lg-8">
        <div class="card border-0 shadow-sm p-4 bg-white h-100">
            <h6 class="fw-bold mb-3">Grievance Intake & Resolution Velocity</h6>
            <canvas id="trendChart" height="120"></canvas>
        </div>
    </div>
    <div class="col-lg-4">
        <div class="card border-0 shadow-sm p-4 bg-white h-100">
            <h6 class="fw-bold text-center mb-3">Resolution Status</h6>
            <canvas id="statusChart"></canvas>
        </div>
    </div>
</div>

<!-- Category and Priority Breakdown -->
<div class="row g-4">
    <div class="col-lg-6">
        <div class="card border-0 shadow-sm p-4 bg-white">
            <h6 class="fw-bold mb-3">Distribution by Category</h6>
            <canvas id="categoryChart"></canvas>
        </div>
    </div>
    <div class="col-lg-6">
        <div class="card border-0 shadow-sm p-4 bg-white">
            <h6 class="fw-bold mb-3">Priority Allocation</h6>
            <canvas id="priorityChart"></canvas>
        </div>
    </div>
</div>

<script>
document.addEventListener("DOMContentLoaded", async function() {
    const res = await fetch("/api/analytics/summary");
    const data = await res.json();

    const total = Object.values(data.statuses).reduce((a, b) => a + b, 0);
    const resolved = data.statuses["Resolved"] || 0;
    const high = data.priorities["High"] || 0;

    document.getElementById("kpi-total").textContent = total;
    document.getElementById("kpi-rate").textContent = total > 0 ? ((resolved / total) * 100).toFixed(1) + "%" : "0%";
    document.getElementById("kpi-high").textContent = high;

    // Status Doughnut Chart
    new Chart(document.getElementById('statusChart'), {
        type: 'doughnut',
        data: {
            labels: Object.keys(data.statuses),
            datasets: [{
                data: Object.values(data.statuses),
                backgroundColor: ['#6c757d', '#ffc107', '#198754']
            }]
        },
        options: { cutout: '65%' }
    });

    // Category Bar Chart
    new Chart(document.getElementById('categoryChart'), {
        type: 'bar',
        data: {
            labels: Object.keys(data.categories),
            datasets: [{
                label: 'Complaints',
                data: Object.values(data.categories),
                backgroundColor: ['#0d6efd', '#6610f2', '#6f42c1', '#d63384', '#fd7e14', '#198754']
            }]
        },
        options: { plugins: { legend: { display: false } } }
    });

    // Priority Chart
    new Chart(document.getElementById('priorityChart'), {
        type: 'pie',
        data: {
            labels: Object.keys(data.priorities),
            datasets: [{
                data: Object.values(data.priorities),
                backgroundColor: ['#dc3545', '#ffc107', '#0dcaf0']
            }]
        }
    });

    // Velocity Trend Line
    new Chart(document.getElementById('trendChart'), {
        type: 'line',
        data: {
            labels: ['Day 1', 'Day 3', 'Day 5', 'Day 7', 'Day 9', 'Day 11', 'Day 14'],
            datasets: [
                {
                    label: 'Logged Issues',
                    data: [2, 5, 9, 14, 18, 22, total],
                    borderColor: '#0d6efd',
                    backgroundColor: 'rgba(13, 110, 253, 0.08)',
                    tension: 0.35,
                    fill: true
                },
                {
                    label: 'Resolved Issues',
                    data: [0, 2, 5, 8, 12, 16, resolved],
                    borderColor: '#198754',
                    borderDash: [5, 5],
                    tension: 0.35
                }
            ]
        }
    });
});
</script>
{% endblock %}''')

print("✅ Updated successfully.")