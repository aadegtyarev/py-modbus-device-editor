import traceback
from modules import template_reader
from modules import ui_manager
from tkinter import *


class App:
    reader = None
    ui = None
    mb = None
    max_col = 2  # количество колонок с виджетами +1

    def __init__(self):
        # Создаём объекты для работы
        self.ui = ui_manager.UiManager()
        self.ui.btn_open_template.bind("<ButtonPress-1>", self.btn_open_template_click)

        self.reader = template_reader.TemplateReader()

        self.ui.write_log("Настройте параметры подключения и откройте шаблон.")
        self.ui.win.mainloop()

    def btn_open_template_click(self, event):
        file_patch = self.ui.open_file()
        if len(file_patch) > 0:
            self.ui.delete_widgets()

            try:
                if self.load_template(file_patch):
                    self.create_interface()

            except Exception as e:
                self.ui.write_log("Ошибка:")
                self.ui.write_log(traceback.format_exc())

    def create_interface(self):
        if self.create_pages():
            self.create_groups()

    def load_template(self, file_patch):
        self.ui.write_log("Открываю файл {}".format(file_patch))
        try:
            self.reader.read_template(file_patch)
            return True
        except Exception as e:
            self.ui.write_log("Ошибка:")
            self.ui.write_log(traceback.format_exc())
            return False

    def create_pages(self):
        self.ui.write_log("Создаю вкладки.")

        try:
            groups = self.reader.get_groups()

            for i in range(len(groups)):
                group = groups[i]
                title = self.reader.get_translate(group.get("title"))
                group_id = group.get("id")
                # print(group)

                if group.get("group") == None:
                    group_widget = self.ui.create_tab(group_id, title)
                    group_widget.condition = group.get("condition")

            return True
        except Exception as e:
            self.ui.write_log("Ошибка:")
            self.ui.write_log(traceback.format_exc())
            return False

    def create_groups(self):
        self.ui.write_log("Создаю группы.")

        groups = self.reader.get_groups()

        for i in range(len(groups)):
            group = groups[i]
            title = self.reader.get_translate(group.get("title"))
            parent_id = group.get("group")
            group_id = group.get("id")
            parent = self.ui.get_widget(parent_id)

            if parent != None:
                if parent.curr_col < self.max_col:
                    curr_frame = self.get_current_frame(parent)
                    parent.curr_col += 1
                else:
                    curr_frame = self.ui.create_row(parent, parent_id + "_row")
                    parent.curr_frame = curr_frame
                    parent.curr_col = 0
                    parent.curr_row += 1

                group_widget = self.ui.create_group(
                    curr_frame, group_id, title, side=LEFT, anchor=NW
                )
                group_widget.condition = group.get("condition")
                # self.ui.create_label(group_widget, group_id, group_id)
            else:
                group_widget = self.ui.get_widget(group_id)

            if group_widget != None:
                self.create_params(group_id, group_widget)

    def create_params(self, group_id, group_widget):
        return False
        params = self.reader.get_params_by_group(group_id)
        parent = self.get_current_frame(group_widget)

        if len(params) > 0:
            for i in range(len(params)):
                param = params[i]
                self.create_widget(
                    widget_id=key, group_widget=group_widget, param=param
                )
        # print(group_id, parent.type)

        # ToDo сделать создание виджетов

    def get_param_type(self, param):
        if ("enum" in param):
            return 'enum'

        if ("scale" in param):
            return "double"
        
        return "int"

    def create_widget(self, widget_id, group_widget, param):
        print(self.get_param_type(param))
        return False

    def get_current_frame(self, parent):
        if parent.type == "tab":
            curr_frame = parent.curr_frame
        else:
            curr_frame = parent
        return curr_frame


app = App()
