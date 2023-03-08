import traceback
from modules import wb_template_reader
from modules import ui_manager
from tkinter import *

json_file = 'templates/config-wb-mr6c.json'
reader = wb_template_reader.WbTemplateReader()
ui = ui_manager.UiManager()


# Создаём окно с содержимым


ui.write_log('Загружаю шаблон')
reader.read_template(json_file)
ui.write_log('Получаю группы')
groups = reader.get_groups()
ui.write_log('Получаю список параметров')
params = reader.get_parameters()


def is_main_group(item):
    return 'group' not in item


def get_params_by_group(id):
    res = {}
    for key in params:
        if (params[key]['group'] == id):
            res[key] = params[key]
    return res


max_col = 2


def fill_window():
    for item in groups:
        title = reader.get_translate(item['title'])
        id_group = item['id']
        if (is_main_group(item)):
            group_widget = ui.create_tab(id_group, title)
            curr_frame = group_widget.curr_frame
        else:
            parent_id = item['group']
            parent = ui.widgets[parent_id]
            if (parent != None):
                # print('[parent_id: {} ] curr_row: {} curr_col: {}  title: {}'.format
                #       (parent_id, parent.curr_row, parent.curr_col, title))
                if (parent.type == 'tab'):
                    if (item.get('ui_options') == None):
                        curr_frame = parent.curr_frame
                        if(parent.curr_col < max_col):
                            group_widget = ui.create_group(
                                curr_frame, id_group, title, side=LEFT, anchor=NW)

                            parent.curr_col += 1
                        else:
                            curr_frame = ui.create_row(
                                parent, parent_id+'_row')
                            parent.curr_frame = curr_frame

                            group_widget = ui.create_group(
                                curr_frame, id_group, title, side=LEFT, anchor=NW)

                            parent.curr_col = 0
                            parent.curr_row += 1
            else:
                print('Не нашёл контрол {}'.format(parent_id))

        parameters = get_params_by_group(id_group)

        for key in parameters:
            item = parameters[key]
            title = reader.get_translate(item['title'])
            param_type = reader.get_parameter_type(item)
            if (group_widget.type == 'tab'):
                group_widget = group_widget.child_wrap

            if (param_type == 'enum'):
                default = item['default']
                dic = reader.get_enum_dic(item)
                param_widget = ui.create_combobox(
                    group_widget, key, title, dic, default)
            else:
                default = item.get('default')
                min_ = item.get('min')
                max_ = item.get('max')
                if('scale' in item):
                    value_type = 'double'
                else:
                    value_type = 'inc'

                param_widget = ui.create_spinbox(
                    group_widget, key, title, min_, max_, value_type, default)


try:
    ui.write_log('Формирую интерфейс')
    fill_window()
    ui.write_log('Формирую интерфейс... OK')
except Exception as e:
    ui.write_log('Ошибка:')
    ui.write_log(traceback.format_exc())


ui.win.mainloop()
