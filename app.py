import os
import streamlit as st
from decouple import config

# Database & SQL imports
from langchain import hub
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import PromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

# Load environment variables
os.environ['OPENAI_API_KEY'] = config('OPENAI_API_KEY')

st.set_page_config(
    page_title='Assistente de Estoque',
    page_icon='🤖',
    layout="wide"
)

st.title('🤖 Assistente Inteligente de Estoque')

# --- Sidebar Configuration ---
with st.sidebar:
    st.header('Configurações')
    
    # Model Selection
    model_options = [
        'gpt-3.5-turbo',
        'gpt-4',
        'gpt-4-turbo',
        'gpt-4o-mini',
        'gpt-4o',
    ]
    selected_model = st.selectbox(
        label='Selecione o modelo LLM',
        options=model_options,
        index=4 # Default to gpt-4o-mini
    )
    
    st.markdown('### Sobre')
    st.markdown('Este agente consulta um banco de dados de estoque utilizando um modelo GPT e apresenta as respostas em um formato de chat interativo.')
    
# --- Initialize DB Agent System ---
def query_db_agent(model_name, user_question):
    model = ChatOpenAI(model=model_name)
    try:
        db = SQLDatabase.from_uri('sqlite:///stock_database_teste.db')
        toolkit = SQLDatabaseToolkit(db=db, llm=model)
        
        # Usando o Tool Calling Agent em vez de ReAct Agent
        system_message = hub.pull('hwchase17/openai-tools-agent')

        agent = create_tool_calling_agent(
            llm=model,
            tools=toolkit.get_tools(),
            prompt=system_message,
        )

        agent_executor = AgentExecutor(
            agent=agent,
            tools=toolkit.get_tools(),
            verbose=True,
        )

        prompt_str = '''
        Use as ferramentas necessárias para responder perguntas relacionadas ao
        estoque de produtos. Você fornecerá insights sobre produtos, preços, 
        reposição de estoque e relatórios conforme solicitado pelo usuário.
        A resposta final deve ter uma formatação amigável de visualização para o usuário.
        Se forem vários itens colocar na vertical em formato de lista com bullet.
        Sempre inclua um título explicando o que é a resposta.
        Sempre responda em português brasileiro.
        Pergunta: {q}
        '''
        prompt_template = PromptTemplate.from_template(prompt_str)
        formatted_prompt = prompt_template.format(q=user_question)
        
        output = agent_executor.invoke({'input': formatted_prompt})
        return output.get('output')
    except Exception as e:
        return f"Erro ao acessar o banco de dados de estoque: {e}"

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

    with st.spinner('Consultando o banco de dados...'):
        response = query_db_agent(selected_model, question)

        st.chat_message('ai').write(response)
        st.session_state.messages.append({'role': 'ai', 'content': response})
