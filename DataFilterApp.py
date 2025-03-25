import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from FolderManager import FolderManager, Tag
import json, os
from PIL import Image, ImageTk


class MovieEntry:
    def __init__(self):
        pass


class DataFilterApp:
    def __init__(self, root):
        self.root = root
        self.set_working_directory()

        self.root.title("Data Filter Application")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)

        self.folder_manager = FolderManager(self.directory)
        self.set_dict_data()
        self.data = pd.DataFrame(self.dict_data)

        self.create_widgets()
        self.display_all_data()

    def set_working_directory(self):
        try:
            with open("init.json", "r") as f:
                d = json.load(f)
                self.directory = d["dir"]
        except:
            self.directory = filedialog.askdirectory(title="Select Data Directory")
            with open("init.json", "w") as f:
                json.dump({"dir": self.directory}, f)

    def set_dict_data(self):
        self.dict_data = [a.info for a in self.folder_manager.get_movies()]

    def create_widgets(self):
        self.create_top_frame()
        self.create_filter_frame()
        self.create_data_frame()
        self.create_photo_view()
        self.create_movie_entries()
        self.create_treeview()
        self.create_json_viewer()
        self.create_status_var()
        self.bind_all()

    def reset_movies(self):
        self.folder_manager.reset_movie_info()
        self.set_dict_data()
        try:
            self.display_all_data()
        except:
            pass

    def create_top_frame(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=5, padx=10, fill="x")
        load_button = ttk.Button(
            top_frame,
            text="Reset Movies Data",
            command=self.reset_movies,
        )
        load_button.pack(side="right", padx=5)

    def create_filter_frame(self):
        filter_frame = ttk.LabelFrame(self.root, text="Filter Options")
        filter_frame.pack(pady=5, padx=10, fill="x")

        if len(self.dict_data) > 0:
            available_fields = list(self.dict_data[0].keys())
        else:
            available_fields = []

        ttk.Label(filter_frame, text="Filter Field:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.filter_type = ttk.Combobox(filter_frame, state="readonly")
        self.filter_type["values"] = available_fields
        if available_fields:
            self.filter_type.current(0)
        self.filter_type.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.filter_type.bind("<<ComboboxSelected>>", self._on_filter_type_change)

        ttk.Label(filter_frame, text="Filter Method:").grid(
            row=0, column=2, padx=5, pady=5, sticky="w"
        )
        self.filter_method = ttk.Combobox(filter_frame, state="readonly")
        self.filter_method["values"] = (
            "equals",
            "greater than",
            "less than",
            "contains",
        )
        self.filter_method.current(0)
        self.filter_method.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        ttk.Label(filter_frame, text="Filter Value:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )
        self.filter_value = ttk.Entry(filter_frame, width=20)
        self.filter_value.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.filter_button = ttk.Button(
            filter_frame, text="Apply Filter", command=self.apply_filter
        )
        self.filter_button.grid(row=1, column=2, padx=5, pady=5)

        self.reset_button = ttk.Button(
            filter_frame, text="Reset Filter", command=self.reset_filter
        )
        self.reset_button.grid(row=1, column=3, padx=5, pady=5)

        self._on_filter_type_change(None)

    def create_data_frame(self):
        self.data_frame = ttk.LabelFrame(self.root, text="Data Display")
        self.data_frame.pack(pady=5, padx=10, fill="both", expand=True)

        self.notebook = ttk.Notebook(self.data_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.photo_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.photo_frame, text="Photo View")

        self.table_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Table View")

        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="Chart View")

        self.json_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.json_frame, text="JSON View")

    def create_photo_view(self):
        self.canvas = tk.Canvas(self.photo_frame)
        self.canvas.pack(side="left", fill="both", expand=True)

        y_scrollbar = ttk.Scrollbar(
            self.photo_frame, orient="vertical", command=self.canvas.yview
        )
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=y_scrollbar.set)

        self.inner_frame = ttk.Frame(self.canvas)
        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.inner_window = self.canvas.create_window(
            (0, 0), window=self.inner_frame, anchor="nw"
        )

    def create_movie_entries(self):
        self.image_references = []
        target_height = 128
        for movie in self.folder_manager.get_movies():
            movie_entry_frame = ttk.Frame(
                self.inner_frame, borderwidth=2, relief="solid"
            )
            movie_entry_frame.pack(fill="x", padx=5, pady=2)

            image = Image.open(movie.get_image_path())
            aspect_ratio = image.width / image.height
            new_width = int(target_height * aspect_ratio)
            image = image.resize((new_width, target_height))
            photo = ImageTk.PhotoImage(image)

            self.image_references.append(photo)

            image_label = tk.Label(movie_entry_frame, image=photo)
            image_label.pack(side="left")

            title_label = tk.Label(movie_entry_frame, text=movie.title)
            title_label.bind(
                "<Button-1>", lambda _, path=movie.path: self.open_file_path(path)
            )
            title_label.pack(side="left", expand=True, padx=10)

    def create_treeview(self):
        y_scrollbar = ttk.Scrollbar(self.table_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        x_scrollbar = ttk.Scrollbar(self.table_frame, orient=tk.HORIZONTAL)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # Create treeview
        self.tree = ttk.Treeview(
            self.table_frame,
            yscrollcommand=y_scrollbar.set,
            xscrollcommand=x_scrollbar.set,
        )

        # Configure scrollbars
        y_scrollbar.config(command=self.tree.yview)
        x_scrollbar.config(command=self.tree.xview)

        # Setup treeview columns
        self.tree["columns"] = list(self.data.columns)
        self.tree.column("#0", width=0, stretch=tk.NO)  # Hide the first column

        for col in self.data.columns:
            self.tree.column(col, anchor=tk.W, width=100)
            self.tree.heading(col, text=col, anchor=tk.W)

        # Pack treeview
        self.tree.pack(fill="both", expand=True)

    def create_json_viewer(self):
        y_scrollbar = ttk.Scrollbar(self.json_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.json_text = tk.Text(
            self.json_frame, wrap=tk.WORD, yscrollcommand=y_scrollbar.set
        )
        self.json_text.pack(fill="both", expand=True)
        y_scrollbar.config(command=self.json_text.yview)

    def create_status_var(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def bind_all(self):
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_scroll)  # Windows/macOS
        self.canvas.bind_all("<Button-4>", self._on_mouse_scroll)  # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mouse_scroll)  # Linux scroll down

    def _on_mouse_scroll(self, event):
        if event.delta:  # Windows/macOS
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
        elif event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")

    def _on_filter_type_change(self, event):
        filter_type = self.filter_type.get()

        # Clear previous filter value
        self.filter_value.delete(0, tk.END)

        # Provide hint based on filter type
        if not self.dict_data:
            return

    def open_file_path(self, path):
        try:
            os.startfile(path)
        except:
            self.status_var.set("Could't open folder")

    def apply_filter(self):
        filter_type = self.filter_type.get()
        filter_method = self.filter_method.get()
        filter_value = self.filter_value.get()

        if not filter_value:
            messagebox.showwarning("Filter Error", "Please enter a valid filter value.")
            return

        # Apply filter based on type and method
        filtered_data = []

        try:
            for item in self.dict_data:
                if filter_type in item:
                    item_value = item[filter_type]

                    # Convert to appropriate type for comparison
                    try:
                        if isinstance(item_value, (int, float)):
                            filter_value_converted = float(filter_value)
                        else:
                            filter_value_converted = filter_value
                    except ValueError:
                        # If conversion fails, use string comparison
                        item_value = str(item_value)
                        filter_value_converted = filter_value

                    # Apply filter based on method
                    if filter_method == "equals":
                        if str(item_value) == str(filter_value_converted):
                            filtered_data.append(item)
                    elif filter_method == "greater than":
                        if (
                            isinstance(item_value, (int, float))
                            and item_value > filter_value_converted
                        ):
                            filtered_data.append(item)
                    elif filter_method == "less than":
                        if (
                            isinstance(item_value, (int, float))
                            and item_value < filter_value_converted
                        ):
                            filtered_data.append(item)
                    elif filter_method == "contains":
                        if (
                            str(filter_value_converted).lower()
                            in str(item_value).lower()
                        ):
                            filtered_data.append(item)

            # Convert filtered data to DataFrame for display
            filtered_df = pd.DataFrame(filtered_data)

            # Update display with filtered data
            self.display_filtered_data(filtered_df, filtered_data)
            self.status_var.set(f"Filtered: {len(filtered_data)} records found")

        except Exception as e:
            messagebox.showerror("Filter Error", f"Error applying filter: {str(e)}")

    def reset_filter(self):
        # Reset to show all data
        self.display_all_data()
        self.status_var.set(f"Filter reset: {len(self.dict_data)} records displayed")

    def display_all_data(self):
        self.display_filtered_data(self.data, self.dict_data)

    def display_filtered_data(self, filtered_df, filtered_dict_data):
        # update photo view
        # for item in self.inner_frame.get_children
        # Clear existing data in tree view
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add filtered data to treeview
        if not filtered_df.empty:
            for i, row in filtered_df.iterrows():
                self.tree.insert("", tk.END, values=list(row))

        # Update JSON view
        self.json_text.delete(1.0, tk.END)
        if filtered_dict_data:
            json_str = json.dumps(filtered_dict_data, indent=2)
            self.json_text.insert(tk.END, json_str)

        # Update chart
        self.update_chart(filtered_df)

    def update_chart(self, data):
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        if data.empty:
            ttk.Label(self.chart_frame, text="No data to display").pack(expand=True)
            return

        # Create figure and axis
        fig, ax = plt.subplots(figsize=(8, 4))

        # Determine chart type based on filter
        filter_type = self.filter_type.get()

        # Create appropriate chart based on data type
        if filter_type in data.columns:
            if data[filter_type].dtype in [int, float]:
                # Numeric data - create histogram
                ax.hist(data[filter_type], bins=10, edgecolor="black")
                ax.set_title(f"Distribution of {filter_type}")
                ax.set_xlabel(filter_type)
                ax.set_ylabel("Frequency")
            else:
                # Categorical data - create bar chart
                counts = data[filter_type].value_counts()
                counts.plot(kind="bar", ax=ax)
                ax.set_title(f"Count by {filter_type}")
                ax.set_ylabel("Count")
                ax.tick_params(axis="x", rotation=45)
        else:
            ax.text(
                0.5,
                0.5,
                "Select a valid field to display chart",
                horizontalalignment="center",
                verticalalignment="center",
                transform=ax.transAxes,
            )

        # Create canvas
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def main():
    def _quit():
        root.quit()
        root.destroy()

    root = tk.Tk()
    root.protocol("WM_DELETE_WINDOW", _quit)
    app = DataFilterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
