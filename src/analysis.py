import os
from openai import OpenAI
from dotenv import load_dotenv
from database import fetch_reviews, update_sentiment
import json
from visuals import create_word_clouds, create_sentiment_barchart

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_sentiment_for_all():
    """Loop through all reviews and analyze each one with OpenAI, and then pass the data to the visualization functions."""
    reviews = fetch_reviews()

    # Lists to hold all our data
    all_sentiments = []
    all_positive_aspects = []
    all_negative_aspects = []

    print("Starting analysis...")

    for review_id, text in reviews:
        analysis = get_detailed_analysis(text)

        if analysis:
            sentiment = analysis.get("sentiment", "Error")
            pos_aspects = analysis.get("positive_aspects", [])
            neg_aspects = analysis.get("negative_aspects", [])
            
            # Add data to our lists
            all_sentiments.append(sentiment)
            all_positive_aspects.extend(pos_aspects) # .extend adds all items from a list
            all_negative_aspects.extend(neg_aspects)

        #update_sentiment(review_id, sentiment) < -- temporarily disabled
        print(f"Review {review_id}: {sentiment}"): +{pos_aspects} / -{neg_aspects}")

    print("...Analysis complete!")
    print("\n--- Summary ---")
    print(f"Overall Sentiments: {all_sentiments}")
    print(f"All Positive Aspects: {all_positive_aspects}")
    print(f"All Negative Aspects: {all_negative_aspects}")

    # --- Step 3: Call Visualizers ---
    # This will generate and show our charts
    print("Generating visualizations...")
    create_sentiment_barchart(all_sentiments)
    create_word_clouds(all_positive_aspects, all_negative_aspects)
    print("Visualizations complete. Check the new windows.")

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
        sentiment = response.choices[0].message.content.strip()
        return sentiment
    except Exception as e:
        print("Error:", e)
        return "Error"
