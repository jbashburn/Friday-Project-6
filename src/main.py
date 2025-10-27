import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, scrolledtext
from dotenv import load_dotenv
import threading  # For running analysis in the background
import os         # To find image files
import queue      # For thread-safe messages

# --- Import Pillow for images ---
try:
    from PIL import Image, ImageTk
except ImportError:
    print("--- CRITICAL ERROR ---")
    print("Pillow library not found. Please install it to show images:")
    print("pip install Pillow")
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
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# --- Define image paths ---
VISUALS_DIR = os.path.join(os.path.dirname(__file__), "..", "visuals")
BAR_CHART_PATH = os.path.join(VISUALS_DIR, "sentiment_chart.png")
POSITIVE_WC_PATH = os.path.join(VISUALS_DIR, "positive_aspects_wordcloud.png")
NEGATIVE_WC_PATH = os.path.join(VISUALS_DIR, "negative_aspects_wordcloud.png")
RECOMMENDATIONS_PATH = os.path.join(VISUALS_DIR, "recommendations.txt")

# --- Create a queue for logging ---
log_queue = queue.Queue()


# --- GUI functions ---

def analyze_reviews_thread(log_queue):
    """
    This function runs in the background thread.
    It calls the main analysis function.
    """
    analyze_btn.config(text="Analyzing...", state="disabled")
    results_btn.config(state="disabled")
    recs_btn.config(state="disabled") 

    try:
        analyze_sentiment_for_all(log_queue)
        log_queue.put("--- ANALYSIS COMPLETE ---")
    except Exception as e:
        log_queue.put(f"\n--- ANALYSIS FAILED ---\n{e}\n")
    finally:
        log_queue.put("--- ENABLE_BUTTONS ---")


def start_analysis():
    """Starts the analysis thread."""
    messagebox.showinfo(
        "Analysis Started",
        "Analysis is running in the background. See the log box in the main window for live progress."
    )
    log_box.config(state="normal")
    log_box.delete('1.0', tk.END)
    log_box.config(state="disabled")
    
    analysis_thread = threading.Thread(target=analyze_reviews_thread, args=(log_queue,))
    analysis_thread.start()

def show_reviews():
    """Load and display reviews from database."""
    try:
        reviews = fetch_reviews()
        if reviews is None:
             messagebox.showerror("Database Error", "Could not fetch data. Check console for details.")
             return
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not fetch data:\n{e}")
        return

    if not reviews:
        messagebox.showinfo("No Data", "No reviews found in database.")
        return
    
    for item in tree.get_children():
        tree.delete(item)
    for r in reviews:
        tree.insert("", "end", values=r)
    log_queue.put(f"Loaded {len(reviews)} reviews into the table.\n")


def show_results():
    """
    Open a new window *with scrollbars* and display the generated chart images.
    """
    log_queue.put("Attempting to show results...\n")
    
    if not (os.path.exists(BAR_CHART_PATH) and 
            os.path.exists(POSITIVE_WC_PATH) and 
            os.path.exists(NEGATIVE_WC_PATH)):
        messagebox.showerror(
            "Error", 
            "Image files not found.\n"
            "Please run 'Analyze Sentiment' first and wait for it to complete."
        )
        return

    results_window = Toplevel(root)
    results_window.title("Analysis Results")
    results_window.geometry("1000x800") 

    main_frame = tk.Frame(results_window)
    main_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(main_frame)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollable_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        
    scrollable_frame.bind("<Configure>", on_frame_configure)

    try:
        tk.Label(scrollable_frame, text="Sentiment Distribution", font=("Segoe UI", 14, "bold")).pack(pady=(10,0))
        img1 = Image.open(BAR_CHART_PATH)
        img1 = img1.resize((500, 400), Image.Resampling.LANCZOS)
        tk_img1 = ImageTk.PhotoImage(img1)
        
        lbl1 = tk.Label(scrollable_frame, image=tk_img1)
        lbl1.pack(pady=5)
        
        tk.Label(scrollable_frame, text="Positive Aspects", font=("Segoe UI", 14, "bold")).pack(pady=(10,0))
        img2 = Image.open(POSITIVE_WC_PATH)
        img2 = img2.resize((450, 225), Image.Resampling.LANCZOS)
        tk_img2 = ImageTk.PhotoImage(img2)
        
        lbl2 = tk.Label(scrollable_frame, image=tk_img2)
        lbl2.pack(pady=5)
        
        tk.Label(scrollable_frame, text="Negative Aspects", font=("Segoe UI", 14, "bold")).pack(pady=(10,0))
        img3 = Image.open(NEGATIVE_WC_PATH)
        img3 = img3.resize((450, 225), Image.Resampling.LANCZOS)
        tk_img3 = ImageTk.PhotoImage(img3)
        
        lbl3 = tk.Label(scrollable_frame, image=tk_img3)
        lbl3.pack(pady=5)
        
        results_window.img_ref1 = tk_img1
        results_window.img_ref2 = tk_img2
        results_window.img_ref3 = tk_img3

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load images. Is 'Pillow' installed?\n{e}")
        results_window.destroy()

