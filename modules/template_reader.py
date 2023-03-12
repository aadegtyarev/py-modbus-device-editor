import json


class TemplateReader:
    template = None

    def read_template(self, file_patch):
        with open(file_patch, "r") as j:
            self.template = json.load(j)

    def get_device_name(self):
        return self.template.get("device_name")


    def get_groups(self):
        return self.template.get("groups")


    def get_params(self):
        return self.template.get("params")

    def get_params_by_group(self, group_id):
        res = {}
        params = self.get_params()
        for key in params:
            if params[key]["widget"].get("group") == group_id:
                res[key] = params[key]
        return res       

    def get_enum_dic(self, param):
        value_options = param["widget"].get("value_options")
        enum = value_options["enum"]
        enum_titles = value_options["enum_titles"]

        for i in range(len(enum_titles)):
            enum_titles[i] = enum_titles[i]

        dic = {"enum": enum, "enum_titles": enum_titles}
        return dic


    def calc_condition(self, condition, values):
        try:
            return eval(condition, {}, values)
        except Exception as e:
            print(
                "Ошибка в выражении: {}\n {}".format(condition, traceback.format_exc())
            )
            return False
