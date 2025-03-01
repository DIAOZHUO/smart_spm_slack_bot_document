from __future__ import annotations


from Util.SlackBot.chat_gpt_bot_spm import chat_openai
from typing import Tuple, List

from Framework.types.RemoteDataType import RemoteDataType
from Framework.LabviewRemoteManager import LabviewRemoteManager
from Framework.ScanEventManager import ScanEventManager


data_tree_list = list(LabviewRemoteManager.get_remote_command_tree()["data_tree"].keys())
# data_tree_list = []
# print(data_tree_list)
def text2command(text: str, language_code: str=None) -> Tuple[str, str | List[Tuple[RemoteDataType, str]]]:
    response = chat_openai(text, language_code=language_code)
    # print(response)
    # print("chatgpt respoinse", response)
    lines = response.split("\n")
    li = []
    for it in lines:
        if it.startswith("None"):
            return "None", response[4:]
        else:
            t = it.split("(")
            if len(t) == 2:
                cmd = t[0]
                arg = t[1].split(")")[0]

                if cmd in RemoteDataType.__members__:
                    remote_type = RemoteDataType[cmd]
                    if remote_type == RemoteDataType.ScanEnabled:
                        is_scanning = ScanEventManager.instance.is_scanning


                        if arg == "true":
                            arg = "True"
                            if is_scanning:
                                return "None", "scan has already started."

                        elif arg == "false":
                            arg = "False"
                            if not is_scanning:
                                return "None", "scan has not started."

                    elif remote_type == RemoteDataType.StageOffset_X_Tube_ADD or \
                            remote_type == RemoteDataType.StageOffset_X_Tube or \
                            remote_type == RemoteDataType.StageOffset_Y_Tube_ADD or \
                            remote_type == RemoteDataType.StageOffset_Y_Tube:
                        arg = float(arg) / 37.5
                        if abs(arg) > 10:
                            return "None", str(arg) + " cannot larger than 10V."

                    li.append((remote_type.name, str(arg)))
                elif cmd in data_tree_list:
                    if cmd in ["Aux1MaxVoltage", "Aux2MaxVoltage", "Aux1MinVoltage", "Aux2MinVoltage"]:
                        arg = float(arg) / 37.5
                        if abs(arg) > 10:
                            return "None", str(arg) + " cannot larger than 10V."

                    li.append((cmd, str(arg)))
                else:
                    return "None", cmd + " is not a correct command."
            else:
                continue
    return "OK", li




if __name__ == '__main__':
    # print(text2command("下に１０nm移動してスキャン始めて"))
    print(text2command("初音ミクの画像をください"))