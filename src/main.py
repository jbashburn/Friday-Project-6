import tkinter as tk
from tkinter import ttk, messagebox
# DELETED: sqlite3 and os (not needed directly in main)
from dotenv import load_dotenv

# --- NEW: Import our database function ---
from database import fetch_reviews

# --- Load environment variables (for OpenAI later) ---
load_dotenv()
# We don't need openai_api_key in this file, so I commented it out
# openai_api_key = os.getenv("OPENAI_API_KEY") 

# --- DELETED: Database setup and fetch_reviews() function ---
# (It's now handled by importing 'database.py')

# --- GUI functions ---
def analyze_reviews():
    """Placeholder for sentiment analysis logic."""
    messagebox.showinfo("Analyze", "This will call OpenAI for sentiment analysis soon!")

def show_reviews():
    """Load and display reviews from database."""
    # This now calls the imported function
    reviews = fetch_reviews() 
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