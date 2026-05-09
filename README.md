<div align="center">
  
# 🤖 Assistente Inteligente de Estoque 📦

![Python](https://img.shields.io/badge/🐍_Python-3.12-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/🌐_Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![LangChain](https://img.shields.io/badge/🦜_LangChain-1C3C3C?style=for-the-badge)
![OpenAI](https://img.shields.io/badge/🧠_OpenAI-412991?style=for-the-badge&logo=openai&logoColor=white)
![SQLite](https://img.shields.io/badge/🗄️_SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

</div>

---

**Bem-vindo ao Assistente Inteligente de Estoque!** 🎉  
Um chatbot interativo poderoso e inteligente que facilita a consulta e análise do seu banco de dados de produtos. Utilizando inteligência artificial, ele permite que você converse com o seu banco de dados em linguagem natural, obtendo respostas completas sem escrever uma linha de SQL! 🤯

---

## 📋 Pré-requisitos 🛠️

Antes de decolar 🚀, você vai precisar de algumas coisas instaladas e configuradas:

- 🐍 **Python 3.12** (Adicionado às variáveis de ambiente / `PATH`)
- 🔑 **Chave de API da OpenAI** (Para dar vida ao nosso assistente)
- 💻 **Sistema Windows** (Para utilizar o script automatizado)

---

## 🚀 Instalação e Configuração ⚙️

Pensamos em tudo! O projeto conta com um script automatizado que prepara o ambiente todinho para você em poucos cliques. 🪄

### 1. Preparando o Ambiente
Abra o **PowerShell** na raiz do projeto e execute a mágica:

```powershell
.\update_project.ps1
```
> 💡 *O script cria o ambiente virtual, atualiza as ferramentas base, instala todas as dependências do `requirements.txt` e ainda cria o arquivo `.env`.*

### 2. Configurando as Chaves 🗝️
1. Abra o arquivo `.env` (criado automaticamente pelo script).
2. Substitua o valor padrão pela sua chave real da OpenAI:
   ```env
   OPENAI_API_KEY='sk-SuaChaveDaOpenAiAqui...'
   ```

---

## 💻 Como Executar ▶️

Com o motor aquecido, hora de rodar a interface web interativa do Streamlit:

1. No terminal (com o ambiente `venv` ativado), mande o comando:
   ```bash
   streamlit run app.py
   ```
2. 🌐 Uma nova aba abrirá instantaneamente no seu navegador! (Se não abrir, clique no link `http://localhost:8501` no terminal).
3. 🎛️ **Bônus:** Na aba lateral (Sidebar), você pode alternar facilmente entre as versões dos modelos de linguagem (como *gpt-4o-mini*, *gpt-4*).

---

## 🗣️ O que eu posso perguntar? 🤔

Aqui é onde a diversão começa! O nosso agente de IA é inteligente o suficiente para entender dezenas de contextos. Olha só alguns exemplos para testar:

### 📦 Verificação Geral
- *"Quais produtos temos em estoque atualmente?"*
- *"Quantas unidades do teclado Logitech K380 estão disponíveis?"*
- *"Liste todos os produtos da marca Intel."*

### 🚨 Reposição e Alertas (Estoque Baixo)
- *"Quais produtos estão com estoque zerado e precisam de reposição?"*
- *"Mostre todos os itens que têm menos de 10 unidades no estoque."*

### 💰 Valores e Precificação
- *"Qual é o nosso produto mais caro no banco de dados?"*
- *"Qual a média de preço dos periféricos da marca Logitech?"*
- *"Qual é o valor total investido em estoque atualmente?"*

### 📊 Relatórios Organizados
- *"Gere um relatório completo dos produtos organizados por preço do maior para o menor."*
- *"Crie uma lista vertical com bullet points com todos os fones e placas de vídeo (RTX) que constam no sistema."*

---

## ℹ️ Informações Importantes sobre o Projeto

⚠️ **Aviso de Sessão / Histórico:**
Este aplicativo foi desenvolvido com foco em testes, apresentação de portfólio e demonstração de tecnologias (LangChain + OpenAI Tools + Bancos Relacionais). Por esse motivo, **o histórico do chat é mantido exclusivamente em memória (`st.session_state`)**.
Isso significa que, ao recarregar a página (F5) ou reiniciar a aplicação, **todas as mensagens anteriores serão apagadas**. O agente extrairá sempre os dados mais recentes do banco a cada pergunta, mas não lembrará do contexto passado em novas abas.

<div align="center">
  <br/>
  
  > **Nota:** As consultas funcionam baseadas no banco de dados SQLite `estoque.db` presente na raiz da aplicação. O modelo fará todo o trabalho pesado de transformar a sua pergunta em uma consulta SQL válida por baixo dos panos! ⚙️

  <br/>
  Feito com ❤️, muito Python e IA! ✨
</div>