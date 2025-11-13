# backend/core/mensagens.py
"""
Templates de mensagens para serem usadas nas funções.
"""

from datetime import datetime
from decimal import Decimal
from uuid import UUID


class GastosMessages:
    """Mensagens para operações de gastos"""

    @staticmethod
    def create_success(
        mensagem_usuario: str,
        categoria: str,
        valor: Decimal,
        data: datetime,
        uuid: UUID,
    ) -> str:
        return (
            '✅ *GASTO REGISTRADO COM SUCESSO!*\n\n'
            f'📝 "{mensagem_usuario}"  "{(categoria)}"\n\n'
            f'💵 Valor: R$ {float(valor):.2f}\n\n'
            f'📅 Data: {data.strftime("%d/%m/%Y")}\n\n\n'
            f'⚙️ `{uuid}`\n'
        )

    @staticmethod
    def consult_success(
        uuid: UUID,
        mensagem: str,
        valor: Decimal,
        data: datetime,
        categoria: str,
    ) -> str:
        return (
            f'🔍 *DETALHES DO GASTO*\n\n'
            f'📝 {mensagem}\n'
            f'💵 R$ {float(valor):.2f}\n'
            f'📅 {data.strftime("%d/%m/%Y")}\n'
            f'🏷️ {categoria}\n\n'
            f'⚙️ `{uuid}`'
        )

    @staticmethod
    def consult_all_success(
        total: Decimal,
        gastos_por_categoria: dict,
    ) -> str:
        return (
            f'📊 *RESUMO DOS SEUS GASTOS*\n\n'
            f'💵 Total: R$ {float(total):.2f}\n\n'
            '*Gasto por categoria:*\n\n'
            f'🍱 Alimentação: R$ {float(gastos_por_categoria.get("alimentacao", 0)):.2f}\n'
            f'🏠 Moradia: R$ {float(gastos_por_categoria.get("moradia", 0)):.2f}\n'
            f'📖 Educação: R$ {float(gastos_por_categoria.get("educacao", 0)):.2f}\n'
            f'🧑🏻‍⚕️ Saúde: R$ {float(gastos_por_categoria.get("saude", 0)):.2f}\n'
            f'🚕 Transporte: R$ {float(gastos_por_categoria.get("transporte", 0)):.2f}\n'
            f'🎰 Lazer: R$ {float(gastos_por_categoria.get("lazer", 0)):.2f}\n'
            f'💸 Outros: R$ {float(gastos_por_categoria.get("outros", 0)):.2f}'
        )
    
    @staticmethod
    def consult_all_success_by_data(
    periodo: str,
    total: Decimal,
    gastos_por_categoria: dict,
    ) -> str:
        return (
            f'📊 *RESUMO DOS SEUS GASTOS - {periodo.upper()}*\n\n'
            f'💵 Total: R$ {float(total):.2f}\n\n'
            '*Gasto por categoria:*\n\n'
            f'🍱 Alimentação: R$ {float(gastos_por_categoria.get("alimentacao", 0)):.2f}\n'
            f'🏠 Moradia: R$ {float(gastos_por_categoria.get("moradia", 0)):.2f}\n'
            f'📖 Educação: R$ {float(gastos_por_categoria.get("educacao", 0)):.2f}\n'
            f'🧑🏻‍⚕️ Saúde: R$ {float(gastos_por_categoria.get("saude", 0)):.2f}\n'
            f'🚕 Transporte: R$ {float(gastos_por_categoria.get("transporte", 0)):.2f}\n'
            f'🎰 Lazer: R$ {float(gastos_por_categoria.get("lazer", 0)):.2f}\n'
            f'💸 Outros: R$ {float(gastos_por_categoria.get("outros", 0)):.2f}'
        )
    
    @staticmethod
    def listar_gastos_recentes(gastos: list) -> str:
        emoji_categoria = {
            'alimentacao': '🍱',
            'moradia': '🏠',
            'educacao': '📖',
            'saude': '🧑🏻‍⚕️',
            'transporte': '🚕',
            'lazer': '🎰',
            'outros': '💸'
        }

        linhas = []
        for g in gastos:
            categoria = g.get('categoria_name', 'outros').lower()
            emoji_cat = emoji_categoria.get(categoria, '❓')
            data_formatada = datetime.fromisoformat(g['created_at']).strftime('%d/%m/%Y')

            linha = (
                f'{emoji_cat}  {'📅'} {data_formatada}\n'
                f'R$ {float(g["value"]):.2f} - {g["message"]}\n'
                f'⚙️ `{g["id"]}`'
            )
            linhas.append(linha)

        return f'📊 *Seus últimos {len(linhas)} gastos:*\n\n' + '\n\n'.join(linhas)

    @staticmethod
    def edit_success() -> str:
        return '🆙 Gasto atualizado com sucesso!'

    @staticmethod
    def delete_success() -> str:
        return '🗑️ Gasto deletado com sucesso!'


