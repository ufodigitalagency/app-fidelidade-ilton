"""
Ilton Fidelidade Digital – Streamlit App
======================================

This application implements a customer loyalty program for a local
barbershop. Customers can check their points or register a new card,
while barbers can manage points, edit or delete client records and
view all registrations. The interface has been redesigned for a
modern, mobile-friendly experience. All functionality from the
original app remains intact.

Credentials Handling
--------------------

To connect with Google Sheets the app needs a service account. It
attempts to load these credentials from Streamlit's secrets manager.
It will first look for keys under `gcp_service_account` (used by the
original code) and then under `gcp_credentials` (our earlier naming).
If neither is found it falls back to a local `credenciais.json` file.

"""

from __future__ import annotations

import json
import urllib.parse
from typing import Optional, Tuple, List

import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials


# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION & GLOBAL STYLES
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="Ilton Fidelidade Digital",
    page_icon="✂️",
    layout="centered",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

    header, footer { visibility: hidden; height: 0; }

    .stApp {
        background-color: #0E1117;
        color: #E0E0E0;
        font-family: 'Montserrat', sans-serif;
    }
    h1 {
        color: #F9DC5C;
        text-align: center;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    p.lead {
        text-align: center;
        color: #A7A7A7;
        margin-top: 0;
        margin-bottom: 1.2rem;
    }

    .card {
        background: #1C2028;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
        margin-bottom: 1.5rem;
    }

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

    input, textarea, select {
        background-color: #2A2D36 !important;
        border: 1px solid #444 !important;
        color: #FFFFFF !important;
        border-radius: 5px !important;
        padding: 0.5rem !important;
    }

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

    @media (max-width: 640px) {
        .stColumns {
            flex-direction: column !important;
        }
    }

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
# 2. GOOGLE SHEETS CONNECTION
# -----------------------------------------------------------------------------

SCOPES: List[str] = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def load_credentials() -> Credentials:
    """Load service account credentials.

    Try to load credentials from Streamlit secrets. The app checks both
    `gcp_service_account` and `gcp_credentials` keys (to support
    different naming conventions). If neither exists, it attempts to
    read from a local `credenciais.json` file. If all methods fail,
    raise a RuntimeError.
    """
    cred_dict: dict
    for key in ("gcp_service_account", "gcp_credentials"):
        try:
            raw = st.secrets[key]  # type: ignore[arg-type]
            if isinstance(raw, dict):
                cred_dict = dict(raw)
            else:
                cred_dict = json.loads(raw)
            break
        except Exception:
            continue
    else:
        # Fallback to local file
        try:
            with open("credenciais.json", encoding="utf-8") as f:
                cred_dict = json.load(f)
        except Exception as exc:
            raise RuntimeError(
                "Credenciais não encontradas. Defina-as em 'gcp_service_account' ou 'gcp_credentials'"
                " no st.secrets ou forneça um arquivo credenciais.json." ) from exc

    if "private_key" in cred_dict and isinstance(cred_dict["private_key"], str):
        cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
    return Credentials.from_service_account_info(cred_dict, scopes=SCOPES)


def open_sheet() -> gspread.Worksheet:
    """Authorize and return the first worksheet of the loyalty sheet."""
    creds = load_credentials()
    client = gspread.authorize(creds)
    return client.open("Barbearia_Fidelidade").sheet1


try:
    PLANILHA = open_sheet()
except Exception as err:
    st.error(f"⚠️ Erro ao conectar ao Google Sheets: {err}")
    st.stop()


def get_all_clients() -> List[dict]:
    try:
        return PLANILHA.get_all_records()
    except Exception:
        return []


def find_client(phone: str) -> Tuple[Optional[dict], Optional[int]]:
    for idx, record in enumerate(get_all_clients()):
        if str(record.get("Telefone", "")).strip() == str(phone).strip():
            return record, idx + 2
    return None, None


def add_client(phone: str, name: str, email: str) -> None:
    PLANILHA.insert_row([str(phone), str(name), str(email), 0], 2)


def update_points(row: int, points: int) -> None:
    PLANILHA.update_cell(row, 4, int(points))


def update_client(row: int, phone: str, name: str, email: str) -> None:
    PLANILHA.update_cell(row, 1, str(phone))
    PLANILHA.update_cell(row, 2, str(name))
    PLANILHA.update_cell(row, 3, str(email))


def delete_client(row: int) -> None:
    PLANILHA.delete_rows(row)


# -----------------------------------------------------------------------------
# 3. NAVIGATION STATE
# -----------------------------------------------------------------------------

if "pagina_atual" not in st.session_state:
    st.session_state["pagina_atual"] = "inicio"


def mudar_pagina(nova: str) -> None:
    st.session_state["pagina_atual"] = nova


# -----------------------------------------------------------------------------
# 4. UI COMPONENTS
# -----------------------------------------------------------------------------

def exibir_logo() -> None:
    try:
        st.image("logo.png", use_container_width=True)
    except Exception:
        pass


def rodape() -> None:
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
# 5. PAGES
# -----------------------------------------------------------------------------

def pagina_inicio() -> None:
    exibir_logo()
    st.title("Cartão Fidelidade")
    st.markdown(
        "<p class='lead'>Bem-vindo! Escolha seu acesso abaixo.</p>",
        unsafe_allow_html=True,
    )
    col_cli, col_barb = st.columns(2, gap="medium")
    with col_cli:
        if st.button("💇‍♂️ Área do Cliente", type="primary"):
            mudar_pagina("cliente")
            st.experimental_rerun()
    with col_barb:
        if st.button("🔒 Área Restrita", type="primary"):
            mudar_pagina("barbeiro")
            st.experimental_rerun()
    rodape()


def pagina_cliente() -> None:
    back_col, _ = st.columns([1, 5])
    with back_col:
        if st.button("⬅️ Voltar", type="secondary"):
            mudar_pagina("inicio")
            st.experimental_rerun()

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
    col_back, col_logout = st.columns([1, 1])
    with col_back:
        if st.button("⬅️ Voltar", type="secondary", key="voltar_admin"):
            mudar_pagina("inicio")
            st.experimental_rerun()

    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

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

    with col_logout:
        if st.button("Sair", type="secondary", key="logout_admin"):
            st.session_state["autenticado"] = False
            st.experimental_rerun()

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
# 6. MAIN ROUTER
# -----------------------------------------------------------------------------

def main() -> None:
    pagina = st.session_state.get("pagina_atual", "inicio")
    if pagina == "inicio":
        pagina_inicio()
    elif pagina == "cliente":
        pagina_cliente()
    elif pagina == "barbeiro":
        pagina_barbeiro()
    else:
        pagina_inicio()


if __name__ == "__main__":
    main()
