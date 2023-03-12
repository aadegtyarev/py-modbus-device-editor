import json
import re
import traceback
from pathlib import Path
import argparse
import os


class WbTemplateReader:
    wb_template = ""

    def read_template(self, json_file):
        self.wb_template = ""
        try:
            with open(json_file, "r") as j:
                self.wb_template = json.load(j)
        except:
            print("Не смог открыть файл {}".format(json_file))

    def get_device_name(self):
        return self.wb_template["device"]["name"]

    def get_title(self):
        return self.wb_template.get("title")

    def get_device_id(self):
        return self.wb_template["device"]["id"]

    def convert_list(self, src_list):
        list_ = list(src_list)
        dic = {}
        for i in range(len(list_)):
            dic[list_[i]["id"]] = list_[i]
        return dic

    def convert_dic(self, src_dic):
        dic = dict(src_dic)
        list_ = []
        for key in dic:
            dic[key]["id"] = key
            list_.append(dic[key])        
        return list_        

    def get_parameters(self):
        params = self.wb_template["device"].get("parameters")
        if type(params) != list:
            params = self.convert_dic(params)
        return params

    def get_setups(self):
        setup = self.wb_template["device"].get("setup")
        return setup

    def get_groups(self):
        groups = self.wb_template["device"].get("groups")
        if type(groups) != list:
            groups = self.convert_dic(groups)
        return groups
    
    def get_translations(self):
        return self.wb_template["device"].get("translations")

    def get_translate(self, string, language="ru"):
        device = self.wb_template["device"]

        if "translations" in device:
            if language in device["translations"]:
                if string in device["translations"][language]:
                    return device["translations"][language][string]
                else:
                    return string
            else:
                return string


class WbConvertTemplate:
    reader = None

    def __init__(self, src_dir, dest_dir):
        paths = sorted(Path(".").glob("{}/*.json".format(src_dir)))
        files_list = list(map(str, paths))

        for i in range(len(files_list)):
            self.convert(files_list[i], dest_dir)

    def convert(self, file_patch, dest_dir):
        template = {}
        self.reader = WbTemplateReader()

        try:
            self.reader.read_template(file_patch)
            template_title = self.reader.get_title()
            device_name = self.reader.get_device_name()
            wb_groups = self.reader.get_groups()
            wb_params = self.reader.get_parameters()
            wb_translate = self.reader.get_translations()
            wb_setup = self.reader.get_setups()

            template = {
                "title": template_title,
                "device":{
                    "name": device_name,
                    "groups": wb_groups,
                    "parameters": wb_params,
                    "translations": wb_translate,
                    "setup": wb_setup                   
                }
            }

            f = open("{}/{}.json".format(dest_dir, device_name.replace("/", "_")), "w")
            json.dump(template, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print("{} {}".format(e, traceback.format_exc()))

parser = argparse.ArgumentParser()
parser.add_argument("--src_dir", nargs="?", default="")
parser.add_argument("--dest_dir", nargs="?", default="")

args = parser.parse_args()

os.makedirs(args.dest_dir, exist_ok=True)

convert = WbConvertTemplate(args.src_dir, args.dest_dir)