class GastosErrors:
    """Mensagens de erro para gastos"""

    @staticmethod
    def create_validation() -> str:
        return (
            '❌ Para criar um gasto é necessário:\n'
            '• Descrição com no mínimo 1 caractere\n'
            '• Valor maior que R$ 0,00\n\n'
            '💬 Precisa de ajuda? É só perguntar!'
        )

    @staticmethod
    def create_error() -> str:
        return (
            '❌ Ops! Algo deu errado ao criar o gasto.\n\n'
            'Tente novamente em alguns instantes.\n\n'
            '📞 Precisa de ajuda? Digite "Suporte"\n'
        )
    
    @staticmethod
    def delete_error() -> str:
        return (
            '❌ Ops! Algo deu errado ao tentar deletar o gasto.\n\n'
            'Tente novamente em alguns instantes.\n\n'
            '📞 Precisa de ajuda? Digite "Suporte"\n'
        )

    @staticmethod
    def user_not_found() -> str:
        return (
            '🚫 *Acesso negado*\n\n'
            'Você ainda não tem acesso ao serviço.\n\n'
            '🌐 Assine agora e tenha controle total das suas finanças:\n'
            'www.seusite.com/assinar\n\n'
            '💰 Planos a partir de R$ 9,90/mês'
        )

    @staticmethod
    def consult_error() -> str:
        return (
            '❌ Erro ao buscar seus gastos.\n\n'
            'Tente novamente em alguns instantes.\n\n'
            '📞 Precisa de ajuda? Digite "Suporte"'
        )

    @staticmethod
    def gastos_not_found() -> str:
        return (
            '📭 *Nenhum gasto encontrado*\n\n'
            'Você ainda não registrou gastos.\n'
            'Comece agora! É só me dizer o que gastou.\n\n'
            '💡 _Exemplo: "Gastei 50 reais no almoço"_'
        )


class MetasMessages:
    """Mensagens para operações de metas"""

    @staticmethod
    def create_success(name: str, value: Decimal, time: str) -> str:
        return (
            f'✅ *META CRIADA COM SUCESSO!*\n\n'
            f'🎯 {name}\n'
            f'💵 Valor: R$ {float(value):.2f}\n'
            f'📅 Prazo: {time}\n\n'
            '💪 Vamos alcançar essa meta juntos!'
        )

    @staticmethod
    def list_success(metas: list) -> str:
        if not metas:
            return (
                '📊 *SUAS METAS*\n\n'
                'Você ainda não possui metas cadastradas.\n\n'
                '💡 Digite "Suporte" para aprender a criar uma meta\n'
            )

        resultado = '🎯 *SUAS METAS*\n\n'
        for meta in metas:
            progresso = (
                float(meta['value_actual']) / float(meta['value'])
            ) * 100
            barra = '█' * int(progresso / 10) + '░' * (
                10 - int(progresso / 10)
            )

            resultado += (
                f'• *{meta["name"]}*\n\n'
                f'  🟢 R$ {float(meta["value_actual"]):.2f}  /  R$ {float(meta["value"]):.2f}\n\n'
                f'  📅 {meta["time"]}\n\n'
                f'  {barra} {progresso:.1f}%\n\n'
                f'  ⚙️ `{meta["id"]}`\n\n\n'
            )
        return resultado

    @staticmethod
    def update_success(
        name: str, value_actual: Decimal, value_total: Decimal
    ) -> str:
        progresso = (float(value_actual) / float(value_total)) * 100
        barra = '█' * int(progresso / 10) + '░' * (10 - int(progresso / 10))

        return (
            f'🆙 *META ATUALIZADA!*\n\n'
            f'🎯  {name}\n\n'
            f'🟢 R$ {float(value_actual):.2f}  /  R$ {float(value_total):.2f}\n\n'
            f'{"🎉 *Parabéns! Meta atingida!*" if progresso >= 100 else f"💪 Faltam R$ {float(value_total - value_actual):.2f}"}\n\n'
            f'{barra} {progresso:.1f}%'
        )

    @staticmethod
    def view_meta_success(meta: dict) -> str:
        progresso = (float(meta['value_actual']) / float(meta['value'])) * 100
        falta = float(meta['value']) - float(meta['value_actual'])
        barra = '█' * int(progresso / 10) + '░' * (10 - int(progresso / 10))

        status = '✅ Concluída' if progresso >= 100 else '⏳ Em andamento'

        return (
            f'🎯 *{meta["name"]}*\n'
            f'{status}\n\n'
            f'💰 Atual: R$ {float(meta["value_actual"]):.2f}\n\n'
            f'🎯 Meta: R$ {float(meta["value"]):.2f}\n\n'
            f'📅 Prazo: {meta["time"]}\n\n'
            f'{"🎉 *Parabéns! Você atingiu sua meta!*" if progresso >= 100 else f"💪 Faltam R$ {falta:.2f} para atingir a meta"}\n\n'
            f'{barra} {progresso:.1f}%\n\n'
            f'⚙️ `{meta["id"]}`'
        )

    @staticmethod
    def delete_success() -> str:
        return '🗑️ Meta deletada com sucesso!'

    @staticmethod
    def not_found() -> str:
        return (
            '❌ *Meta não encontrada*\n\n'
            'O ID informado não existe.\n'
            'Verifique se copiou corretamente.\n\n'
            '💡 Use _"Minhas metas"_ para ver todas'
        )


