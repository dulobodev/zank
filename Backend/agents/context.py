# agents/context.py
import re
from contextvars import ContextVar

LID_REGEX = re.compile(r'^\d+@lid$')

# Context variables para armazenar dados do usuário atual
current_user_phone: ContextVar[str] = ContextVar(
    'current_user_phone', default=''
)

current_user_id: ContextVar[str] = ContextVar(  # ✅ NOVO
    'current_user_id', default=''
)

def get_current_user_phone() -> str:
    """Retorna o telefone do usuário atual do contexto."""
    phone = current_user_phone.get()
    if not phone:
        raise ValueError('User phone not set in context')
    return phone

def get_current_user_id() -> str:  # ✅ NOVO
    """Retorna o ID do usuário atual do contexto."""
    user_id = current_user_id.get()
    if not user_id:
        raise ValueError('User ID not set in context')
    return user_id

def set_current_user_phone(phone: str):
    """Define o telefone do usuário atual no contexto."""
    clean_phone = clean_whatsapp_phone(phone, remove_country_code=True)
    current_user_phone.set(clean_phone)

def set_current_user_id(user_id: str):  # ✅ NOVO
    """Define o ID do usuário atual no contexto."""
    current_user_id.set(user_id)

def is_lid(identifier: str) -> bool:
    """Verifica se o identificador combina com padrão LID: número + sufixo '@lid'."""
    return bool(LID_REGEX.match(identifier))

def extract_lid(identifier: str) -> str:
    """Extrai o LID puro removendo o sufixo @lid."""
    return identifier.replace('@lid', '').strip()

def clean_whatsapp_phone(
    phone: str, remove_country_code: bool = False, country_code: str = '55'
) -> str:
    """Limpa número de telefone WhatsApp removendo sufixos e formatação."""
    clean = (
        phone.replace('@c.us', '')
        .replace('@s.whatsapp.net', '')
        .replace('@lid', '')
        .strip()
    )
    clean = re.sub(r'[\s\-\(\)]', '', clean)

    if remove_country_code and clean.startswith(country_code):
        clean = clean[len(country_code):]

    return clean

def normalize_phone_to_whatsapp(phone: str, country_code: str = '55') -> str:
    """Normaliza telefone para formato WhatsApp (@c.us)."""
    clean = clean_whatsapp_phone(phone, remove_country_code=False)

    if not clean.startswith(country_code):
        clean = f'{country_code}{clean}'

    if not clean.endswith('@c.us'):
        clean = f'{clean}@c.us'

    return clean
