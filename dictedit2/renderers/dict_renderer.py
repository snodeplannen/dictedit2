import tkinter as tk
from dictedit2.renderers.base import CustomDataTypeRenderer as DataTypeRenderer, CustomDataTypeRenderer


class DictRendererCustom(CustomDataTypeRenderer):
    def render(self, item):
        frame = self.create_frame(bg_color=self.appearance()["bg_color"])
        self.create_header(frame)
        # Render each key-value pair
        for i, (key, value) in enumerate(item.items()):
            key_label = tk.Label(frame, text=key, bg=self.appearance()["bg_color"], anchor="w")
            key_label.grid(row=i+1, column=0, sticky="w")
            key_label.bind("<Double-Button-1>", lambda event, k=key, r=i+1: self.edit_key(k, frame, r))

            value_frame = tk.Frame(frame, bg=self.appearance()["bg_color"])
            value_frame.grid(row=i+1, column=1, sticky="ew")
            self.editor.render_item(value, value_frame, self.path + (key,))

            remove_button = tk.Button(
                frame,
                text="-",
                command=lambda k=key: self.remove_key(k),
                bg=self.appearance()["bg_color"]
            )
            remove_button.grid(row=i+1, column=2, sticky="e", padx=5)

        # Add a single plus button at the end for adding new keys
        add_button = tk.Button(
            frame,
            text="+",
            command=self.add_key,
            bg=self.appearance()["bg_color"]
        )
        add_button.grid(row=len(item)+1, column=0, sticky="w", padx=5)
        print(f"DEBUG: Rendered {len(item)} items with Add Key button at row {len(item) + 1}")

    def add_key(self):
        # Generate a unique key name
        base_key = "new_key"
        existing_keys = list(self.editor.get_data_at_path(self.path).keys())
        counter = 1
        new_key = f"{base_key}_{counter}"
        while new_key in existing_keys:
            counter += 1
            new_key = f"{base_key}_{counter}"

        # Add the new key with a default value
        try:
            self.editor.update_data(self.path, lambda d: d.update({new_key: ""}))
        except Exception as e:
            print(f"Error adding key: {e}")

        # Re-render the UI
        self.editor.render()

    def edit_key(self, old_key, frame, row):
        def on_focus_out(event):
            new_key = entry.get()
            if new_key and new_key != old_key:
                try:
                    self.editor.update_key(self.path + (old_key,), new_key)
                except Exception as e:
                    print(f"Error updating key: {e}")
            entry.destroy()
            self.editor.render()

        entry = tk.Entry(frame, font=self.appearance()["font"])
        entry.insert(0, old_key)
        entry.grid(row=row, column=0, sticky="w")
        entry.bind("<FocusOut>", on_focus_out)
        entry.bind("<Return>", lambda event: entry.event_generate("<FocusOut>"))
        entry.focus_set()

    def remove_key(self, key):
        try:
            self.editor.update_data(self.path, lambda d: d.pop(key))
        except Exception as e:
            print(f"Error removing key: {e}")
        self.editor.render()

    def get_metadata(self):
        return {
            "name": "Dictionary Item",
            "help_text": "This is a dictionary item.",
            "context_menu": [],
            "default_width": 10,
            "multiline": False,
            "height": 5,
            "action_buttons": {}
        }

    def appearance(self):
        return {"bg_color": "lightblue", "font": "Arial"}