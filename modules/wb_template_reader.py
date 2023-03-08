import json
import re


class WbTemplateReader:

    wb_template = ''

    def read_template(self, json_file):
        self.wb_template = ''
        with open(json_file, 'r') as j:
            self.wb_template = json.load(j)
            return 0

    def get_device_name(self):
        return self.wb_template['device']['name']

    def get_device_id(self):
        return self.wb_template['device']['id']

    def get_parameters(self):
        return self.wb_template['device']['parameters']

    def get_groups(self):
        return self.wb_template['device']['groups']

    def get_translate(self, string, language='ru'):
        device = self.wb_template['device']

        if 'translations' in device:
            if language in device['translations']:
                if string in device['translations'][language]:
                    return device['translations'][language][string]
                else:
                    return string
            else:
                return string

    def get_parameter_type(self, item):
        if 'enum' in item:
            return 'enum'

        return 'value'

    def get_group(self, id):
        groups = self.get_groups()
        i = 0
        res = None
        while i < len(groups):
            if (groups[i].get('id') == id):
                res = groups[i]
                break
            i += 1
        return res

    def get_parameter(self, id):
        parameters = self.get_parameters()
        res = None
        for key in parameters:
            if (key == id):
                res = parameters[key]
                break
        return res

    def get_enum_dic(self, item):
        enum = item['enum']
        enum_titles = item['enum_titles']

        for i in range(len(enum_titles)):
            enum_titles[i] = self.get_translate(enum_titles[i])

        dic = {'enum': enum, 'enum_titles': enum_titles}
        return dic

    def calc_condition(self, condition, values):
        condition = condition.replace('&&', 'and')
        condition = condition.replace('||', 'or')
        try:
            return eval(condition, {}, values)
        except Exception as e:
            print('Ошибка в выражении: {}\n {}'.format(
                condition, traceback.format_exc()))
            return False
