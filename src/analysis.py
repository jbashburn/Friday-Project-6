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
    print(f"CRITICAL ERROR: Failed to configure OpenAI API: {e}") 
# --- END ---

# Define path for the new recommendations file
RECOMMENDATIONS_PATH = os.path.join(os.path.dirname(__file__), "..", "visuals", "recommendations.txt")


def analyze_sentiment_for_all(log_queue):
    """
    Loop through all reviews, analyze them, generate visuals,
    and finally, generate a recommendations report.
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
        
        time.sleep(0.01) 
        analysis = get_detailed_analysis(text, log_queue) 

        if analysis:
            sentiment = analysis.get("sentiment", "Error")
            pos_aspects = analysis.get("positive_aspects", [])
            neg_aspects = analysis.get("negative_aspects", [])
            
            all_sentiments.append(sentiment)
            all_positive_aspects.extend(pos_aspects)
            all_negative_aspects.extend(neg_aspects)
            
            log_msg = f"Review {review_id} ({index+1}/{len(reviews)}) {sentiment}: +{pos_aspects} / -{neg_aspects}\n"
            log_queue.put(log_msg)
            
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

    # --- NEW: Step 4: Generate Recommendations ---
    log_queue.put("\nGenerating final recommendations report...\n")
    try:
        # Get the Top 5 most common positive and negative aspects
        pos_counts = collections.Counter(all_positive_aspects).most_common(5)
        neg_counts = collections.Counter(all_negative_aspects).most_common(5)

        # Call new function to get report from OpenAI
        report_text = get_recommendations(pos_counts, neg_counts, len(reviews), log_queue)
        
        if report_text:
            # Save the report to a file
            with open(RECOMMENDATIONS_PATH, "w", encoding="utf-8") as f:
                f.write(report_text)
            log_queue.put("Recommendations report saved to visuals/recommendations.txt\n")
        else:
            log_queue.put("Failed to generate recommendations report.\n")
            
    except Exception as e:
        log_queue.put(f"Failed to generate recommendations report: {e}\n")
    # --- END NEW STEP ---


def get_detailed_analysis(text, log_queue):
    """
    Ask OpenAI for a detailed analysis of a *single review*.
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
            response_format={"type": "json_object"}, 
            messages=[{"role": "user", "content": prompt}]
        )
        sentiment_json = json.loads(response.choices[0].message.content)
        return sentiment_json
    except Exception as e:
        log_queue.put(f"Review skipped. API Error: {e}\n")
        return None


# --- NEW: Function to generate final report ---
def get_recommendations(pos_counts, neg_counts, total_reviews, log_queue):
    """
    Ask OpenAI to act as a product manager and write a recommendations report
    based on the aggregated data.
    """
    
    # Format the counts into a nice string
    pos_summary = ", ".join([f"'{item}' ({count} mentions)" for item, count in pos_counts])
    neg_summary = ", ".join([f"'{item}' ({count} mentions)" for item, count in neg_counts])

    system_prompt = "You are a senior product manager at Apple, writing a summary for the Vision Pro engineering team. Your tone is professional, insightful, and concise."
    
    user_prompt = f"""
    Here is a summary of the top feedback points from {total_reviews} customer reviews.

    Key Strengths (Most Praised):
    {pos_summary}

    Key Weaknesses (Most Criticized):
    {neg_summary}

    Based *only* on this data, please provide:
    1. A brief (1-2 sentence) overview of the general customer sentiment.
    2. A bullet-point list of 3-5 actionable recommendations for improvement, clearly tied to the weaknesses.
    3. A brief (1-2 sentence) conclusion on what to prioritize.

    Format the response clearly with headings.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # Use a smart model for this
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        log_queue.put(f"Recommendations API Error: {e}\n")
        return None

