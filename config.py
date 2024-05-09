import dashscope
import tiktoken

# 文件前缀
dir_system = 'stepGeneration/system'
dir_prompt = 'stepGeneration/prompt'
dir_query = 'stepGeneration/query'
# openAI编码
enc = tiktoken.get_encoding("cl100k_base")
# prompt文件

prompt_load_order = ['robot_role.txt',
                     'robot_action.txt',
                     'robot_environment.txt',
                     'output_format.txt',
                     'robot_example.txt',
                     'hand_guideline.txt'
                     ]
'''
prompt_load_order = ['robot_role.txt',
                     'robot_action.txt',
                     'robot_environment.txt',
                     'output_format.txt',
                     'robot_example.txt'
                     ]
prompt_load_order = ['robot_role.txt',
                     'robot_action.txt',
                     'output_format.txt',
                     'robot_example.txt'
                     ]
'''
# 'hand_guideline.txt'
# qwen的api秘钥
dashscope.api_key = "your-key"
# 公司内部的大模型的API接口
url = "url"
# openAI的api秘钥
credentials = {
    "openai":
        {
            "YOUR_ORG_ID": "your-organization-id",
            "OPENAI_API_KEY": "your-openai-api-key"
        }
}
