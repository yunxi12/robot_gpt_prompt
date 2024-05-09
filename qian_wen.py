import json
import os
import re
from config import *
from input import text
from dashscope.api_entities.dashscope_response import Role


class QianWen:
    def __init__(self, prompt_load_file):
        self.environment = None
        self.json_dict = None
        self.api_key = dashscope.api_key
        self.model = 'qwen-turbo'
        self.messages = []
        self.max_token_length = 6000  # 根据模型来定
        self.last_response = None
        self.query = ''
        self.instruction = ''
        fp_system = os.path.join(dir_system, 'system.txt')

        with open(fp_system, 'r') as f:
            data = f.read()
        self.system_message = {"role": Role.SYSTEM, "content": data}

        # 加载提示文件
        for prompt_name in prompt_load_file:
            fp_prompt = os.path.join(dir_prompt, prompt_name)
            with open(fp_prompt, 'r') as f:
                data = f.read()
            data_split = re.split(r'\[user]\n|\[assistant]\n', data)
            data_split = [item for item in data_split if len(item) != 0]
            assert len(data_split) % 2 == 0
            for i, item in enumerate(data_split):
                # self.messages.append({"role": "user", "content": item})
                if i % 2 == 0:
                    self.messages.append({"role": Role.USER, "content": item})
                else:
                    self.messages.append({"role": Role.ASSISTANT, "content": item})
        fp_query = os.path.join(dir_query, 'query.txt')
        with open(fp_query, 'r') as f:
            self.query = f.read()

    def create_prompt(self):
        # 初始化prompt
        prompt = [self.system_message]
        for message in self.messages:
            prompt.append({"role": message['role'], "content": message['content']})
        # 计算prompt的token长度
        response = dashscope.Tokenization.call(model=self.model, messages=self.messages)
        length = response['usage']['input_tokens']
        print("prompt_length: %s" % response['usage']['input_tokens'])
        if length > self.max_token_length:
            print("prompt too long. truncated.")
            # truncate the prompt by removing the oldest two messages
            self.messages = self.messages[2:]
            prompt = self.create_prompt()
        return prompt

    def generate(self, message, environment, is_user_feedback=False):
        if is_user_feedback:
            self.messages.append({'role': Role.USER, 'content': message + "\n" + self.instruction})
        else:
            text_base = self.query
            if text_base.find('[ENVIRONMENT]') != -1:
                text_base = text_base.replace('[ENVIRONMENT]', json.dumps(environment))
            if text_base.find('[INSTRUCTION]') != -1:
                text_base = text_base.replace('[INSTRUCTION]', message)
                self.instruction = text_base
            self.messages.append({"role": Role.USER, "content": text_base})
        response = dashscope.Generation.call(model=self.model, messages=self.create_prompt(), result_format='message')
        self.last_response = response.output.choices[0]['message']['content']
        self.last_response = self.extract_json_part(self.last_response)
        self.last_response = self.last_response.replace("'", "\"")
        print(self.last_response)
        with open('qianWen_last_response.txt', 'w') as f:
            f.write(self.last_response)

        self.json_dict = json.loads(self.last_response, strict=False)
        # 上一次输出的environment_after，变成下一次的environment_before
        # self.environment = self.json_dict["task_cohesion"]["environment_after"]
        self.environment = self.json_dict["environment_after"]

        print(self.environment)

        if len(self.messages) > 0 and self.last_response is not None:
            self.messages.append({"role": Role.ASSISTANT, "content": self.last_response})
        return self.json_dict

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
    scenario_name = "shelf"
    environment, instructions = text(scenario_name)
    aimodel = QianWen(prompt_load_file=prompt_load_order)

    if not os.path.exists('./qwen_out/' + scenario_name):
        os.makedirs('./qwen_out/' + scenario_name)

    for i, instruction in enumerate(instructions):
        aimodel.generate(instruction, environment, is_user_feedback=False)

        while True:
            user_feedback = input('user feedback (return empty if satisfied): ')
            if user_feedback == 'q':
                # aimodel.dump_json(f'./out/{scenario_name}/{i}')
                exit()
            if user_feedback != '':
                aimodel.generate(user_feedback, environment, is_user_feedback=True)
            else:
                # update the current environment
                environment = aimodel.environment
                break
        aimodel.dump_json(f'./qwen_out/{scenario_name}/{i}')
