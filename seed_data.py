import sqlite3
import random
from datetime import datetime, timedelta

conn = sqlite3.connect("grievance.db")
cursor = conn.cursor()

sample_complaints = [
    ("Projector flickering in Room 304", "Projector in Room 304 flickers and shuts down after 10 minutes of lecture.", "ECE Block", "Infrastructure", "High", "Resolved", "AV & Maintenance", "Replaced HDMI port and cable."),
    ("Power sockets dead on study desks", "Power outlets on the second-floor study desks are dead. Cannot charge laptops.", "Main Library", "Infrastructure", "Low", "Submitted", "Electrical Dept", ""),
    ("Elevator stuck on 3rd floor", "Elevator in Main Academic Block is stuck and making grinding noises.", "Main Academic Block", "Infrastructure", "High", "Resolved", "Estate Office", "Hydraulic sensor serviced."),
    ("Data Structures faculty absence", "Faculty for Data Structures has missed classes for two consecutive weeks without substitute.", "CS Department", "Academics", "High", "In Progress", "Academic Dean", "Arranged guest faculty for makeup syllabus."),
    ("Internal marks portal error", "Internal assessment marks were not updated on student portal before deadline.", "Exam Cell", "Academics", "Medium", "Resolved", "Exam Section", "Marks re-uploaded and verified on portal."),
    ("Elective timetable clash", "Elective 2 lecture timetable clashes with mandatory ML lab practical.", "Mechanical Block", "Academics", "Medium", "Submitted", "Academic Dean", ""),
    ("Reference textbooks unavailable", "Textbooks listed in syllabus are unavailable in library reference section.", "Central Library", "Academics", "Low", "In Progress", "Library Section", "Purchase indent approved for 15 copies."),
    ("Water geyser broken in Block 2", "Water geyser in Hostel Block 2 is broken, no hot water in winter.", "Boys Hostel 2", "Hostel", "High", "Resolved", "Hostel Warden", "New heating coil installed."),
    ("Subpar mess dinner quality", "Mess dinner was undercooked and cold. Need hygiene inspection.", "Hostel Mess 1", "Hostel", "Medium", "In Progress", "Mess Committee", "Notice issued to catering contractor."),
    ("Severe water shortage 3rd floor", "Severe water shortage on the third floor washrooms since morning.", "Hostel Block 3", "Hostel", "High", "In Progress", "Plumbing Dept", "Overhead tank motor repaired."),
    ("Bus Route 4 delayed by 50 mins", "College bus Route 4 arrived 50 minutes late at terminal stop.", "Route 4 Stop", "Transport", "Medium", "Resolved", "Transport In-charge", "Alternative backup bus deployed on route."),
    ("Reckless driving Route 11", "Bus driver on Route 11 was overspeeding and driving dangerously on highway.", "City Route 11", "Transport", "High", "In Progress", "Transport In-charge", "Driver summoned for inquiry."),
    ("Scholarship verification pending", "Scholarship verification documents have been pending for a month with registrar.", "Admin Block", "Administration", "Medium", "In Progress", "Registrar Office", "Documents forwarded to state portal."),
    ("Fee payment receipt not generated", "Fee receipt was not generated after successful online bank deduction.", "Accounts Section", "Administration", "High", "Resolved", "Accounts Dept", "Transaction reconciled; e-receipt emailed."),
    ("Cafeteria washrooms dirty", "Restrooms near ground floor cafeteria are filthy and lack running water.", "Canteen Area", "Cleanliness and Sanitation", "High", "In Progress", "Sanitation Head", "Janitor assigned on hourly rotation."),
    ("Dustbins overflowing behind Block C", "Garbage containers behind block C are overflowing with waste paper and plastic.", "Behind Block C", "Cleanliness and Sanitation", "Medium", "Resolved", "Sanitation Head", "Cleared and added two extra dumpsters."),
    ("Stray dogs in cafeteria", "Stray dogs wandering freely inside college cafeteria dining area.", "Cafeteria", "Cleanliness and Sanitation", "High", "In Progress", "Campus Security", "Gate netting reinforced."),
    ("Water dispenser foul smell", "Water dispenser near department lobby smells foul.", "Dept Lobby", "Cleanliness and Sanitation", "High", "Resolved", "Estate Office", "RO filters and ultraviolet candles replaced.")
]

for idx, item in enumerate(sample_complaints, start=200):
    cid = f"GRV-{idx:04d}"
    cursor.execute("""
        INSERT OR IGNORE INTO complaints 
        (complaint_id, student_id, title, description, location, category, subcategory, priority, status, assigned_dept, resolution_notes)
        VALUES (?, 2, ?, ?, ?, ?, 'General', ?, ?, ?, ?)
    """, (cid, item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7]))

conn.commit()
conn.close()
print("✅ Seeded 18 realistic complaints across all departments!")