def show_recommendations():
    """
    Open a new window and display the recommendations.txt file.
    """
    log_queue.put("Opening recommendations...\n")
    
    if not os.path.exists(RECOMMENDATIONS_PATH):
        messagebox.showerror(
            "Error", 
            "Recommendations file not found.\n"
            "Please run 'Analyze Sentiment' first and wait for it to complete."
        )
        return
        
    try:
        recs_window = Toplevel(root)
        recs_window.title("Analysis & Recommendations")
        recs_window.geometry("700x600")

        # --- THIS IS THE FIX ---
        # Changed 'pad_x=10' to 'padx=10' 
        # Changed 'pad_y=10' to 'pady=10'
        recs_text = scrolledtext.ScrolledText(recs_window, wrap=tk.WORD, font=("Segoe UI", 10), padx=10, pady=10)
        # --- END FIX ---
        
        recs_text.pack(fill="both", expand=True)

        with open(RECOMMENDATIONS_PATH, "r", encoding="utf-8") as f:
            report_content = f.read()

        recs_text.insert(tk.END, report_content)
        recs_text.config(state="disabled")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to read recommendations file:\n{e}")


def process_log_queue():
    """
    Check the queue for new messages and update the log box.
    """
    try:
        msg = log_queue.get_nowait() 
        
        if msg == "--- ENABLE_BUTTONS ---":
            analyze_btn.config(text="Analyze Sentiment", state="normal")
            results_btn.config(text="Show Results", state="normal")
            recs_btn.config(state="normal") 
            messagebox.showinfo(
                "Analysis Complete",
                "Analysis is complete! You can now click 'Show Results' or 'View Recommendations'."
            )
        elif msg == "--- ANALYSIS COMPLETE ---":
             log_box.config(state="normal")
             log_box.insert(tk.END, msg + "\n")
             log_box.config(state="disabled")
             log_box.see(tk.END)
        else:
            log_box.config(state="normal")
            log_box.insert(tk.END, msg) 
            log_box.config(state="disabled")
            log_box.see(tk.END)
            
    except queue.Empty:
        pass
    finally:
        root.after(100, process_log_queue)


# --- Main window setup ---
root = tk.Tk()
root.title("Apple Vision Pro Sentiment Analysis")
root.geometry("800x750")

style = ttk.Style()
style.theme_use("clam") 
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

title_label = tk.Label(root, text="Apple Vision Pro Customer Feedback", font=("Segoe UI", 16, "bold"))
title_label.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

load_btn = tk.Button(button_frame, text="Load Reviews", font=("Segoe UI", 10), command=show_reviews)
load_btn.grid(row=0, column=0, padx=10, ipady=2)

analyze_btn = tk.Button(button_frame, text="Analyze Sentiment", font=("Segoe UI", 10, "bold"), command=start_analysis)
analyze_btn.grid(row=0, column=1, padx=10, ipady=2)

results_btn = tk.Button(button_frame, text="Show Results", font=("Segoe UI", 10), command=show_results, state="disabled")
results_btn.grid(row=0, column=2, padx=10, ipady=2)

recs_btn = tk.Button(button_frame, text="View Recommendations", font=("Segoe UI", 10), command=show_recommendations, state="disabled")
recs_btn.grid(row=0, column=3, padx=10, ipady=2)

# --- Treeview to display reviews ---
tree_frame = tk.Frame(root)
tree_frame.pack(pady=10, fill="both", expand=True, padx=20)

columns = ("ID", "Review")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=10)
tree.heading("ID", text="ID")
tree.heading("Review", text="Review")
tree.column("ID", width=50, anchor="center", stretch=False)
tree.column("Review", width=700)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")
tree.pack(side="left", fill="both", expand=True)

# --- Live Log Box ---
log_frame = tk.Frame(root, pady=10)
log_frame.pack(fill="both", expand=True, padx=20)

log_label = tk.Label(log_frame, text="Live Analysis Log", font=("Segoe UI", 12, "bold"))
log_label.pack()

log_box = scrolledtext.ScrolledText(log_frame, height=10, font=("Courier New", 9), state="disabled", wrap=tk.WORD)
log_box.pack(fill="both", expand=True)


# --- Start GUI ---
root.after(100, process_log_queue) # Start the queue checker
root.mainloop()

#final main file