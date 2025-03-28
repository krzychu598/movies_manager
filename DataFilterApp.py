import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from FolderManager import FolderManager, Tag
import json, os
from PIL import Image, ImageTk


class DataFilterApp:
    def __init__(self, root):
        self.root = root
        self.folder_manager = FolderManager()
        try:
            self.folder_manager.initialize()
        except:
            directory = filedialog.askdirectory(title="Select Data Directory")
            self.folder_manager.initialize(directory)

        self.root.title("Data Filter Application")
        self.root.geometry("800x600")
        self.root.minsize(800, 600)
        # self.root.state("zoomed")
        # root.configure(bg="#2E2E2E")

        self.movies = self.folder_manager.get_movies()

        self.create_widgets()
        self.display_all_data()

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

        if len(self.folder_manager.movies) > 0:
            available_fields = self.folder_manager.get_keys()
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

    def clear_movie_entries(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

    def create_movie_entries(self):
        self.image_references = []
        target_height = 128
        for movie in self.movies:
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

            text = f"{movie.title} ({movie.year})\nDirector:\t{movie.director}"  # \tScreenplay:\t{", ".join(movie.screenplay)}
            title_label = tk.Label(
                movie_entry_frame,
                text=text,
            )
            title_label.bind(
                "<Button-1>", lambda _, path=movie.path: self.open_file_path(path)
            )
            title_label.pack(anchor="nw", padx=10)

            cast = movie.info.get("cast", None)
            if cast:
                cast = f"\nCast:\t{movie.info["cast"][0]["name"]}, {movie.info["cast"][1]["name"]}"
                cast_label = tk.Label(movie_entry_frame, text=cast)
                cast_label.pack(anchor="nw", padx=10)

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

        data = pd.DataFrame(
            [movie.displayable_info() for movie in self.folder_manager.get_movies()]
        )
        self.tree["columns"] = list(data.columns)
        self.tree.column("#0", width=0, stretch=tk.NO)  # Hide the first column

        for col in data.columns:
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
        self.filter_value.delete(0, tk.END)

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

        filtered_data = self.folder_manager.apply_filter(
            filter_type, filter_method, filter_value
        )

        self.movies = filtered_data
        self.display_filtered_data(filtered_data)
        self.status_var.set(f"Filtered: {len(filtered_data)} records found")

    def reset_filter(self):
        self.display_all_data()
        self.status_var.set(f"Filter reset: {len(self.dict_data)} records displayed")

    def display_all_data(self):
        self.display_filtered_data(self.folder_manager.get_movies())

    def display_filtered_data(self, movies):
        filtered_dict_displayable = [movie.displayable_info() for movie in movies]
        df = pd.DataFrame(filtered_dict_displayable)
        filtered_df = df[["title"] + [col for col in df.columns if col != "title"]]
        filtered_all_data = [movie.info for movie in movies]

        # Update photo view
        self.clear_movie_entries()
        self.create_movie_entries()

        # Update tree view
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not filtered_df.empty:
            for i, row in filtered_df.iterrows():
                self.tree.insert("", tk.END, values=list(row))

        # Update JSON view
        self.json_text.delete(1.0, tk.END)
        if movies:
            json_str = json.dumps(filtered_all_data, indent=2)
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

        fig, ax = plt.subplots(figsize=(8, 4))

        filter_type = self.filter_type.get()

        if filter_type in data.columns:
            if data[filter_type].dtype in [int, float]:
                ax.hist(data[filter_type], bins=10, edgecolor="black")
                ax.set_title(f"Distribution of {filter_type}")
                ax.set_xlabel(filter_type)
                ax.set_ylabel("Frequency")
            else:
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
