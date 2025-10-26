import sqlite3
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "feedback.db")
VISUALS_DIR = os.path.join(os.path.dirname(__file__), "..", "visuals")

def generate_barchart():
    """Create a bar chart of sentiment counts."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # FIXED: Changed 'feedback' to 'reviews'
    cursor.execute("SELECT sentiment, COUNT(*) FROM reviews GROUP BY sentiment")
    data = cursor.fetchall()
    conn.close()

    sentiments = [row[0] for row in data]
    counts = [row[1] for row in data]

    plt.bar(sentiments, counts)
    plt.title("Sentiment Distribution")
    plt.xlabel("Sentiment")
    plt.ylabel("Count")
    plt.savefig(os.path.join(VISUALS_DIR, "sentiment_chart.png"))
    plt.close()

def generate_wordcloud():
    """Generate a word cloud of all feedback text."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # FIXED: Changed 'review' to 'review_text' and 'feedback' to 'reviews'
    cursor.execute("SELECT review_text FROM reviews")
    text = " ".join([row[0] for row in cursor.fetchall()])
    conn.close()

    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text)
    wordcloud.to_file(os.path.join(VISUALS_DIR, "aspect_wordcloud.png"))