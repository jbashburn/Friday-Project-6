import os
from openai import OpenAI
from dotenv import load_dotenv
import json
import time
import collections # Built-in library, no install needed

# --- Import our other modules ---
from database import fetch_reviews 
from visuals import generate_wordcloud, generate_barchart

# Load API Key from .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# --- Configure the OpenAI API key ---
try:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY not found in .env file.")
    client = OpenAI(api_key=OPENAI_API_KEY) 
    print("DEBUG: OpenAI client configured successfully.")
except Exception as e:
    print(f"CRITICAL ERROR: Failed to configure OpenAI API: {e}")
# --- END ---


def analyze_sentiment_for_all():
    """
    Loop through all reviews, analyze them with OpenAI,
    and then call visualization functions.
    """
    try:
        reviews = fetch_reviews()
        if not reviews:
            print("CRITICAL ERROR: No reviews found in database.")
            return
        print(f"Successfully loaded {len(reviews)} reviews from database.")

    except Exception as e:
        print(f"CRITICAL ERROR: Could not fetch reviews from database: {e}")
        return 

    # 1. Create empty lists to store results
    all_sentiments = []
    all_positive_aspects = []
    all_negative_aspects = []

    print("Starting analysis with OpenAI API (with 0.5s delay)...") 

    # 2. Loop through reviews and analyze
    for review_id, text in reviews:
        
        # --- SPEED FIX: Set to 0.5 seconds ---
        # If you get a Rate Limit error, change this to 1 or 2
        time.sleep(0.5) 
        
        analysis = get_detailed_analysis(text) 

        if analysis:
            sentiment = analysis.get("sentiment", "Error")
            pos_aspects = analysis.get("positive_aspects", [])
            neg_aspects = analysis.get("negative_aspects", [])
            
            # Add results to our lists
            all_sentiments.append(sentiment)
            all_positive_aspects.extend(pos_aspects) # .extend() adds all items from the list
            all_negative_aspects.extend(neg_aspects)
            
            print(f"Review {review_id} ({sentiment}): +{pos_aspects} / -{neg_aspects}")
        else:
            print(f"Review {review_id}: Failed to analyze (skipped).")
            all_sentiments.append("Error") # Add placeholder to keep lists in sync

    print("...Analysis complete!")

    # --- Step 3: Call Visualizers ---
    print("Generating visualizations...")
    
    try:
        # Pass the list of sentiments
        generate_barchart(all_sentiments)
        print("Sentiment bar chart generated.")
    except Exception as e:
        print(f"Bar chart generation FAILED: {e}")

    # --- Generate word clouds ---
    positive_text = " ".join(all_positive_aspects)
    if positive_text:
        generate_wordcloud(positive_text, "positive_aspects_wordcloud.png")
        print("Positive aspects word cloud generated.")
    else:
        print("No positive aspects found, skipping word cloud.")

    negative_text = " ".join(all_negative_aspects)
    if negative_text:
        generate_wordcloud(negative_text, "negative_aspects_wordcloud.png")
        print("Negative aspects word cloud generated.")
    else:
        print("No negative aspects found, skipping word cloud.")

    print("Visualizations complete. Check the 'visuals' folder.")


def get_detailed_analysis(text):
    """
    Ask OpenAI for a detailed analysis and return structured JSON.
    """
    prompt = f"""
    Analyze this customer review about the Apple Vision Pro.
    Provide a JSON response with three keys:
    1. "sentiment": (string) The overall sentiment. Must be one of: Positive, Negative, or Neutral.
    2. "positive_aspects": (list of strings) A list of specific features or aspects the user liked (e.g., "display", "eye tracking").
    3. "negative_aspects": (list of strings) A list of specific features or aspects the user disliked (e.g., "battery life", "weight", "price").

    If there are no positive or negative aspects, return an empty list [].

    Review: "{text}"

    JSON Response:
    """
   
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            # --- THIS IS THE JSON FIX ---
            # Tell the API to *only* return valid JSON.
            response_format={"type": "json_object"}, 
            # --- END FIX ---
            messages=[{"role": "user", "content": prompt}]
        )
        
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
