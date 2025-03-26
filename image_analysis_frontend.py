import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import json
import threading
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
from objectdetection import analyze_all_images  # Assuming the previous script is saved as analyze_images.py

class ImageAnalysisFrontend:
    def __init__(self, master):
        self.master = master
        master.title("Image Usage Analyzer")
        master.geometry("1200x800")
        master.configure(bg='#2c3e50')  # Dark blue-gray background

        # Custom Style
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Modern theme
        
        # Configure styles
        self.style.configure('TLabel', background='#2c3e50', foreground='white', font=('Segoe UI', 10, 'bold'))
        self.style.configure('TButton', 
            font=('Segoe UI', 10, 'bold'), 
            background='#3498db',  # Bright blue
            foreground='white'
        )
        self.style.map('TButton', 
            background=[('active', '#2980b9'), ('pressed', '#2c3e50')]
        )
        self.style.configure('Treeview', 
            background='#34495e',  # Darker blue-gray
            foreground='white',
            rowheight=30,
            fieldbackground='#34495e'
        )
        self.style.configure('Treeview.Heading', 
            background='#2c3e50', 
            foreground='white', 
            font=('Segoe UI', 10, 'bold')
        )

        # Main Frame
        self.main_frame = ttk.Frame(master, style='TFrame')
        self.main_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        # Left Side - Folder Selection and Controls
        self.left_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Image Preview Area
        self.preview_label = ttk.Label(self.left_frame, text="Image Preview", style='TLabel')
        self.preview_label.pack(pady=(10, 5))

        self.preview_canvas = tk.Canvas(self.left_frame, width=400, height=300, bg='#34495e')
        self.preview_canvas.pack(pady=10)

        # Folder Selection
        self.create_folder_selection_section()

        # Right Side - Results and Analysis
        self.right_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        # Results Treeview
        self.create_results_section()

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self.left_frame, 
            style='Horizontal.TProgressbar', 
            length=400, 
            mode='determinate'
        )
        self.progress_bar.pack(pady=10)

        # Status Label
        self.status_label = ttk.Label(self.left_frame, text="", style='TLabel')
        self.status_label.pack(pady=5)

    def create_folder_selection_section(self):
        # Image Folder Selection
        self.image_folder_label = ttk.Label(self.left_frame, text="Select Image Folder:", style='TLabel')
        self.image_folder_label.pack(pady=(10, 5))

        folder_frame = ttk.Frame(self.left_frame)
        folder_frame.pack(fill=tk.X, pady=5)

        self.folder_path = tk.StringVar()
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.folder_path, width=40)
        self.folder_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        self.browse_button = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        self.browse_button.pack(side=tk.RIGHT)

        # Compress Folder Selection
        self.compress_folder_label = ttk.Label(self.left_frame, text="Select Compress Folder:", style='TLabel')
        self.compress_folder_label.pack(pady=(10, 5))

        compress_frame = ttk.Frame(self.left_frame)
        compress_frame.pack(fill=tk.X, pady=5)

        self.compress_path = tk.StringVar()
        self.compress_entry = ttk.Entry(compress_frame, textvariable=self.compress_path, width=40)
        self.compress_entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))

        self.compress_browse_button = ttk.Button(compress_frame, text="Browse", command=self.browse_compress_folder)
        self.compress_browse_button.pack(side=tk.RIGHT)

        # Analyze Button
        self.analyze_button = ttk.Button(self.left_frame, text="Analyze Images", command=self.start_analysis)
        self.analyze_button.pack(pady=20)

    def create_results_section(self):
        # Results Label
        results_label = ttk.Label(self.right_frame, text="Analysis Results", style='TLabel')
        results_label.pack(pady=(10, 5))

        # Results Frame
        results_frame = ttk.Frame(self.right_frame)
        results_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Treeview for Results
        self.results_tree = ttk.Treeview(results_frame, 
            columns=('Image', 'Phone Usage', 'Explanation'), 
            show='headings', 
            selectmode='browse'
        )
        self.results_tree.heading('Image', text='Image')
        self.results_tree.heading('Phone Usage', text='Phone Usage')
        self.results_tree.heading('Explanation', text='Explanation')
        
        self.results_tree.column('Image', width=100, anchor='center')
        self.results_tree.column('Phone Usage', width=100, anchor='center')
        self.results_tree.column('Explanation', width=500)

        # Scrollbars
        results_scrollbar_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_tree.yview)
        results_scrollbar_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.results_tree.xview)
        self.results_tree.configure(yscroll=results_scrollbar_y.set, xscroll=results_scrollbar_x.set)

        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        results_scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        results_scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Bind selection event to show image preview
        self.results_tree.bind('<<TreeviewSelect>>', self.show_image_preview)

        # Buttons Frame
        buttons_frame = ttk.Frame(self.right_frame)
        buttons_frame.pack(pady=10)

        # Save Results Button
        self.save_button = ttk.Button(buttons_frame, text="Save Results", command=self.save_results)
        self.save_button.pack(side=tk.LEFT, padx=5)

        # Generate Report Button
        self.report_button = ttk.Button(buttons_frame, text="Generate Report", command=self.generate_report)
        self.report_button.pack(side=tk.LEFT, padx=5)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.update_preview_images(folder_selected)

    def browse_compress_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.compress_path.set(folder_selected)

    def update_preview_images(self, folder_path):
        # Clear previous preview
        self.preview_canvas.delete('all')
        
        # Get image files
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        # Display up to 4 preview images
        image_files = image_files[:4]
        
        # Calculate grid layout
        cols = 2
        rows = (len(image_files) + 1) // 2
        cell_width = self.preview_canvas.winfo_width() // cols
        cell_height = self.preview_canvas.winfo_height() // rows

        for i, filename in enumerate(image_files):
            try:
                # Open and resize image
                img_path = os.path.join(folder_path, filename)
                img = Image.open(img_path)
                img.thumbnail((cell_width-10, cell_height-10))
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                
                # Calculate position
                row = i // cols
                col = i % cols
                x = col * cell_width + cell_width // 2
                y = row * cell_height + cell_height // 2
                
                # Display image
                self.preview_canvas.create_image(x, y, image=photo)
                self.preview_canvas.image = photo  # Keep a reference
            except Exception as e:
                print(f"Error loading preview image {filename}: {e}")

    def start_analysis(self):
        # Clear previous results
        for i in self.results_tree.get_children():
            self.results_tree.delete(i)

        image_folder = self.folder_path.get()
        compress_folder = self.compress_path.get()

        if not image_folder or not compress_folder:
            messagebox.showerror("Error", "Please select both image and compress folders")
            return

        # Disable analyze button during processing
        self.analyze_button.config(state=tk.DISABLED)
        self.status_label.config(text="Analyzing images...")
        self.progress_bar['value'] = 0

        # Run analysis in a separate thread
        thread = threading.Thread(target=self.run_analysis, args=(image_folder, compress_folder))
        thread.start()

    def run_analysis(self, image_folder, compress_folder):
        try:
            # Call the analysis function
            results = analyze_all_images(image_folder, compress_folder)

            # Update UI in main thread
            self.master.after(0, self.update_analysis_results, results)
        except Exception as e:
            # Show error in main thread
            self.master.after(0, self.show_analysis_error, str(e))

    def update_analysis_results(self, results):
        # Populate results tree
        for image, data in results.items():
            self.results_tree.insert('', 'end', values=(
                image, 
                data['answer'].capitalize(), 
                data['explanation']
            ))

        # Re-enable analyze button and update status
        self.analyze_button.config(state=tk.NORMAL)
        self.status_label.config(text=f"Analysis complete. {len(results)} images analyzed.")
        self.progress_bar['value'] = 100

        messagebox.showinfo("Analysis Complete", f"Analyzed {len(results)} images")

    def show_analysis_error(self, error_message):
        # Re-enable analyze button and show error
        self.analyze_button.config(state=tk.NORMAL)
        self.status_label.config(text="Analysis failed.")
        messagebox.showerror("Error", f"An error occurred: {error_message}")

    def show_image_preview(self, event):
        # Get selected item
        selected_item = self.results_tree.selection()
        if not selected_item:
            return

        # Get image filename
        values = self.results_tree.item(selected_item[0])['values']
        image_name = values[0]

        # Find full path to image
        image_folder = self.folder_path.get()
        image_path = os.path.join(image_folder, image_name)

        # Show detailed preview
        self.show_detailed_image_preview(image_path)

    def show_detailed_image_preview(self, image_path):
        # Create a new window for detailed preview
        preview_window = tk.Toplevel(self.master)
        preview_window.title("Image Preview")
        preview_window.geometry("600x600")
        preview_window.configure(bg='#2c3e50')

        # Load and resize image
        img = Image.open(image_path)
        img.thumbnail((500, 500))
        photo = ImageTk.PhotoImage(img)

        # Create label to show image
        preview_label = ttk.Label(preview_window, image=photo)
        preview_label.image = photo  # Keep a reference
        preview_label.pack(expand=True, padx=20, pady=20)

        # Add image filename
        filename_label = ttk.Label(preview_window, 
            text=os.path.basename(image_path), 
            style='TLabel'
        )
        filename_label.pack(pady=10)

    def save_results(self):
        # Collect results
        results = {}
        for item in self.results_tree.get_children():
            values = self.results_tree.item(item)['values']
            results[values[0]] = {
                'answer': values[1].lower(),
                'explanation': values[2]
            }

        # Save to JSON file
        if results:
            save_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if save_path:
                with open(save_path, 'w') as f:
                    json.dump(results, f, indent=4)
                messagebox.showinfo("Success", f"Results saved to {save_path}")
        else:
            messagebox.showwarning("Warning", "No results to save")

    def generate_report(self):
        # Collect results data
        results = [
            self.results_tree.item(item)['values'] 
            for item in self.results_tree.get_children()
        ]

        if not results:
            messagebox.showwarning("Warning", "No analysis results to generate report")
            return

        # Create a new window for the report
        report_window = tk.Toplevel(self.master)
        report_window.title("Analysis Report")
        report_window.geometry("800x600")
        report_window.configure(bg='#2c3e50')

        # Create matplotlib figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        fig.patch.set_facecolor('#2c3e50')
        
        # Count usage types
        usage_counts = {}
        for _, usage, _ in results:
            usage_counts[usage] = usage_counts.get(usage, 0) + 1

        # Pie chart of usage types
        ax1.pie(usage_counts.values(), labels=usage_counts.keys(), autopct='%1.1f%%', 
                colors=['#3498db', '#2ecc71', '#e74c3c'])
        ax1.set_title('Phone Usage Distribution', color='white')

        # Bar plot of usage explanation lengths
        explanation_lengths = [len(exp) for _, _, exp in results]
        ax2.hist(explanation_lengths, bins=10, color='#3498db', edgecolor='white')
        ax2.set_title('Explanation Length Distribution', color='white')
        ax2.set_xlabel('Explanation Length', color='white')
        ax2.set_ylabel('Frequency', color='white')

        # Customize plot colors
        ax1.set_facecolor('#2c3e50')
        ax2.set_facecolor('#2c3e50')
        for spine in ax1.spines.values():
            spine.set_edgecolor('white')
        for spine in ax2.spines.values():
            spine.set_edgecolor('white')
        ax1.tick_params(colors='white')
        ax2.tick_params(colors='white')

        # Embed plot in Tkinter window
        canvas = FigureCanvasTkAgg(fig, master=report_window)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)

        # Summary text
        summary_text = f"""
        Total Images Analyzed: {len(results)}
        Usage Distribution:
        {chr(10).join(f"- {usage}: {count}" for usage, count in usage_counts.items())}
        """
        summary_label = ttk.Label(report_window, text=summary_text, style='TLabel')
        summary_label.pack(pady=10)

def main():
    root = tk.Tk()
    app = ImageAnalysisFrontend(root)
    root.mainloop()

if __name__ == "__main__":
    main()