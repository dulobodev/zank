from typing import Optional
from uuid import UUID

from backend.agents.context import get_current_user_phone
from backend.services.mapping_service import get_mapping_service


async def get_current_user_id() -> Optional[UUID]:
    """
    Funcao para pegar o id do usuario com o seu telefone.
    """
    try:
        user_phone = get_current_user_phone()
        mapping = get_mapping_service()
        user_id = await mapping.get_user_id_by_phone(user_phone)
        return user_id
    except Exception:
        return None
