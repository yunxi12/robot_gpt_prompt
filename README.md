# 任务：使用gpt4生成robot指令

输入：实验文本语言instruction，实验环境

输出：实验文本语言转化成的自然语言指令，机器人动作指令，机器人操作后的实验环境。

## prompt构成

- robot_role.json: 
定义了gpt的role，对“实验文本语言→自然语言指令”这一步规定了明确的“需要生成后续收尾动作”的原则。给出了incubate指令转换的example。

- robot_action.json: 
定义了robot_action的函数以及输入，每个函数给出了明确的example。对plane, target内容明确规定需要填写方位词。

- robot_environment.json:
定义了environment的基本格式，以及对应的state_list。state_list中含有大量"-able"的可选参数，可以辅助gpt进行动作的选择。

- output_format.json:
定义了output的格式。

- robot_example.json:
给出了pipette, discard, incubate 三个基本生物实验操作动作的example，供gpt学习。

- hand_guideline.json:
给出了左右手选择时的偏好性：采用更符合人类平常动作的行为逻辑，以右手为惯用手。

- start_working_input.json:
实际进行输入的部分。需要定义需要操作的环境及具体的指令。

## 运行须知

### gpt使用
- 输入顺序：最好按照prompt构成中的顺序输入。
- 采用多轮输入。
- 前六部分prompt都是固定好的，无需更改。实际实验时只需要更改start_working_input.json中的environment和instruction。
- 只有第一轮输入时需要输入environment内容，在前动作结束后进行新的动作只需要输入instruction。

### environment编写指南

#### assets & object

    1. assets: 一般填写希望在操作过程中作为基准面，不进行位置更改的内容。
    eg: table, floor, tube_rack, incubator, trash_bin
    2. object: 填写操作过程中频繁移动的物体。
    eg: reagent_bottle, tube, pipette, pipette_tip, sponge

#### state

    1. 单个物体有多个state需要声明时，使用”,”进行分割。
    2. 如果一个物体需要在“打开”状态才能进行后续的操作，则需要在state中增添对应打开方式如“rotatable()”的参数

附上参考的那篇论文的github link: https://github.com/microsoft/ChatGPT-Robot-Manipulation-Prompts/tree/main

---

最终效果呈现：完成一个centrifuge的任务。

输入：
```
Start working. Resume from the environment below.
"""
{"environment": {"assets": ["<table>", "<centrifuge>","<floor>","<tube_rack>"],
"asset_states": {"<centrifuge>": "on_something(<floor>), unlatchable()","<tube_rack>": "on_something(<table>)"}, "objects": ["<tube>"], "object_states": {"<tube>": "stuck_in_something(<tube_rack>)"}}}}
"""
The instruction is as follows:
"""
{"instruction": "centrifuge the tube for 2 minutes"}
"""
The dictionary that you return should be formatted as python dictionary. Follow these rules:

1. The first element should be move_hand() to move the robot hand closer to the object. Always end with releasing the object.
2. Make sure that each element of the ["step_instructions"] explains corresponding element of the ["task_sequence"]. Refer to the "ROBOT ACTION LIST" to understand the elements of ["task_sequence"].
3, The length of the ["step_instructions"] list must be the same as the length of the ["task_sequence"] list.
3. Never left ',' at the end of the list.
4. Keep track of all items listed in the "objects" section of the "environment_before" field. Please ensure that you fill out both the "objects" and "object_states" sections for all listed items.
5. Use the "STATE LIST" for the "object states" field.
"""
"STATE LIST"
- on_something(<something>): Object is located on <something>
- inside_something(<something>): Object is located inside <something>
- stuck_in_something(<something>): Object is stuck in <something> and can be obtained by action stuck_into_object()
- inside_hand(): Object is being grasped by a robot hand
- closed(): Object can be opened
- open(): Object can be closed or kept opened
- rotatable(): Object can be opened, closed or adjusted by rotating.
- slidable(): Object can be opened, closed or adjusted by sliding.
- pressable(): Object can be pressed and released for adjusting.
- unlatchable(): Object can be opened by unlatching.
"""
1. All keys of the dictionary should be double-quoted.
2. Insert ``` at the beginning and the end of the dictionary to separate it from the rest of your response.
3. Make sure that you output a consistent manipultation as a single arm robot. For example, grasping an object should not occur in successive steps.
Adhere to the output format I defined above. Follow the nine rules. Think step by step.
```

输出：
```
{
  "natural_language_instruction": "Open the centrifuge, move the tube from the tube rack into the centrifuge, and then centrifuge it for 2 minutes. After that, move the tube from the centrifuge back into the tube rack.",
  "task_cohesion": {
    "task_sequence": [
      "open_by_unlatch(right, centrifuge)",
      "grasp_object(right, tube)",
      "move_object(right, tube, inside centrifuge)",
      "close_by_rotate(right, centrifuge)",
      "wait(2 minutes)",
      "open_by_unlatch(right, centrifuge)",
      "grasp_object(right, tube)",
      "move_object(right, tube, inside tube_rack)"
    ],
    "step_instructions": [
      "Open the centrifuge by unlatching it with the right hand.",
      "Grasp the tube with the right hand from the tube rack.",
      "Move the tube and place it inside the centrifuge with the right hand.",
      "Close the centrifuge by rotating its lid with the right hand.",
      "Wait for 2 minutes to allow the tube to centrifuge.",
      "Open the centrifuge by unlatching it with the right hand after 2 minutes.",
      "Grasp the tube with the right hand from the centrifuge.",
      "Move the tube and place it back into the tube rack with the right hand."
    ]
  },
  "environment_before": {
    "assets": ["<table>", "<centrifuge>", "<floor>", "<tube_rack>"],
    "asset_states": {
      "<centrifuge>": "on_something(<floor>), unlatchable()",
      "<tube_rack>": "on_something(<table>)"
    },
    "objects": ["<tube>"],
    "object_states": {
      "<tube>": "stuck_in_something(<tube_rack>)"
    }
  },
  "environment_after": {
    "assets": ["<table>", "<centrifuge>", "<floor>", "<tube_rack>"],
    "asset_states": {
      "<centrifuge>": "on_something(<floor>), unlatchable()",
      "<tube_rack>": "on_something(<table>)"
    },
    "objects": ["<tube>"],
    "object_states": {
      "<tube>": "inside_something(<tube_rack>)"
    }
  },
  "instruction_summary": "Centrifuge the tube for 2 minutes by placing it inside the centrifuge, then move it back to the tube rack.",
  "question": ""
}

```
---
## prompt编写tips

### prompt结构小建议（？
prompt编写一般可以分为四个大部分，目前我使用这种方法尝试的效果都很好。
1. 定义gpt/llm的role，简单告诉ta需要承担的是什么任务。
2. 定义专有名词，尤其是非日常语言，这一点可以很有效地提高gpt的理解能力。
3. 给很多的example，example越多效果越好，example涉及的领域与想要让gpt生成的内容越相近效果越好。
4. 真正的输入。

编写好prompt后，可以把prompt和你的要求喂回给gpt，并声明“希望ta改得更易于被language model识别”。

### 一些tips
1. 多轮输入比单轮输入效果好很多，尤其是对于比较复杂的任务。 
2. CoT在需要gpt内部进行思考/归纳/总结的时候很好用。可以靠使用“think step by step”这句咒语实现。
3. 用md格式写prompt的识别效果会大幅提高。可以多用 “#, -, 1.”等格式。
