import json
import openai
import os
import re
from config import *
from input import text


class ChatGPT:
    def __init__(self, credentials, prompt_load_order):

        # 使用openAI的api  版本(0.28.1)
        openai.organization = credentials["openai"]["YOUR_ORG_ID"]
        openai.api_key = credentials["openai"]["OPENAI_API_KEY"]
        self.credentials = credentials
        self.messages = []
        self.max_token_length = 8000
        self.max_completion_length = 1000
        self.last_response = None
        self.query = ''
        self.instruction = ''
        self.environment = None
        self.json_dict = None
        # load prompt file
        fp_system = os.path.join(dir_system, 'system.txt')
        with open(fp_system) as f:
            data = f.read()
        self.system_message = {"role": "system", "content": data}

        for prompt_name in prompt_load_order:
            fp_prompt = os.path.join(dir_prompt, prompt_name)
            with open(fp_prompt) as f:
                data = f.read()
            # data_spilit = re.split(r'\[user\]\n|\[assistant\]\n', data)
            data_spilit = re.split(r'\[user]\n|\[assistant]\n', data)
            data_spilit = [item for item in data_spilit if len(item) != 0]
            # it starts with user and ends with system
            # 一定要保证prompt中的user、assistant一一对应，否则报错
            assert len(data_spilit) % 2 == 0
            for i, item in enumerate(data_spilit):
                if i % 2 == 0:
                    self.messages.append({"sender": "user", "text": item})
                else:
                    self.messages.append({"sender": "assistant", "text": item})
        fp_query = os.path.join(dir_query, 'query.txt')
        with open(fp_query) as f:
            self.query = f.read()

    # See
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/chatgpt#chatml
    def create_prompt(self):
        prompt = [self.system_message]
        for message in self.messages:
            prompt.append(
                {"role": message['sender'], "content": message['text']})
        prompt_content = ""
        for message in prompt:
            prompt_content += message["content"]
        print('prompt length: ' + str(len(enc.encode(prompt_content))))
        if len(enc.encode(prompt_content)) > self.max_token_length - \
                self.max_completion_length:
            print('prompt too long. truncated.')
            # truncate the prompt by removing the oldest two messages
            self.messages = self.messages[2:]
            prompt = self.create_prompt()
        return prompt

    def extract_json_part(self, text):
        # because the json part is in the middle of the text, we need to extract it.
        # json part is between ``` and ```.
        # skip if there is no json part
        if text.find('```') == -1:
            return text
        text_json = text[text.find(
            '```') + 3:text.find('```', text.find('```') + 3)]
        return text_json

    def generate(self, message, environment, is_user_feedback=False):
        if is_user_feedback:
            self.messages.append({'sender': 'user',
                                  'text': message + "\n" + self.instruction})
        else:
            text_base = self.query
            if text_base.find('[ENVIRONMENT]') != -1:
                text_base = text_base.replace(
                    '[ENVIRONMENT]', json.dumps(environment))
            if text_base.find('[INSTRUCTION]') != -1:
                text_base = text_base.replace('[INSTRUCTION]', message)
                self.instruction = text_base
            self.messages.append({'sender': 'user', 'text': text_base})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            # "gpt-4" is available, too. Check the available models in https://platform.openai.com/docs/models/
            messages=self.create_prompt(),
            temperature=0.1,
            max_tokens=self.max_completion_length,
            top_p=0.5,
            frequency_penalty=0.0,
            presence_penalty=0.0)
        self.last_response = response['choices'][0].message.content  # 返回信息
        print(self.last_response)
        self.last_response = self.extract_json_part(self.last_response)
        self.last_response = self.last_response.replace("'", "\"")
        # dump to a text file
        with open('last_response.txt', 'w') as f:
            f.write(self.last_response)
        try:
            self.json_dict = json.loads(self.last_response, strict=False)
            self.environment = self.json_dict["environment_after"]
        except BaseException:
            self.json_dict = None
            import pdb
            pdb.set_trace()

        if len(self.messages) > 0 and self.last_response is not None:
            self.messages.append(
                {"sender": "assistant", "text": self.last_response})

        return self.json_dict

    def dump_json(self, dump_name=None):
        if dump_name is not None:
            # dump the dictionary to json file dump 1, 2, ...
            fp = os.path.join(dump_name + '.json')
            with open(fp, 'w') as f:
                json.dump(self.json_dict, f, indent=4)


if __name__ == "__main__":

    scenario_name = "shelf"
    environment, instructions = text(scenario_name)
    aimodel = ChatGPT(credentials, prompt_load_order=prompt_load_order)

    if not os.path.exists('./out/' + scenario_name):
        os.makedirs('./out/' + scenario_name)
    for i, instruction in enumerate(instructions):
        print(json.dumps(environment))
        text = aimodel.generate(instruction, environment, is_user_feedback=False)
        while True:
            user_feedback = input(
                'user feedback (return empty if satisfied): ')
            if user_feedback == 'q':
                exit()
            if user_feedback != '':
                text = aimodel.generate(
                    user_feedback, environment, is_user_feedback=True)
            else:
                # update the current environment
                environment = aimodel.environment
                break
        aimodel.dump_json(f'./out/{scenario_name}/{i}')
