import traceback
import unicodedata
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from http import HTTPStatus
from typing import Optional
from uuid import UUID

import httpx
from langchain_core.tools import tool

from backend.core.mensagens import (
    BaseErrors,
    GastosErrors,
    GastosMessages,
    HelpMessages,
    MetasMessages,
)
from backend.core.settings import Settings
from backend.services.mapping_service import get_mapping_service
from backend.utils.utils import get_current_user_id

settings = Settings()

API_URL = 'http://localhost:8000'
API_TOKEN = settings.BOT_API_KEY


def remove_acentos(texto: str) -> str:
    """Remove acentos de texto"""
    return (
        unicodedata.normalize('NFKD', texto)
        .encode('ASCII', 'ignore')
        .decode('ASCII')
    )


async def api_request(method: str, endpoint: str, **kwargs):
    """Faz requisição HTTP para API"""
    headers = {'X-API-Key': API_TOKEN, 'Content-Type': 'application/json'}
    
    async with httpx.AsyncClient() as client:
        if method == 'POST':
            response = await client.post(
                f'{API_URL}{endpoint}',
                headers=headers,
                timeout=30.0,
                **kwargs,
            )
        elif method == 'GET':
            response = await client.get(
                f'{API_URL}{endpoint}',
                headers=headers,
                timeout=30.0,
                **kwargs,
            )
        elif method == 'PUT':
            response = await client.put(
                f'{API_URL}{endpoint}',
                headers=headers,
                timeout=30.0,
                **kwargs,
            )
        elif method == 'PATCH':  # ← ADICIONE ISSO!
            response = await client.patch(
                f'{API_URL}{endpoint}',
                headers=headers,
                timeout=30.0,
                **kwargs,
            )
        elif method == 'DELETE':
            response = await client.delete(
                f'{API_URL}{endpoint}',
                headers=headers,
                timeout=30.0,
                **kwargs,
            )
        else:  
            raise ValueError(f"Método HTTP não suportado: {method}")
        
        response.raise_for_status()
        return response.json()



@tool
async def adicionar_gasto(valor: float, categoria: str, descricao: str) -> str:
    """
    Adiciona um novo gasto do usuário.

    Args:
        valor: Valor em reais (float positivo)
        categoria: Escolha uma: alimentacao, transporte, moradia,
            saude, educacao, lazer, outros
        descricao: Descrição do gasto (ex: "almoço", "uber",
            "conta de luz")

    Returns:
        Mensagem de confirmação formatada
    """
    try:
        mapping = get_mapping_service()

        descricao_limpa = remove_acentos(descricao)

        if valor <= 0 or not descricao_limpa.strip():
            return GastosErrors.create_validation()

        user_id = await get_current_user_id()

        if not user_id:
            return GastosErrors.not_found()

        categoria_id = await mapping.get_categoria_id_by_name(categoria)

        if not categoria_id:
            return GastosErrors.not_found()

        valor_decimal = Decimal(str(valor))

        result = await api_request(
            'POST',
            '/bot/',
            json={
                'message': descricao_limpa,
                'value': str(valor_decimal),
                'categoria_id': str(categoria_id),
                'user_id': str(user_id),
            },
        )

        data_criacao = datetime.now()

        if 'created_at' in result and result['created_at']:
            try:
                data_criacao = datetime.fromisoformat(
                    result['created_at'].replace('Z', '+00:00')
                )
            except Exception:
                data_criacao = datetime.now()

        return GastosMessages.create_success(
            mensagem_usuario=descricao_limpa,
            categoria=categoria,
            valor=valor_decimal,
            data=data_criacao,
            uuid=UUID(result['id']),
        )

    except Exception as e:
        print(f'Erro em adicionar_gasto: {e}')
        return GastosErrors.create_error()


