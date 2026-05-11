import os
import time
import requests
import streamlit as st
from decouple import config
from dotenv import load_dotenv

# Database & SQL imports
from langchain.agents import create_react_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

# Providers
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_community.chat_models import ChatOllama

import warnings
warnings.filterwarnings("ignore") # Ignorando todos warnings chatos temporariamente do console

# Load environment variables
load_dotenv()

# Função para checar se a chave é válida
def is_valid_key(key_val):
    if not key_val:
        return False
    key_val = key_val.strip().strip("'").strip('"')
    if not key_val:
        return False
    
    val_lower = key_val.lower()
    placeholders = ['sua-chave', 'suachave', 'sk-suachave']
    for p in placeholders:
        if p in val_lower:
            return False
            
    return True

# Função para checar se o Ollama está rodando localmente
def is_ollama_running():
    try:
        # A API padrão do Ollama responde na porta 11434
        response = requests.get('http://localhost:11434/', timeout=1)
        if response.status_code == 200:
            return True
        return False
    except requests.exceptions.RequestException:
        return False

# Função para buscar dinamicamente os modelos instalados no Ollama
def get_ollama_models():
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            data = response.json()
            models_list = data.get('models', [])
            
            # Retorna um dicionário {id_modelo: nome_de_exibicao}
            model_dict = {}
            for m in models_list:
                model_name = m.get('name')
                model_dict[model_name] = f"{model_name.capitalize()} 🦙"
                
            return model_dict
        return {}
    except requests.exceptions.RequestException:
        return {}

# Lendo as chaves com fallback
openai_raw = config('OPENAI_API_KEY', default=os.getenv('OPENAI_API_KEY'))
groq_raw = config('GROQ_API_KEY', default=os.getenv('GROQ_API_KEY'))

# Lista de provedores válidos
provider_options = []

# Checa ativamente se o Ollama está instalado e rodando
if is_ollama_running():
    provider_options.append('Ollama (Offline)')

if is_valid_key(groq_raw):
    os.environ['GROQ_API_KEY'] = groq_raw.strip("'").strip('"')
    provider_options.append('Groq')

if is_valid_key(openai_raw):
    os.environ['OPENAI_API_KEY'] = openai_raw.strip("'").strip('"')
    provider_options.append('OpenAI')

st.set_page_config(
    page_title='Assistente de Estoque',
    page_icon='🤖',
    layout="wide"
)

st.title('🤖 Assistente Inteligente de Estoque')

# --- Sidebar Configuration ---
with st.sidebar:
    st.header('Configurações')
    
    if not provider_options:
        st.error("Nenhuma IA disponível! Configure uma chave no arquivo .env ou inicie o aplicativo Ollama no seu PC.")
        st.stop()

    selected_provider = st.selectbox(
        label='Selecione o provedor de IA',
        options=provider_options
    )
    
    # Model Selection based on Provider
    if selected_provider == 'Groq':
        model_options = {
            'llama-3.1-8b-instant': 'Llama 3 8B 💸',
            'llama-3.3-70b-versatile': 'Llama 3 70B 💸💸',
        }
        default_index = 0 # llama-3.1-8b
    elif selected_provider == 'OpenAI':
        model_options = {
            'gpt-4o-mini': 'gpt-4o-mini 💸',
            'gpt-3.5-turbo': 'gpt-3.5-turbo 💸',
            'gpt-4o': 'gpt-4o 💸💸',
            'gpt-4-turbo': 'gpt-4-turbo 💸💸💸',
            'gpt-4': 'gpt-4 💸💸💸💸',
        }
        default_index = 0 # gpt-4o-mini
    elif selected_provider == 'Ollama (Offline)':
        # Busca a lista real de modelos baixados no PC do usuário
        model_options = get_ollama_models()
        
        # Fallback caso a API devolva vazio por algum motivo
        if not model_options:
            model_options = {'llama3:latest': 'Llama 3 🦙'}
            
        default_index = 0
        
    model_ids = list(model_options.keys())
    
    selected_model_id = st.selectbox(
        label='Selecione o modelo LLM',
        options=model_ids,
        format_func=lambda x: model_options[x],
        index=default_index
    )
    
    if selected_provider == 'Ollama (Offline)':
        st.success("✅ Ollama detectado e conectado!")
    
    st.markdown('### Sobre')
    st.markdown('Este agente consulta um banco de dados de estoque utilizando um modelo de IA e apresenta as respostas em um formato de chat interativo.')
    
