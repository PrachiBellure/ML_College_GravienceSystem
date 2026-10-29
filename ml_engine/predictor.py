import os
import pickle
from sklearn.metrics.pairwise import cosine_similarity

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE_DIR, "model.pkl"), "rb") as f:
    model = pickle.load(f)
with open(os.path.join(BASE_DIR, "tfidf.pkl"), "rb") as f:
    vectorizer = pickle.load(f)

HIGH_PRIORITY = ["danger", "hazard", "fire", "shock", "leakage", "broken", "emergency", "stuck", "shortage"]
LOW_PRIORITY = ["slow", "delayed", "suggestion", "minor", "noise"]

def classify_text(text):
    if not text.strip():
        return "Other", "General"
    vec = vectorizer.transform([text])
    cat = model.predict(vec)[0]
    return cat, "General Issue"

def assign_priority(text):
    t = text.lower()
    if any(k in t for k in HIGH_PRIORITY):
        return "High"
    if any(k in t for k in LOW_PRIORITY):
        return "Low"
    return "Medium"

def find_similar(target_text, records, threshold=0.35):
    if not records or not target_text.strip():
        return []
    corpus = [r["description"] for r in records]
    corpus_vecs = vectorizer.transform(corpus)
    target_vec = vectorizer.transform([target_text])
    scores = cosine_similarity(target_vec, corpus_vecs)[0]
    
    matches = []
    for idx, s in enumerate(scores):
        if s >= threshold:
            matches.append({
                "complaint_id": records[idx]["complaint_id"],
                "title": records[idx]["title"],
                "similarity": round(float(s) * 100, 1),
                "status": records[idx]["status"]
            })
    return sorted(matches, key=lambda x: x["similarity"], reverse=True)[:3]
