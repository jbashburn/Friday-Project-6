import os
from openai import OpenAI
from dotenv import load_dotenv
from database import fetch_reviews, update_sentiment
import json
from visuals import generate_wordcloud, generate_barchart
import time

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
    """Loop through all reviews and analyze each one with OpenAI, and then pass the data to the visualization functions."""
    try:
        reviews = fetch_reviews()
    except Exception as e:
        print(f"CRITICAL ERROR: Could not fetch reviews from database: {e}")
        print("Please check your database file, table name ('reviews'), and column names ('id', 'review_text').")
        return # Stop execution if we can't get data

    all_sentiments = []
    all_positive_aspects = []
    all_negative_aspects = []

    print("Starting analysis with OpenAI API (with 2-second delay)...") 

    for review_id, text in reviews:
        
        # --- THE FIX ---
        # Increased delay from 1 to 2 seconds to respect the rate limit.
        time.sleep(2) 
        # --- END FIX ---
        
        analysis = get_detailed_analysis(text)

        if analysis:
            sentiment = analysis.get("sentiment", "Error")
            pos_aspects = analysis.get("positive_aspects", [])
            neg_aspects = analysis.get("negative_aspects", [])
            
            all_sentiments.append(sentiment)
            all_positive_aspects.extend(pos_aspects) 
            all_negative_aspects.extend(neg_aspects)

            print(f"Review {review_id} {sentiment}): +{pos_aspects} / -{neg_aspects}")
        else:
            print(f"Review {review_id}: Failed to analyze (skipped).")

    print("...Analysis complete!")
    print("\n--- Summary ---")
    print(f"Overall Sentiments: {all_sentiments}")
    print(f"All Positive Aspects: {all_positive_aspects}")
    print(f"All Negative Aspects: {all_negative_aspects}")

    # --- Step 3: Call Visualizers ---
    print("Generating visualizations...")
    
    print("Bar chart generation skipped (requires database update).")

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


# --- THIS IS THE OPENAI FUNCTION ---
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
            messages=[{"role": "user", "content": prompt}]
        )
        sentiment_json = json.loads(response.choices[0].message.content.strip())
        return sentiment_json
    except json.JSONDecodeError as e:
        # This will catch the 'char 0' error
        print(f"Review skipped. API Error: {e}")
        if 'response' in locals():
            print(f"DEBUG: OpenAI returned this (which is not JSON): {response.choices[0].message.content}")
        else:
            print("DEBUG: OpenAI returned an empty response or other connection error.")
        return None
    except Exception as e:
        # This will catch other errors (like authentication)
        print(f"Review skipped. A different API Error occurred: {e}")
        return None