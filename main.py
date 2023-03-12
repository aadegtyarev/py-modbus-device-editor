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
        self.create_pages()
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

            for key in groups:
                group = groups[key]

                if group.get("group") == None:
                    group_widget = self.ui.create_tab(key, group.get("title"))
                    group_widget.condition = group.get("condition")


            return True
        except Exception as e:
            self.ui.write_log("Ошибка:")
            self.ui.write_log(traceback.format_exc())
            return False

    def create_groups(self):
        self.ui.write_log("Создаю группы.")

        groups = self.reader.get_groups()

        for key in groups:
            group = groups[key]
            title = group.get("title")
            parent_id = group.get("group")
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
                                curr_frame, key, title, side=LEFT, anchor=NW
                            )
                group_widget.condition = group.get("condition")
                # self.ui.create_label(group_widget, key, key)
            else:
                group_widget = self.ui.get_widget(key)

            if (group_widget != None):
                self.create_params(key, group_widget)

    def create_params(self, group_id, group_widget):
        params = self.reader.get_params_by_group(group_id)
        parent = self.get_current_frame(group_widget)

        if (len(params)>0):
            for key in params:
                param = params[key]
                self.create_widget(
                    widget_id=key,
                    group_widget=group_widget,
                    param=param
                )
                # print(group_id, parent.type)


                #ToDo сделать создание виджетов
    
    def create_widget(self, widget_id, group_widget, param):
        param_type = param["widget"].get("type")

        if param_type == "enum":
            title = param["widget"].get("title")
            dic = self.reader.get_enum_dic(param)
            default = param["widget"].get("default")
            
            self.ui.create_combobox(
                parent= group_widget, 
                id= widget_id, 
                title =title, 
                dic=dic, 
                default = default, 
                width=50,
                side=TOP, 
                anchor=NW
                )

    def get_current_frame(self, parent):
        if parent.type == "tab":
            curr_frame = parent.curr_frame
        else:
            curr_frame = parent
        return curr_frame


app = App()
