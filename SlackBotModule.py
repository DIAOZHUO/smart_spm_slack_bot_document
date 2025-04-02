import asyncio
import time
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.socket_mode.aiohttp import SocketModeClient
from slack_sdk.socket_mode.response import SocketModeResponse
from slack_sdk.socket_mode.request import SocketModeRequest
from Util.SlackBot.chat_gpt_bot_spm import chat_closeai
from Util.SlackBot.text2command_parser import text2command

from enum import Enum
import numpy as np
import SPMUtil as spmu
# from Framework.LabviewRemoteManager import LabviewRemoteManager
# from Framework.ScanEventManager import ScanEventManager, ScanEventState
# from Framework.ScanFileManager import ScanFileManager
from BaseClass.BaseModule import BaseModule
import matplotlib.pyplot as plt

from lingua import Language, LanguageDetectorBuilder
languages = [Language.ENGLISH, Language.JAPANESE, Language.CHINESE]
lang_detector = LanguageDetectorBuilder.from_languages(*languages).build()


__last_language_code__ = "en"
def detect_language(text):
    global __last_language_code__
    try:
        lang = lang_detector.detect_language_of(text)
        if lang is None:
            __last_language_code__ = "xx"
        elif lang == Language.CHINESE:
            __last_language_code__ = "zh"
        elif lang == Language.ENGLISH:
            __last_language_code__ = "en"
        elif lang == Language.JAPANESE:
            __last_language_code__ = "ja"
    finally:
        return __last_language_code__



class BotCommandType(Enum):
    chat = "chat"
    get = "get"
    set = "set"
    file = "file"
    help = "help"
    misc = "misc"


# channel_name = "hatsunemiku-bot-stm"
import api_key
SLACK_APP_TOKEN = api_key.SLACK_APP_TOKEN
SLACK_BOT_TOKEN = api_key.SLACK_BOT_TOKEN

