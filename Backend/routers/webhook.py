# backend/routers/webhook.py
import traceback
import unicodedata

from fastapi import APIRouter, BackgroundTasks

from Backend.agents.context import (
    clean_whatsapp_phone,
    is_lid,
    set_current_user_phone,
    set_current_user_id,
)
from Backend.agents.finance_agent import process_message
from Backend.core.mensagens import BaseErrors
from Backend.models.webhook import WAHAWebhook
from Backend.services.mapping_service import get_mapping_service
from Backend.services.whatsapp_service import WhatsAppService

router = APIRouter(prefix='/webhook', tags=['webhook'])


def remove_acentos(texto: str) -> str:
    """
    Remove acentos de texto para compatibilidade com LLM.

    Args:
        texto: Texto com acentos (ex: "almoço")

    Returns:
        Texto sem acentos (ex: "almoco")
    """
    return (
        unicodedata.normalize('NFKD', texto)
        .encode('ASCII', 'ignore')
        .decode('ASCII')
    )


async def process_and_reply(user_phone: str, message: str, session_name: str):
    """
    Processa mensagem e envia resposta.

    Args:
        user_phone: Telefone do usuário (pode ser LID ou número normal)
        message: Mensagem recebida
        session_name: Nome da sessão WAHA
    """
    # PRÉ-PROCESSAR: Remover acentos para o LLM processar
    message_normalized = remove_acentos(message)

    try:
        mapping = get_mapping_service()

        # Verifica se é LID e resolve para número real
        phone_to_send = user_phone
        if is_lid(user_phone):
            print(f'🔍 Detectado LID: {user_phone}')
            resolved = await mapping.resolve_phone_from_lid(user_phone)
            if resolved:
                phone_to_send = resolved
                print(f'✅ LID resolvido para: {phone_to_send}')
            else:
                print(f'❌ Falha ao resolver LID: {user_phone}')
                return

        # Busca user_id usando o telefone original (pode ser LID)
        user_id = await mapping.get_user_id_by_phone(user_phone)
        
        if not user_id:
            print('❌ Usuário não encontrado no banco')
            whatsapp = WhatsAppService()
            await whatsapp.send_message(
                phone=phone_to_send,
                text=BaseErrors.user_not_found(),
                session=session_name,
            )
            return

        print(f'✅ Usuário encontrado: {user_id}')

        user_data = await mapping.get_user(user_phone)
        
        if not user_data:
            print('❌ Erro ao buscar dados completos do usuário')
            whatsapp = WhatsAppService()
            await whatsapp.send_message(
                phone=phone_to_send,
                text=BaseErrors.user_not_found(),
                session=session_name,
            )
            return
        
        if user_data.get('access_denied', False):
            print(f'🚫 Acesso negado para usuário {user_data["username"]}: {user_data["reason"]}')
            
            whatsapp = WhatsAppService()
            
            if user_data["reason"] == "subscription_expired":
                # Assinatura expirada
                await whatsapp.send_message(
                    phone=phone_to_send,
                    text=BaseErrors.user_expired_subscription(),
                    session=session_name,
                )
            return

        print(f'✅ Usuário {user_data["username"]} tem acesso autorizado')

        clean_phone = clean_whatsapp_phone(phone_to_send, remove_country_code=True)
        set_current_user_phone(clean_phone)
        

        set_current_user_id(user_data['user_id']) 
 
        response = await process_message(message_normalized, clean_phone)

        if not response or not response.strip():
            print('⚠️ Resposta vazia, não enviando mensagem')
            return

        whatsapp = WhatsAppService()
        await whatsapp.send_message(
            phone=phone_to_send,
            text=response,
            session=session_name,
        )

        print(f'✅ Mensagem enviada com sucesso para {user_data["username"]}')

    except Exception as e:
        print(f'\n{"=" * 60}')
        print('❌ ERRO EM process_and_reply')
        print(f'{"=" * 60}')
        print(f'Tipo: {type(e).__name__}')
        print(f'Mensagem: {e}')
        print('\nTraceback completo:')
        traceback.print_exc()
        print(f'{"=" * 60}\n')

        # Envia mensagem de erro genérica para o usuário
        try:
            whatsapp = WhatsAppService()
            await whatsapp.send_message(
                phone=phone_to_send,
                text=BaseErrors.generic_error(),
                session=session_name,
            )
        except:
            print('❌ Erro ao enviar mensagem de erro')


@router.post('/')
async def webhook(data: WAHAWebhook, background_tasks: BackgroundTasks):
    """
    Endpoint para receber webhooks do WAHA.

    Args:
        data: Dados do webhook
        background_tasks: Processamento em background
    """
    if not data.is_valid_message():
        return {'status': 'ignored', 'reason': 'invalid message'}

    user_phone = data.payload.from_number
    message = data.payload.body
    session = data.session

    print(data)
    background_tasks.add_task(process_and_reply, user_phone, message, session)

    return {'status': 'accepted'}
