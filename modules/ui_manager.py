from tkinter import *
import tkinter as tk
from tkinter import ttk
import tkinter.scrolledtext as scrolltext
import serial.tools.list_ports

from tkinter import filedialog
from datetime import datetime
from . import ui_scroll_frame


class UiManager:
    widgets = {}
    win = None
    log = None
    notebook = None

    btn_read_params = None
    btn_write_params = None
    btn_open_template = None

    def __init__(self):
        self.win = Tk()
        self.win.title('Python Modbus Device Editor')
        self.win.geometry('1366x750')

        style = ttk.Style(self.win)
        style.theme_use("clam")

# Верхняя часть окна с настройками подключения
        top_frame = self.create_frame(
            parent=self.win,
            id='nodel_top_frame',
            side=TOP,
            fill=X,
            expand=False,
            height=50
        )

        mb_settings = self.create_group(
            parent=top_frame,
            id='nodel_mb_settings',
            title='Настройки подключения',
            side=LEFT,
            fill=BOTH,
            expand=False
        )

        mb_port = self.create_combobox(
            parent=mb_settings,
            id='nodel_mb_port',
            title='Порт',
            dic=self.get_ports(),
            default=0,
            width=40,
            side=LEFT,
            anchor=SW
        )

        mb_baudrate = self.create_combobox(
            parent=mb_settings,
            id='nodel_mb_baudrate',
            title='Порт',
            dic=self.gen_baudrate_dic(),
            default=9600,
            width=8,
            side=LEFT,
            anchor=SW
        )

        mb_bytesize = self.create_combobox(
            parent=mb_settings,
            id='nodel_mb_bytesize',
            title='Биты данных',
            dic=self.gen_bytesize_dic(),
            default=8,
            width=8,
            side=LEFT,
            anchor=SW
        )

        mb_parity = self.create_combobox(
            parent=mb_settings,
            id='nodel_mb_parity',
            title='Четность',
            dic=self.gen_parity_dic(),
            default='N',
            width=8,
            side=LEFT,
            anchor=SW
        )

        mb_stopbits = self.create_combobox(
            parent=mb_settings,
            id='nodel_mb_stopbits',
            title='Стоп биты',
            dic=self.gen_stopbits_dic(),
            default=2,
            width=8,
            side=LEFT,
            anchor=SW
        )

        mb_actions = self.create_group(
            parent=top_frame,
            id='nodel_mb_actions',
            title='Чтение/запись параметров',
            side=LEFT,
            fill=BOTH,
            expand=True
        )

        self.mb_slave_id = self.create_spinbox(
            parent=mb_actions,
            id='nodel_mb_slave_id',
            title='Адрес',
            min_=0,
            max_=247,
            value_type='int',
            default=1,
            width=4,
            description=False,
            side=LEFT
        )

        self.btn_open_template = self.create_button(
            parent=mb_actions,
            id='nodel_btn_open_template',
            title='Открыть шаблон',
            side=LEFT,
            anchor=SW
        )

        self.btn_read_params = self.create_button(
            parent=mb_actions,
            id='nodel_btn_read_params',
            title='Читать параметры',
            side=LEFT,
            anchor=SW
        )

        self.btn_write_params = self.create_button(
            parent=mb_actions,
            id='nodel_btn_write_params',
            title='Записать параметры',
            side=LEFT,
            anchor=SW
        )

# Нижняя часть окна
        bottom_frame = self.create_frame(
            parent=self.win,
            id='nodel_bottom_frame',
            side=TOP,
            fill=BOTH,
            expand=True
        )

# Левый фрейм
        left_frame = self.create_group(
            parent=bottom_frame,
            id='nodel_left_frame',
            title='Настройки устройства',
            side=LEFT,
            fill=BOTH,
            expand=True
        )

        self.notebook = self.create_notebook(
            parent=left_frame,
            id='nodel_params_notebook',
            side=TOP,
            fill=BOTH,
            expand=True
        )

