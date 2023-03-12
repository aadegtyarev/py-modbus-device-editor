import traceback
from modules import template_reader
from modules import ui_manager
from tkinter import *
from modules import modbus


class App:
    reader = None
    ui = None
    # mb = None
    max_col = 2  # количество колонок с виджетами +1

    def __init__(self):
        # создаём объекты для работы
        self.ui = ui_manager.UiManager()
        self.ui.btn_open_template.bind("<ButtonPress-1>", self.btn_open_template_click)
        self.ui.btn_read_params.bind("<ButtonPress-1>", self.btn_read_params_click)

        self.reader = template_reader.TemplateReader()

        self.ui.write_log("Настройте параметры подключения и откройте шаблон.")
        self.ui.win.mainloop()

    # действие при нажатии на кнопку Открыть шаблон
    def btn_open_template_click(self, event):
        file_patch = self.ui.open_file()
        if len(file_patch) > 0:
            # удаляем виджеты от предыдущего шаблона
            self.ui.delete_widgets()

            try:
                # загружаем выбранный шаблон
                if self.load_template(file_patch):
                    # если всё ОК — рисуем интерфейс
                    self.create_interface()

            except Exception as e:
                self.ui.write_log("Ошибка:")
                self.ui.write_log(traceback.format_exc())

    def create_interface(self):
        # если у нас есть параметры без групп, например, режимы — создаём для них отдельную вкладку
        params_without_group = self.reader.get_params_without_group()

        if len(params_without_group) > 0:
            parent = self.ui.create_tab("mode_params_group", "Режим")
            curr_frame = parent.curr_frame

            # перебираем безгрупные параметры и создаём для них виджеты
            for i in range(len(params_without_group)):
                param = params_without_group[i]
                self.create_widget(widget_id=param["id"], parent=parent, param=param)

        # создаём вкладки из групп без поля group
        if self.create_pages():
            # создаём группы внутри вкладок
            if self.create_groups():
                self.widgets_hide_by_condition()

    # открываем шаблон
    def load_template(self, file_patch):
        self.ui.write_log("Открываю файл {}".format(file_patch))
        try:
            # парсинг
            self.reader.read_template(file_patch)
            return True
        except Exception as e:
            self.ui.write_log("Ошибка:")
            self.ui.write_log(traceback.format_exc())
            return False

    # создание страниц
    def create_pages(self):
        self.ui.write_log("Создаю вкладки.")

        try:
            groups = self.reader.get_groups()

            for i in range(len(groups)):
                group = groups[i]
                title = self.reader.get_translate(group.get("title"))
                group_id = group.get("id")
                # print(group)
                # если у группы нет родителя, то создаём вкладку
                if group.get("group") == None:
                    group_widget = self.ui.create_tab(group_id, title)
                    group_widget.condition = group.get("condition")

            return True
        except Exception as e:
            self.ui.write_log("Ошибка:")
            self.ui.write_log(traceback.format_exc())
            return False

    # создание групп
    def create_groups(self):
        self.ui.write_log("Создаю группы.")

        groups = self.reader.get_groups()

        try:
            for i in range(len(groups)):
                group = groups[i]
                title = self.reader.get_translate(group.get("title"))
                parent_id = group.get("group")
                group_id = group.get("id")
                parent = self.ui.get_widget(parent_id)

                # а тут магия распределения групп по вкладкам
                if (
                    parent != None
                ):  # если у группы нет родителя, то есть это у нас вкладка, то
                    # проверяем, не вышли ли за пределы максимального числа колонок
                    if parent.curr_col < self.max_col:
                        # если не вышли, то получаем текущий фрейм (строку) и потом увеличиваем счётчик колонок
                        curr_frame = self.get_current_frame(parent)
                        parent.curr_col += 1
                    else:
                        # если счётчик колонок равен максимальном числу колонок на вкладке, то
                        # создаём новую строку, обнуляем счётчик колонок и увеличиваем счётчик строк
                        curr_frame = self.ui.create_row(parent, parent_id + "_row")
                        parent.curr_frame = curr_frame
                        parent.curr_col = 0
                        parent.curr_row += 1

                    # создаём новую группу с учётом магии выше
                    group_widget = self.ui.create_group(
                        curr_frame, group_id, title, side=LEFT, anchor=NW
                    )
                    # добавляем поле condition — это для того, чтобы понимать, надо ли показывать
                    # эту группу при выбранных параметрах
                    group_widget.condition = group.get("condition")
                    # self.ui.create_label(group_widget, group_id, group_id)
                else:
                    # а если родитель у группы есть, то получаем текущий виджет с нужным id
                    group_widget = self.ui.get_widget(group_id)

                # если виджет группы существует — создаём параметры в ней
                if group_widget != None:
                    self.create_params(group_id, group_widget)
                else:
                    print("Виджет для группы {} не существует".format(group_id))
            return True
        except Exception as e:
            self.ui.write_log("Ошибка:")
            self.ui.write_log(traceback.format_exc())
            return False

    def create_params(self, group_id, group_widget):
        params = self.reader.get_params_by_group(group_id)
        parent = self.get_current_frame(group_widget)

        if len(params) > 0:
            for i in range(len(params)):
                param = params[i]
                id = param["id"]
                widget = self.create_widget(widget_id=id, parent=parent, param=param)
                widget.condition = param.get("condition")
                parent.condition = param.get("condition")

    def get_value_type_type(self, param):
        if "enum" in param:
            return "enum"

        if "scale" in param:
            return "double"

        return "int"

    def create_widget(self, widget_id, parent, param):
        value_type = self.get_value_type_type(
            param
        )  # от типа значения зависит ти и настройки создаваемого виджета

        param_id = param["id"]
        param_title = self.reader.get_translate(param.get("title"))
        param_default = param.get("default")

        # есть перечисление — создаём combobox
        if value_type == "enum":
            cmbx_dic = self.reader.get_enum_dic(param)
            widget = self.ui.create_combobox(
                parent=parent,
                id=param_id,
                title=param_title,
                dic=cmbx_dic,
                default=param_default,
                width=50,
                side=TOP,
                anchor=NW,
            )
            widget.bind("<<ComboboxSelected>>", self.combobox_selected)
        # если это число, создаём spinbox и указываем ему нужный формат
        if value_type == "int" or value_type == "double":
            min_ = param.get("min")
            max_ = param.get("max")
            description = param.get("description")
            widget = self.ui.create_spinbox(
                parent=parent,
                id=param_id,
                title=param_title,
                min_=min_,
                max_=max_,
                value_type=value_type,
                default=param_default,
                width=5,
                description=description,
                side=TOP,
                anchor=NW,
            )

        return widget

    # получаем текущий фрейм
    def get_current_frame(self, parent):
        if parent.type == "tab":
            curr_frame = parent.curr_frame
        else:
            curr_frame = parent
        return curr_frame

    def combobox_selected(self, event):
        self.widgets_hide_by_condition()

    def widgets_hide_by_condition(self):
        values = self.ui.get_values()
        widgets = self.ui.get_widgets()

        for key in widgets:
            item = widgets[key]

            if (
                item.type == "group"
                or item.type == "spinbox"
                or item.type == "combobox"
            ):
                if hasattr(item, "condition"):
                    condition = item.condition
                    if condition != None:
                        visible = self.reader.calc_condition(condition, values)
                    else:
                        visible = True

                    if visible:
                        self.ui.widget_show(key)
                    else:
                        self.ui.widget_hide(key)

    def btn_read_params_click(self, event):
        mb_params = self.ui.get_modbus_params()

        client = modbus.ModbusRTUClient(mb_params)
        slave_id = int(mb_params["slave_id"])
        if client.connect():
            self.ui.write_log("Открыл порт")
            self.read_params_from_modbus(client, slave_id)
            self.widgets_hide_by_condition()
        else:
            self.ui.write_log("Не смог открыть порт {}".format(mb_params["port"]))
        client.disconnect()
        return False

    def read_params_from_modbus(self, client, slave_id):
        params = self.reader.get_params()
        if len(params) > 0:
            for i in range(len(params)):
                param = params[i]
                address = int(param["address"])
                if param["reg_type"] == "holding":
                    try:
                        value = client.read_holding(
                            slave_id=slave_id, reg_address=address
                        )

                        self.ui.set_value(param["id"], value, scale=param.get("scale"))
                        self.ui.widget_enable(param["id"])

                    except Exception as e:
                        if "ExceptionResponse" in "%s" % e:
                            self.ui.widget_disable(param["id"])
                            self.ui.write_log("Регистр {} не читается.".format(address))
                        if "ModbusIOException" in "%s" % e:
                            self.ui.write_log("Нет связи с устройством.")
                            break


app = App()
