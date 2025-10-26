import os
from openai import OpenAI
from dotenv import load_dotenv
from database import fetch_reviews, update_sentiment

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_sentiment_for_all():
    """Loop through all reviews and analyze each one with OpenAI."""
    reviews = fetch_reviews()
    for review_id, text in reviews:
        sentiment = get_sentiment(text)
        update_sentiment(review_id, sentiment)
        print(f"Review {review_id}: {sentiment}")

def get_sentiment(text):
    """Ask OpenAI for sentiment (positive, negative, or neutral)."""
    prompt = f"""
    Determine the sentiment of this customer review about the Apple Vision Pro.
    Respond with only one word: Positive, Negative, or Neutral.

    Review: {text}
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