class SlackBotModule(BaseModule):

    def __init__(self, channel_name, block=False):
        super().__init__()
        # ScanEventManager.instance.ScanUpdateEvent += self._OnScanEventUpdate
        # ScanFileManager.instance.ScanFileAddEvent += self._OnSaveFileAdd

        self.broadcast_scan = False

        self.ignored_user_id_list = []

        self.channel_name = channel_name
        self.socket_client = SocketModeClient(
            app_token=SLACK_APP_TOKEN,  # xapp-A111-222-xyz
            web_client=AsyncWebClient(token=SLACK_BOT_TOKEN)  # xoxb-111-222-xyz
        )
        self.web_client = WebClient(token=SLACK_BOT_TOKEN)


        loop = asyncio.get_event_loop()
        if block:
            loop.run_until_complete(self.main())
        else:
            # thread = threading.Thread(target=lambda:loop.run_forever(), args=())
            # thread.daemon = True
            # thread.start()
            loop.create_task(self.main())




    async def send_message_async(self, msg):
        try:
            response = await self.socket_client.web_client.chat_postMessage(channel="#" + self.channel_name, text=msg)
            assert response["message"]["text"] == msg
        except SlackApiError as e:
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
            raise e

    def send_message(self, msg):
        try:
            response = self.web_client.chat_postMessage(
                channel="#" + self.channel_name, text=msg
            )
        except SlackApiError as e:
            assert e.response["error"]

    async def send_file_async(self, title, file_path):
        upload_and_then_share_file = await self.socket_client.web_client.files_upload(
            channels="#" + self.channel_name,
            title=title,
            file=file_path,
        )
        return upload_and_then_share_file

    def send_file(self, title, file_path):
        upload_and_then_share_file = self.web_client.files_upload(
            channels="#" + self.channel_name,
            title=title,
            file=file_path,
        )
        return upload_and_then_share_file

    async def get_channel_id(self):
        try:
            conversation_id = None
            c_list = await self.socket_client.web_client.conversations_list()
            for c in c_list["channels"]:
                if c["name"] == self.channel_name:
                    conversation_id = c["id"]
                    print(f"Found conversation ID: {conversation_id}")
                    break
            return conversation_id
        except SlackApiError as e:
            print(f"Error: {e}")
            return None

    async def main(self):
        time.sleep(1)
        info = await self.socket_client.web_client.auth_test()
        print(type(self).__name__, "get bot id:", info)
        channel_id = await self.get_channel_id()
        self.ignored_user_id_list.append(info['user_id'])

        # await send_message("おはよー1")

        # Use async method
        async def process(socket_client: SocketModeClient, req: SocketModeRequest):
            if req.type == "events_api":
                # Acknowledge the request anyway
                response = SocketModeResponse(envelope_id=req.envelope_id)
                # Don't forget having await for method calls
                await socket_client.send_socket_mode_response(response)
                # print(req.payload)
                # Add a reaction to the message if it's a new message
                if req.payload["event"]["type"] == "message" and req.payload["event"].get("subtype") is None \
                        and req.payload["event"]['user'] not in self.ignored_user_id_list:
                    await socket_client.web_client.reactions_add(
                        name="eyes",
                        channel=req.payload["event"]["channel"],
                        timestamp=req.payload["event"]["ts"],
                    )
                    # print(req.payload["event"]['channel'])
                    if req.payload["event"]['channel'] == channel_id:
                        await self.task_on_message_received(req)
                elif req.payload["event"]["type"] == "message" and req.payload["event"].get("subtype") == \
                        "channel_join" and req.payload["event"]['user'] not in self.ignored_user_id_list:
                    if req.payload["event"]['channel'] == channel_id:
                        await self.send_message_async(self._welcome_message(req.payload["event"]['user']))

        # Add a new listener to receive messages from Slack
        # You can add more listeners like this
        self.socket_client.socket_mode_request_listeners.append(process)
        # Establish a WebSocket connection to the Socket Mode servers
        await self.socket_client.connect()
        # Just not to stop this process
        await asyncio.sleep(float("inf"))

    async def task_on_message_received(self, req: SocketModeRequest):

        if self.enabled:
            received_msg = req.payload["event"]['text'].replace("\n", "")
            s = received_msg.split("@@@")

            if len(s) == 1:
                await self.socket_client.web_client.reactions_add(
                    name="two_hearts",
                    channel=req.payload["event"]["channel"],
                    timestamp=req.payload["event"]["ts"],
                )

            #     text to command
                mes, cmd = text2command(s[0], language_code=detect_language(received_msg))
                print(mes, cmd)
                if mes == "None":
                    await self.send_message_async(mes+":" + cmd)
                elif mes == "OK":
                    for it in cmd:
                        remote_type, arg = it
                        print(remote_type, arg)
                        # send command to spm
                        #LabviewRemoteManager.instance.SendLabviewRemoteData_Command(remote_type, arg)
                        await asyncio.sleep(0.5)
                        await self.send_message_async(remote_type + ":" + arg)

            elif len(s) == 2:
                try:

                    """
                    do command here
                    """
                    command = BotCommandType[s[0]]
                    if command == BotCommandType.chat:
                        t = chat_closeai(s[1], user_id=req.payload["event"]["channel"], language_code=detect_language(s[1]))
                        await self.send_message_async(t)

                    if command == BotCommandType.get:
                        # get value in spm
                        # str = LabviewRemoteManager.instance.GetLabviewRemoteDataWithBlock_Command(s[1])
                        await self.send_message_async("BotCommandType.get")
                    if command == BotCommandType.set:
                        _s = s[1].split("=")
                        # set value in spm
                        # LabviewRemoteManager.instance.SendLabviewRemoteData_Command(_s[0], _s[1])
                    if command == BotCommandType.help:
                        # print help message
                        # await self.send_message_async(LabviewRemoteManager.instance.help_message())
                        pass
                    if command == BotCommandType.file:
                        await self.send_file_async(file_path=s[1]+".pkl", title=s[1])

                    await self.socket_client.web_client.reactions_add(
                        name="sparkles",
                        channel=req.payload["event"]["channel"],
                        timestamp=req.payload["event"]["ts"],
                    )

                except SlackApiError as e:
                    await self.socket_client.web_client.reactions_add(
                        name="broken_heart",
                        channel=req.payload["event"]["channel"],
                        timestamp=req.payload["event"]["ts"],
                    )
            else:
                await self.socket_client.web_client.reactions_add(
                    name="broken_heart",
                    channel=req.payload["event"]["channel"],
                    timestamp=req.payload["event"]["ts"],
                )


    """
    Yield scan events in the SPM system
    """
    # def _OnScanEventUpdate(self, sender, data):
    #     if self._enabled:
    #         if self.broadcast_scan:
    #             if data == ScanEventState.Start:
    #                 self.send_message(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")+"スキャン始めましたよ～")
    #             if data == ScanEventState.Finish:
    #                 self.send_message(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")+"スキャン終わりましたよ～")
    #             if data == ScanEventState.Stopped:
    #                 self.send_message(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")+"スキャンが止められました＞＜")


    """
    Get scan result and send to SNS
    """
    # def _OnSaveFileAdd(self, sender, data):
    #     if self._enabled:
    #         length = len(ScanFileManager.instance.scanHistoryFileDict.values())
    #         dataSerializer = list(ScanFileManager.instance.scanHistoryFileDict.values())[length - 1]
    #         if "FWFW_ZMap" in dataSerializer.data_dict.keys():
    #             self._save_fig(dataSerializer.data_dict["FWFW_ZMap"], "./slack_temp.png")
    #             self.send_file(file_path="./slack_temp.png", title=dataSerializer.path)


    @staticmethod
    def _save_fig(map, figName):
        plt.clf()
        map = spmu.flatten_map(np.asarray(map).copy(), spmu.FlattenMode.Average)
        map = spmu.filter_2d.gaussian_filter(map, 1)
        map = spmu.formula.topo_map_correction(map)
        plt.imshow(map, cmap="afmhot")
        plt.savefig(figName, transparent=True)

    def _welcome_message(self, user_id) -> str:
        return "<@" + user_id + ">" + "ようこそ" + self.channel_name + "へ⸜( ´ ꒳ ` )⸝♡︎\r\nこれは( ⁎ᵕᴗᵕ⁎ )❤あたしと素敵な♡STMデート♡をするためのチャンネルです.♡(｡☌ᴗ☌｡)\r\n具体的な使い方は以下のドキュメントをご覧になってください～₍ᐢ⑅•ᴗ•⑅ᐢ₎♡～\r\n" \
               + "https://github.com/DIAOZHUO/smart_spm_slack_bot_document/blob/main/SlackBot.md\r\n" \
               + "♥═━┈┈ ♡═━┈┈ ♥═━┈┈ ♡═━┈┈\r\n\r\nあなた(〃ﾉдﾉ)と一緒にときめく♡STM像♡を見ながら, 一緒にロマンチックな♡STMトーク♡をしたくて～～\r\nもう待ちきれません～～(///ω///)✺◟(∗❛ัᴗ❛ั∗)◞✺"










if __name__ == '__main__':
    slack = SlackBotModule("hatsunemiku-bot-stm", block=True)

