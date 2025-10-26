Project 6: Apple Vision Pro Feedback Analysis Tool

Description

This project is a Python application built for the Apple Vision Pro product team. Its purpose is to analyze a database of customer feedback reviews (feedback.db) to understand customer sentiment and identify key product strengths and weaknesses.

The application uses the OpenAI API (gpt-4o-mini) to perform advanced sentiment analysis and aspect-based extraction on each review. The results are then aggregated and presented in a user-friendly GUI built with tkinter.

This tool allows the team to move beyond simple positive/negative ratings and get actionable insights into what specific features customers (dis)like, culminating in an AI-generated recommendations report for future product improvements.

Features

Tkinter GUI: A clean, multi-button graphical interface to load, analyze, and view results.

Database Integration: Safely reads all customer reviews from the provided feedback.db (SQLite) file without modifying it.

AI-Powered Sentiment Analysis: Individually categorizes each review as "Positive," "Negative," or "Neutral."

AI-Powered Aspect Extraction: Identifies specific product features mentioned (e.g., "weight," "display," "battery life") and the sentiment tied to them.

Live Progress Log: A scrollable log box in the main window shows the analysis progress in real-time, so you don't have to watch the terminal.

Asynchronous Analysis: The entire OpenAI analysis runs in a separate thread, so the GUI never freezes or becomes unresponsive.

Visual Data Presentation: Generates and displays three key charts in a scrollable pop-up window:

Sentiment Distribution (Bar Chart)

Top Positive Aspects (Word Cloud)

Top Negative Aspects (Word Cloud)

AI-Generated Recommendations: After all reviews are processed, the app uses the AI one last time to summarize the findings and generate a "Product Manager" report with actionable recommendations.

How to Set Up

1. Check Python Version
Ensure you have Python 3.7 or newer installed.

2. Create a Project Folder
Create a main folder for your project (e.g., FRIDAY-PROJECT-6). All files will go inside this.

3. Install Required Libraries
This project requires several Python libraries. You can install them all at once by running:

pip install -r requirements.txt


Or, you can install them manually:

pip install openai python-dotenv matplotlib wordcloud Pillow


4. Create Your .env File
In the main project folder (at the same level as src), you must create a file named .env
Inside this file, add your OpenAI API key like this:

OPENAI_API_KEY=sk-YourSecretApiKeyGoesHere


5. Final File Structure
Your folder should look like this:

FRIDAY-PROJECT-6/
data/
 -feedback.db

src/
-analysis.py
-database.py
-main.py
-visuals.py

visuals/
(This folder will be created automatically)
-.env
-README.md
-requirements.txt


How to Run

Open your terminal or command prompt.

Navigate to the src folder: cd FRIDAY-PROJECT-6/src

Run the main application file:

python main.py


The main application window will appear.

How to Use the Application

Load Reviews: Click this button first. It will securely read the feedback.db file and display all 79 reviews in the main table.

Analyze Sentiment: Click this button to begin the analysis. A pop-up will confirm it has started.

Watch the Live Analysis Log at the bottom of the window to see the progress in real-time.

The "Analyze Sentiment" button will be disabled while it's running.

This process will take a few minutes (about 45-60 seconds for 79 reviews).

Wait for Completion: When the analysis is finished, a pop-up will appear, and the "Show Results" and "View Recommendations" buttons will become clickable.

Show Results: Click this to open a new, scrollable window containing the Sentiment Bar Chart and the Positive/Negative Aspect Word Clouds.

View Recommendations: Click this to open a final, scrollable window displaying the AI-generated report with actionable insights and recommendations for the engineering team.

Project File Descriptions

src/main.py: The main application file. You run this to start the GUI. It handles the window, buttons, and threading.

src/database.py: A simple module that contains one function, fetch_reviews(), to read data from data/feedback.db.

src/analysis.py: The "brains" of the operation.

analyze_sentiment_for_all(): Loops through all reviews.

get_detailed_analysis(): Calls the OpenAI API for a single review to get sentiment/aspects.

get_recommendations(): Calls the OpenAI API a final time with a summary to get the report.

src/visuals.py: Contains the functions generate_barchart() and generate_wordcloud() that create and save the .png image files.

data/feedback.db: The SQLite database file containing the customer reviews.

visuals/ (directory): This folder is created automatically by the app to store the saved charts and the recommendations.txt file.