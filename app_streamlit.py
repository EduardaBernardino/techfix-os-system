import streamlit as st
import pandas as pd
from supabase import create_client, Client

st.set_page_config(page_title="TechFix - Painel do Gerente", layout="wide", page_icon="💻")

# Conexão com Supabase usando st.secrets ou fallback para .env
@st.cache_resource
def init_supabase() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

    return create_client(url, key)

supabase = init_supabase()

st.title("💻 TechFix Informática - Painel Gerencial")

STATUS_OPCOES = ['Aberto', 'Em análise', 'Aguardando peça', 'Concluído', 'Entregue']

def carregar_dados():
    try:
        # Busca unindo ordens_servico e clientes
        res = supabase.table("ordens_servico").select(
            "id, modelo_computador, problema_relatado, status, data_abertura, data_atualizacao, cliente_id, clientes(nome, email, celular_whatsapp, endereco)"
        ).execute()

        if not res.data:
            return pd.DataFrame()

        flat_data = []
        for row in res.data:
            cliente = row.get("clientes") or {}
            flat_data.append({
                "OS": row["id"],
                "Cliente ID": row["cliente_id"],
                "Cliente": cliente.get("nome", "N/A"),
                "E-mail": cliente.get("email", "N/A"),
                "Celular": cliente.get("celular_whatsapp", "N/A"),
                "Endereço": cliente.get("endereco", "N/A"),
                "Modelo": row["modelo_computador"],
                "Problema": row["problema_relatado"],
                "Status": row["status"],
                "Data Abertura": row["data_abertura"],
                "Data Atualização": row["data_atualizacao"]
            })
        return pd.DataFrame(flat_data)
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame()

df = carregar_dados()

# Abas de Navegação
tab_consultar, tab_cadastrar, tab_editar, tab_indicadores = st.tabs([
    "📋 Consultar OS", "➕ Cadastrar OS", "✏️ Editar/Excluir", "📊 Indicadores"
])

# --- ABA 1: CONSULTAR ---
with tab_consultar:
    st.subheader("Consultar e Filtrar Ordens de Serviço")

    st.sidebar.header("🔍 Filtros de Busca")
    filtro_busca = st.sidebar.text_input("Buscar por Nome ou E-mail")
    filtro_status = st.sidebar.multiselect("Filtrar por Status", options=STATUS_OPCOES, default=STATUS_OPCOES)

    df_filtrado = df.copy()

    if not df_filtrado.empty:
        if filtro_status:
            df_filtrado = df_filtrado[df_filtrado["Status"].isin(filtro_status)]

        if filtro_busca:
            busca = filtro_busca.lower()
            df_filtrado = df_filtrado[
                df_filtrado["Cliente"].str.lower().str.contains(busca) |
                df_filtrado["E-mail"].str.lower().str.contains(busca)
            ]

        st.dataframe(df_filtrado, use_container_width=True)

        # Bônus: Exportar CSV (+0,5)
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Exportar em CSV",
            data=csv,
            file_name="ordens_de_servico_techfix.csv",
            mime="text/csv"
        )
    else:
        st.info("Nenhuma ordem de serviço cadastrada.")

# --- ABA 2: CADASTRAR ---
with tab_cadastrar:
    st.subheader("Cadastrar Nova OS Manualmente")
    with st.form("form_novo_cadastro"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Cliente")
            email = st.text_input("E-mail")
            celular = st.text_input("Celular/WhatsApp")
            endereco = st.text_input("Endereço")
        with col2:
            modelo = st.text_input("Modelo do Computador")
            problema = st.text_area("Problema Relatado")
            status_inicial = st.selectbox("Status Inicial", STATUS_OPCOES, index=0)

        submitted = st.form_submit_button("Cadastrar OS")

        if submitted:
            if all([nome, email, celular, endereco, modelo, problema]):
                try:
                    # Verifica/Cria Cliente
                    res_c = supabase.table("clientes").select("id").eq("email", email.strip()).execute()
                    if res_c.data:
                        c_id = res_c.data[0]["id"]
                    else:
                        novo_c = supabase.table("clientes").insert({
                            "nome": nome.strip(), "email": email.strip(),
                            "celular_whatsapp": celular.strip(), "endereco": endereco.strip()
                        }).execute()
                        c_id = novo_c.data[0]["id"]

                    # Cria OS
                    supabase.table("ordens_servico").insert({
                        "cliente_id": c_id,
                        "modelo_computador": modelo.strip(),
                        "problema_relatado": problema.strip(),
                        "status": status_inicial
                    }).execute()

                    st.success("Ordem de serviço cadastrada com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao cadastrar: {e}")
            else:
                st.warning("Preencha todos os campos obrigatórios.")

# --- ABA 3: EDITAR / EXCLUIR ---
with tab_editar:
    st.subheader("Gerenciamento de Registros")
    if not df.empty:
        os_selecionada = st.selectbox("Selecione o Número da OS:", df["OS"].unique())

        dados_os = df[df["OS"] == os_selecionada].iloc[0]

        col_ed1, col_ed2 = st.columns(2)
        with col_ed1:
            st.markdown(f"**Cliente ID:** {dados_os['Cliente ID']}")
            novo_endereco = st.text_input("Endereço do Cliente", value=dados_os["Endereço"])
            novo_email = st.text_input("E-mail", value=dados_os["E-mail"])
            novo_celular = st.text_input("Celular/WhatsApp", value=dados_os["Celular"])
        with col_ed2:
            st.markdown(f"**Equipamento:** {dados_os['Modelo']}")
            idx_status = STATUS_OPCOES.index(dados_os["Status"]) if dados_os["Status"] in STATUS_OPCOES else 0
            novo_status = st.selectbox("Status da OS", STATUS_OPCOES, index=idx_status)
            novo_problema = st.text_area("Problema Relatado", value=dados_os["Problema"])

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("💾 Salvar Alterações"):
                try:
                    # Atualiza cliente
                    supabase.table("clientes").update({
                        "endereco": novo_endereco,
                        "email": novo_email,
                        "celular_whatsapp": novo_celular
                    }).eq("id", dados_os["Cliente ID"]).execute()

                    # Atualiza OS
                    supabase.table("ordens_servico").update({
                        "status": novo_status,
                        "problema_relatado": novo_problema
                    }).eq("id", os_selecionada).execute()

                    st.success("Dados atualizados com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao atualizar: {e}")

        with col_btn2:
            st.markdown("### Exclusão de Registros")
            confirmar = st.checkbox("Confirmo que desejo excluir esta OS.")
            if st.button("🗑️ Excluir OS", type="primary"):
                if confirmar:
                    try:
                        supabase.table("ordens_servico").delete().eq("id", os_selecionada).execute()
                        st.success(f"OS Nº {os_selecionada} removida!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Erro ao excluir: {e}")
                else:
                    st.warning("Marque a caixa de confirmação antes de excluir.")
    else:
        st.info("Sem dados disponíveis para edição.")

# --- ABA 4: INDICADORES ---
with tab_indicadores:
    st.subheader("Indicadores de Desempenho")
    if not df.empty:
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total de OS", len(df))
        col_m2.metric("OS Abertas", len(df[df["Status"] == "Aberto"]))
        col_m3.metric("OS Concluídas", len(df[df["Status"] == "Concluído"]))

        st.markdown("---")
        st.markdown("### Distribuição de OS por Status")
        status_counts = df["Status"].value_counts().reindex(STATUS_OPCOES, fill_value=0)
        st.bar_chart(status_counts)
    else:
        st.info("Nenhum dado disponível para exibir métricas.")