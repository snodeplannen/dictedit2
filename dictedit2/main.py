# main.py
import tkinter as tk
from tkinter import filedialog
import json
import logging
from editor import DataEditor

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def on_data_changed(data):
    logger.info("Data changed: %s", data)

def export_data(data):
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info("Data exported to %s", file_path)

def import_data(editor):
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'r') as f:
            imported_data = json.load(f)
        editor.data = imported_data
        editor.render()
        logger.info("Data imported from %s", file_path)

def add_custom_button(editor, frame):
    def custom_action():
        logger.info("Custom button clicked!")

    custom_button = tk.Button(frame, text="Custom Action", command=custom_action, bg="lightgrey")
    custom_button.pack(side=tk.LEFT, padx=5, pady=5)

# Sample data for testing
sample_data = {
    "name": "Example",
    "items": [
        {"id": 1, "label": "Item 1", "subitems": [{"subid": 1, "sublabel": "sub-item 1"}, {"subid": 2, "sublabel": "sub-item 2"}]},
        {"id": 2, "label": "Item 2"},
        {"id": 3, "label": "Item 3", "details": {"status": "active", "value": 123}}
    ],
    "settings": {
        "option1": True,
        "option2": "value2"
    },
    "matrix": [
        [1, 2, 3],
        [4, 5, 6],
        [7, 8, 9]
    ],
    "nested_arrays": [
        [
            ["a", "b"],
            ["c", "d"]
        ],
        [
            [1, 2],
            [3, 4]
        ]
    ]
}

# Initialize Tkinter
root = tk.Tk()
root.title("Enhanced Data Editor")

# Create editor instance
editor = DataEditor(root, sample_data, callbacks={"on_data_changed": on_data_changed}, window_size=(800, 600))

# Add menu for export/import functionality
menu_bar = tk.Menu(root)
file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Export", command=lambda: export_data(editor.data))
file_menu.add_command(label="Import", command=lambda: import_data(editor))
menu_bar.add_cascade(label="File", menu=file_menu)
root.config(menu=menu_bar)

# Add custom button
control_frame = tk.Frame(root, bg="white")
control_frame.pack(side=tk.BOTTOM, fill=tk.X)
add_custom_button(editor, control_frame)

# Start main loop
root.mainloop()