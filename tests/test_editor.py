import unittest
from dictedit2.core.editor import DataEditor
import tkinter as tk

class TestDataEditor(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.data = {"key": "value"}
        self.editor = DataEditor(self.root, self.data)

    def test_initial_data(self):
        self.assertEqual(self.editor.data, {"key": "value"})

    def test_update_value(self):
        self.editor.update_value(("key",), "new_value")
        self.assertEqual(self.editor.data["key"], "new_value")

if __name__ == "__main__":
    unittest.main()