from abc import ABC, abstractmethod
import logging
import tkinter as tk
from tkinter import Scrollbar, Canvas, Menu
#from dictedit2.renderers.dict_renderer import DictRenderer as DictRenderer
import uuid
#from base import CanvasWithScrollbar, TypeConverter, RendererFactory

logger = logging.getLogger(__name__)

class CustomFrame(tk.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget_id = str(uuid.uuid4())

class CustomLabel(tk.Label):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget_id = str(uuid.uuid4())

class CustomButton(tk.Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widget_id = str(uuid.uuid4())

# GUI Utility Class
class GUIUtils:
    widget_tooltips = {}
    widget_ids = {}

    @staticmethod
    def create_frame(parent, bg_color):
        frame = CustomFrame(parent, bd=1, relief=tk.GROOVE, bg=bg_color, padx=5, pady=5)
        frame.grid(sticky="ew", padx=10, pady=5)
        parent.columnconfigure(0, weight=1)
        return frame

    @staticmethod
    def create_label(parent, text, bg_color, font=None):
        label = CustomLabel(parent, text=text, bg=bg_color, anchor="w", font=font)
        return label

    @staticmethod
    def create_button(parent, text, command, bg_color, tooltip=None):
        button = CustomButton(parent, text=text, command=command, bg=bg_color)
        if tooltip:
            GUIUtils.add_tooltip(button, tooltip)
        return button

    @staticmethod
    def assign_widget_id(widget):
        widget_id = widget.widget_id
        GUIUtils.widget_ids[widget_id] = widget

    @staticmethod
    def add_tooltip(widget, text):
        widget_id = widget.widget_id
        GUIUtils.widget_tooltips[widget_id] = None

        def on_enter(event):
            if GUIUtils.widget_tooltips[widget_id] is None:
                x, y, _, _ = widget.bbox("insert") if "bbox" in dir(widget) else (0, 0, 0, 0)
                x += widget.winfo_rootx()
                y += widget.winfo_rooty() + 20
                tooltip = tk.Toplevel(widget)
                tooltip.wm_overrideredirect(True)
                tooltip.geometry(f"+{x}+{y}")
                label = tk.Label(tooltip, text=text, bg="yellow", relief="solid", borderwidth=1)
                label.pack()
                GUIUtils.widget_tooltips[widget_id] = tooltip

        def on_leave(event):
            tooltip = GUIUtils.widget_tooltips.get(widget_id)
            if tooltip:
                tooltip.destroy()
                GUIUtils.widget_tooltips[widget_id] = None

        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)


class CanvasWithScrollbar:
    """Encapsulates a Canvas with a vertical scrollbar."""
    def __init__(self, master, width, height):
        self.canvas = Canvas(master, width=width, height=height)
        self.scrollbar = Scrollbar(master, orient=tk.VERTICAL, command=self.canvas.yview)
        self.frame = tk.Frame(self.canvas)

        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Mouse scrolling support
        self.canvas.bind_all("<MouseWheel>", self._on_mouse_scroll)

    def _on_mouse_scroll(self, event):
        self.canvas.yview_scroll(-1 * (event.delta // 120), "units")

class TypeConverter:
    """Handles type conversions for editor values."""
    @staticmethod
    def convert_to_type(value, target_type):
        try:
            return target_type(value)
        except ValueError:
            logger.warning(f"Cannot convert value '{value}' to {target_type.__name__}.")
            return value


class RendererFactory:
    """Creates appropriate renderers based on data type."""
    @staticmethod
    def get_renderer(editor, item, parent, path):
        if isinstance(item, dict):
            from dictedit2.renderers.dict_renderer import DictRendererCustom
            return DictRendererCustom(editor, parent, path, GUIUtils())
        elif isinstance(item, list):
            from dictedit2.renderers.list_renderer import ListRendererCustom
            return ListRendererCustom(editor, parent, path, GUIUtils())
        else:
            from dictedit2.renderers.value_renderer import ValueRendererCustom
            return ValueRendererCustom(editor, parent, path, GUIUtils())

class CustomDataTypeRenderer(ABC):
    """Base class for all custom data type renderers with standardized callbacks and behaviors."""

    def __init__(self, editor, parent, path, gui_utils, readonly=False, auto_resize=False, default_value=None):
        self.editor = editor
        self.parent = parent
        self.path = path
        self.gui_utils = gui_utils
        self.readonly = readonly
        self.auto_resize = auto_resize
        self.default_value = default_value
        self.custom_bindings = {}
        self.context_menu = None
        self.default_keypress_handler = lambda event: logger.debug(f"Key pressed: {event.keysym}")
        self.default_click_handler = lambda event: logger.debug(f"Mouse clicked at: ({event.x}, {event.y})")
        self.on_click = self.default_click_handler
        self.on_key_press = self.default_keypress_handler

    @abstractmethod
    def render(self, item):
        pass

    @abstractmethod
    def get_metadata(self):
        pass

    @abstractmethod
    def appearance(self):
        pass

    def create_frame(self, bg_color):
        frame = self.gui_utils.create_frame(self.parent, bg_color)
        self._add_custom_bindings(frame)
        #self._add_help_tooltip(frame)
        return frame

    def _add_custom_bindings(self, frame):
        """Add default and custom key and mouse bindings for enhanced interaction."""
        frame.bind("<KeyPress>", self.on_key_press)
        frame.bind("<Button-1>", self.on_click)
        frame.bind("<Button-3>", self._show_context_menu)

        for event, callback in self.custom_bindings.items():
            frame.bind(event, callback)

    def _add_help_tooltip(self, widget):
        """Show help text on mouse hover."""
        metadata = self.get_metadata()
        help_text = metadata.get("help_text", "")

        if help_text:
            GUIUtils.add_tooltip(widget, help_text)

    def _show_context_menu(self, event):
        metadata = self.get_metadata()
        context_menu_items = metadata.get("context_menu", [])

        if not context_menu_items:
            return

        if not self.context_menu:
            self.context_menu = Menu(self.parent, tearoff=0)

        # Clear existing menu
        self.context_menu.delete(0, "end")

        # Populate menu dynamically
        for item in context_menu_items:
            label = item.get("label", "")
            command = item.get("command", lambda: logger.info("No command assigned."))
            self.context_menu.add_command(label=label, command=command)

        self.context_menu.post(event.x_root, event.y_root)

    def resize_field(self, field, content):
        metadata = self.get_metadata()
        default_width = metadata.get("default_width", 10)
        multiline = metadata.get("multiline", False)
        auto_resize = metadata.get("auto_resize", self.auto_resize)

        if multiline and isinstance(field, tk.Text):
            lines = content.split('\n')
            height = max(1, len(lines))
            field.configure(wrap=tk.WORD, height=height)

            # Adjust width based on the longest line
            max_line_length = max(len(line) for line in lines)
            width = max(default_width, max_line_length + 2)
            field.configure(width=width)
        elif auto_resize:
            width = max(default_width, len(content) + 2)
            field.configure(width=width)

    @staticmethod
    def modify_button_behavior(button, new_command):
        """Update the behavior of a button dynamically."""
        button.configure(command=new_command)

    @staticmethod
    def validate_input(input_value):
        """Provide a default input validation mechanism."""
        if not input_value.strip():
            raise ValueError("Input cannot be empty")

    def create_action_buttons(self, frame, actions, row):
        """Standardized creation of action buttons."""
        button_frame = self.gui_utils.create_frame(frame, frame["bg"])
        button_frame.grid(row=row, column=2, sticky="e")

        metadata = self.get_metadata()
        button_metadata = metadata.get("action_buttons", {})

        for action, label in actions.items():
            tooltip = button_metadata.get(action, {}).get("tooltip", None)
            button = self.gui_utils.create_button(
                button_frame,
                text=label,
                command=lambda a=action: self.handle_action(a),
                bg_color=frame["bg"],
                tooltip=tooltip
            )
            button.pack(side=tk.LEFT, padx=2)

    def create_header(self, frame):
        metadata = self.get_metadata()
        header = self.gui_utils.create_label(
            frame,
            text=metadata["name"],
            bg_color=self.appearance()["bg_color"],
            font=("Arial", 10, "bold")
        )
        header.grid(row=0, column=0, columnspan=3, sticky="w")

    def handle_action(self, action):
        logger.debug(f"Action '{action}' triggered at path {self.path}")

    def render_with_validation(self, item, entry_field):
        """Render item with input validation on focus out."""
        if self.default_value is not None and item is None:
            item = self.default_value

        if isinstance(entry_field, tk.Text):
            entry_field.insert("1.0", str(item))
        else:
            entry_field.insert(0, str(item))

        if self.readonly:
            entry_field.configure(state="readonly")
        else:
            entry_field.bind("<FocusOut>", lambda e: self._validate_and_update(entry_field))
            entry_field.bind("<KeyRelease>", lambda e: self._resize_field_on_key_release(entry_field))

        self.resize_field(entry_field, str(item))

    def _resize_field_on_key_release(self, entry):
        if isinstance(entry, tk.Text):
            content = entry.get("1.0", "end-1c")
        else:
            content = entry.get()
        self.resize_field(entry, content)

    def _validate_and_update(self, entry):
        try:
            if isinstance(entry, tk.Text):
                value = entry.get("1.0", "end-1c")
            else:
                value = entry.get()
            self.validate_input(value)
            self.editor.update_value(self.path, value)
        except ValueError as e:
            logger.error(f"Validation failed: {e}")
