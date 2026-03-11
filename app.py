"""
Ilton Fidelidade Digital – Modernised Streamlit App
===================================================

This application implements a customer loyalty program for a local barbershop.
Customers can register or check their points balance, while the barber can
award points, reset balances, edit or delete records, and view all
participants. The design has been overhauled for a responsive, mobile-first
experience while preserving all original functionality.

Key features:

* Responsive layout: components stack gracefully on narrow screens and
  align neatly in two columns on wider displays.
* Unified dark theme with accent colours that highlight interactive
  elements.
* Custom cards group related inputs and outputs for a cleaner look.
* Graceful fallback when credentials are not provided via `st.secrets` by
  loading from a local `credenciais.json` file.
* Modular page functions separated into customer and barber sections.

To deploy this app on Streamlit Cloud, make sure to add your Google service
account JSON either to the secrets manager (under the key
`gcp_credentials`) or provide a `credenciais.json` file in the same
directory as this script.
"""

from __future__ import annotations

import json
import urllib.parse
from typing import List, Tuple, Optional

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & GLOBAL STYLES
# -----------------------------------------------------------------------------

# Configure page settings. A centred layout makes the app look more like a
# dedicated mobile app on large screens while still allowing full width on
# smaller devices.
st.set_page_config(
    page_title="Ilton Fidelidade Digital",
    page_icon="✂️",
    layout="centered",
)

