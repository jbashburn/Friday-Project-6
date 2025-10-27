Friday Project 6: Advanced Sentiment Analysis App of Customer Reviews

This project is an app built for the Apple Vision Pro product team to analyze a database of customer feedback, using Tkinter GUI and python.

The app uses the OpenAI API (gpt-4o-mini) to perform advanced sentiment analysis, with a Live Progress Log, visual presentation, and an ai-generated recommendation report.

    User will create a .env foldler to enter the API key. You can use your own API key.

Files include:
    FRIDAY-PROJECT-6
    
    data
        feedback

    src with python files
        analysis.py
        database.py
        main.py
        visuals.py

    visuals 
        .env (you will create)
        README.md
        requirements.txt

How to Set Up

1. Create a Project Folder
2. Install Libraries
        run:

            pip install -r requirements.txt

        or manually:

            pip install openai python-dotenv matplotlib wordcloud Pillow

3. Create .env File
        In the main project folder, you must create a file named .env
        Inside this file, add the API key:
        OPENAI_API_KEY=

FRIDAY-PROJECT-6/
data folder, feedback.db

src folder 
    analysis.py 
    database.py
    main.py
    visuals.py

visuals/
(This folder will be created automatically)
    .env
    README.md
    requirements.txt

How to Run

    Open your terminal or cmd prompt.

    Navigate to the src folder: cd FRIDAY-PROJECT-6/src

    Run the main app file:

        main.py

How to Use the App:

    In order, you will load reviews, watch the live analysis log,, show results, and view recommendations, in that order

    This process will take a few minutes (about 45-60 seconds for 79 reviews).

File Descriptions

    main.py: The main app file. You run this to start the GUI. It handles the window, buttons, and threading.

    database.py: A simple module that contains one function, fetch_reviews(), to read data from feedback.db.

    analysis.py: The "brains" of the operation.

        analyze_sentiment_for_all(): Loops all reviews

        get_detailed_analysis(): Calls the OpenAI API for a single reviewto get analysis

        get_recommendations(): Calls the OpenAI API a final time with a summary to get the report

    visuals.py: Contains the functions generate_barchart() and generate_wordcloud() that create and save the .png image files.

    feedback.db: The SQLite database file containing the customer reviews.

    visuals: This folder is created automatically by the app to store the saved charts and the recommendations.txt file..
