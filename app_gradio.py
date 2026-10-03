import os
import re
import gradio as gr
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Variáveis de ambiente SUPABASE_URL e SUPABASE_KEY são obrigatórias.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def validar_email(email: str) -> bool:
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    return bool(re.match(pattern, email.strip()))

def validar_celular(celular: str) -> bool:
    return celular.isdigit() and 10 <= len(celular) <= 13

def cadastrar_os(nome, endereco, email, celular, modelo, problema):
    # Validações básicas de campos vazios
    if not all([nome, endereco, email, celular, modelo, problema]):
        return "❌ Erro: Todos os campos são obrigatórios."

    email_clean = email.strip()
    celular_clean = re.sub(r'\D', '', celular)  # remove não-dígitos para garantir

    if not validar_email(email_clean):
        return "❌ Erro: Formato de e-mail inválido."

    if not validar_celular(celular_clean):
        return "❌ Erro: Celular deve conter apenas números (DDD + Número), entre 10 e 13 dígitos."

    try:
        # 1. Verifica se o cliente já existe pelo e-mail
        res_cliente = supabase.table("clientes").select("id").eq("email", email_clean).execute()

        if res_cliente.data:
            cliente_id = res_cliente.data[0]["id"]
            # Atualiza dados cadastrais caso tenham mudado
            supabase.table("clientes").update({
                "nome": nome.strip(),
                "endereco": endereco.strip(),
                "celular_whatsapp": celular_clean
            }).eq("id", cliente_id).execute()
        else:
            # Cria novo cliente
            novo_cliente = supabase.table("clientes").insert({
                "nome": nome.strip(),
                "endereco": endereco.strip(),
                "email": email_clean,
                "celular_whatsapp": celular_clean
            }).execute()

            if not novo_cliente.data:
                return "❌ Erro ao registrar novo cliente."
            cliente_id = novo_cliente.data[0]["id"]

        # 2. Cria a ordem de serviço
        nova_os = supabase.table("ordens_servico").insert({
            "cliente_id": cliente_id,
            "modelo_computador": modelo.strip(),
            "problema_relatado": problema.strip(),
            "status": "Aberto"
        }).execute()

        if nova_os.data:
            os_id = nova_os.data[0]["id"]
            return f"✅ Ordem de Serviço Nº {os_id} criada com sucesso!"
        else:
            return "❌ Erro ao criar a Ordem de Serviço."

    except Exception as e:
        return f"❌ Erro de comunicação com o banco de dados: {str(e)}"

# Interface Responsiva com Gradio Blocks
with gr.Blocks(title="TechFix Informática - Cadastro de OS", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🛠️ TechFix Informática")
    gr.Markdown("### Sistema de Abertura de Ordens de Serviço")

    with gr.Row():
        with gr.Column():
            gr.Markdown("#### Dados do Cliente")
            txt_nome = gr.Textbox(label="Nome Completo", placeholder="Ex: João da Silva")
            txt_email = gr.Textbox(label="E-mail", placeholder="exemplo@email.com")
            txt_celular = gr.Textbox(label="Celular/WhatsApp (Apenas números)", placeholder="61999998888")
            txt_endereco = gr.Textbox(label="Endereço Completo", placeholder="Rua 1, Quadra 2, Lote 3")

        with gr.Column():
            gr.Markdown("#### Dados do Equipamento")
            txt_modelo = gr.Textbox(label="Modelo do Computador/Notebook", placeholder="Ex: Dell Inspiron 15")
            txt_problema = gr.Textbox(label="Problema Apresentado", lines=4, placeholder="Descreva o defeito relatado pelo cliente...")

    out_mensagem = gr.Textbox(label="Status da Operação", interactive=False)

    with gr.Row():
        btn_limpar = gr.Button("🧹 Limpar Campos", variant="secondary")
        btn_enviar = gr.Button("🚀 Cadastrar OS", variant="primary")

    btn_enviar.click(
        fn=cadastrar_os,
        inputs=[txt_nome, txt_endereco, txt_email, txt_celular, txt_modelo, txt_problema],
        outputs=[out_mensagem]
    )

    btn_limpar.click(
        fn=lambda: ("", "", "", "", "", "", ""),
        inputs=[],
        outputs=[txt_nome, txt_endereco, txt_email, txt_celular, txt_modelo, txt_problema, out_mensagem]
    )

if __name__ == "__main__":
    # share=True gera um link público temporário para testes no celular
    app.launch(share=True)