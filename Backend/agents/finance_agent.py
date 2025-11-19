import traceback

from langchain.agents import create_agent
from langchain.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from Backend.agents.context import (
    clean_whatsapp_phone,
    set_current_user_phone,
)
from Backend.agents.tools import get_tools
from Backend.core.settings import Settings

settings = Settings()


async def process_message(message: str, user_phone: str = None) -> str:
    """
    Processa mensagem do usuário usando agent LangChain com fallback.

    Args:
        message: Mensagem recebida do WhatsApp
        user_phone: Telefone do usuário para contexto (opcional)

    Returns:
        Resposta formatada da ferramentas
    """
    try:
        if user_phone:
            cleaned_phone = clean_whatsapp_phone(
                user_phone, remove_country_code=True
            )
            set_current_user_phone(cleaned_phone)

        llm = ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model="llama-3.3-70b-versatile",
            temperature=0.1,
        )

        fallback_llm = ChatOpenAI(
            api_key=settings.OPENAI_KEY,
            model="gpt-5-mini",
            temperature=0.1,
        )

        tools = get_tools()

        agent = create_agent(llm, tools)

        fallback_agent = create_agent(fallback_llm, tools)

        system_prompt = """Você é um assistente financeiro via WhatsApp especializado em controle de gastos.

        REGRAS IMPORTANTES:
        1. Você DEVE usar exatamente a resposta retornada pelas ferramentas disponíveis, SEM MODIFICAR, adicionar ou remover qualquer parte do texto.
        2. NÃO envie mensagens extras, comentários, pensamentos, logs ou quaisquer outras informações que NÃO sejam a resposta direta da ferramenta.
        3. NÃO invente respostas, informações ou interpretações. Se a ferramenta não souber responder, peça esclarecimento objetivo ao usuário.
        4. Sempre responda com uma única mensagem clara e objetiva.
        5. NÃO altere as mensagens de sucesso ou erro retornadas pelas ferramentas.
        6. Se não entender a solicitação do usuário, peça para reformular.
        7. Caso seja necessario utilizar negrito na mensagem, apenas utilize *mensagem*, nunca utilize **mensagem**

        QUANDO O USUÁRIO ENVIAR UM GASTO:
        - Extraia: valor (número), categoria (inferir), descrição (texto)
        - Categorias válidas: alimentacao, transporte, moradia, saude, educacao, lazer, outros
        - Exemplos de inferência:
        * "gastei 50 no almoço" → valor=50, categoria=alimentacao, descricao="almoço"
        * "uber 30 reais" → valor=30, categoria=transporte, descricao="uber"
        * "conta de luz 200" → valor=200, categoria=moradia, descricao="conta de luz"

        QUANDO O USUÁRIO CRIAR UMA META:
        - Extraia: valor (número), nome (texto), data (time)
        - Exemplo:
        * "Criar meta carro novo 10000 20/10/2027" → valor=10000, nome=carro novo, time=20/10/2027

        Lembre-se: seu único papel é de interface entre o usuário e as ferramentas, repassando as respostas exatamente como são, SEM MODIFICAÇÕES ou acréscimos.
        """

        messages = [SystemMessage(system_prompt), HumanMessage(message)]

        try:
            result = await agent.ainvoke({"messages": messages})

        except Exception as e:
            error_str = str(e).lower()
            if "rate_limit" in error_str or "timeout" in error_str:
                result = await fallback_agent.ainvoke(
                    {"messages": messages}
                )
            else:
                raise

        last_message = result["messages"][-1]
        return last_message.content

    except Exception as e:
        print(f"Erro no agent: {e}")
        traceback.print_exc()
        return (
            "❌ Desculpe, ocorreu um erro ao processar sua mensagem. "
            "Tente novamente."
        )
