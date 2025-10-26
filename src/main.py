import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from dotenv import load_dotenv
import threading  # For running analysis in the background
import os         # To find image files

# --- Import Pillow for images ---
try:
    from PIL import Image, ImageTk
except ImportError:
    print("--- CRITICAL ERROR ---")
    print("Pillow library not found. Please install it to show images:")
    print("pip install Pillow")
    # Show a popup error if tkinter is already running
    try:
        root = tk.Tk()
        root.withdraw() # Hide the root window
        messagebox.showerror("Missing Library", "Pillow library not found.\nPlease run 'pip install Pillow' in your terminal.")
    except:
        pass
    exit() # Exit the script

# --- Import our functions ---
from database import fetch_reviews
from analysis import analyze_sentiment_for_all

# --- Load environment variables ---
# Loads the .env file from the parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# --- Define image paths ---
VISUALS_DIR = os.path.join(os.path.dirname(__file__), "..", "visuals")
BAR_CHART_PATH = os.path.join(VISUALS_DIR, "sentiment_chart.png")
POSITIVE_WC_PATH = os.path.join(VISUALS_DIR, "positive_aspects_wordcloud.png")
NEGATIVE_WC_PATH = os.path.join(VISUALS_DIR, "negative_aspects_wordcloud.png")


# --- GUI functions ---
def analyze_reviews_thread():
    """
    Run the sentiment analysis in a new thread
    to prevent the GUI from freezing.
    """
    # Disable buttons during analysis
    analyze_btn.config(text="Analyzing...", state="disabled")
    results_btn.config(state="disabled")

    try:
        # Run the (long) analysis function
        analyze_sentiment_for_all()
        
        # Show success message
        messagebox.showinfo(
            "Analysis Complete",
            "Analysis is complete! You can now click 'Show Results'."
        )
    except Exception as e:
        messagebox.showerror("Analysis Error", f"An error occurred during analysis:\n{e}")
    finally:
        # Re-enable buttons
        analyze_btn.config(text="Analyze Sentiment", state="normal")
        results_btn.config(text="Show Results", state="normal")


def start_analysis():
    """Starts the analysis thread."""
    messagebox.showinfo(
        "Analysis Started",
        "Analysis is running in the background. This may take a few minutes.\n"
        "See the console for progress.\n"
        "The app will notify you when it's done."
    )
    # Run the analysis in a separate thread
    analysis_thread = threading.Thread(target=analyze_reviews_thread)
    analysis_thread.start()

def show_reviews():
    """Load and display reviews from database."""
    try:
        reviews = fetch_reviews()
        if reviews is None: # Check if fetch_reviews failed
             messagebox.showerror("Database Error", "Could not fetch data. Check console for details.")
             return
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not fetch data:\n{e}")
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
    print(f"Loaded {len(reviews)} reviews into the table.")


def show_results():
    """
    Open a new window and display the generated chart images.
    """
    print("Attempting to show results...")
    
    # Check if files exist first
    if not (os.path.exists(BAR_CHART_PATH) and 
            os.path.exists(POSITIVE_WC_PATH) and 
            os.path.exists(NEGATIVE_WC_PATH)):
        messagebox.showerror(
            "Error", 
            "Image files not found.\n"
            "Please run 'Analyze Sentiment' first and wait for it to complete."
        )
        return

    # Create a new "Toplevel" window
    results_window = Toplevel(root)
    results_window.title("Analysis Results")
    results_window.geometry("1000x800") # Adjusted size

    try:
        # --- 1. Bar Chart ---
        tk.Label(results_window, text="Sentiment Distribution", font=("Segoe UI", 14, "bold")).pack(pady=(10,0))
        img1 = Image.open(BAR_CHART_PATH)
        img1 = img1.resize((500, 400), Image.Resampling.LANCZOS)
        tk_img1 = ImageTk.PhotoImage(img1)
        
        lbl1 = tk.Label(results_window, image=tk_img1)
        lbl1.pack(pady=5)
        
        # --- 2. Positive Word Cloud ---
        tk.Label(results_window, text="Positive Aspects", font=("Segoe UI", 14, "bold")).pack(pady=(10,0))
        img2 = Image.open(POSITIVE_WC_PATH)
        img2 = img2.resize((450, 225), Image.Resampling.LANCZOS)
        tk_img2 = ImageTk.PhotoImage(img2)
        
        lbl2 = tk.Label(results_window, image=tk_img2)
        lbl2.pack(pady=5)
        
        # --- 3. Negative Word Cloud ---
        tk.Label(results_window, text="Negative Aspects", font=("Segoe UI", 14, "bold")).pack(pady=(10,0))
        img3 = Image.open(NEGATIVE_WC_PATH)
        img3 = img3.resize((450, 225), Image.Resampling.LANCZOS)
        tk_img3 = ImageTk.PhotoImage(img3)
        
        lbl3 = tk.Label(results_window, image=tk_img3)
        lbl3.pack(pady=5)
        
        # IMPORTANT: Keep a reference to the images, or they will disappear
        results_window.img_ref1 = tk_img1
        results_window.img_ref2 = tk_img2
        results_window.img_ref3 = tk_img3

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load images. Is 'Pillow' installed?\n{e}")
        results_window.destroy()

# --- Main window setup ---
root = tk.Tk()
root.title("Apple Vision Pro Sentiment Analysis")
root.geometry("800x600") # Made window a bit taller

# --- Style ---
style = ttk.Style()
style.theme_use("clam") # A clean, modern theme
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

# --- Title ---
title_label = tk.Label(root, text="Apple Vision Pro Customer Feedback", font=("Segoe UI", 16, "bold"))
title_label.pack(pady=10)

# --- Buttons ---
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

load_btn = tk.Button(button_frame, text="Load Reviews", font=("Segoe UI", 10), command=show_reviews, width=15)
load_btn.grid(row=0, column=0, padx=10, ipady=2) # ipady = internal padding

analyze_btn = tk.Button(button_frame, text="Analyze Sentiment", font=("Segoe UI", 10, "bold"), command=start_analysis, width=15)
analyze_btn.grid(row=0, column=1, padx=10, ipady=2)

results_btn = tk.Button(button_frame, text="Show Results", font=("Segoe UI", 10), command=show_results, width=15, state="disabled")
results_btn.grid(row=0, column=2, padx=10, ipady=2)

# --- Table (Treeview) to display reviews ---
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10, fill="both", expand=True, padx=20)

columns = ("ID", "Review")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
tree.heading("ID", text="ID")
tree.heading("Review", text="Review")
tree.column("ID", width=50, anchor="center", stretch=False)
tree.column("Review", width=700)

# --- Scrollbar ---
scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tree.pack(side="left", fill="both", expand=True)


# --- Start GUI ---
root.mainloop()
