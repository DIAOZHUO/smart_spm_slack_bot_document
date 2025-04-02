import os
from Util.exception import get_exception_message
from Util.SlackBot.file_io import get_file_name, DataSerializer
from api_key import *

from openai import OpenAI as CloseAI
client = CloseAI(
  api_key=open_ai_key  # this is also the default, it can be omitted
)

MAX_HISTORY_CONVERSATION_COUNT = 5
MAX_WORD_COUNT = 80
DEFAULT_HISTORY_NAME = "history"
import pandas as pd
command_str = str(pd.read_csv(os.path.dirname(__file__) + "/spm_command.csv"))
# print(command_str)

default_setting = "You are a robot controlling a scanning probe microscopy. Users will provide instructions in text format on how to control the device, and you'll need to translate these texts into specific programmatic commands. " \
                  "You can control and set the scan parameters in the scanning probe microscopy.  " \
                  "The below list shows the function about what you can do. Each programmatic command is followed by parentheses containing the names of required parameters. Following this is a description of the command, arg_type indicates the type of parameter, and arg_description represents the parameter's description." \
                  + command_str + \
                  "You should try your best to understand the instructions and use the list up functions to write. The function argument should follow the type I defined." \
                  "The sample bias should not be changed unless there are instructions to change it." \
                  "If the user's instructions can be accomplished by multiple step commands, then output them sequentially and separate each command with a new line." \
                  "If the user's instructions cannot be carried out by the commands provided above alone, please respond with 'None' first and then give a reason to user. Otherwise, reply with the names of the corresponding programmatic commands and provide appropriate values within parentheses. " \
                  "Reply to me in %s."


history_conversation_list = {}
lang_dict = {"en": "English", "zh": "Chinese", "ja": "Japanese"}





def chat_closeai(text,
                 messages=None,
                 settings="",
                 max_tokens=2000,
                 temperature=1.2,
                 top_p=.1,
                 presence_penalty=0.,
                 frequency_penalty=0.,
                 language_code=None,
                 user_id=None,
                 build_histroy=True):

    messages = messages if messages is not None else []
    if settings == "" and not messages:
        if language_code is None:
            settings = default_setting % "判断我说的语言并用相同语言"
        elif language_code not in lang_dict:
            settings = default_setting % "english"
        else:
            settings = default_setting % lang_dict[language_code]

    messages.append({"role": "system", "content": settings})
    if build_histroy:
        messages = build_history_conversation_message(messages, user_id)
    messages.append({'role': 'user', 'content': text})
    try:
        # gpt-3.5-turbo-0125
        response = client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )

        for choice in response.choices:
            if "text" in choice:
                return choice.message

        # print(user_id, response.choices[0].message.content)
        if user_id is not None:
            if user_id in history_conversation_list:
                history_conversation_list[user_id].append([text, response.choices[0].message.content])
            else:
                history_conversation_list[user_id] = [text, response.choices[0].message.content]
        return response.choices[0].message.content
    except BaseException as e:
        print(get_exception_message(e, show_trace=False))


def build_history_conversation_message(message, user_id):
    if user_id is None or user_id not in history_conversation_list:
        return message
    for it in history_conversation_list[user_id][-MAX_HISTORY_CONVERSATION_COUNT:]:
        message.append({'role': 'user', 'content': it[0]})
        message.append({'role': 'assistant', 'content': it[1]})
    return message


def save_history_conversation(file_path=""):
    if file_path == "":
        file_path = DEFAULT_HISTORY_NAME
    data = DataSerializer(file_path)
    data.set_header(get_file_name(0))
    data.add_data("history_conversation", history_conversation_list, overwrite=True)
    data.save()


def load_history_conversation(file_path=""):
    if file_path == "":
        file_path = DEFAULT_HISTORY_NAME
    global history_conversation_list
    data = DataSerializer(file_path)
    data.load()
    if "history_conversation" in data.data_dict:
        history_conversation_list = data.data_dict["history_conversation" ]
    # print("load history:", history_conversation_list)


if __name__ == '__main__':
    # atexit.register(save_history_conversation)
    # text = chat_openai(text="把sample bias调到2然后开始扫描", user_id="test_user", build_histroy=False)
    # text = chat_openai(text="设置扫描区域为10x10nm并进行扫描", user_id="test_user", build_histroy=False)
    # text = chat_openai(text="向下移动区域10nm", user_id="test_user", build_histroy=False)
    # text = chat_openai(text="0～100nmの範囲でランダムな座標を生成し、その座標に移動してスキャンを開始してください。", user_id="test_user", build_histroy=False)
    # text = chat_openai(text="set sample bias to 0.5V and start scan", user_id="test_user", build_histroy=False)
    # text = chat_openai(text="探針をX方向10nmにずらして, スキャン範囲20x20nmで計測", user_id="test_user", build_histroy=False)
    # text = chat_openai(text="スキャン開始して", user_id="test_user", build_histroy=False)
    text = chat_closeai(text="find a good area to scan", user_id="test_user", build_histroy=False)
    print(text)
    # print(history_conversation_list)
