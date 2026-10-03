# 🛠️ TechFix Informática - Sistema de Ordens de Serviço

Solução web full-stack desenvolvida para substituir o atendimento em papel de uma assistência técnica por um sistema digital integrado em nuvem.

## Arquitetura & Tecnologias

* **Banco de Dados:** Supabase (PostgreSQL na nuvem com restrições de integridade, triggers e validações)
* **Atendimento no Balcão / Mobile:** Python + Gradio (`app_gradio.py`)
* **Painel do Gerente / Dashboard:** Python + Streamlit (`app_streamlit.py`)
* **Linguagem:** Python 3.10+

---

## 📁 Estrutura do Repositório

```text
techfix/
├── sql/
│   └── schema.sql        # Script DDL de criação do banco de dados
├── evidencias/          # Prints de funcionamento das aplicações e do banco
├── app_gradio.py        # Interface de cadastro de clientes e abertura de OS
├── app_streamlit.py     # Painel gerencial (CRUD, filtros, gráficos e exportação)
├── .env.example         # Modelo para variáveis de ambiente
├── requirements.txt     # Dependências Python do projeto
└── README.md
