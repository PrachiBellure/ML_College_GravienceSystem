# ML-Powered College Grievance Management & Analytics System

An end-to-end intelligent campus grievance redressal and analytical platform. The system leverages Natural Language Processing (NLP) and supervised machine learning to classify unstructured student complaints across institutional departments, detect duplicate tickets in real time using vector similarity, and provide administrative decision-support analytics.

---

## Key Features

- **Automated Departmental Routing:** Uses a TF-IDF vectorizer (unigrams + bigrams) paired with a Multinomial Logistic Regression classifier to route complaints across 6 distinct campus departments.
- **Real-Time Duplicate Detection:** Computes pairwise Cosine Similarity ($\ge 35\%$ threshold) against active grievances in the database to flag recurring complaints.
- **Heuristic Urgency Scoring:** Assigns dynamic priority ratings (**High**, **Medium**, **Low**) on submission based on emergency and disruption keyword patterns.
- **Administrative Triage Console:** Role-gated portal allowing campus administrators to reassign departments, modify lifecycle states (`Submitted` $\rightarrow$ `In Progress` $\rightarrow$ `Resolved`), and attach audited resolution notes.
- **Executive Analytics Engine:** Interactive Chart.js dashboards tracking resolution velocity, intake distributions, and key institutional performance metrics.
- **Secure Architecture:** Built with parameterized SQL execution and PBKDF2/SHA-256 password salting.

---

## Supported Institutional Departments

1. **Infrastructure:** Wi-Fi outages, projector malfunctions, lab computer failures, electrical issues.
2. **Academics:** Timetable clashes, faculty absences, exam queries, library resource requests.
3. **Hostel:** Room maintenance, plumbing issues, water geyser breakdowns, mess food quality.
4. **Transport:** College bus delays, route alterations, schedule discrepancies.
5. **Cleanliness & Sanitation:** Restroom hygiene, waste disposal, cafeteria sanitation.
6. **Administration:** Fee receipt issues, scholarship clearances, hall ticket verification.

---

## Tech Stack

- **Backend:** Python, Flask
- **Machine Learning & NLP:** Scikit-learn (TF-IDF Vectorizer, Multinomial Logistic Regression, Cosine Similarity), Pandas, NumPy
- **Database:** SQLite3
- **Frontend:** Jinja2 Templates, Bootstrap 5, Chart.js
- **WSGI / Production Ready:** Gunicorn

---

## Project Structure

```text
├── ml_engine/
│   ├── dataset.csv         # Domain-specific campus training corpus
│   ├── predictor.py        # Inference pipeline & Cosine Similarity logic
│   ├── model.pkl           # Serialized Logistic Regression model
│   └── tfidf.pkl           # Serialized TF-IDF vocabulary matrix
├── templates/              # Jinja2 HTML templates (Student & Admin dashboards)
├── static/css/             # Responsive UI styling
├── app.py                  # Core Flask controller and routing logic
├── database.py             # SQLite schema and user management functions
├── seed_data.py            # Test dataset seeder with realistic complaints
├── setup_project.py        # Environment setup and model training pipeline
├── grievance.db            # Local SQLite database
└── requirements.txt        # Python dependency manifest.


## Screenshots

| Student Grievance Submission | Duplicate Ticket Detection |
| :---: | :---: |
| ![Student Dashboard](screenshots/student_dashboard.png) | ![Duplicate Alert](screenshots/duplicate_alert.png) |

| Admin Triage Console | Executive Analytics Dashboard |
| :---: | :---: |
| ![Admin Triage](screenshots/admin_triage.png) | ![Analytics Dashboard](screenshots/analytics_dashboard.png) |
