import logging
import tkinter as tk

from dictedit2.components.base import CanvasWithScrollbar, TypeConverter, RendererFactory

logger = logging.getLogger(__name__)

class DataEditor:
    def __init__(self, master, data, callbacks=None, window_size=(800, 600)):
        self.master = master
        self.data = data
        self.callbacks = callbacks or {}

        self.canvas_with_scrollbar = CanvasWithScrollbar(master, *window_size)
        self.frame = self.canvas_with_scrollbar.frame

        self._is_rendering = False
        self.render()

    def render(self):
        if self._is_rendering:
            return
        self._is_rendering = True

        self.clear_widgets()
        self.render_data()
        self._is_rendering = False

    def clear_widgets(self):
        for widget in self.frame.winfo_children():
            widget.destroy()

    def render_data(self):
        self.render_item(self.data, self.frame, path=())
        self.notify_callback("on_data_changed", self.data)

    def notify_callback(self, event, *args):
        if event in self.callbacks:
            self.callbacks[event](*args)

    def render_item(self, item, parent, path):
        renderer = RendererFactory.get_renderer(self, item, parent, path)
        renderer.render(item)

    def update_key(self, path, new_key):
        old_key = path[-1]
        parent_path = path[:-1]
        parent_data = self.data
        for p in parent_path:
            parent_data = parent_data[p]

        if new_key in parent_data:
            logger.error(f"Key '{new_key}' already exists in parent data.")
            return

        parent_data[new_key] = parent_data.pop(old_key)
        self.render()

    def add_button(self, parent, path, action, row, column=0):
        text = "+" if "add" in action else "-"
        button = tk.Button(parent, text=text, command=lambda p=path, a=action: self.handle_action(p, a))
        button.grid(row=row, column=column, padx=2, pady=2)

    def handle_action(self, path, action):
        parent_data = self.data
        for p in path[:-1]:
            parent_data = parent_data[p]

        target = path[-1]

        try:
            if action == "add_item":
                if isinstance(parent_data, list):
                    parent_data.insert(target, None)  # Use None as a placeholder for any datatype
            elif action == "remove_item":
                if isinstance(parent_data, list):
                    parent_data.pop(target)
            elif action == "remove_key":
                if isinstance(parent_data, dict):
                    del parent_data[target]
        except (IndexError, KeyError) as e:
            logger.error(f"Error handling action '{action}': {e}")

        self.render()

    def get_data_at_path(self, path):
        data = self.data
        for segment in path:
            data = data[segment]
        return data

    def update_value(self, path, new_value):
        current_value = self.get_data_at_path(path)
        new_value = TypeConverter.convert_to_type(new_value, type(current_value))

        if current_value == new_value:
            logger.debug("No change in value, skipping update.")
            return
        self.update_data(path[:-1], lambda d: d.__setitem__(path[-1], new_value))

    def update_data(self, path, update_func):
        logger.debug(f"update_data called with path={path}")
        data = self.data
        try:
            for key in path:
                data = data[key]

            previous_state = data.copy() if isinstance(data, dict) else list(data)
            update_func(data)

            if data == previous_state:
                logger.debug("No changes detected, skipping re-render.")
                return

            logger.debug(f"Data after update at path {path}: {self.data}")
            self.render()
        except Exception as e:
            logger.error(f"Error in update_data: {e}")