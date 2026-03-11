import streamlit as st
import pandas as pd
from PIL import Image
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E CSS
# ==========================================
st.set_page_config(page_title="Ilton Fidelidade Digital", page_icon="✂️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap');
    [data-testid="collapsedControl"] {display: none;}
    [data-testid="stToolbar"] {visibility: hidden;}
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    h1 { font-family: 'Montserrat', sans-serif !important; color: #D4AF37 !important; text-align: center; text-transform: uppercase; letter-spacing: 2px; margin-top: -30px; font-size: 2.8rem !important; }
    h2, h3 { color: #C0C0C0 !important; }
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 51, 51, 0.6); } 70% { box-shadow: 0 0 0 12px rgba(255, 51, 51, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 51, 51, 0); } }
    div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(45deg, #ff1a1a, #e60000) !important; color: white !important; border-radius: 8px !important; border: none !important; font-weight: 800 !important; text-transform: uppercase; letter-spacing: 1px; animation: pulse 2s infinite; transition: transform 0.2s ease-in-out !important; padding: 10px !important; }
    div[data-testid="stButton"] button[kind="primary"]:hover { transform: scale(1.03); background: linear-gradient(45deg, #ff4d4d, #ff0000) !important; }
    div[data-testid="stButton"] button[kind="secondary"] { background-color: #2A2A2A !important; color: #AAAAAA !important; border: 1px solid #444 !important; border-radius: 8px !important; font-weight: bold !important; text-transform: uppercase; transition: 0.3s !important; }
    div[data-testid="stButton"] button[kind="secondary"]:hover { background-color: #333 !important; color: #FFF !important; border-color: #666 !important; }
    .btn-zap { background-color: #25D366 !important; color: white !important; border-radius: 8px; border: none; padding: 10px; font-weight: bold; width: 100%; text-transform: uppercase; text-align: center; display: block; text-decoration: none; margin-top: 15px; transition: 0.3s; }
    .btn-zap:hover { background-color: #1ebe57 !important; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div { background-color: #1a1c24 !important; color: white !important; border: 1px solid #444 !important; transition: 0.3s; }
    .stTextInput>div>div>input:focus { border-color: #2b7cff !important; box-shadow: 0 0 8px rgba(255, 51, 51, 0.6) !important; }
    table { color: #FAFAFA !important; background-color: #1a1c24 !important; border-radius: 8px; width: 100%; }
    thead tr th { background-color: #2b7cff !important; color: white !important; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #111; color: #666; text-align: center; padding: 12px; font-size: 0.75rem; border-top: 1px solid #222; z-index: 999; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXÃO COM GOOGLE SHEETS E FUNÇÕES
# ==========================================
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    credentials = Credentials.from_service_account_file("credenciais.json", scopes=scopes)
    gc = gspread.authorize(credentials)
    planilha = gc.open("Barbearia_Fidelidade").sheet1
except Exception as e:
    st.error("⚠️ Erro crítico: Não foi possível conectar ao Google Sheets. Verifique o arquivo credenciais.json.")
    st.stop()

def get_all_clients():
    try:
        return planilha.get_all_records()
    except:
        return []

def find_client(telefone):
    registros = get_all_clients()
    for i, reg in enumerate(registros):
        if str(reg.get('Telefone', '')).strip() == str(telefone).strip():
            return reg, i + 2 # +2 porque a linha 1 é o cabeçalho e o índice começa em 0
    return None, None

def add_client(telefone, nome, email):
    planilha.append_row([str(telefone), str(nome), str(email), 0])

def update_points(linha, pontos):
    planilha.update_cell(linha, 4, int(pontos)) # Coluna 4 é a coluna de Pontos

# NAVEGAÇÃO
if 'pagina_atual' not in st.session_state:
    st.session_state['pagina_atual'] = 'inicio'

def mudar_pagina(nova_pagina):
    st.session_state['pagina_atual'] = nova_pagina

# ==========================================
# 3. INTERFACE GERAL (LOGO)
# ==========================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    try:
        st.image("logo.png", use_container_width=True)
    except FileNotFoundError:
        pass

st.title("Cartão Fidelidade")

# ==========================================
# TELA 1: INÍCIO 
# ==========================================
if st.session_state['pagina_atual'] == 'inicio':
    st.write("<br><h4 style='text-align: center; color: #C0C0C0;'>Selecione seu acesso:</h4><br>", unsafe_allow_html=True)
    col_vazia_esq, col_btn_cli, col_btn_barb, col_vazia_dir = st.columns([1, 3, 3, 1])
    
    with col_btn_cli:
        if st.button("💇‍♂️ Área do Cliente", type="primary", use_container_width=True):
            mudar_pagina('cliente')
            st.rerun()
    with col_btn_barb:
        if st.button("🔒 RESTRITO", type="primary", use_container_width=True):
            mudar_pagina('barbeiro')
            st.rerun()

# ==========================================
# TELA 2: ÁREA DO CLIENTE
# ==========================================
elif st.session_state['pagina_atual'] == 'cliente':
    if st.button("⬅️ Voltar ao Início", type="secondary"):
        mudar_pagina('inicio')
        st.rerun()
        
    aba1, aba2 = st.tabs(["🔍 Ver meus pontos", "📝 Quero me cadastrar"])
    
    with aba1:
        st.subheader("Já é cliente?")
        telefone_busca = st.text_input("Digite seu WhatsApp (ex: 35999999999):", key="busca_cli")
        
        if st.button("Buscar meus pontos", type="primary"):
            if telefone_busca:
                cliente, _ = find_client(telefone_busca)
                
                if cliente:
                    nome = cliente['Nome']
                    pontos = int(cliente['Pontos'])
                    st.success(f"Olá, {nome}!")
                    st.info(f"Você tem **{pontos} ponto(s)** de 10.")
                    
                    progresso = pontos / 10 if pontos <= 10 else 1.0
                    st.progress(progresso)
                    
                    if pontos >= 10:
                        st.balloons()
                        st.warning("🎉 Parabéns! Você completou o cartão. Seu próximo corte é GRÁTIS!")
                else:
                    st.error("Número não encontrado. Faça seu cadastro na aba ao lado!")
            else:
                st.warning("Por favor, digite seu número.")

    with aba2:
        st.subheader("Novo por aqui?")
        st.write("Faça seu cadastro rápido e comece a juntar pontos!")
        novo_nome = st.text_input("Qual o seu nome?")
        novo_telefone = st.text_input("Seu WhatsApp (apenas números, com DDD):", key="cad_cli")
        novo_email = st.text_input("Seu E-mail:") 
        
        if st.button("Criar meu Cartão Fidelidade", type="primary"):
            if novo_nome and novo_telefone and novo_email:
                cliente_existente, _ = find_client(novo_telefone)
                if cliente_existente:
                    st.error("Opa! Esse número de WhatsApp já está cadastrado. Vá na aba 'Ver meus pontos'.")
                else:
                    add_client(novo_telefone, novo_nome, novo_email)
                    st.success(f"Show, {novo_nome}! Seu cadastro foi feito. Você já pode avisar o barbeiro no seu próximo corte!")
                    st.balloons()
            else:
                st.warning("Preencha todos os campos para criar o cartão.")

# ==========================================
# TELA 3: ÁREA DO BARBEIRO
# ==========================================
elif st.session_state['pagina_atual'] == 'barbeiro':
    col_voltar, col_sair = st.columns([1, 1])
    with col_voltar:
        if st.button("⬅️ Voltar", type="secondary"):
            mudar_pagina('inicio')
            st.rerun()
            
    st.subheader("Painel de Controle")
    
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    if not st.session_state['autenticado']:
        senha = st.text_input("Senha de Acesso", type="password")
        if st.button("Entrar no Painel", type="primary"):
            if senha == "barba123":
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
                
    if st.session_state['autenticado']:
        with col_sair:
            if st.button("Sair (Logout)", type="secondary"):
                st.session_state['autenticado'] = False
                st.rerun()
                
        acao = st.radio("Selecione a ação:", ["Gerenciar Pontos", "Ver Todos os Clientes"], horizontal=True)

        if acao == "Gerenciar Pontos":
            registros = get_all_clients()
            opcoes_clientes = [""] + [f"{reg['Nome']} - {reg['Telefone']}" for reg in registros]
            cliente_selecionado = st.selectbox("Digite ou selecione o Nome/WhatsApp do cliente:", opcoes_clientes)

            if cliente_selecionado != "":
                telefone_cli = cliente_selecionado.split(" - ")[-1]
                cliente, linha = find_client(telefone_cli)
                
                if cliente:
                    cli_nome = cliente['Nome']
                    cli_pontos = int(cliente['Pontos'])
                    cli_email = cliente['Email']
                    
                    st.write("---")
                    st.write(f"👤 **Cliente:** {cli_nome} | 📧 **E-mail:** {cli_email}")
                    st.write(f"⭐ **Pontos Atuais:** {cli_pontos} de 10")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("➕ Adicionar 1 Ponto", type="primary"):
                            novos_pontos = cli_pontos + 1
                            update_points(linha, novos_pontos)
                            st.success(f"Ponto adicionado! Total: {novos_pontos}")
                            
                            if novos_pontos < 10:
                                msg = f"Fala {cli_nome}, beleza? Você acabou de ganhar +1 ponto no seu Cartão Fidelidade do Ilton Cabeleireiro! ✂️\n\nVocê já tem {novos_pontos} pontos. Faltam só {10 - novos_pontos} para o seu corte GRÁTIS!"
                            else:
                                msg = f"Parabéns {cli_nome}! 🎉 Você completou 10 pontos no seu Cartão Fidelidade do Ilton Cabeleireiro! Seu próximo corte é GRÁTIS! ✂️"
                                st.warning("⚠️ ATENÇÃO: Cliente atingiu 10 pontos! Próximo corte é grátis.")
                                st.balloons()
                            
                            msg_encoded = urllib.parse.quote(msg)
                            link_zap = f"https://wa.me/55{telefone_cli}?text={msg_encoded}"
                            st.markdown(f'<a href="{link_zap}" target="_blank" class="btn-zap">📱 Enviar Aviso no WhatsApp</a>', unsafe_allow_html=True)
                            
                    with col2:
                        if st.button("🔄 Zerar Pontos", type="primary"):
                            update_points(linha, 0)
                            st.success("Pontos zerados. Novo ciclo iniciado!")
                            st.rerun()

        elif acao == "Ver Todos os Clientes":
            registros = get_all_clients()
            if registros:
                df = pd.DataFrame(registros)
                st.table(df)
            else:
                st.info("Nenhum cliente cadastrado ainda.")

# ==========================================
# 6. RODAPÉ 
# ==========================================
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
    <div class="footer">
        Desenvolvido por UFO Digital Agency<br>
        Ilton Cabeleireiro - +55 35 8702-2576 - Rua Delfim Moreira, 332 - Centro Ouro Fino MG. CNPJ: 17.254.024/0001-70
    </div>
""", unsafe_allow_html=True)