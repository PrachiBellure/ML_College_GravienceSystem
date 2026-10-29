import os
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DATA = [
    ("Wi-Fi in Block B is completely down and not connecting.", "Infrastructure"),
    ("Slow internet speed and frequent disconnections in library.", "Infrastructure"),
    ("Projector in Room 304 is flickering and turns off.", "Infrastructure"),
    ("Power outlets on the second-floor study desks are dead.", "Infrastructure"),
    ("Elevator in Main Academic Block is stuck on third floor.", "Infrastructure"),
    ("Data Structures professor has been absent for two weeks.", "Academics"),
    ("Internal assessment marks were not updated on student portal.", "Academics"),
    ("Elective subject clashed with mandatory lab session.", "Academics"),
    ("Textbooks listed in syllabus are unavailable in library.", "Academics"),
    ("Water geyser in Hostel Block 2 is broken, no hot water.", "Hostel"),
    ("Mess dinner was cold and quality was subpar today.", "Hostel"),
    ("Hostel room door latch is broken and cannot be locked.", "Hostel"),
    ("Severe water shortage on the third floor washrooms.", "Hostel"),
    ("College bus Route 4 arrived 50 minutes late at stop.", "Transport"),
    ("Bus driver on Route 11 was overspeeding dangerously.", "Transport"),
    ("Evening shuttle service is consistently overcrowded.", "Transport"),
    ("RFID card reader fails to authenticate student passes.", "Transport"),
    ("Scholarship verification documents have been pending.", "Administration"),
    ("Fee receipt was not generated after online deduction.", "Administration"),
    ("Bonafide certificate request ignored by admin desk.", "Administration"),
    ("Restrooms near ground floor cafeteria are filthy.", "Cleanliness and Sanitation"),
    ("Garbage containers behind block C are overflowing.", "Cleanliness and Sanitation"),
    ("Stray dogs wandering freely inside college cafeteria.", "Cleanliness and Sanitation"),
    ("Water dispenser near department lobby smells foul.", "Cleanliness and Sanitation")
]

def train():
    df = pd.DataFrame(RAW_DATA * 5, columns=["description", "category"])
    df.to_csv(os.path.join(BASE_DIR, "dataset.csv"), index=False)

    vec = TfidfVectorizer(ngram_range=(1, 2), stop_words="english")
    X = vec.fit_transform(df["description"])
    y = df["category"]

    model = LogisticRegression(max_iter=1000)
    model.fit(X, y)

    with open(os.path.join(BASE_DIR, "model.pkl"), "wb") as f:
        pickle.dump(model, f)
    with open(os.path.join(BASE_DIR, "tfidf.pkl"), "wb") as f:
        pickle.dump(vec, f)
    print("ML model and vectorizer saved.")

if __name__ == "__main__":
    train()