@tool
async def ver_gasto(gasto_id: str) -> str:
    """
    Exibe detalhes de um gasto específico pelo ID.
    
    Args:
        gasto_id: UUID do gasto (formato: 550e8400-e29b-41d4-a716-446655440000)
    
    Returns:
        Detalhes formatados do gasto com categoria
    """
    try:
        user_id = await get_current_user_id()
        
        if not user_id:
            return GastosErrors.not_found()
        
        # ← PASSO 1: Busca o gasto pela API (retorna categoria_id)
        gasto_data = await api_request('GET', f'/bot/gastos/{gasto_id}')
        
        # Verifica se o gasto pertence ao usuário
        if gasto_data['user_id'] != str(user_id):
            return BaseErrors.not_permission()
        
        categoria_id = gasto_data['categoria_id']
        print(f"DEBUG: Buscando categoria para ID {categoria_id}")
        
        # ← PASSO 2: Busca TODAS as categorias da API e encontra pelo ID
        # Isso é mais confiável que mapeamento hardcoded
        try:
            # Nova chamada para buscar todas as categorias
            categorias_response = await api_request(
                'GET', 
                '/categorias',  # ← Assumindo que existe esta rota
                params={'limit': 100, 'offset': 0}
            )
            categorias = categorias_response.get('categorias', [])
            
            # Encontra a categoria pelo ID
            categoria_encontrada = None
            for cat in categorias:
                if str(cat['id']) == categoria_id:
                    categoria_encontrada = cat['name']
                    break
            
            # Fallback: se não encontrar, usa mapeamento manual
            if not categoria_encontrada:
                fallback_map = {
                    '1': 'alimentacao',
                    '2': 'transporte', 
                    '3': 'moradia',
                    '4': 'saude',
                    '5': 'educacao',
                    '6': 'lazer',
                    '7': 'outros'
                }
                categoria_encontrada = fallback_map.get(categoria_id, 'outros')
                print(f"DEBUG: Usando fallback para categoria_id {categoria_id} → {categoria_encontrada}")
            
            categoria_name = categoria_encontrada
            print(f"DEBUG: Categoria encontrada: {categoria_name}")
            
        except Exception as cat_error:
            print(f"Erro ao buscar categorias: {cat_error}")
            # Fallback mais simples se a API de categorias falhar
            fallback_map = {
                '1': 'alimentacao',
                '2': 'transporte', 
                '3': 'moradia',
                '4': 'saude',
                '5': 'educacao',
                '6': 'lazer',
                '7': 'outros'
            }
            categoria_name = fallback_map.get(categoria_id, 'outros')
            print(f"DEBUG: Fallback simples: {categoria_name}")
        
        # Formata a data
        try:
            data_criacao = datetime.fromisoformat(
                gasto_data['created_at'].replace('Z', '+00:00')
            )
        except Exception:
            data_criacao = datetime.now()
        
        # ← PASSO 3: Usa a mensagem formatada existente
        mensagem = GastosMessages.consult_success(
            uuid=UUID(gasto_data['id']),
            mensagem=gasto_data['message'],
            valor=Decimal(str(gasto_data['value'])),
            data=data_criacao,
            categoria=categoria_name,
        )
        
        return mensagem
        
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
        print(f"HTTP Error em ver_gasto: {error_msg}")
        
        if e.response.status_code == HTTPStatus.NOT_FOUND:
            return GastosErrors.not_found()
        elif e.response.status_code == HTTPStatus.FORBIDDEN:
            return BaseErrors.not_permission()
        else:
            return BaseErrors.generic_error()
    
    except KeyError as e:
        print(f"KeyError em ver_gasto: {e}")
        print(f"Dados recebidos: {gasto_data if 'gasto_data' in locals() else 'N/A'}")
        return '❌ Erro na estrutura dos dados do gasto. Tente novamente.'
    
    except Exception as e:
        print(f'Erro geral em ver_gasto: {e}')
        traceback.print_exc()
        return GastosErrors.consult_error()
 

