import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import collections  # Built-in counter, no install needed

# Finds the 'visuals' folder one level up from this 'src' folder
VISUALS_DIR = os.path.join(os.path.dirname(__file__), "..", "visuals")

# --- MAKE SURE THE VISUALS DIRECTORY EXISTS ---
try:
    os.makedirs(VISUALS_DIR, exist_ok=True)
except OSError as e:
    print(f"Error creating visuals directory: {e}")

def generate_barchart(sentiment_list):
    """Create a bar chart of sentiment counts from a list."""
    
    if not sentiment_list:
        print("Skipping bar chart: No sentiment data provided.")
        return
        
    # 1. Use Counter to count items in the list (e.g., {'Positive': 40, 'Negative': 35, ...})
    data = collections.Counter(sentiment_list)

    # 2. Get the labels (sentiments) and values (counts)
    sentiments = list(data.keys())
    counts = list(data.values())

    # 3. Create the plot
    plt.figure(figsize=(8, 6))
    plt.bar(sentiments, counts, color=['green', 'red', 'grey', 'blue']) # Added colors
    plt.title("Sentiment Distribution")
    plt.xlabel("Sentiment")
    plt.ylabel("Count")
    
    # 4. Save the plot
    plt.savefig(os.path.join(VISUALS_DIR, "sentiment_chart.png"))
    plt.close() # Close plot to free up memory

def generate_wordcloud(text_data, filename):
    """Generate a word cloud from the provided text and save to a file."""
    
    if not text_data.strip():
        print(f"Skipping {filename}: No text data provided.")
        return

    # Generate word cloud
    wordcloud = WordCloud(width=800, 
                          height=400, 
                          background_color="white",
                          colormap="viridis").generate(text_data)
                          
    save_path = os.path.join(VISUALS_DIR, filename)
    
    # Save the file
    wordcloud.to_file(save_path)

#final visuals file