class BaseErrors:
    """Mensagens de erro gerais da aplicação"""

    @staticmethod
    def user_not_found() -> str:
        return (
            '🚫 *Acesso negado*\n\n'
            'Você ainda não tem acesso ao serviço.\n\n'
            '🌐 Assine agora e tenha controle total das suas finanças:\n'
            'www.seusite.com/assinar\n\n'
            '💰 Planos a partir de R$ 9,90/mês'
        )

    @staticmethod
    def user_expired_subscription() -> str:
        return (
            '⏰ *Assinatura expirada!*\n\n'
            'Renove agora para continuar usando:\n'
            'www.seusite.com/renovar\n\n'
            '✨ Não perca o controle das suas finanças!'
        )

    @staticmethod
    def generic_error() -> str:
        return (
            '❌ *Erro inesperado*\n\n'
            'Algo deu errado. Tente novamente.\n\n'
            '📞 Suporte: email@example.com'
        )

    @staticmethod
    def not_permission() -> str:
        return (
            '🚨 *Sem permissão*\n\n'
            'Você não pode alterar registros de outros usuários.\n\n'
            '📞 Dúvidas? Contate: email@example.com'
        )


class HelpMessages:
    """Mensagens de ajuda"""

@staticmethod
def commands() -> str:
    """
    Mensagem de ajuda principal, agora mais intuitiva e explicativa.
    Explica o uso do bot de forma natural, com exemplos reais e dicas.
    """
    return (
        '👋 *Olá! Eu sou seu assistente financeiro pessoal!*\n\n'
        'Meu nome é FinBot e estou aqui para te ajudar a controlar '
        'suas finanças de forma simples e natural. Você não precisa '
        'memorizar comandos complicados – é só conversar comigo como '
        'falaria com um amigo! 💬 Eu entendo linguagem cotidiana e '
        'vou te guiar passo a passo.\n\n'
        
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '🚀 *COMO EU FUNCIONO? (É FÁCIL!)*\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '• Fale naturalmente: "Gastei 30 reais no café da manhã"\n'
        '• Eu pergunto detalhes se precisar (como categoria)\n'
        '• Respondo com confirmações claras e emojis para facilitar\n'
        '• Se algo não entender, peço esclarecimentos sem complicar\n'
        '• Sempre mostro IDs dos registros para você editar depois\n\n'
        '💡 *Dica rápida:* Use palavras como "gastei", "paguei", "comprei" '
        'para registrar. Para ver relatórios, diga "meus gastos" ou "quanto gastei".\n\n'
        
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '💰 *REGISTRAR SEUS GASTOS*\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        'Eu categorizo automaticamente, mas você pode especificar!\n\n'
        '*Exemplos simples:*\n'
        '• _"Gastei 45 reais no almoço no shopping"_\n'
        '• _"Paguei 80 de Uber para o trabalho"_\n'
        '• _"150 reais na conta de luz este mês"_\n'
        '• _"Comprei 25 em transporte de ônibus"_\n\n'
        '*Se quiser categoria específica:*\n'
        '• _"Gastei 100 em alimentação no supermercado"_\n'
        '• _"20 reais em lazer no cinema"_\n\n'
        'Após registrar, eu confirmo tudo e dou um ID único para editar depois! 🎉\n\n'
        
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '📊 *VER E ANALISAR GASTOS*\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        'Peça relatórios de qualquer período ou categoria – eu mostro totais e detalhes.\n\n'
        '*Exemplos para visão geral:*\n'
        '• _"Meus gastos recentes"_ (últimos 5)\n'
        '• _"Gastos de hoje"_ ou _"Gastos desta semana"_\n'
        '• _"Resumo do mês"_ ou _"Analise meus gastos"_\n'
        '• _"Quanto gastei em total?"_\n\n'
        '*Por categoria ou período:*\n'
        '• _"Gastos em alimentação este mês"_\n'
        '• _"Quanto em transporte na semana?"_\n'
        '• _"Meus gastos no ano"_\n\n'
        '*Detalhe específico:*\n'
        '• _"Ver gasto #550e8400-e29b-41d4-a716-446655440000"_ '
        '(use o ID que eu te mostro nas confirmações)\n\n'
        'Eu mostro totais por categoria com emojis para ficar visual! 📈\n\n'
        
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '🛠️ *EDITAR OU REMOVER GASTOS*\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        'Errou? Sem problema, é rápido corrigir!\n\n'
        '*Exemplos:*\n'
        '• _"Deletar o último gasto"_ (remove o mais recente)\n'
        '• _"Excluir gasto #abc123"_ (use o ID específico)\n'
        '• _"Editar gasto #abc123 para 50 reais em lazer"_\n\n'
        'Eu confirmo sempre antes de alterar e mostro o que mudou! 🔄\n\n'
        
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '🎯 *CRIAR E ACOMPANHAR METAS*\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        'Defina objetivos e veja seu progresso com barras visuais!\n\n'
        '*Criar meta:*\n'
        '• _"Criar meta de poupar 1000 reais até 31/12/2025"_\n'
        '• _"Meta de 500 em saúde para 15/06/2025"_\n\n'
        '*Ver metas:*\n'
        '• _"Minhas metas"_ (lista todas com % de progresso)\n'
        '• _"Ver meta #123e4567-e89b-12d3-a456-426614174000"_ '
        '(detalhes e status)\n\n'
        '*Atualizar progresso:*\n'
        '• _"Adicionei 200 na meta #abc123"_ (atualiza o valor acumulado)\n'
        '• _"Deletar meta #abc123"_\n\n'
        'Eu mostro barras de progresso e celebro quando você atinge! 🏆\n\n'
        
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '🆘 *PRECISA DE MAIS AJUDA?*\n'
        '━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n'
        '• Diga _"Suporte"_, _"Ajuda"_ ou _"Como usar?"_ para mais dicas\n'
        '• _"Tutoriais"_ para exemplos passo a passo\n'
        '• Se algo der errado, eu explico e sugiro o que fazer\n\n'
        '📱 *Categorias disponíveis (eu sugiro se não especificar):*\n'
        '• alimentacao (🍱)\n'
        '• transporte (🚕)\n'
        '• moradia (🏠)\n'
        '• saude (🧑🏻‍⚕️)\n'
        '• educacao (📖)\n'
        '• lazer (🎰)\n'
        '• outros (💸)\n\n'
        
        '💪 *Por que eu sou útil?* Eu te ajudo a economizar tempo, '
        'evitar gastos desnecessários e alcançar suas metas. '
        'Vamos começar? Me conte o que você gastou hoje! 🚀\n\n'
        
        '📞 *Dúvidas técnicas?* Contate: suporte@seuapp.com '
        'ou visite www.seusite.com/ajuda'
    )

    
    @staticmethod
    def welcome(nome_usuario: str) -> str:
        return (
            f"👋 Seja bem-vindo, {nome_usuario}!\n\n"
            "Sou seu assistente para controle financeiro! 🎯\n\n"
            "Aqui você pode:\n"
            "• Registrar e analisar seus gastos 💸\n"
            "• Criar e acompanhar metas financeiras 🎯\n"
            "• Consultar relatórios detalhados em qualquer momento 📊\n\n"
            "Fique à vontade para conversar comigo de forma natural.\n"
            "É só dizer o que deseja fazer!\n\n"
            "💡 *Se precisar de ajuda para aprender como usar as funções, digite \"Suporte\" e receba instruções completas!*"
        )
