import traceback
from modules import wb_template_reader
from modules import ui_manager
from modules import modbus
from tkinter import *


class App:
    json_file = None
    reader = None
    ui = None
    mb = None
    groups = {}
    params = {}
    max_col = 2  # количество колонок с виджетами +1
    reg_errors_count = 0
    reg_count = 0

    def __init__(self):
        # Создаём объекты для работы
        self.reader = wb_template_reader.WbTemplateReader()
        self.ui = ui_manager.UiManager()
        self.mb = modbus.ModbusRTUClient()

        # Подписываемся на события кнопок
        self.ui.btn_open_template.bind("<ButtonPress-1>", self.btn_open_template_click)
        self.ui.btn_read_params.bind("<ButtonPress-1>", self.btn_read_params_click)
        self.ui.btn_write_params.bind("<ButtonPress-1>", self.btn_write_params_click)

        self.ui.write_log("Настройте параметры подключения и откройте шаблон.")
        self.ui.win.mainloop()

    def load_template(self, filepath):
        try:
            self.ui.write_log("Загружаю шаблон {}".format(filepath))
            self.reader.read_template(filepath)
            self.ui.write_log("Получаю группы.")
            self.groups = self.reader.get_groups()
            self.ui.write_log("Получаю список параметров.")
            self.params = self.reader.get_parameters()

            device_name = self.reader.get_device_name()
            self.ui.write_log("=== {} ===".format(device_name))
            self.ui.write_log(
                "В шаблоне {} {}.".format(
                    len(self.params),
                    self.numeral_noun_declension(
                        len(self.params), "параметр", "параметра", "параметров"
                    ),
                )
            )
            self.ui.get_widget("nodel_left_frame").config(
                text="Настройки {}".format(device_name)
            )
            return True
        except Exception as e:
            self.ui.write_log("Ошибка:")
            self.ui.write_log(traceback.format_exc())
            return False

    def is_main_group(self, item):
        return "group" not in item

    def get_params_by_group(self, id):
        res = {}
        for key in self.params:
            if self.params[key].get("group") == id:
                res[key] = self.params[key]
        return res

    def get_params_without_group(self):
        res = {}
        for key in self.params:
            if self.params[key].get("group") == None:
                res[key] = self.params[key]
        return res

    def create_widget(self, group_widget, param_id, param_item):
        condition = param_item.get("condition")
        title = self.reader.get_translate(param_item["title"])
        group_widget.condition = condition
        if group_widget.type == "tab":
            group_widget = group_widget.child_wrap
        param_type = self.reader.get_parameter_type(param_item)

        if param_type == "enum":
            default = param_item["default"]
            dic = self.reader.get_enum_dic(param_item)
            param_widget = self.ui.create_combobox(
                group_widget, param_id, title, dic, default, width=40, anchor=NW
            )
        else:
            default = param_item.get("default")
            min_ = param_item.get("min")
            max_ = param_item.get("max")
            if "scale" in param_item:
                value_type = "double"
            else:
                value_type = "inc"

            param_widget = self.ui.create_spinbox(
                group_widget,
                param_id,
                title,
                min_,
                max_,
                value_type,
                default,
                width=20,
                description=True,
                anchor=NW,
            )
        param_widget.condition = condition

    def fill_window_params_without_group(self):
        params_without_group = self.get_params_without_group()

        if len(params_without_group) > 0:
            group_widget = self.ui.create_tab("mode_params_group", "Режим")
            curr_frame = group_widget.curr_frame

            for key in params_without_group:
                item = params_without_group[key]
                self.create_widget(group_widget, key, item)

    def fill_window(self):
        # Перебираем группы и создаём для верхнего уровня табы, а для остальных — группы
        for item in self.groups:
            title = self.reader.get_translate(item["title"])
            condition = item.get("condition")
            id_group = item["id"]
            if self.is_main_group(item):
                group_widget = self.ui.create_tab(id_group, title)
                curr_frame = group_widget.curr_frame
            else:
                parent_id = item["group"]
                parent = self.ui.get_widget(parent_id)
                if parent != None:
                    # print('[parent_id: {} ] curr_row: {} curr_col: {}  title: {}'.format
                    #       (parent_id, parent.curr_row, parent.curr_col, title))
                    if parent.type == "tab":
                        if item.get("ui_options") == None:
                            curr_frame = parent.curr_frame
                            if parent.curr_col < self.max_col:
                                group_widget = self.ui.create_group(
                                    curr_frame, id_group, title, side=LEFT, anchor=NW
                                )

                                parent.curr_col += 1
                            else:
                                curr_frame = self.ui.create_row(
                                    parent, parent_id + "_row"
                                )
                                parent.curr_frame = curr_frame

                                group_widget = self.ui.create_group(
                                    curr_frame, id_group, title, side=LEFT, anchor=NW
                                )

                                parent.curr_col = 0
                                parent.curr_row += 1
                else:
                    print("Не нашёл контрол {}.".format(parent_id))

            # Запрашиваем параметры, у которых одна группа
            parameters = self.get_params_by_group(id_group)
            # Перебираем параметры с одной группой и создаём для них виджеты
            for key in parameters:
                item = parameters[key]
                self.create_widget(group_widget, key, item)

    # взято из интернета: https://ru.stackoverflow.com/a/1413836
    def numeral_noun_declension(
        self, number, nominative_singular, genetive_singular, nominative_plural
    ):
        return (
            (number in range(5, 20))
            and nominative_plural
            or (1 in (number, (diglast := number % 10)))
            and nominative_singular
            or ({number, diglast} & {2, 3, 4})
            and genetive_singular
            or nominative_plural
        )

    # когда меняем значение параметра-комбобокса — показывает или скрываем другие
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

    def btn_open_template_click(self, event):
        filepath = self.ui.open_file()
        if len(filepath) > 0:
            self.ui.delete_widgets()

            try:
                if self.load_template(filepath):
                    self.ui.write_log("Формирую интерфейс редактора.")

                    self.fill_window_params_without_group()  # создаём виджеты для параметров без групп, например, режимов
                    self.fill_window()  # создаём виджеты для остальных параметров

                    # Скрываем виджеты, которые не должны быть отображены
                    self.widgets_hide_by_condition()
                    self.ui.write_log(
                        "Укажите адрес устройства, а потом прочитайте из него параметры. Внесите изменения и запишите параметры в устройство."
                    )
            except Exception as e:
                self.ui.write_log("Ошибка:")
                self.ui.write_log(traceback.format_exc())

    # Чтение параметров из устройства

    def read_parameters(self, slave_id):
        self.mb.ui = self.ui
        self.errors_count = 0
        self.reg_count = 0

        for key in self.params:
            items = self.params.get(key)
            reg_type = items["reg_type"]
            if reg_type == "holding":
                try:
                    value = self.mb.read_holding(slave_id, items["address"])
                    self.reg_count += 1
                    widget = self.ui.get_widget(key)
                    value = value[0]
                    if widget.type == "spinbox":
                        if "scale" in items:
                            scale = items["scale"]
                            value = value * scale
                            widget.set(value)
                        else:
                            widget.set(value)
                    else:
                        if widget.type == "combobox":
                            dic = widget.dic
                            index = dic["enum"].index(value)
                            widget.current(index)
                except Exception as e:
                    msg = "%s" % e
                    if "ExceptionResponse" in msg:
                        self.errors_count += 1
                        self.ui.write_log(
                            "Регистр {} не читается.".format(items["address"])
                        )
                        self.ui.widget_disable(key)
                    else:
                        if "ModbusIOException" in msg:
                            self.ui.write_log(
                                "Не смог подключиться к устройству. Проверьте настройки подключения."
                            )
                        break

    def btn_read_params_click(self, event):
        try:
            mb_params = self.ui.get_modbus_params()
            self.mb.init(mb_params)
            slave_id = int(mb_params["slave_id"])

            self.ui.write_log("Читаю регистры устройства {}.".format(slave_id))

            self.mb.connect()
            self.read_parameters(slave_id)
            self.widgets_hide_by_condition()

            self.mb.disconnect()
            if self.errors_count > 0:
                self.ui.write_log(
                    "Прочитал из устройства {} {}. Не смог прочитать {}, они будут недоступны для редактирования.".format(
                        self.reg_count,
                        self.numeral_noun_declension(
                            self.reg_count, "параметр", "параметра", "параметров"
                        ),
                        self.errors_count,
                    )
                )
            else:
                self.ui.write_log("Прочитал, можно вносить изменения.")
        except Exception as e:
            self.ui.write_log(e)
            # print(traceback.format_exc())

    # Запись параметров в устройство
    def write_parameters(self, slave_id):
        self.reg_errors_count = 0
        self.reg_count = 0
        for key in self.params:
            items = self.params.get(key)
            if items["reg_type"] == "holding":
                value = self.ui.get_value(key)
                if value != None:
                    if "scale" in items:
                        value = value / items["scale"]
                    try:
                        value = self.mb.write_holding(slave_id, items["address"], value)
                        self.reg_count += 1
                    except Exception as e:
                        msg = "%s" % e
                        if "IllegalValue" in msg:
                            self.reg_errors_count += 1
                            self.ui.write_log(
                                "Регистр {} не записывается.".format(items["address"])
                            )
                        else:
                            if "Message" in msg:
                                self.ui.write_log("Не смог подключиться к устройству.")
                            break

    def btn_write_params_click(self, event):
        try:
            mb_params = self.ui.get_modbus_params()
            self.mb.init(mb_params)
            slave_id = int(mb_params["slave_id"])

            self.ui.write_log("Пишу параметры устройства {}.".format(slave_id))

            self.mb.connect()
            self.write_parameters(slave_id)
            self.mb.disconnect()
            self.ui.write_log(
                "Записал {} {}. Не смог записать {}.".format(
                    self.reg_count,
                    self.numeral_noun_declension(
                        self.reg_count, "параметр", "параметра", "параметров"
                    ),
                    self.reg_errors_count,
                )
            )
        except Exception as e:
            self.ui.write_log(e)


app = App()
