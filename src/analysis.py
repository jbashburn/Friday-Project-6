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
except Exception as e:
    # Use print here, as queue isn't running yet
    print(f"CRITICAL ERROR: Failed to configure OpenAI API: {e}") 
# --- END ---


def analyze_sentiment_for_all(log_queue): # <-- NEW: Accept log_queue
    """
    Loop through all reviews, analyze them with OpenAI,
    and then call visualization functions.
    Logs progress to the provided queue.
    """
    try:
        reviews = fetch_reviews()
        if not reviews:
            log_queue.put("CRITICAL ERROR: No reviews found in database.\n")
            return
        log_queue.put(f"Successfully loaded {len(reviews)} reviews from database.\n")

    except Exception as e:
        log_queue.put(f"CRITICAL ERROR: Could not fetch reviews from database: {e}\n")
        return 

    all_sentiments = []
    all_positive_aspects = []
    all_negative_aspects = []

    log_queue.put(f"Starting analysis of {len(reviews)} reviews (0.5s delay)...\n") 

    for index, (review_id, text) in enumerate(reviews):
        
        # --- SPEED: Set to 0.5 seconds ---
        # If you get a Rate Limit error, change this to 1 or 2
        time.sleep(0.5) 
        
        analysis = get_detailed_analysis(text, log_queue) # Pass queue for error logging

        if analysis:
            sentiment = analysis.get("sentiment", "Error")
            pos_aspects = analysis.get("positive_aspects", [])
            neg_aspects = analysis.get("negative_aspects", [])
            
            all_sentiments.append(sentiment)
            all_positive_aspects.extend(pos_aspects)
            all_negative_aspects.extend(neg_aspects)
            
            # --- THIS IS THE LIVE UPDATE ---
            log_msg = f"Review {review_id} ({index+1}/{len(reviews)}) {sentiment}: +{pos_aspects} / -{neg_aspects}\n"
            log_queue.put(log_msg)
            # --- END LIVE UPDATE ---
            
        else:
            log_queue.put(f"Review {review_id}: Failed to analyze (skipped).\n")
            all_sentiments.append("Error")

    log_queue.put("\n...Analysis loop complete!\n")

    # --- Step 3: Call Visualizers ---
    log_queue.put("Generating visualizations...\n")
    
    try:
        generate_barchart(all_sentiments)
        log_queue.put("Sentiment bar chart generated.\n")
    except Exception as e:
        log_queue.put(f"Bar chart generation FAILED: {e}\n")

    # --- Generate word clouds ---
    positive_text = " ".join(all_positive_aspects)
    if positive_text:
        generate_wordcloud(positive_text, "positive_aspects_wordcloud.png")
        log_queue.put("Positive aspects word cloud generated.\n")
    else:
        log_queue.put("No positive aspects found, skipping word cloud.\n")

    negative_text = " ".join(all_negative_aspects)
    if negative_text:
        generate_wordcloud(negative_text, "negative_aspects_wordcloud.png")
        log_queue.put("Negative aspects word cloud generated.\n")
    else:
        log_queue.put("No negative aspects found, skipping word cloud.\n")

    log_queue.put("Visualizations complete.\n")


def get_detailed_analysis(text, log_queue): # <-- NEW: Accept log_queue
    """
    Ask OpenAI for a detailed analysis and return structured JSON.
    Logs errors to the provided queue.
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
            response_format={"type": "json_object"}, # Force JSON output
            messages=[{"role": "user", "content": prompt}]
        )
        
        sentiment_json = json.loads(response.choices[0].message.content)
        return sentiment_json
    
    except json.JSONDecodeError as e:
        log_queue.put(f"Review skipped. API Error: {e}\n")
        if 'response' in locals():
            log_queue.put(f"DEBUG: OpenAI returned (not JSON): {response.choices[0].message.content}\n")
        else:
            log_queue.put("DEBUG: OpenAI returned an empty response or other connection error.\n")
        return None
    except Exception as e:
        log_queue.put(f"Review skipped. A different API Error occurred: {e}\n")
        return None

