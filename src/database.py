import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "feedback.db")

def fetch_reviews():
    """Return all review text and IDs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Adjust column/table names to match your database
    cursor.execute("SELECT id, review_text FROM reviews")
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_sentiment(review_id, sentiment):
    """Save sentiment result for a specific review."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Add a sentiment column to your table if it doesn’t exist yet
    cursor.execute("UPDATE reviews SET sentiment=? WHERE id=?", (sentiment, review_id))
    conn.commit()
    conn.close()
