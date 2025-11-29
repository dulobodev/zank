import traceback

from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, update
import httpx

from Backend.agents.context import (
    clean_whatsapp_phone,
    extract_lid,
    is_lid,
)
from Backend.core.database import get_session_context
from Backend.core.settings import Settings
from Backend.models.models import User

settings = Settings()


class MappingService:
    """Serviço para mapeamento de usuários e resolução de telefones."""
    
    def __init__(
        self,
        api_url: str,
        api_token: str,
        waha_api_key: str,
        waha_url: str = 'http://localhost:3000',
        waha_session: str = 'default',
    ):
        self.api_url = api_url
        self.waha_url = waha_url
        self.waha_session = waha_session
        self.headers = {
            'X-API-Key': api_token,
            'Content-Type': 'application/json',
        }
        self.waha_headers = {
            'X-API-Key': waha_api_key,
            'Content-Type': 'application/json',
        }

    async def resolve_phone_from_lid(
        self,
        lid_identifier: str,
    ) -> Optional[str]:
        """Resolve um LID para um número de telefone usando a API do WAHA."""
        try:
            lid = extract_lid(lid_identifier)

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'{self.waha_url}/api/{self.waha_session}/lids/{lid}',
                    headers=self.waha_headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                return data.get('pn')
        except Exception as e:
            print(f'Erro ao resolver LID: {e}')
            return None


    async def get_user_id_by_phone(
        self,
        phone: str,
    ) -> Optional[UUID]:
        """Busca o user_id pelo telefone, resolvendo LID se necessário."""
        try:
            if is_lid(phone):
                print(
                    f'Detectado LID: {phone}.\n'
                    'Resolvendo para número de telefone...'
                )
                resolved_phone = await self.resolve_phone_from_lid(phone)

                if not resolved_phone:
                    print(
                        f'Não foi possível resolver o LID {phone} para\n'
                        'um número de telefone.'
                    )
                    return None

                phone = resolved_phone
                print(f'LID resolvido. Usando telefone: {phone}')

            clean_phone = clean_whatsapp_phone(
                phone,
                remove_country_code=True,
            )
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'{self.api_url}/users/by-phone/{clean_phone}',
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                print(response)
                print(data)
                return UUID(data['id'])

        except httpx.HTTPStatusError as e:
            print(
                f'Erro HTTP ao buscar user_id para {phone}: '
                f'{e.response.status_code}'
            )
            return None
        except Exception as e:
            print(f'Erro ao buscar user_id: {e}')
            return None

    async def get_user(self, phone: str) -> Optional[dict]:
        """Busca dados do usuário pelo telefone."""
        try:
            if is_lid(phone):
                print(f'Detectado LID: {phone}. Resolvendo para número de telefone...')
                resolved_phone = await self.resolve_phone_from_lid(phone)
                if not resolved_phone:
                    print(f'❌ Não foi possível resolver o LID {phone}')
                    return None
                phone = resolved_phone
                print(f'LID resolvido. Usando telefone: {phone}')
            
            clean_phone = clean_whatsapp_phone(phone, remove_country_code=True)
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'{self.api_url}/users/by-phone/{clean_phone}',
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                user_data = response.json()
                print(f'✅ Dados do usuário via API: {user_data}')

            user_id = UUID(user_data['id'])

            async with get_session_context() as session:
                user = await session.scalar(
                    select(User).where(User.id == user_id)
                )
                
                if not user:
                    print(f'❌ Usuário {user_id} não encontrado no banco')
                    return None

                print(f'✅ Usuário carregado do banco: {user.username} (ID: {user.id})')

                return {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'phone': user.phone,
                    'user_id': user_id
                }

        except httpx.HTTPStatusError as e:
            print(f'❌ Erro HTTP ao buscar user: {e.response.status_code}')
            return None
        except Exception as e:
            print(f'❌ Erro ao buscar user: {e}')
            traceback.print_exc()
            return None

    async def get_categoria_id_by_name(
        self,
        nome: str,
    ) -> Optional[UUID]:
        """Busca o ID da categoria pelo nome, normalizando sinônimos."""
        nome_normalized = nome.lower().strip()

        categorias_map = {
            'alimentacao': [
                'alimentacao',
                'comida',
                'almoço',
                'jantar',
                'lanche',
            ],
            'transporte': [
                'transporte',
                'uber',
                'taxi',
                'onibus',
                'gasolina',
            ],
            'moradia': [
                'moradia',
                'aluguel',
                'condominio',
                'luz',
                'agua',
            ],
            'saude': [
                'saude',
                'remedio',
                'farmacia',
                'consulta',
                'medico',
            ],
            'educacao': [
                'educacao',
                'curso',
                'livro',
                'mensalidade',
            ],
            'lazer': [
                'lazer',
                'cinema',
                'streaming',
                'viagem',
                'show',
            ],
            'outros': [
                'outros',
                'diverso',
            ],
        }

        categoria_key = None
        for key, synonyms in categorias_map.items():
            if nome_normalized in synonyms:
                categoria_key = key
                break

        if not categoria_key:
            categoria_key = 'outros'

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'{self.api_url}/categorias/by-name/{categoria_key}',
                    headers=self.headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                data = response.json()
                return UUID(data['id'])
        except Exception as e:
            print(f'Erro ao buscar categoria_id: {e}')
            return None


def get_mapping_service() -> MappingService:
    """Retorna instância singleton do MappingService."""
    if not hasattr(get_mapping_service, '_instance'):
        get_mapping_service._instance = MappingService(
            api_url='http://localhost:8000',
            api_token=settings.BOT_API_KEY,
            waha_api_key=settings.WAHA_API_KEY,
            waha_url='http://localhost:3000',
            waha_session='default',
        )
    return get_mapping_service._instance
