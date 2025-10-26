import sqlite3
import os

# Finds the 'data' folder one level up from this 'src' folder
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "feedback.db")

def fetch_reviews():
    """Return all review text and IDs."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Fetches all reviews from the 'reviews' table
        cursor.execute("SELECT id, review_text FROM reviews")
        rows = cursor.fetchall()
        conn.close()
        return rows
    except sqlite3.Error as e:
        print(f"CRITICAL: Database connection error or query failed: {e}")
        print(f"Attempted to connect to: {DB_PATH}")
        print("Please ensure 'data/feedback.db' exists and the table is named 'reviews'.")
        return None # Return None to signal an error