@tool
async def listar_gastos_recentes(limite: int = 5) -> str:
    """
    Lista os gastos recentes do usuário, formatando a mensagem via GastosMessages.
    """
    try:
        user_id = await get_current_user_id()

        if not user_id:
            return GastosErrors.not_found()

        data = await api_request(
            'GET',
            f'/bot/user/{user_id}',
            params={'limit': limite, 'offset': 0},
        )

        gastos = data.get('gastos', [])

        if not gastos:
            return GastosErrors.no_gastos_found()

        # Usa a mensagem formatada da classe GastosMessages
        mensagem = GastosMessages.listar_gastos_recentes(gastos[:limite])

        return mensagem

    except Exception as e:
        print(f'❌ TOOL ERROR: {e}')
        traceback.print_exc()
        return GastosErrors.consult_error()
    

@tool
async def listar_gastos(limite: int = 200) -> str:
    """
    Lista os do usuário.

    Util quando o usuario pede para analisar os seus gastos,
    nao retornamos tudo nessa funcao, mas damos uma visao geral
    dos seus gastos

    Returns:
        Resumo formatado de todos os gastos
    """
    try:
        user_id = await get_current_user_id()

        if not user_id:
            return GastosErrors.not_found()

        data = await api_request(
            'GET',
            f'/bot/user/{user_id}',
            params={'limit': limite, 'offset': 0},
        )

        gastos = data.get('gastos', [])

        if not gastos:
            return GastosErrors.no_gastos_found()

        total = sum(float(g['value']) for g in gastos)

        gastos_por_categoria = {
            'alimentacao': 0,
            'moradia': 0,
            'educacao': 0,
            'saude': 0,
            'transporte': 0,
            'lazer': 0,
            'outros': 0,
        }

        for gasto in gastos: 
            categoria = gasto.get('categoria_name', 'outros')
            gastos_por_categoria[categoria] += float(gasto['value'])

        return GastosMessages.consult_all_success(
            total=Decimal(str(total)),
            gastos_por_categoria=gastos_por_categoria,
        )

    except Exception as e:
        print(f'❌ TOOL ERROR: {e}')
        traceback.print_exc()
        return GastosErrors.consult_error()


@tool
async def deletar_gasto(gasto_id: str) -> str:
    """
    Deleta um gasto específico pelo ID.

    Args:
        gasto_id: UUID do gasto
            (formatos: 550e8400-e29b-41d4-a716-446655440000 ou `70d450af-396b-48d9-b48b-38cb-5e41567c`)
        se o UUID vier nesse formato `70d450af-396b-48d9-b48b-38cb-5e41567c`, retire os Backtick

    Returns:
        Mensagem de confirmação
    """
    try:
        user_id = await get_current_user_id()

        gasto_data = await api_request('GET', f'/bot/gastos/{gasto_id}')

        if gasto_data['user_id'] != str(user_id):
            return BaseErrors.not_permission()

        await api_request('DELETE', f'/bot/gastos/{gasto_id}/{user_id}')
        return GastosMessages.delete_success()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND:
            return GastosErrors.not_found()
        return BaseErrors.generic_error()

    except Exception as e:
        print(f'Erro em deletar_gasto: {e}')
        return GastosErrors.create_error()


@tool
async def editar_gasto(
    gasto_id: str,
    novo_valor: Optional[float] = None,
    nova_descricao: Optional[str] = None,
    nova_categoria: Optional[str] = None,
) -> str:
    """
    Edita um gasto existente.

    Args:
        gasto_id: UUID do gasto
        novo_valor: Novo valor (opcional)
        nova_descricao: Nova descrição (opcional)
        nova_categoria: Nova categoria (opcional)

    Returns:
        Mensagem de confirmação
    """
    try:
        mapping = get_mapping_service()

        user_id = await get_current_user_id()

        gasto_data = await api_request('GET', f'/bot/gastos/{gasto_id}')

        if gasto_data['user_id'] != str(user_id):
            return BaseErrors.not_permission()

        categoria_id = gasto_data['categoria_id']
        if nova_categoria:
            categoria_id = await mapping.get_categoria_id_by_name(
                nova_categoria
            )

        descricao_final = nova_descricao or gasto_data['message']
        if nova_descricao:
            descricao_final = remove_acentos(nova_descricao)

        payload = {
            'message': descricao_final,
            'value': str(novo_valor or gasto_data['value']),
            'categoria_id': str(categoria_id),
        }

        await api_request(
            'PUT', f'/bot/gastos/{gasto_id}/{user_id}', json=payload
        )

        return GastosMessages.edit_success()

    except Exception as e:
        print(f'Erro em editar_gasto: {e}')
        return GastosErrors.create_error()


