class TelegramClient:
    def __init__(self, session, token, chat_id) -> None:
        self.session = session
        self.token = token
        self.chat_id = chat_id
        self.headers = {"Content-Type": "applicaton/json"}
        self.url = f"https:////api.telegram.org/bot{token}/"

    def send_message(self, message: str):
        self.session.post(f"{self.url}/sendMessage", json={
            "chat_id": self.chat_id,
            "text": message
        })
