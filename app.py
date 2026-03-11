import streamlit as st
import pandas as pd
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials
import json

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILO GLOBAL
# ==========================================
# Centralize a aplicação com um fundo escuro e tipografia moderna.
st.set_page_config(
    page_title="Ilton Fidelidade Digital",
    page_icon="✂️",
    layout="centered",
)

# Carrega fontes e ajusta cores para uma experiência mais agradável em dispositivos móveis.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    * { box-sizing: border-box; }
    
    /* Remover cabeçalho e rodapé padrão do Streamlit */
    header, footer { display: none !important; }
    
    /* Configuração geral de fontes e cores */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
        font-family: 'Montserrat', sans-serif;
    }

    h1 {
        color: #D4AF37;
        text-align: center;
        font-weight: 700;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    h4 {
        color: #C0C0C0;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 1rem;
    }

    /* Estilização de botões primários e secundários */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(45deg, #ff7e5f, #feb47b);
        border: none;
        color: #fff;
        font-weight: 700;
        border-radius: 8px;
        padding: 14px 0;
        width: 100%;
        box-shadow: 0 4px 12px rgba(255, 126, 95, 0.4);
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: transform 0.2s ease;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        transform: scale(1.03);
    }

    div[data-testid="stButton"] button[kind="secondary"] {
        background-color: #1A1A1A;
        color: #AAAAAA;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 12px 0;
        width: 100%;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 1px;
    }

    /* Campos de entrada */
    input, textarea, select {
        background-color: #1a1c24 !important;
        border: 1px solid #444 !important;
        color: #FAFAFA !important;
        border-radius: 6px !important;
        padding: 10px !important;
        width: 100% !important;
    }

    /* Tabelas */
    table {
        background-color: #1a1c24 !important;
        color: #FAFAFA !important;
        width: 100% !important;
        border-radius: 8px;
    }
    thead tr th {
        background-color: #2b7cff !important;
        color: white !important;
    }

    /* Área de botões principais alinhados responsivamente */
    .main-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
        margin: 2rem 0;
    }
    @media (max-width: 768px) {
        .main-buttons {
            flex-direction: column;
        }
    }

    /* Rodapé personalizado */
    .rodape-ufo {
        margin-top: 3rem;
        text-align: center;
        color: #444;
        font-size: 0.65rem;
        border-top: 1px solid #1A1A1A;
        padding: 0.8rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# 2. CONEXÃO COM GOOGLE SHEETS (VIA CREDENCIAIS)
# ==========================================
# Define escopos de acesso para planilha e drive.
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Tenta carregar as credenciais do arquivo de segredos do Streamlit ou dispara erro amigável.
try:
    cred_dict = json.loads(st.secrets["gcp_credentials"])
    # Ajusta formatação da chave privada
    cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
    credentials = Credentials.from_service_account_info(cred_dict, scopes=scopes)
    gc = gspread.authorize(credentials)
    planilha = gc.open("Barbearia_Fidelidade").sheet1
except Exception as e:
    st.error(f"⚠️ Erro ao conectar ao Google Sheets: {e}")
    st.stop()

# Funções auxiliares para lidar com registros
def get_all_clients():
    """Retorna todos os registros da planilha ou lista vazia."""
    try:
        return planilha.get_all_records()
    except Exception:
        return []

def find_client(telefone: str):
    """Localiza um cliente pelo telefone. Retorna (registro, linha)."""
    registros = get_all_clients()
    for idx, reg in enumerate(registros):
        if str(reg.get("Telefone", "")).strip() == str(telefone).strip():
            # +2 pois a primeira linha é cabeçalho e enumerate começa em 0
            return reg, idx + 2
    return None, None

def add_client(telefone: str, nome: str, email: str) -> None:
    """Insere um novo cliente na segunda linha da planilha."""
    planilha.insert_row([str(telefone), str(nome), str(email), 0], 2)

def update_points(linha: int, pontos: int) -> None:
    """Atualiza a coluna de pontos de um registro específico."""
    planilha.update_cell(linha, 4, int(pontos))

# ==========================================
# 3. NAVEGAÇÃO ENTRE PÁGINAS
# ==========================================
if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "inicio"

def mudar_pagina(nova_pagina: str) -> None:
    st.session_state["pagina_atual"] = nova_pagina

# ==========================================
# 4. COMPONENTES DE INTERFACE
# ==========================================
def exibir_logo():
    """Exibe o logo centralizado se estiver disponível."""
    try:
        st.image("logo.png", use_container_width=True)
    except Exception:
        pass

def rodape():
    """Exibe o rodapé personalizado."""
    st.markdown(
        """
        <div class="rodape-ufo">
            Desenvolvido por UFO Digital Agency<br>
            Ilton Cabeleireiro - +55 35 8702‑2576
        </div>
        """,
        unsafe_allow_html=True,
    )

# ==========================================
# 5. PÁGINAS
# ==========================================
def pagina_inicio():
    """Tela inicial com seleção de acesso."""
    exibir_logo()
    st.title("Cartão Fidelidade")
    st.markdown("<h4>Selecione seu acesso:</h4>", unsafe_allow_html=True)

    # Botões principais organizados responsivamente
    col_cli, col_barb = st.columns(2)
    with col_cli:
        if st.button("💇‍♂️ Área do Cliente", type="primary"):
            mudar_pagina("cliente")
            st.experimental_rerun()
    with col_barb:
        if st.button("🔒 Área Restrita", type="primary"):
            mudar_pagina("barbeiro")
            st.experimental_rerun()

    rodape()

def pagina_cliente():
    """Tela para consulta de pontos e cadastro de novos clientes."""
    # Botão de voltar
    col_voltar, _ = st.columns([1, 3])
    with col_voltar:
        if st.button("⬅️ Voltar", type="secondary"):
            mudar_pagina("inicio")
            st.experimental_rerun()

    aba_consulta, aba_cadastro = st.tabs(["🔍 Meus pontos", "📝 Cadastrar"])

    # Aba de consulta de pontos
    with aba_consulta:
        st.divider()
        telefone_busca = st.text_input(
            "Seu WhatsApp (somente números):",
            placeholder="Ex.: 35987654321",
            key="busca_cli",
        )
        if st.button("Buscar meus pontos", type="primary"):
            if telefone_busca.strip():
                cliente, linha = find_client(telefone_busca)
                if cliente:
                    nome = cliente.get("Nome", "")
                    pontos = int(cliente.get("Pontos", 0))
                    st.success(f"Olá, {nome}!")
                    st.info(f"Você tem **{pontos} ponto(s)** de 10.")
                    progresso = min(pontos / 10, 1.0)
                    st.progress(progresso)
                    if pontos >= 10:
                        st.balloons()
                        st.warning("🎉 Você completou seu cartão! Próximo corte é grátis!")
                else:
                    st.error("Número não encontrado.")
            else:
                st.warning("Informe o seu número para buscar.")

    # Aba de cadastro de novo cliente
    with aba_cadastro:
        st.divider()
        novo_nome = st.text_input("Nome:", key="novo_nome")
        novo_telefone = st.text_input(
            "WhatsApp (com DDD):",
            placeholder="Ex.: 35987654321",
            key="novo_telefone",
        )
        novo_email = st.text_input("E-mail:", key="novo_email")
        if st.button("Criar Cartão", type="primary"):
            if all([novo_nome.strip(), novo_telefone.strip(), novo_email.strip()]):
                cliente_existente, _ = find_client(novo_telefone)
                if cliente_existente:
                    st.error("Número já cadastrado.")
                else:
                    add_client(novo_telefone, novo_nome, novo_email)
                    st.success(f"{novo_nome}! Cadastro realizado com sucesso.")
                    st.balloons()
            else:
                st.warning("Preencha todos os campos para continuar.")

    rodape()

def pagina_barbeiro():
    """Tela restrita para o barbeiro gerenciar pontos e clientes."""
    # Voltar e sair
    col_voltar, col_sair = st.columns([1, 1])
    with col_voltar:
        if st.button("⬅️ Voltar", type="secondary"):
            mudar_pagina("inicio")
            st.experimental_rerun()

    # Controle de autenticação
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        senha = st.text_input("Senha de acesso:", type="password")
        if st.button("Entrar", type="primary"):
            if senha == "barba123":
                st.session_state["autenticado"] = True
                st.experimental_rerun()
            else:
                st.error("Senha incorreta!")
        rodape()
        return

    # Se autenticado, mostra botão de sair
    with col_sair:
        if st.button("Sair (Logout)", type="secondary"):
            st.session_state["autenticado"] = False
            st.experimental_rerun()

    st.divider()
    acao = st.selectbox(
        "O que deseja fazer?",
        ["Gerenciar Pontos", "Editar/Excluir", "Ver Todos"],
    )

    # --- Gerenciar Pontos ---
    if acao == "Gerenciar Pontos":
        registros = get_all_clients()
        opcoes = [""] + [f"{reg['Nome']} - {reg['Telefone']}" for reg in registros]
        cliente_sel = st.selectbox("Selecionar cliente:", opcoes)
        if cliente_sel != "":
            telefone_cli = cliente_sel.split(" - ")[-1]
            cliente, linha = find_client(telefone_cli)
            if cliente:
                nome_cli = cliente.get("Nome", "")
                pontos_cli = int(cliente.get("Pontos", 0))
                st.markdown(f"**{nome_cli}** | ⭐ **{pontos_cli}/10 Pontos**")
                col_add, col_reset = st.columns(2)
                with col_add:
                    if st.button("➕ 1 Ponto", type="primary"):
                        novos_pontos = pontos_cli + 1
                        update_points(linha, novos_pontos)
                        st.success(f"Total de pontos: {novos_pontos}")
                        # Monta mensagem de WhatsApp
                        if novos_pontos < 10:
                            msg = (
                                f"Fala {nome_cli}, beleza? Você ganhou +1 ponto no Cartão Fidelidade! ✂️\n\n"
                                f"Faltam apenas {10 - novos_pontos} para o corte GRÁTIS!"
                            )
                        else:
                            msg = (
                                f"Parabéns {nome_cli}! 🎉 Você completou 10 pontos! Próximo corte é GRÁTIS! ✂️"
                            )
                        msg_encoded = urllib.parse.quote(msg)
                        st.markdown(
                            f'<a href="https://wa.me/55{telefone_cli}?text={msg_encoded}" '
                            f'target="_blank" class="btn-zap">📱 Avisar no Whats</a>',
                            unsafe_allow_html=True,
                        )
                with col_reset:
                    if st.button("🔄 Zerar", type="secondary"):
                        update_points(linha, 0)
                        st.success("Pontos zerados.")
                        st.experimental_rerun()

    # --- Editar / Excluir cliente ---
    elif acao == "Editar/Excluir":
        registros = get_all_clients()
        opcoes = [""] + [f"{reg['Nome']} - {reg['Telefone']}" for reg in registros]
        cliente_sel = st.selectbox("Cliente:", opcoes)
        if cliente_sel != "":
            telefone_cli = cliente_sel.split(" - ")[-1]
            cliente, linha = find_client(telefone_cli)
            if cliente:
                novo_nome = st.text_input("Nome:", value=cliente.get("Nome", ""))
                novo_telefone = st.text_input("WhatsApp:", value=cliente.get("Telefone", ""))
                novo_email = st.text_input("E‑mail:", value=cliente.get("Email", ""))
                col_save, col_delete = st.columns(2)
                with col_save:
                    if st.button("💾 Salvar", type="primary"):
                        # Atualiza individualmente cada campo
                        planilha.update_cell(linha, 1, str(novo_telefone))
                        planilha.update_cell(linha, 2, str(novo_nome))
                        planilha.update_cell(linha, 3, str(novo_email))
                        st.success("Registro atualizado com sucesso.")
                with col_delete:
                    if st.button("🗑️ Excluir", type="secondary"):
                        planilha.delete_rows(linha)
                        st.success("Registro excluído com sucesso.")
                        st.experimental_rerun()

    # --- Ver todos os clientes ---
    elif acao == "Ver Todos":
        registros = get_all_clients()
        if registros:
            st.table(pd.DataFrame(registros))
        else:
            st.info("Nenhum cliente cadastrado.")

    rodape()

# ==========================================
# 6. FLUXO PRINCIPAL
# ==========================================
def main():
    pagina = st.session_state.get("pagina_atual", "inicio")
    if pagina == "inicio":
        pagina_inicio()
    elif pagina == "cliente":
        pagina_cliente()
    elif pagina == "barbeiro":
        pagina_barbeiro()


if __name__ == "__main__":
    main()