# Правый фрейм
        right_frame = self.create_group(
            parent=bottom_frame,
            id='nodel_right_frame',
            title='Журнал',
            side=LEFT,
            fill=Y
        )

        self.log = self.create_scrolled_text(
            parent=right_frame,
            id='nodel_log',
            width=50,
            side=LEFT,
            fill=BOTH,
            expand=True,
        )
        self.log.configure(state='disabled')

    def write_log(self, text):
        self.log.configure(state='normal')
        res = self.log.insert(END, '{} | {}\n'.format(
            f"{datetime.now():%H:%M:%S}", text))
        self.log.configure(state='disabled')
        return 0

    def create_frame(self, parent, id, side, fill, expand, **args):
        frame = ttk.Frame(parent, **args)
        frame.pack(padx=5, pady=5, side=side,
                   fill=fill, expand=expand)
        frame.type = 'frame'
        self.widgets[id] = frame
        return frame

    def create_viewport(self, parent, id):
        scrool_frame = ui_scroll_frame.ScrollFrame(parent)
        viewport = scrool_frame.viewPort
        scrool_frame.pack(side=LEFT, fill=BOTH, expand=True)
        viewport.type = 'viewport'
        self.widgets[id] = viewport
        return viewport

    def create_row(self, parent, id):
        row_frame = ttk.Frame(parent)
        row_frame.type = 'row'
        row_frame.pack(padx=5, pady=5, side=TOP,
                       fill='x', expand='no')
        self.widgets[id] = row_frame
        return row_frame

    def create_notebook(self, parent, id, **opts):
        notebook = ttk.Notebook(parent)
        notebook.pack(**opts)
        notebook.type = 'notebook'
        self.widgets[id] = notebook
        return notebook

    def create_tab(self, id, title):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text=title)
        tab.type = 'nb_tab'
        self.widgets[id+'nb_tab'] = tab

        viewport = self.create_viewport(tab, id)
        viewport.curr_row = 0
        viewport.curr_col = 0
        viewport.curr_frame = self.create_row(viewport, id+'_row')
        viewport.type = 'tab'
        viewport.child_wrap = self.create_group(
            viewport.curr_frame, id+'_wrap', 'Базовые', side=LEFT, anchor=NW)
        self.widgets[id] = viewport
        return viewport

    def create_scrolled_text(self, parent, id, width, **opts):
        scrolled_text = scrolltext.ScrolledText(
            parent, width=width, wrap="word")
        scrolled_text.pack(**opts)
        scrolled_text.type = 'scrolled_text'
        self.widgets[id] = scrolled_text
        return scrolled_text

    def create_group(self, parent, id, title, relief=GROOVE, **opts):
        group = ttk.LabelFrame(parent, text=title, relief=relief)
        group.type = 'group'
        group.pack(padx=5, pady=5, **opts)
        self.widgets[id] = group
        return group

    def create_label(self, parent, id, title, **opts):
        label = ttk.Label(parent, text=title)
        label.type = 'label'
        label.pack(padx=5, pady=5, **opts)
        self.widgets[id] = label
        return label

    def create_button(self, parent, id, title, command=None, **opts):
        button = ttk.Button(parent, text=title, command=command)
        button.type = 'button'
        button.pack(padx=5, pady=5, **opts)
        self.widgets[id] = button
        return button

    def create_combobox(self, parent, id, title, dic, default, width, **opts):
        enums = dic['enum_titles']
        group = self.create_group(
            parent, id+'title', title, relief=FLAT, **opts)
        combobox = ttk.Combobox(group, values=enums,
                                state="readonly", width=width)
        combobox.type = 'combobox'
        combobox.dic = dic
        combobox.pack(padx=5, pady=0, side=TOP, anchor=NW)
        self.widgets[id] = combobox

        if (default in dic['enum']):
            index = dic['enum'].index(default)
        else:
            index = 0
        combobox.current(index)
        return combobox

    def get_combobox_format(self, value_type):
        if (value_type == 'double'):
            fmt = '%.2f'
        else:
            fmt = '%.0f'
        return fmt

    def create_spinbox(self, parent, id, title, min_, max_, value_type, default, width, description, **opts):
        if (min_ == None):
            min_ = 0.0
        if (max_ == None):
            max_ = 100.0
        fmt = self.get_combobox_format(value_type)

        group = self.create_group(
            parent, id+'title', title, relief=FLAT, **opts)
        spinbox = ttk.Spinbox(group, from_=min_, to=max_,
                              format=fmt, width=width)

        if (default == None):
            default = 0
        spinbox.set(default)

        spinbox.type = 'spinbox'
        spinbox.pack(padx=5, pady=0, side=TOP, anchor=NW)
        self.widgets[id] = spinbox

        if (description):
            self.create_label(group, id+'_decsription',
                              'min:{} max:{} default: {}'.format(min_, max_, default))
        return spinbox

    def is_exists_widget(self, id):
        return (widgets.get(id) != None)

    def get_values(self):
        widgets = self.widgets
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
        widget = self.widgets[widget_id]
        widget.pack_forget()

    def widget_show(self, widget_id):
        widget = self.widgets[widget_id]
        widget.pack(opts)

    def open_file(self):
        file_patch = filedialog.askopenfilename()
        return file_patch

    def remove_widgets_item(self, key):
        print('Удаляю id:{} type:{}'.format(key, self.widgets[key].type))
        self.widgets[key].destroy()
        del self.widgets[key]

    def delete_widgets(self):
        widgets = dict(self.widgets)
        for key in widgets:
            if ('nodel_' not in key):
                self.remove_widgets_item(key)

    def get_ports(self):
        enum = []
        enum_titles = []
        ports = list(serial.tools.list_ports.comports())
        for port, desc, hwid in sorted(ports):
            enum.append(port)
            enum_titles.append("{}: {}".format(port, desc))

        return {'enum': enum, 'enum_titles': enum_titles}

    def gen_baudrate_dic(self):
        enum = [9600, 19200, 38400, 57600, 115200]
        enum_titles = [
            '9600',
            '19200',
            '38400',
            '57600',
            '115200'
        ]
        return {'enum': enum, 'enum_titles': enum_titles}

    def gen_bytesize_dic(self):
        enum = [5, 6, 7, 8]
        enum_titles = [
            '5',
            '6',
            '7',
            '8'
        ]
        return {'enum': enum, 'enum_titles': enum_titles}

    def gen_parity_dic(self):
        enum = ['N', 'E', 'O']
        enum_titles = [
            'N',
            'E',
            'O'
        ]
        return {'enum': enum, 'enum_titles': enum_titles}

    def gen_stopbits_dic(self):
        enum = [1, 2]
        enum_titles = [
            '1',
            '2'
        ]
        return {'enum': enum, 'enum_titles': enum_titles}
