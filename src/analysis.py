import os
from openai import OpenAI
from dotenv import load_dotenv
from database import fetch_reviews, update_sentiment
import json
from visuals import generate_wordcloud, generate_barchart
import time  # <-- NEW: Import the time module

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_sentiment_for_all():
    """Loop through all reviews and analyze each one with OpenAI, and then pass the data to the visualization functions."""
    try:
        reviews = fetch_reviews()
    except Exception as e:
        print(f"CRITICAL ERROR: Could not fetch reviews from database: {e}")
        print("Please check your database file, table name ('reviews'), and column names ('id', 'review_text').")
        return # Stop execution if we can't get data

    # Lists to hold all our data
    all_sentiments = []
    all_positive_aspects = []
    all_negative_aspects = []

    print("Starting analysis...")

    for review_id, text in reviews:
        
        # --- THIS IS THE FIX ---
        # Add a 1-second delay before *each* API call
        # This stops the API from rate-limiting us.
        time.sleep(1) 
        # --- END FIX ---
        
        analysis = get_detailed_analysis(text)

        if analysis:
            sentiment = analysis.get("sentiment", "Error")
            pos_aspects = analysis.get("positive_aspects", [])
            neg_aspects = analysis.get("negative_aspects", [])
            
            # Add data to our lists
            all_sentiments.append(sentiment)
            all_positive_aspects.extend(pos_aspects) 
            all_negative_aspects.extend(neg_aspects)

            #update_sentiment(review_id, sentiment) < -- temporarily disabled
            print(f"Review {review_id} {sentiment}): +{pos_aspects} / -{neg_aspects}")
        else:
            # This will now print for any review that failed
            print(f"Review {review_id}: Failed to analyze (skipped).")

    print("...Analysis complete!")
    print("\n--- Summary ---")
    print(f"Overall Sentiments: {all_sentiments}")
    print(f"All Positive Aspects: {all_positive_aspects}")
    print(f"All Negative Aspects: {all_negative_aspects}")

    # --- Step 3: Call Visualizers ---
    print("Generating visualizations...")
    
    # generate_barchart() # <-- This needs sentiment to be in the database first. Let's disable it for now.
    print("Bar chart generation skipped (requires database update).")

    # --- Generate two separate word clouds ---
    
    # Join all positive aspects into one giant string
    positive_text = " ".join(all_positive_aspects)
    if positive_text:
        generate_wordcloud(positive_text, "positive_aspects_wordcloud.png")
        print("Positive aspects word cloud generated.")
    else:
        print("No positive aspects found, skipping word cloud.")

    # Join all negative aspects into one giant string
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
        # Parse the response as JSON
        sentiment_json = json.loads(response.choices[0].message.content.strip())
        return sentiment_json
    except Exception as e:
        # UPDATED: More helpful error message
        print(f"Review skipped. API Error (likely rate limit or empty response): {e}")
        return None