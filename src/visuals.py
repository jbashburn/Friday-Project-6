import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
# We no longer need sqlite3 here
# We do not need DB_PATH here

VISUALS_DIR = os.path.join(os.path.dirname(__file__), "..", "visuals")

# --- MAKE SURE THE VISUALS DIRECTORY EXISTS ---
if not os.path.exists(VISUALS_DIR):
    os.makedirs(VISUALS_DIR)

def generate_barchart(sentiment_data_series):
    """Create a bar chart of sentiment counts from a pandas Series."""
    
    # Use pandas to count the sentiments
    data = sentiment_data_series.value_counts()

    sentiments = data.index
    counts = data.values

    plt.figure(figsize=(8, 6)) # Make the chart a bit bigger
    plt.bar(sentiments, counts, color=['green', 'red', 'grey'])
    plt.title("Sentiment Distribution")
    plt.xlabel("Sentiment")
    plt.ylabel("Count")
    plt.savefig(os.path.join(VISUALS_DIR, "sentiment_chart.png"))
    plt.close()

def generate_wordcloud(text_data, filename):
    """Generate a word cloud from the provided text and save to a file."""
    
    # Check if text is empty
    if not text_data.strip():
        print(f"Skipping {filename}: No text data provided.")
        return

    wordcloud = WordCloud(width=800, height=400, background_color="white").generate(text_data)
    save_path = os.path.join(VISUALS_DIR, filename)
    wordcloud.to_file(save_path)