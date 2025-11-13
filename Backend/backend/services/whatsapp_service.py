import httpx

from backend.agents.context import normalize_phone_to_whatsapp
from backend.core.settings import Settings

settings = Settings()


class WhatsAppService:
    def __init__(self):
        self.base_url = settings.WAHA_BASE_URL
        self.api_key = settings.WAHA_API_KEY
        self.session = settings.WAHA_SESSION_NAME

    async def send_message(self, phone: str, text: str, session: str = None):
        session_name = session or self.session
        chat_id = normalize_phone_to_whatsapp(phone)

        url = f'{self.base_url}/api/sendText'

        payload = {'session': session_name, 'chatId': chat_id, 'text': text}

        headers = {
            'X-Api-Key': self.api_key,
            'Content-Type': 'application/json',
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    url, json=payload, headers=headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f'Erro ao enviar mensagem: {e}')
            raise