# --- Initialize DB Agent System ---
def query_db_agent(provider_name, model_name, user_question):
    # Initialize the correct LLM based on provider
    model = None
    try:
        if provider_name == 'OpenAI':
            model = ChatOpenAI(model=model_name)
        elif provider_name == 'Groq':
            model = ChatGroq(model=model_name)
        elif provider_name == 'Ollama (Offline)':
            # ChatOllama usa a API REST local que roda por padrão na porta 11434
            model = ChatOllama(model=model_name)
    except Exception as e:
        return f"Erro ao inicializar o modelo {model_name}. Detalhes: {e}"

    if model is None:
        return "Erro: Modelo não pôde ser inicializado."

    try:
        # OTIMIZAÇÃO DE TOKENS: Limitando a visão do schema para evitar o retorno de DDL gigante
        db = SQLDatabase.from_uri(
            'sqlite:///stock_database_teste.db',
            sample_rows_in_table_info=0, # Define para ZERO para não trazer dados reais no prompt de schema, poupando muitos tokens
            include_tables=[
                'products_product', 
                'inflows_inflow', 
                'outflows_outflow', 
                'brands_brand', 
                'categories_category', 
                'suppliers_supplier'
            ] # Ignora fisicamente todas as tabelas de sistema do Django/Outros
        )
        
        toolkit = SQLDatabaseToolkit(db=db, llm=model)
        
        custom_system_prompt = '''
        Answer the following questions as best you can. You have access to the following tools:

        {tools}

        Use the following format:

        Question: the input question you must answer
        Thought: you should always think about what to do
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ... (this Thought/Action/Action Input/Observation can repeat N times)
        Thought: I now know the final answer
        Final Answer: A resposta final para a pergunta original do usuário.

        IMPORTANT RULES FOR DATABASE QUERIES:
        1. First, use `sql_db_schema` to see the schema of relevant tables. DO NOT use `sql_db_list_tables` as you already only have access to business tables.
        2. Then, build and run your query using `sql_db_query`.
        3. Se uma consulta SQL retornar vazia (ex: []), NÃO repita a mesma consulta. Isso significa que o filtro (WHERE) foi muito restrito ou você presumiu valores que não existem. Ajuste ou afrouxe os seus filtros para continuar explorando os dados.

        BUSINESS RULES:
        - Margem de Lucro (%): Quando questionado sobre a margem de lucro, calcule como `((selling_price * 1.0 / cost_price) - 1) * 100`. Não confunda com lucro nominal (que é apenas `selling_price - cost_price`). DICA: No SQLite, force a conversão para float multiplicando por 1.0 para evitar divisão inteira truncada.

        FORMATTING RULES FOR FINAL ANSWER:
        - ALWAYS respond in Brazilian Portuguese.
        - MANDATÓRIO: A sua resposta final DEVE SEMPRE começar com um título em Markdown (usando ##) que resuma o assunto da pergunta. Exemplo: Se perguntarem "quais itens existem", comece com "## Itens Disponíveis no Estoque".
        - Se a pergunta for genérica (ex: "Quais itens existem?", "Liste os produtos"), use uma lista de tópicos (bullet points) para cada item encontrado.
        - Use formatação de tabela Markdown APENAS se o usuário pedir explicitamente um "relatório" ou "tabela".
        - Para valores monetários, SEMPRE formate no padrão brasileiro: "R$ 9.999,00".
        - Para percentuais, SEMPRE formate no padrão brasileiro: "99,99%".
        - Quando usar tabelas Markdown com números ou valores monetários, VOCÊ DEVE alinhar essas colunas numéricas à direita utilizando `---:` na linha de separação. 
          Exemplo de formatação OBRIGATÓRIA:
          | Nome do Produto | Preço de Custo | Preço de Venda | Qtd |
          |:---|---:|---:|---:|
          | Item Exemplo | R$ 10,00 | R$ 20,00 | 5 |

        CRITICAL INSTRUCTION FOR LLAMA/GROQ/OLLAMA:
        If you already have the data you need from the Observation, DO NOT call `Action: None`. 
        You MUST IMMEDIATELY use `Thought: I now know the final answer` followed by `Final Answer: ...`.
        Never use `Action: None`.
        When giving your final answer, do NOT miss the "Final Answer: " prefix.

        Begin!

        Question: {input}
        Thought:{agent_scratchpad}
        '''
        
        prompt_template = PromptTemplate.from_template(custom_system_prompt)

        agent = create_react_agent(
            llm=model,
            tools=toolkit.get_tools(),
            prompt=prompt_template,
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=toolkit.get_tools(),
            verbose=True, 
            # O parâmetro abaixo corrige o bug do Llama ficar em loop enviando Action: None
            handle_parsing_errors="Formato inválido! Se você já sabe a resposta final, não envie 'Action:'. Apenas escreva 'Thought: I now know the final answer' seguido de 'Final Answer: [sua resposta]'.",
            max_iterations=12, # Aumentado de 8 para 12 para dar fôlego ao modelo nas correções
        )
        
        output = agent_executor.invoke({'input': user_question})
        return output.get('output')
    except Exception as e:
        return f"Erro durante o processamento do agente com banco de dados: {e}"

# --- Chat Interface ---
if 'messages' not in st.session_state:
    st.session_state['messages'] = []
    
for message in st.session_state.messages:
    with st.chat_message(message.get('role')):
        st.write(message.get('content'))

question = st.chat_input('O que deseja saber sobre o estoque?')

if question:
    st.chat_message('user').write(question)
    st.session_state.messages.append({'role': 'user', 'content': question})

    start_time = time.time() # Início da cronometragem
    
    with st.spinner(f'Consultando o banco de dados usando {selected_provider}...'):
        response = query_db_agent(selected_provider, selected_model_id, question)

        end_time = time.time() # Fim da cronometragem
        elapsed_time = end_time - start_time
        
        # Opcional: mostrar uma mensagem de sucesso discreta com o tempo logo acima da resposta
        st.success(f'Tempo gasto no processamento: {elapsed_time:.2f} segundos')

        st.chat_message('ai').write(response)
        st.session_state.messages.append({'role': 'ai', 'content': response})