import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import time
import pandas as pd  # <-- NEW: Import pandas

# --- Import our functions ---
from database import fetch_reviews 
# We no longer import any 'save' function
from visuals import generate_wordcloud, generate_barchart

load_dotenv()

# --- Configure the OpenAI API key ---
try:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if OPENAI_API_KEY:
        print(f"DEBUG: Found API Key starting with: {OPENAI_API_KEY[:8]}...")
    else:
        print("DEBUG: ERROR! OPENAI_API_KEY not found in .env file.")
    
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    client = OpenAI(api_key=OPENAI_API_KEY) 
except Exception as e:
    print(f"CRITICAL ERROR: Failed to configure OpenAI API: {e}")
    print("Please make sure your .env file has a valid OPENAI_API_KEY.")
# --- END ---


def analyze_sentiment_for_all():
    """Loop through all reviews, analyze them, and store in-memory."""
    try:
        # 1. Fetch data from database
        reviews = fetch_reviews()
        if not reviews:
            print("CRITICAL ERROR: No reviews found in database.")
            return
            
        # 2. Load data into a pandas DataFrame
        df = pd.DataFrame(reviews, columns=['id', 'review_text'])
        print(f"Successfully loaded {len(df)} reviews into DataFrame.")

    except Exception as e:
        print(f"CRITICAL ERROR: Could not fetch reviews from database: {e}")
        print("Please check your database file, table name ('reviews'), and column names ('id', 'review_text').")
        return 

    # 3. Create empty lists to store results
    sentiments = []
    positive_aspects_list = []
    negative_aspects_list = []

    print("Starting analysis with OpenAI API (with 2-second delay)...") 

    # 4. Loop through the DataFrame and analyze
    for index, row in df.iterrows():
        review_id = row['id']
        text = row['review_text']
        
        time.sleep(2) 
        analysis = get_detailed_analysis(text)

        if analysis:
            sentiment = analysis.get("sentiment", "Error")
            pos_aspects = analysis.get("positive_aspects", [])
            neg_aspects = analysis.get("negative_aspects", [])
            
            # Add results to our lists
            sentiments.append(sentiment)
            positive_aspects_list.append(pos_aspects)
            negative_aspects_list.append(neg_aspects)
            
            print(f"Review {review_id} {sentiment}): +{pos_aspects} / -{neg_aspects}")
        else:
            print(f"Review {review_id}: Failed to analyze (skipped).")
            # Add "Error" placeholders to keep lists in sync
            sentiments.append("Error")
            positive_aspects_list.append([])
            negative_aspects_list.append([])

    print("...Analysis complete!")
    
    # 5. Add the results as new columns to our DataFrame
    df['sentiment'] = sentiments
    df['positive_aspects'] = positive_aspects_list
    df['negative_aspects'] = negative_aspects_list

    print("\n--- Analysis DataFrame (Top 5) ---")
    print(df.head())
    print("---------------------------------")


    # --- Step 6: Call Visualizers ---
    print("Generating visualizations...")
    
    try:
        # Pass the 'sentiment' column (a pandas Series)
        generate_barchart(df['sentiment'])
        print("Sentiment bar chart generated.")
    except Exception as e:
        print(f"Bar chart generation FAILED: {e}")

    # --- Generate word clouds ---
    # We must "flatten" the list of lists into one big list of words
    
    # Positive
    all_positive_words = [item for sublist in df['positive_aspects'] for item in sublist]
    positive_text = " ".join(all_positive_words)
    if positive_text:
        generate_wordcloud(positive_text, "positive_aspects_wordcloud.png")
        print("Positive aspects word cloud generated.")
    else:
        print("No positive aspects found, skipping word cloud.")

    # Negative
    all_negative_words = [item for sublist in df['negative_aspects'] for item in sublist]
    negative_text = " ".join(all_negative_words)
    if negative_text:
        generate_wordcloud(negative_text, "negative_aspects_wordcloud.png")
        print("Negative aspects word cloud generated.")
    else:
        print("No negative aspects found, skipping word cloud.")

    print("Visualizations complete. Check the 'visuals' folder.")


# --- THIS IS THE OPENAI FUNCTION (WITH THE JSON FIX) ---
def get_detailed_analysis(text):
    """
    Ask OpenAI for a detailed analysis and return structured JSON.
    """
    prompt = f"""
    Analyze this customer review about the Apple Vision Pro.
    Provide a JSON response with three keys:
    1. "sentiment": (string) The overall sentiment. Must be one of: Positive, Negative, or Neutral.
    2. "positive_aspects": (list of strings) A list of specific features or aspects the user liked.
    3. "negative_aspects": (list of strings) A list of specific features or aspects the user disliked.

    If there are no positive or negative aspects, return an empty list [].

    Review: "{text}"

    JSON Response:
    """
   
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            # --- THIS IS THE FIX ---
            # Tell the API to *only* return valid JSON.
            response_format={"type": "json_object"}, 
            # --- END FIX ---
            messages=[{"role": "user", "content": prompt}]
        )
        
        # Now this should always be valid JSON
        sentiment_json = json.loads(response.choices[0].message.content)
        return sentiment_json
    
    except json.JSONDecodeError as e:
        print(f"Review skipped. API Error: {e}")
        if 'response' in locals():
            print(f"DEBUG: OpenAI returned this (which is not JSON): {response.choices[0].message.content}")
        else:
            print("DEBUG: OpenAI returned an empty response or other connection error.")
        return None
    except Exception as e:
        print(f"Review skipped. A different API Error occurred: {e}")
        return None