@tool
async def gastos_periodo(periodo: str) -> str:
    """
    Lista gastos por período específico.

    Args:
        periodo: Escolha um: "hoje", "semana", "mes", "ano"

    Returns:
        Resumo de gastos do período com total por categoria
    """
    try:
        user_id = await get_current_user_id()

        if not user_id:
            return GastosErrors.not_found()

        hoje = date.today()
        periodo_map = {
            'hoje': (hoje, hoje),
            'semana': (hoje - timedelta(days=7), hoje),
            'mes': (hoje.replace(day=1), hoje),
            'ano': (hoje.replace(month=1, day=1), hoje),
        }

        if periodo not in periodo_map:
            return '❌ Período inválido. Use: hoje, semana, mes ou ano'

        start_date, end_date = periodo_map[periodo]

        data = await api_request(
            'GET',
            f'/bot/user/{user_id}',
            params={
                'limit': 1000,
                'offset': 0,
                'start_date': str(start_date),
                'end_date': str(end_date),
            },
        )

        gastos = data.get('gastos', [])

        if not gastos:
            return GastosErrors.no_gastos_found()

        gastos_por_categoria = {}
        total_geral = Decimal(0)

        for gasto in gastos:
            cat_name = gasto.get('categoria_name', 'outros')
            valor = Decimal(str(gasto['value']))

            gastos_por_categoria[cat_name] = (
                gastos_por_categoria.get(cat_name, Decimal(0)) + valor
            )
            total_geral += valor

        periodo_formatado = {
            'hoje': 'hoje',
            'semana': 'esta semana',
            'mes': 'este mês',
            'ano': 'este ano',
        }[periodo]

        return GastosMessages.consult_all_success_by_data(
            periodo=periodo_formatado,
            total=total_geral,
            gastos_por_categoria=gastos_por_categoria,
        )

    except Exception as e:
        print(f'Erro em gastos_periodo: {e}')
        return GastosErrors.consult_error()


@tool
async def total_por_categoria(categoria: str) -> str:
    """
    Mostra total gasto em uma categoria específica no mês atual.

    Args:
        categoria: Nome da categoria (alimentacao, transporte, etc)

    Returns:
        Total gasto na categoria
    """
    try:
        mapping = get_mapping_service()

        user_id = await get_current_user_id()

        if not user_id:
            return GastosErrors.not_found()

        categoria_id = await mapping.get_categoria_id_by_name(categoria)
        if not categoria_id:
            return '❌ Categoria não encontrada'

        hoje = date.today()
        start_date = hoje.replace(day=1)

        data = await api_request(
            'GET',
            f'/bot/user/{user_id}',
            params={
                'limit': 1000,
                'offset': 0,
                'start_date': str(start_date),
                'end_date': str(hoje),
            },
        )

        gastos = data.get('gastos', [])
        total = sum(
            Decimal(str(g['value']))
            for g in gastos
            if g['categoria_id'] == str(categoria_id)
        )

        if total == 0:
            return f'📊 Nenhum gasto em {categoria} este mês'

        return f'📊 Total em {categoria} este mês: R$ {float(total):.2f}'

    except Exception as e:
        print(f'Erro em total_por_categoria: {e}')
        return GastosErrors.consult_error()


