from tkinter import *
import tkinter as tk
import tkinter.scrolledtext as scrolledtext
from tkinter import ttk
from datetime import datetime
from modules import wb_template_reader
from modules import ui_scroll_frame
import traceback
from modules import ui_manager

json_file = 'templates/config-wb-mr6c.json'
ui_widgets = {}
reader = wb_template_reader.WbTemplateReader()

# ui = ui_manager.UiManager()


def create_frame(parent, id, side, fill, expand):
    fr = ttk.Frame(parent)
    fr.pack(padx=5, pady=5, side=side, fill=fill, expand=expand)
    return fr


# Создаём окно с содержимым
root = Tk()
root.geometry('1366x750')

style = ttk.Style(root)
style.theme_use("clam")

top_frame = ttk.Frame(root, height=50)
top_frame.pack(fill='x', side=TOP)

bottom_frame = create_frame(root, id='buttom_frame',
                            side=TOP, fill=BOTH, expand=True)

left_frame = ttk.LabelFrame(bottom_frame, text='Настройки устройства')
left_frame.pack(padx=5, pady=5, side=LEFT, fill=BOTH, expand=True)

notebook = ttk.Notebook(left_frame)
notebook.pack(fill=BOTH, expand=True)

righ_frame = ttk.LabelFrame(bottom_frame, text='Журнал')
righ_frame.pack(padx=5, pady=5, side=LEFT, fill='y')

log = scrolledtext.ScrolledText(
    righ_frame, width=50, wrap="word")
log.pack(side=LEFT, fill=BOTH, expand=True)


def write_log(text):
    log.configure(state='normal')
    res = log.insert(END, '{} | {}\n'.format(
        f"{datetime.now():%H:%M:%S}", text))
    log.configure(state='disabled')
    return res


write_log('Загружаю шаблон')
reader.read_template(json_file)
write_log('Получаю группы')
groups = reader.get_groups()
write_log('Получаю список параметров')
params = reader.get_parameters()


def create_viewport(parent, id):
    scrool_frame = ui_scroll_frame.ScrollFrame(parent)
    viewport = scrool_frame.viewPort
    scrool_frame.pack(side=LEFT, fill=BOTH, expand=True)
    ui_widgets[id] = scrool_frame
    return viewport


def create_row(parent):
    row_frame = ttk.Frame(parent)
    row_frame.type = 'row'
    row_frame.pack(padx=5, pady=5, side=TOP, fill='x', expand='no')
    return row_frame


def create_group(parent, id, title, relief=GROOVE, side=LEFT, fill=NONE, expand=False):
    group = ttk.LabelFrame(parent, text=title, relief=relief)
    group.type = 'group'
    group.pack(padx=5, pady=5, side=side, anchor=NW)
    ui_widgets[id] = group
    return group


def create_tab(notebook, id, title):
    tab = ttk.Frame(notebook)
    notebook.add(tab, text=title)
    viewport = create_viewport(tab, id)
    viewport.curr_row = 0
    viewport.curr_col = 0
    viewport.curr_frame = create_row(viewport)
    viewport.type = 'tab'
    viewport.child_wrap = create_group(
        viewport.curr_frame, id+'_wrap', 'Базовые')
    ui_widgets[id] = viewport
    return viewport


def create_label(parent, id, title):
    label = ttk.Label(parent, text=title)
    label.type = 'label'
    label.pack(padx=5, pady=5, anchor=NW)
    ui_widgets[id] = label
    return label


def create_combobox(parent, id, title, dic, default):
    enums = dic['enum_titles']
    group = create_group(parent, id+'title', title, FLAT, TOP)
    combobox = ttk.Combobox(group, values=enums, state="readonly", width=40)
    combobox.type = 'combobox'
    combobox.dic = dic
    combobox.pack(padx=5, pady=0, side=TOP, anchor=NW)
    ui_widgets[id] = combobox

    if (default in dic['enum']):
        index = dic['enum'].index(default)
    else:
        index = 0
    combobox.current(index)
    return combobox


def get_combobox_format(value_type):
    if (value_type == 'double'):
        fmt = '%.2f'
    else:
        fmt = '%.0f'
    return fmt


def create_spinbox(parent, id, title, min_, max_, value_type, default):
    if (min_ == None):
        min_ = 0.0
    if (max_ == None):
        max_ = 100.0
    fmt = get_combobox_format(value_type)

    group = create_group(parent, id+'title', title, FLAT, TOP)
    spinbox = ttk.Spinbox(group, from_=min_, to=max_, format=fmt, width=20)

    if (default == None):
        default = 0
    spinbox.set(default)

    spinbox.type = 'spinbox'
    spinbox.pack(padx=5, pady=0, side=TOP, anchor=NW)
    ui_widgets[id] = spinbox

    create_label(group, id+'_decsription',
                 'min:{} max:{} default: {}'.format(min_, max_, default))
    return spinbox


def is_main_group(item):
    return 'group' not in item


def is_exists_widget(id):
    return (ui_widgets.get(id) != None)


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
            group_widget = create_tab(notebook, id_group, title)
            curr_frame = group_widget.curr_frame
        else:
            parent_id = item['group']
            parent = ui_widgets[parent_id]
            if (parent != None):
                # print('[parent_id: {} ] curr_row: {} curr_col: {}'.format(parent_id,
                #                                                           parent.curr_row, parent.curr_col))
                if (parent.type == 'tab'):
                    if (item.get('ui_options') == None):
                        curr_frame = parent.curr_frame
                        if(parent.curr_col < max_col):
                            group_widget = create_group(
                                curr_frame, id_group, title)

                            parent.curr_col += 1
                        else:
                            curr_frame = create_row(parent)
                            parent.curr_frame = curr_frame

                            group_widget = create_group(
                                curr_frame, id_group, title)

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
                param_widget = create_combobox(
                    group_widget, key, title, dic, default)
            else:
                default = item.get('default')
                min_ = item.get('min')
                max_ = item.get('max')
                if('scale' in item):
                    value_type = 'double'
                else:
                    value_type = 'inc'

                param_widget = create_spinbox(
                    group_widget, key, title, min_, max_, value_type, default)


try:
    write_log('Формирую интерфейс')
    fill_window()
    write_log('Формирую интерфейс... OK')
except Exception as e:
    write_log('Ошибка:')
    write_log(traceback.format_exc())


root.mainloop()
