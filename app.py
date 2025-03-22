import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from format import FolderManager, Tag
import json


class DataFilterApp:
    def __init__(self, root, directory):
        self.root = root
        self.root.title("Data Filter Application")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        self.folder_manager = FolderManager(directory)
        self.update_dict_data()
        self.data = pd.DataFrame(self.dict_data)
        self.create_widgets()
        self.display_data()

    def update_dict_data(self):
        info = []
        for movie in self.folder_manager.movies.values():
            info.append(movie.info)
        self.dict_data = info

    def create_widgets(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", pady=5, padx=10)

        # Add button to load dictionary data
        load_button = ttk.Button(
            top_frame, text="Load Dictionary Data", command=self.load_dictionary_data
        )
        load_button.pack(side="right", padx=5)

        # Create frame for filter options
        filter_frame = ttk.LabelFrame(self.root, text="Filter Options")
        filter_frame.pack(pady=5, padx=10, fill="x")

        # Get available filter types from the first dictionary
        if len(self.dict_data) > 0:
            available_fields = list(self.dict_data[0].keys())
        else:
            available_fields = []

        # Filter type selection
        ttk.Label(filter_frame, text="Filter Field:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )
        self.filter_type = ttk.Combobox(filter_frame, state="readonly")
        self.filter_type["values"] = available_fields
        if available_fields:
            self.filter_type.current(0)
        self.filter_type.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.filter_type.bind("<<ComboboxSelected>>", self.on_filter_type_change)

        # Filter method selection
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

        # Filter value input
        ttk.Label(filter_frame, text="Filter Value:").grid(
            row=1, column=0, padx=5, pady=5, sticky="w"
        )
        self.filter_value = ttk.Entry(filter_frame, width=20)
        self.filter_value.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Add filter button
        self.filter_button = ttk.Button(
            filter_frame, text="Apply Filter", command=self.apply_filter
        )
        self.filter_button.grid(row=1, column=2, padx=5, pady=5)

        # Reset filter button
        self.reset_button = ttk.Button(
            filter_frame, text="Reset Filter", command=self.reset_filter
        )
        self.reset_button.grid(row=1, column=3, padx=5, pady=5)

        # Set default filter values based on selected type
        self.on_filter_type_change(None)

        # Create a frame for displaying data
        self.data_frame = ttk.LabelFrame(self.root, text="Data Display")
        self.data_frame.pack(pady=5, padx=10, fill="both", expand=True)

        # Create a notebook with tabs for table and chart views
        self.notebook = ttk.Notebook(self.data_frame)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        # Table view tab
        self.table_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.table_frame, text="Table View")

        # Chart view tab
        self.chart_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_frame, text="Chart View")

        # Raw JSON view tab
        self.json_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.json_frame, text="JSON View")

        # Create treeview for data table
        self.create_treeview()

        # Create JSON viewer
        self.create_json_viewer()

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w"
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def create_treeview(self):
        # Create scrollbars
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
        # Create scrollbars
        y_scrollbar = ttk.Scrollbar(self.json_frame)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create text widget for JSON display
        self.json_text = tk.Text(
            self.json_frame, wrap=tk.WORD, yscrollcommand=y_scrollbar.set
        )
        self.json_text.pack(fill="both", expand=True)

        # Configure scrollbar
        y_scrollbar.config(command=self.json_text.yview)

    def load_dictionary_data(self):
        # In a real application, you would open a file dialog here
        # For this example, we'll just show a message
        messagebox.showinfo(
            "Load Data",
            "In a real application, this would open a file dialog to select a JSON file with dictionary data.",
        )

        # Example of how you might load data in a real application:
        """
        from tkinter import filedialog
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    self.dict_data = json.load(file)
                    self.data = pd.DataFrame(self.dict_data)
                    
                    # Update filter types based on new data
                    if self.dict_data:
                        available_fields = list(self.dict_data[0].keys())
                        self.filter_type['values'] = available_fields
                        self.filter_type.current(0)
                    
                    # Display the loaded data
                    self.display_data()
                    self.status_var.set(f"Loaded {len(self.dict_data)} records from {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load data: {str(e)}")
        """

    def on_filter_type_change(self, event):
        filter_type = self.filter_type.get()

        # Clear previous filter value
        self.filter_value.delete(0, tk.END)

        # Provide hint based on filter type
        if not self.dict_data:
            return

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
        self.display_data()
        self.status_var.set(f"Filter reset: {len(self.dict_data)} records displayed")

    def display_data(self):
        # Display all data
        self.display_filtered_data(self.data, self.dict_data)

    def display_filtered_data(self, filtered_df, filtered_dict_data):
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
    dir = filedialog.askdirectory(title="Select Data Directory")
    dir.replace("/", "\\")
    app = DataFilterApp(root, dir)
    root.mainloop()


if __name__ == "__main__":
    main()
