import json
import os
import re
import requests
from config import *


class ApiModel:
    def __init__(self, prompt_load_file, model):
        self.instruction = None
        self.last_response = None
        self.data = None
        self.model = model
        self.messages = []
        self.query = ''
        self.max_token_length = 8000
        fp_system = os.path.join(dir_system, 'system.txt')
        with open(fp_system, 'r') as f:
            self.initial_message = f.read()
        for prompt_name in prompt_load_file:
            fp_prompt = os.path.join(dir_prompt, prompt_name)
            with open(fp_prompt, 'r') as f:
                data = f.read()
            data_split = re.split(r'\[user]\n|\[assistant]\n', data)

            data_split = [item for item in data_split if len(item) != 0]
            # 一个prompt文件只能有一个user和一个assistant,否则出错
            self.messages.append({"ask": data_split[0], "answer": data_split[1]})
        fp_query = os.path.join(dir_query, 'query.txt')
        with open(fp_query, 'r') as f:
            self.query = f.read()

    def create_prompt(self):
        # 初始化prompt
        prompt = [{"ask": self.initial_message, "answer": "understood."}]
        for message in self.messages:
            prompt.append(message)
        # 计算prompt的token长度
        response = []
        length = 10
        print("prompt_length: %s" % length)
        if length > self.max_token_length:
            print("prompt too long. truncated.")
            # truncate the prompt by removing the oldest two messages
            self.messages = self.messages[2:]
            prompt = self.create_prompt()
        return prompt

    def generate(self, message, environment):
        text_base = self.query
        if text_base.find('[ENVIRONMENT]') != -1:
            text_base = text_base.replace('[ENVIRONMENT]', json.dumps(environment))
        if text_base.find('[INSTRUCTION]') != -1:
            text_base = text_base.replace('[INSTRUCTION]', message)
            self.instruction = text_base
        self.data = {
            "model_name": self.model,
            "prompt": text_base,
            "history": self.create_prompt()
        }
        print(self.data)
        post = requests.post(url=url, json=self.data)
        if post.status_code == 200:
            if post.json()["data"]:
                json_data = post.json()  # ["data"]["result"]
                self.last_response = json_data["data"]["result"]
                self.last_response = self.extract_json_part(self.last_response)
                self.last_response = self.last_response.replace("'", "\"")
                print(self.last_response)
                with open('api_last_response.txt', 'w') as f:
                    f.write(self.last_response)
            else:
                print("No response")
        else:
            print('请求失败:', post.status_code)

    def dump_json(self, dump_name=None):
        if dump_name is not None:
            # dump the dictionary to json file dump 1, 2, ...
            fp = os.path.join(dump_name + '.json')
            with open(fp, 'w') as f:
                json.dump(self.json_dict, f, indent=4)

    def extract_json_part(self, text):
        if text.find('```') == -1:
            return text
        text_json = text[text.find('```') + 3:text.find('```', text.find('```') + 3)]
        text_json = text_json[text_json.find('{'):]
        return text_json


if __name__ == '__main__':
    api = ApiModel(prompt_load_file=prompt_load_order, model="qwen-7b")
    # api = ApiModel(prompt_load_file=prompt_load_order, model="gpt-3.5-turbo")
    environment = {
        "assets": [
            "<table>",
            "<window>",
            "<trash_bin>",
            "<floor>"],
        "asset_states": {
            "<table>": "next_to(<window>)",
            "<trash_bin>": "on_something(<floor>)"},
        "objects": ["<sponge>"],
        "object_states": {
            "<sponge>": "on_something(<table>)"}}
    instructions = [
        'Get the sponge from the table and wipe the window with it. After that, put the sponge back on the table,'
        'Throw away the sponge on the table']
    for i, instruction in enumerate(instructions):
        api.generate(instruction, environment)
