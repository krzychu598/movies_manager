import tkinter as tk


class ScrollableFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # Canvas and Scrollbar
        self.canvas = tk.Canvas(self, height=300)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        # Configure scroll region
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )

        window = self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind(
            "<Configure>", lambda e: self.canvas.itemconfig(window, width=e.width)
        )

        # Bind mouse scroll
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_scroll)  # Windows/macOS
        self.canvas.bind_all("<Button-4>", self._on_mouse_scroll)  # Linux scroll up
        self.canvas.bind_all("<Button-5>", self._on_mouse_scroll)  # Linux scroll down

        # Layout
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def _on_mouse_scroll(self, event):
        if event.delta:  # Windows/macOS
            self.canvas.yview_scroll(-1 * (event.delta // 120), "units")
        elif event.num == 4:  # Linux scroll up
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:  # Linux scroll down
            self.canvas.yview_scroll(1, "units")

    def add_item(self, text):
        frame = tk.Frame(self.scrollable_frame, bg="lightgray", padx=5, pady=5)
        label = tk.Label(frame, text=text, bg="lightgray")
        button = tk.Button(
            frame, text="Click", command=lambda: print(f"Clicked: {text}")
        )

        label.pack(side="left", padx=10)
        button.pack(side="right", padx=10)
        frame.pack(fill="x", pady=5, padx=10)


# Main application
root = tk.Tk()
root.title("Scrollable Labels")

scrollable = ScrollableFrame(root)
scrollable.pack(fill="both", expand=True, padx=10, pady=10)

# Adding items
for i in range(20):
    scrollable.add_item(f"Item {i+1}")

root.mainloop()
