import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "feedback.db")

def fetch_reviews():
    """Return all review text and IDs."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, review_text FROM reviews")
    rows = cursor.fetchall()
    conn.close()
    return rows

# We have removed the 'update_sentiment' function
# as we are not allowed to modify the database.