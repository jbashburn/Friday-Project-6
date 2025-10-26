# Friday-Project-6
Files for Advanced Sentiment Analysis of Feedback
Apple Vision Pro - Sentiment Analysis ProjectThis project analyzes customer reviews for the Apple Vision Pro, using the OpenAI API to determine sentiment and extract key product aspects. It presents the findings in a Python/Tkinter GUI.Project StructureFRIDAY-PROJECT-6/
├── data/
│   └── feedback.db         (Your professor's database)
├── src/
│   ├── analysis.py       (Handles OpenAI API calls)
│   ├── database.py       (Reads from the database)
│   ├── main.py           (The main Tkinter GUI application)
│   └── visuals.py        (Generates charts and word clouds)
├── visuals/                (This folder will be auto-generated)
│   ├── sentiment_chart.png
│   ├── positive_aspects_wordcloud.png
│   └── negative_aspects_wordcloud.png
├── .env                    (You must create this file)
├── requirements.txt        (All required Python libraries)
└── README.md               (This file)
How to RunInstall Libraries:Open your terminal in the project's root folder and run:pip install -r requirements.txt
Create .env File:In the main FRIDAY-PROJECT-6 folder, create a new file named .env. Open it and add your OpenAI API key like this:OPENAI_API_KEY=sk-YourSecretKeyGoesHere
Run the Application:Run the main.py file from your terminal (make sure you are in the src directory or run it as a module):# Navigate into the src folder first
cd src
# Run the main file
python main.py
Alternatively, just run src/main.py from your VS Code "Run" button.Use the App:Click "Load Reviews" to see the data from feedback.db.Click "Analyze Sentiment". This will run in the background (check your console for progress).Once the analysis is complete, click "Show Results" to see the charts in a new window.