# Custom CSS to apply a cohesive dark theme and style components. The
# responsive rules ensure the button columns stack on narrow viewports. This
# style block also defines a reusable `.card` class for grouping inputs and
# outputs.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

    /* Hide Streamlit default header and footer */
    header, footer { visibility: hidden; height: 0; }

    /* Global styles */
    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
        font-family: 'Montserrat', sans-serif;
    }
    h1 {
        color: #F9DC5C;
        text-align: center;
        margin-bottom: 0.4rem;
        font-weight: 700;
    }
    p.lead {
        text-align: center;
        color: #A7A7A7;
        margin-top: 0;
        margin-bottom: 1.2rem;
    }

    /* Card container */
    .card {
        background: #1C2028;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
        margin-bottom: 1.5rem;
    }

    /* Buttons */
    div[data-testid="stButton"] > button {
        font-weight: 600;
        text-transform: uppercase;
        border-radius: 6px;
        width: 100%;
        padding: 0.6rem 1rem;
        margin-top: 0.5rem;
    }
    div[data-testid="stButton"] > button[kind="primary"] {
        background: linear-gradient(45deg, #ff7e5f, #feb47b);
        color: white;
        border: none;
        box-shadow: 0 4px 12px rgba(255, 126, 95, 0.3);
    }
    div[data-testid="stButton"] > button[kind="primary"]:hover {
        opacity: 0.9;
    }
    div[data-testid="stButton"] > button[kind="secondary"] {
        background: #2A2D36;
        color: #CCCCCC;
        border: 1px solid #444;
    }
    div[data-testid="stButton"] > button[kind="secondary"]:hover {
        background: #383C47;
    }

    /* Inputs */
    input, textarea, select {
        background-color: #2A2D36 !important;
        border: 1px solid #444 !important;
        color: #FFFFFF !important;
        border-radius: 5px !important;
        padding: 0.5rem !important;
    }

    /* Tables */
    table {
        width: 100% !important;
        border-collapse: collapse;
        background-color: #1C2028 !important;
        color: #E0E0E0 !important;
    }
    thead tr th {
        background-color: #2b7cff !important;
        color: white !important;
        padding: 0.5rem 0.75rem;
    }
    tbody tr td {
        padding: 0.45rem 0.75rem;
    }

    /* WhatsApp link button */
    a.btn-zap {
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.5rem 1rem;
        background: #25D366;
        color: white;
        border-radius: 5px;
        font-weight: 600;
        text-decoration: none;
    }
    a.btn-zap:hover {
        opacity: 0.9;
    }

    /* Responsive columns: stack on mobile */
    @media (max-width: 640px) {
        .stColumns {
            flex-direction: column !important;
        }
    }

    /* Footer styling */
    .rodape-ufo {
        text-align: center;
        font-size: 0.75rem;
        color: #666;
        margin-top: 2.5rem;
        border-top: 1px solid #1A1A1A;
        padding-top: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# 2. GOOGLE SHEETS CONNECTION HELPERS
# -----------------------------------------------------------------------------

SCOPES: List[str] = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def load_credentials() -> Credentials:
    """Load Google service account credentials.

    First attempt to load from Streamlit secrets under the key
    `gcp_credentials`. If that fails, fall back to reading the local
    `credenciais.json` file.
    """
    cred_dict: dict
    try:
        # st.secrets is provided by Streamlit when deployed. It may throw
        # KeyError if the key is not present.
        raw = st.secrets["gcp_credentials"]  # type: ignore[arg-type]
        cred_dict = json.loads(raw)
    except Exception:
        # Attempt to read a local file instead.
        try:
            with open("credenciais.json", encoding="utf-8") as f:
                cred_dict = json.load(f)
        except Exception as exc:
            raise RuntimeError(
                "Credenciais não encontradas. Verifique se o arquivo "
                "credenciais.json está presente ou se você configurou "
                "gcp_credentials em st.secrets." ) from exc

    # The private_key stored in JSON may contain literal '\n' that need
    # conversion to actual newlines.
    if "private_key" in cred_dict:
        cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
    return Credentials.from_service_account_info(cred_dict, scopes=SCOPES)


def open_sheet() -> gspread.Worksheet:
    """Authorize and return the first worksheet of the loyalty spreadsheet."""
    creds = load_credentials()
    client = gspread.authorize(creds)
    # Expect the spreadsheet to be named exactly as below. Change if needed.
    return client.open("Barbearia_Fidelidade").sheet1


try:
    PLANILHA = open_sheet()
except Exception as err:
    st.error(f"⚠️ Erro ao conectar ao Google Sheets: {err}")
    st.stop()


def get_all_clients() -> List[dict]:
    """Return all client records from the sheet or an empty list on error."""
    try:
        return PLANILHA.get_all_records()
    except Exception:
        return []


def find_client(phone: str) -> Tuple[Optional[dict], Optional[int]]:
    """Find a client by phone number. Returns (record, row) or (None, None)."""
    for idx, record in enumerate(get_all_clients()):
        if str(record.get("Telefone", "")).strip() == str(phone).strip():
            return record, idx + 2  # +2 to account for header and 0-index
    return None, None


def add_client(phone: str, name: str, email: str) -> None:
    """Add a new client to the sheet below the header."""
    PLANILHA.insert_row([str(phone), str(name), str(email), 0], 2)


def update_points(row: int, points: int) -> None:
    """Update the points value for a client at the given row."""
    PLANILHA.update_cell(row, 4, int(points))


def update_client(row: int, phone: str, name: str, email: str) -> None:
    """Update client information for the given row (phone, name, email)."""
    PLANILHA.update_cell(row, 1, str(phone))
    PLANILHA.update_cell(row, 2, str(name))
    PLANILHA.update_cell(row, 3, str(email))


def delete_client(row: int) -> None:
    """Delete a client record entirely."""
    PLANILHA.delete_rows(row)


# -----------------------------------------------------------------------------
# 3. NAVIGATION MANAGEMENT
# -----------------------------------------------------------------------------

if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "inicio"


def mudar_pagina(nova: str) -> None:
    """Switch pages by updating session state and forcing a rerun."""
    st.session_state["pagina_atual"] = nova


# -----------------------------------------------------------------------------
# 4. UI COMPONENTS
# -----------------------------------------------------------------------------

def exibir_logo() -> None:
    """Display the barbershop logo at full container width."""
    try:
        st.image("logo.png", use_container_width=True)
    except Exception:
        pass


def rodape() -> None:
    """Show a footer with credit information."""
    st.markdown(
        """
        <div class="rodape-ufo">
            Desenvolvido por UFO Digital Agency<br>
            Ilton Cabeleireiro – +55 35 8702‑2576
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# 5. PAGE DEFINITIONS
# -----------------------------------------------------------------------------

def pagina_inicio() -> None:
    """Landing page offering client and barber sections."""
    exibir_logo()
    st.title("Cartão Fidelidade")
    st.markdown(
        "<p class='lead'>Bem-vindo! Escolha seu acesso abaixo.</p>",
        unsafe_allow_html=True,
    )
    col_cliente, col_barbeiro = st.columns(2, gap="medium")
    with col_cliente:
        if st.button("💇‍♂️ Área do Cliente", type="primary"):
            mudar_pagina("cliente")
            st.experimental_rerun()
    with col_barbeiro:
        if st.button("🔒 Área Restrita", type="primary"):
            mudar_pagina("barbeiro")
            st.experimental_rerun()
    rodape()


def pagina_cliente() -> None:
    """Customer area: check points or register a new card."""
    # Back button
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("⬅️ Voltar", type="secondary"):
            mudar_pagina("inicio")
            st.experimental_rerun()

    # Tabs for checking points and registering
    aba_consulta, aba_cadastro = st.tabs(["🔍 Meus Pontos", "📝 Cadastrar"])

    with aba_consulta:
        st.divider()
        with st.container():
            st.subheader("Consultar Pontos")
            telefone_busca = st.text_input(
                "Seu WhatsApp (somente números)",
                placeholder="Ex.: 35987654321",
                key="busca_cli",
            )
            if st.button("Buscar", key="buscar_pontos", type="primary"):
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
                    st.warning("Informe seu número para buscar.")

    with aba_cadastro:
        st.divider()
        with st.container():
            st.subheader("Cadastrar Novo Cliente")
            novo_nome = st.text_input("Nome", key="novo_nome")
            novo_telefone = st.text_input(
                "WhatsApp (com DDD)",
                placeholder="Ex.: 35987654321",
                key="novo_telefone",
            )
            novo_email = st.text_input("E-mail", key="novo_email")
            if st.button("Criar Cartão", type="primary", key="criar_cartao"):
                if all([novo_nome.strip(), novo_telefone.strip(), novo_email.strip()]):
                    cliente_existente, _ = find_client(novo_telefone)
                    if cliente_existente:
                        st.error("Este número já está cadastrado.")
                    else:
                        add_client(novo_telefone, novo_nome, novo_email)
                        st.success(f"{novo_nome}, seu cadastro foi realizado com sucesso!")
                        st.balloons()
                else:
                    st.warning("Preencha todos os campos para continuar.")

    rodape()


def pagina_barbeiro() -> None:
    """Restricted area for barbers to manage points and clients."""
    col_back, col_logout = st.columns([1, 1])
    with col_back:
        if st.button("⬅️ Voltar", type="secondary", key="voltar_admin"):
            mudar_pagina("inicio")
            st.experimental_rerun()

    # Authentication state
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    # If not authenticated, show login form
    if not st.session_state["autenticado"]:
        senha = st.text_input("Senha de acesso", type="password")
        if st.button("Entrar", type="primary", key="login_admin"):
            if senha == "barba123":
                st.session_state["autenticado"] = True
                st.experimental_rerun()
            else:
                st.error("Senha incorreta!")
        rodape()
        return

    # If authenticated, show logout button in the top right
    with col_logout:
        if st.button("Sair", type="secondary", key="logout_admin"):
            st.session_state["autenticado"] = False
            st.experimental_rerun()

    # Main admin interface
    st.divider()
    acao = st.selectbox(
        "O que deseja fazer?",
        ["Gerenciar Pontos", "Editar/Excluir", "Ver Todos"],
    )

    if acao == "Gerenciar Pontos":
        registros = get_all_clients()
        opcoes = [""] + [f"{reg['Nome']} - {reg['Telefone']}" for reg in registros]
        cliente_sel = st.selectbox("Selecionar cliente", opcoes, key="sel_cliente_pontos")
        if cliente_sel:
            telefone_cli = cliente_sel.split(" - ")[-1]
            cliente, linha = find_client(telefone_cli)
            if cliente and linha:
                nome_cli = cliente.get("Nome", "")
                pontos_cli = int(cliente.get("Pontos", 0))
                st.markdown(f"**{nome_cli}** | ⭐ **{pontos_cli}/10 Pontos**")
                col_add, col_reset = st.columns(2, gap="medium")
                with col_add:
                    if st.button("➕ 1 Ponto", type="primary", key="add_point"):
                        novos_pontos = pontos_cli + 1
                        update_points(linha, novos_pontos)
                        st.success(f"Total de pontos: {novos_pontos}")
                        # Compose WhatsApp message
                        if novos_pontos < 10:
                            mensagem = (
                                f"Fala {nome_cli}, tudo bem? Você ganhou +1 ponto no Cartão Fidelidade! ✂️\n\n"
                                f"Faltam apenas {10 - novos_pontos} para o corte GRÁTIS!"
                            )
                        else:
                            mensagem = (
                                f"Parabéns {nome_cli}! 🎉 Você completou 10 pontos! Próximo corte é GRÁTIS! ✂️"
                            )
                        msg_encoded = urllib.parse.quote(mensagem)
                        st.markdown(
                            f'<a href="https://wa.me/55{telefone_cli}?text={msg_encoded}" target="_blank" class="btn-zap">📱 Avisar no Whats</a>',
                            unsafe_allow_html=True,
                        )
                with col_reset:
                    if st.button("🔄 Zerar", type="secondary", key="reset_points"):
                        update_points(linha, 0)
                        st.success("Pontos zerados.")
                        st.experimental_rerun()

    elif acao == "Editar/Excluir":
        registros = get_all_clients()
        opcoes = [""] + [f"{reg['Nome']} - {reg['Telefone']}" for reg in registros]
        cliente_sel = st.selectbox("Cliente", opcoes, key="sel_cliente_edit")
        if cliente_sel:
            telefone_cli = cliente_sel.split(" - ")[-1]
            cliente, linha = find_client(telefone_cli)
            if cliente and linha:
                novo_nome = st.text_input("Nome", value=cliente.get("Nome", ""), key="edit_nome")
                novo_telefone = st.text_input("WhatsApp", value=cliente.get("Telefone", ""), key="edit_fone")
                novo_email = st.text_input("E-mail", value=cliente.get("Email", ""), key="edit_email")
                col_save, col_delete = st.columns(2, gap="medium")
                with col_save:
                    if st.button("💾 Salvar", type="primary", key="save_edit"):
                        update_client(linha, novo_telefone, novo_nome, novo_email)
                        st.success("Registro atualizado com sucesso.")
                with col_delete:
                    if st.button("🗑️ Excluir", type="secondary", key="delete_record"):
                        delete_client(linha)
                        st.success("Registro excluído com sucesso.")
                        st.experimental_rerun()

    elif acao == "Ver Todos":
        registros = get_all_clients()
        if registros:
            df = pd.DataFrame(registros)
            st.table(df)
        else:
            st.info("Nenhum cliente cadastrado.")

    rodape()


# -----------------------------------------------------------------------------
# 6. ROUTER
# -----------------------------------------------------------------------------

def main() -> None:
    """Entry point routing between pages based on session state."""
    pagina = st.session_state.get("pagina_atual", "inicio")
    if pagina == "inicio":
        pagina_inicio()
    elif pagina == "cliente":
        pagina_cliente()
    elif pagina == "barbeiro":
        pagina_barbeiro()
    else:
        # Fallback to home if page name is unexpected
        pagina_inicio()


if __name__ == "__main__":
    main()
