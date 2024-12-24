import tkinter as tk
from .base import CustomDataTypeRenderer

class ListRendererCustom(CustomDataTypeRenderer):
    def render(self, item):
        frame = self.create_frame(bg_color=self.appearance()["bg_color"])
        self.create_header(frame)

        for i, value in enumerate(item):
            list_item_frame = tk.Frame(frame, bg=self.appearance()["bg_color"])
            list_item_frame.grid(row=i+1, column=0, sticky="ew", padx=5, pady=2)
            list_item_frame.columnconfigure(0, weight=1)

            self.editor.render_item(value, list_item_frame, self.path + (i,))

            action_button_frame = tk.Frame(list_item_frame, bg=self.appearance()["bg_color"])
            action_button_frame.grid(row=0, column=1, sticky="e", padx=5, pady=2)

            tk.Button(
                action_button_frame,
                text="-",
                command=lambda index=i: self.editor.handle_action(self.path + (index,), "remove_item")
            ).pack(side=tk.LEFT, padx=2)

            tk.Button(
                action_button_frame,
                text="+",
                command=lambda index=i: self.editor.handle_action(self.path + (index + 1,), "add_item")
            ).pack(side=tk.LEFT, padx=2)

        tk.Button(
            frame,
            text="+",
            command=lambda: self.editor.handle_action(self.path + (len(item),), "add_item")
        ).grid(row=len(item)+1, column=0, sticky="w", padx=5, pady=2)

    def remove_item(self, index):
        try:
            self.editor.update_data(self.path, lambda d: d.pop(index))
        except Exception as e:
            print(f"Error removing item: {e}")
        self.editor.render()

    def add_item(self):
        try:
            self.editor.update_data(self.path, lambda d: d.append(""))
        except Exception as e:
            print(f"Error adding item: {e}")
        self.editor.render()

    def get_metadata(self):
        return {
            "name": "List",
            "short_description": "An ordered collection of items.",
            "help_text": "Use this to store an ordered collection of items.",
            "context_menu": [],
            "default_width": 10,
            "multiline": True,
            "height": 5,
            "action_buttons": {},
            "auto_resize": True  # Enable auto-resize
        }

    def appearance(self):
        return {"bg_color": "lightgreen", "font": "Helvetica"}
