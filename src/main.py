import tkinter as tk
from tkinter import ttk, messagebox
from dotenv import load_dotenv
import threading  # <-- NEW: Import threading

# --- Import our functions ---
from database import fetch_reviews
from analysis import analyze_sentiment_for_all  # <-- NEW: Import analysis function

# --- Load environment variables ---
load_dotenv()

# --- GUI functions ---
def analyze_reviews():
    """
    Run the sentiment analysis in a new thread
    to prevent the GUI from freezing.
    """
    # Show a pop-up so the user knows it's working
    messagebox.showinfo(
        "Analysis Started",
        "Analysis is running in the background. This may take a few minutes.\nSee the console for progress."
    )
    
    # Run the (long) analysis function in a separate thread
    # The 'target' is the function we want to run
    analysis_thread = threading.Thread(target=analyze_sentiment_for_all)
    analysis_thread.start()

def show_reviews():
    """Load and display reviews from database."""
    try:
        reviews = fetch_reviews()
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not fetch data (check DB/table/column names):\n{e}")
        return

    if not reviews:
        messagebox.showinfo("No Data", "No reviews found in database.")
        return
    
    # Clear treeview
    for item in tree.get_children():
        tree.delete(item)
    # Insert new rows
    for r in reviews:
        tree.insert("", "end", values=r)

# --- Main window ---
root = tk.Tk()
root.title("Apple Vision Pro Sentiment Analysis")
root.geometry("800x500")

# --- Title ---
title_label = tk.Label(root, text="Apple Vision Pro Customer Feedback", font=("Segoe UI", 16, "bold"))
title_label.pack(pady=10)

# --- Buttons ---
button_frame = tk.Frame(root)
button_frame.pack(pady=5)

load_btn = tk.Button(button_frame, text="Load Reviews", command=show_reviews)
load_btn.grid(row=0, column=0, padx=10)

analyze_btn = tk.Button(button_frame, text="Analyze Sentiment", command=analyze_reviews)
analyze_btn.grid(row=0, column=1, padx=10)

# --- Table (Treeview) to display reviews ---
columns = ("ID", "Review")
tree = ttk.Treeview(root, columns=columns, show="headings", height=15)
tree.heading("ID", text="ID")
tree.heading("Review", text="Review")
tree.column("ID", width=50, anchor="center")
tree.column("Review", width=700)
tree.pack(pady=10, fill="both", expand=True)

# --- Start GUI ---
root.mainloop()