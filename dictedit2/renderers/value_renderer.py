import tkinter as tk
from dictedit2.components.base import CustomDataTypeRenderer

class ValueRendererCustom(CustomDataTypeRenderer):
    def render(self, item):
        frame = self.create_frame(bg_color="lightyellow")

        metadata = self.get_metadata()
        multiline = metadata.get("multiline", False)

        if multiline:
            entry = tk.Text(frame, wrap=tk.WORD)
        else:
            entry = tk.Entry(frame)

        self.render_with_validation(item, entry)
        entry.grid(sticky="ew", row=1, column=0, columnspan=2)

    def update_value(self, entry):
        new_value = entry.get()
        self.editor.update_value(self.path, new_value)

    def get_metadata(self):
        return {
            "context_menu": [],
            "default_width": 10,
            "multiline": True,
            "height": 5,
            "action_buttons": {},
            "auto_resize": True  # Enable auto-resize
        }

    def appearance(self):
        return {"bg_color": "lightyellow", "font": "Courier"}