@tool
async def criar_meta(nome: str, valor: float, prazo: str) -> str:
    """
    Cria uma nova meta financeira.

    Args:
        nome: Nome da meta (ex: "Poupar para viagem")
        valor: Valor da meta em reais
        prazo: Data limite no formato DD/MM/YYYY

    Returns:
        Mensagem de confirmação
    """
    try:
        user_id = await get_current_user_id()

        if not user_id:
            return GastosErrors.not_found()

        prazo_date = datetime.strptime(prazo, '%d/%m/%Y').date()

        payload = {
            'name': nome,
            'value': str(valor),
            'value_actual': '0',
            'time': str(prazo_date),
            'user_id': str(user_id),
        }

        await api_request('POST', '/bot/metas', json=payload)

        return MetasMessages.create_success(
            name=nome, value=Decimal(str(valor)), time=prazo
        )

    except ValueError:
        return '❌ Data inválida. Use o formato DD/MM/YYYY'
    except Exception as e:
        print(f'Erro em criar_meta: {e}')
        return '❌ Erro ao criar meta. Tente novamente.'


@tool
async def ver_meta(meta_id: str) -> str:
    """
    Exibe detalhes de uma meta específica pelo ID.
    
    Args:
        meta_id: UUID da meta (formato: 550e8400-e29b-41d4-a716-446655440000)
    
    Returns:
        Detalhes formatados da meta com progresso
    """
    try:
        user_id = await get_current_user_id()
        
        if not user_id:
            return GastosErrors.not_found()
        
        # Busca diretamente pela meta usando a rota específica
        meta_data = await api_request('GET', f'/bot/metas/{meta_id}')
        
        # Verifica se a meta pertence ao usuário
        if meta_data['user_id'] != str(user_id):
            return BaseErrors.not_permission()
        
        # Usa a mensagem formatada da classe MetasMessages
        mensagem = MetasMessages.view_meta_success(meta_data)
        
        return mensagem
        
    except httpx.HTTPStatusError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND:
            return MetasMessages.not_found()
        return BaseErrors.generic_error()
    
    except Exception as e:
        print(f'Erro em ver_meta: {e}')
        traceback.print_exc()
        return '❌ Erro ao buscar meta. Tente novamente.'


@tool
async def listar_metas() -> str:
    """
    Lista todas as metas do usuário.

    Returns:
        Lista formatada de metas
    """
    try:
        user_id = await get_current_user_id()

        if not user_id:
            return GastosErrors.not_found()

        data = await api_request(
            'GET',
            f'/bot/metas/user/{user_id}',
            params={'limit': 50, 'offset': 0},
        )

        metas = data.get('metas', [])

        return MetasMessages.list_success(metas)

    except Exception as e:
        print(f'Erro em listar_metas: {e}')
        return '❌ Erro ao listar metas.'


@tool
async def deletar_meta(meta_id: str) -> str:
    """
    Deleta uma meta específica.

    Args:
        meta_id: UUID da meta

    Returns:
        Mensagem de confirmação
    """
    try:
        user_id = await get_current_user_id()

        meta = await api_request('GET', f'/bot/metas/{meta_id}')

        if meta['user_id'] != str(user_id):
            return BaseErrors.not_permission()

        await api_request('DELETE', f'/bot/metas/{meta_id}')

        return MetasMessages.delete_success()

    except httpx.HTTPStatusError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND:
            return MetasMessages.not_found()
        return '❌ Erro ao deletar meta'

    except Exception as e:
        print(f'Erro em deletar_meta: {e}')
        return '❌ Erro ao deletar meta.'


