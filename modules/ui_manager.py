from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Frame, LabelFrame, Notebook, Button, Label, Entry, Combobox, Style
from . import ui_scroll_frame


class UiManager:
    ui_widgets = {}

    def create_frame(self, parent, id, side, fill, expand):
        fr = ttk.Frame(parent)
        fr.pack(padx=5, pady=5, side=side, fill=fill, expand=expand)
        return fr

    def get_values(self):
        widgets = self.ui_widgets
        values = {}

        for key in widgets:
            item = widgets[key]
            if (item.type == 'spinbox'):
                values.update({key: item.get()})

            if (item.type == 'combobox'):
                value = item.get()
                dic = item.dic
                index = dic['enum_titles'].index(value)
                values.update({key: dic['enum'][index]})

        return values

    def widget_hide(self, widget_id):
        widget = self.ui_widgets[widget_id]
        widget.pack_forget()

    def widget_show(self, widget_id):
        widget = self.ui_widgets[widget_id]
        widget.pack(opts)

    def open_file(self):
        file_patch = filedialog.askopenfilename()
        return file_patch

    def remove_widgets_item(self, key):
        self.ui_widgets[key].destroy()
        del self.ui_widgets[key]

    def clear_auto_widgets(self):
        widgets = dict(self.ui_widgets)
        for key in widgets:
            if (widgets[key].auto == True):
                self.remove_widgets_item(key)
