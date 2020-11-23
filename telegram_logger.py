import math
import time

import requests


class TelegramLogger:
    API_BASE_URL = "https://api.telegram.org/bot"
    MESSAGE_MAX_LENGTH = 4095

    def __init__(self, token: str, chat: str):
        self.token = token
        self.chat = chat

    def log(self, message: str):
        # parts = math.ceil(len(message) / self.MESSAGE_MAX_LENGTH)
        # for i in range(0, parts):
        # noinspection PyBroadException
        try:
            requests.post(self.API_BASE_URL + self.token + "/sendMessage", json={
                "chat_id": self.chat,
                "text": message,
                "parse_mode": "HTML",
            })
        except Exception:
            time.sleep(0)