@tool
async def adicionar_valor_meta(meta_id: str, valor: float) -> str:
    """
    Adiciona valor ao progresso de uma meta existente.

    Args:
        meta_id: UUID da meta
        valor: Valor a ser adicionado ao progresso (float positivo)

    Returns:
        Mensagem de confirmação com progresso atualizado
    """
    try:
        user_id = await get_current_user_id()

        if not user_id:
            return GastosErrors.not_found()

        metas_data = await api_request(
            'GET',
            f'/bot/metas/user/{user_id}',
            params={'limit': 100, 'offset': 0},
        )

        meta_atual = next(
            (m for m in metas_data['metas'] if m['id'] == meta_id), None
        )

        if not meta_atual:
            return MetasMessages.not_found()
        
        if meta_atual['user_id'] != str(user_id):
            return BaseErrors.not_permission()

        novo_valor_actual = Decimal(str(meta_atual['value_actual'])) + Decimal(
            str(valor)
        )

        novo_valor_actual = min(
            novo_valor_actual, Decimal(str(meta_atual['value']))
        )

        await api_request(
            'PATCH',
            f'/bot/metas/{meta_id}',
            params={'value_actual': str(novo_valor_actual)},
        )

        return MetasMessages.update_success(
            name=meta_atual['name'],
            value_actual=novo_valor_actual,
            value_total=Decimal(str(meta_atual['value'])),
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND:
            return MetasMessages.not_found()
        return '❌ Erro ao atualizar meta'

    except Exception as e:
        print(f'Erro em adicionar_valor_meta: {e}')
        return '❌ Erro ao adicionar valor à meta. Tente novamente.'


@tool
async def ver_meta(meta_id: str) -> str:
    """
    Exibe detalhes de uma meta específica.

    Args:
        meta_id: UUID da meta

    Returns:
        Detalhes formatados da meta
    """
    try:
        user_id = await get_current_user_id()

        if not user_id:
            return GastosErrors.not_found()

        metas_data = await api_request(
            'GET',
            f'/bot/metas/user/{user_id}',
            params={'limit': 100, 'offset': 0},
        )

        meta = next(
            (m for m in metas_data['metas'] if m['id'] == meta_id), None
        )

        if not meta:
            return MetasMessages.not_found()

        return MetasMessages.view_meta_success(meta)

    except Exception as e:
        print(f'Erro em ver_meta: {e}')
        return '❌ Erro ao buscar meta.'


@tool
async def deletar_ultimo_gasto() -> str:
    """
    Deleta o último gasto adicionado pelo usuário.

    Returns:
        Mensagem de confirmação com detalhes do gasto deletado
    """
    try:
        user_id = await get_current_user_id()

        if not user_id:
            return GastosErrors.not_found()

        data = await api_request(
            'GET',
            f'/bot/user/{user_id}/ultimo-gasto',
        )

        gasto = data['gastos'][0]

        if not gasto:
            return GastosErrors.no_gastos_found()

        await api_request('DELETE', f'/bot/gastos/{gasto["id"]}/{user_id}')

        data_formatada = datetime.fromisoformat(gasto['created_at']).strftime(
            '%d/%m/%Y às %H:%M'
        )

        return (
            '✅ Último gasto deletado com sucesso!\n\n'
            '🗑️ Gasto removido:\n'
            f'• {gasto["message"]}\n'
            f'• R$ {float(gasto["value"]):.2f}\n'
            f'• Categoria: {gasto["categoria_name"]}\n'
            f'• Data: {data_formatada}\n\n'
            f'⚙️ #{gasto["id"]}'
        )

    except httpx.HTTPStatusError as e:
        if e.response.status_code == HTTPStatus.NOT_FOUND:
            return GastosErrors.not_found()
        return GastosErrors.delete_error()

    except Exception as e:
        print(f'Erro em deletar_ultimo_gasto: {e}')
        traceback.print_exc()
        return GastosErrors.delete_error()


@tool
async def ajuda() -> str:
    """
    Mostra comandos disponíveis do bot.

    Essa funcao deve ser chamada para toda mensagem em que o usuario
    pede ajuda para executar um comando, ou aprender mais sobre
    como utilizar as funcoes

    palavras chaves: comandos/suporte/ajuda/funcoes/como usar/tutorial
    quero registrar um gasto/ como faco um gasto/ como crio um gasto/

    Returns:
        Lista de comandos
    """
    return HelpMessages.commands()


def get_tools():
    """Retorna todas as ferramentas disponíveis"""
    return [
        adicionar_gasto,
        listar_gastos,
        listar_gastos_recentes,
        ver_gasto,  # ← NOVA TOOL
        deletar_gasto,
        deletar_ultimo_gasto,
        editar_gasto,
        gastos_periodo,
        total_por_categoria,
        criar_meta,
        listar_metas,
        ver_meta,  # ← MELHORADA
        adicionar_valor_meta,
        deletar_meta,
        ajuda,
    ]
