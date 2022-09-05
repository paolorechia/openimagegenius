import os


class TelegramEnvironment:
    def __init__(self) -> None:
        self.token = os.environ["TELEGRAM_TOKEN"]
        self.chat_id = os.environ["TELEGRAM_CHAT_ID"]


class TelegramClient:
    def __init__(self, session, token, chat_id, logger) -> None:
        self.session = session
        self.token = token
        self.chat_id = chat_id
        self.headers = {"Content-Type": "applicaton/json"}
        self.url = f"https://api.telegram.org/bot{self.token}"
        self.logger = logger

    def send_message(self, message: str):
        self.logger.info("Sending message to telegram: %s", message)
        response = self.session.post(f"{self.url}/sendMessage", json={
            "chat_id": self.chat_id,
            "text": message
        })
        self.logger.info("Telegram response: %s", response.json())


def get_telegram(http_session, logger) -> TelegramClient:
    env = TelegramEnvironment()
    return TelegramClient(http_session, env.token, env.chat_id, logger)
