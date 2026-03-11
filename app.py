import streamlit as st
import pandas as pd
from PIL import Image
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E CSS (EXTREMO MOBILE)
# ==========================================
st.set_page_config(page_title="Ilton Fidelidade Digital", page_icon="✂️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap');
    
    /* 1. ANIQUILAÇÃO TOTAL DAS MARCAS DO STREAMLIT (Coroa e Perfil) */
    header, footer { visibility: hidden !important; display: none !important; }
    [data-testid="stToolbar"] { visibility: hidden !important; display: none !important; }
    #viewerBadge, .viewerBadge_container, .viewerBadge_link { display: none !important; visibility: hidden !important; opacity: 0 !important; }
    iframe[title="Streamlit Community Cloud badge"] { display: none !important; }
    [data-testid="stAppViewContainer"] > div:last-child { display: none !important; }
    
    /* 2. OTIMIZAÇÃO DE ESPAÇO NO TOPO DA TELA */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
        margin-top: -30px !important;
    }
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    /* 3. TÍTULOS E TEXTOS AJUSTADOS */
    h1 { 
        font-family: 'Montserrat', sans-serif !important; 
        color: #D4AF37 !important; 
        text-align: center; 
        text-transform: uppercase; 
        letter-spacing: 2px; 
        font-size: 1.8rem !important; 
        line-height: 1.1;
        margin-top: -10px !important;
    }
    h2, h3 { color: #C0C0C0 !important; text-align: center; }
    h4 { color: #C0C0C0 !important; text-align: center; font-size: 1rem !important; margin-bottom: 20px;}
    
    /* 4. HACK CIRÚRGICO PARA BOTÕES LADO A LADO NO CELULAR SEM QUEBRAR TUDO */
    @media (max-width: 768px) {
        div[data-testid="stHorizontalBlock"] {
            display: flex !important;
            flex-direction: row !important;
            flex-wrap: nowrap !important;
            justify-content: center !important;
            gap: 10px !important;
        }
        div[data-testid="column"] {
            width: 50% !important;
            min-width: 45% !important;
            flex: 1 1 50% !important;
        }
    }
    
    /* 5. BOTÃO: ÁREA DO CLIENTE (Vermelho Pulso) */
    @keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(255, 51, 51, 0.6); } 70% { box-shadow: 0 0 0 10px rgba(255, 51, 51, 0); } 100% { box-shadow: 0 0 0 0 rgba(255, 51, 51, 0); } }
    
    div[data-testid="stButton"] button[kind="primary"] { 
        background: linear-gradient(45deg, #ff1a1a, #e60000) !important; 
        color: white !important; 
        border-radius: 6px !important; 
        border: none !important; 
        font-weight: 800 !important; 
        text-transform: uppercase; 
        font-size: 0.70rem !important; 
        animation: pulse 2s infinite; 
        padding: 15px 2px !important; 
        width: 100%;
        height: 100%;
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    
    /* 6. BOTÃO: ÁREA RESTRITA (Fundo Preto com Contorno Glitch Fino) */
    div[data-testid="stButton"] button[kind="secondary"] { 
        background-color: #050505 !important; 
        color: #FFFFFF !important; 
        border: 1px solid #111111 !important; 
        border-radius: 4px !important; 
        font-weight: 800 !important; 
        text-transform: uppercase; 
        font-size: 0.70rem !important;
        box-shadow: -2px -2px 0px 0px #2b7cff, 2px 2px 0px 0px #ff3333 !important; 
        transition: 0.1s !important; 
        padding: 15px 2px !important; 
        width: 100%;
        height: 100%;
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div[data-testid="stButton"] button[kind="secondary"]:active {
        box-shadow: 2px 2px 0px 0px #2b7cff, -2px -2px 0px 0px #ff3333 !important;
        transform: translate(2px, 2px);
    }

    /* 7. Botões Discretos (Voltar, Sair) */
    div[data-testid="stButton"] button[kind="tertiary"] { 
        background-color: #1A1A1A !important;  
        color: #AAAAAA !important; 
        border: 1px solid #444 !important; 
        border-radius: 6px !important; 
        font-weight: bold !important; 
        text-transform: uppercase; 
        padding: 8px !important; 
        width: 100%;
    }
    
    .btn-zap { background-color: #25D366 !important; color: white !important; border-radius: 6px; border: none; padding: 10px; font-weight: bold; width: 100%; text-transform: uppercase; text-align: center; display: block; text-decoration: none; margin-top: 15px; }
    .stTextInput>div>div>input, .stSelectbox>div>div>div { background-color: #1a1c24 !important; color: white !important; border: 1px solid #444 !important; text-align: center; }
    table { color: #FAFAFA !important; background-color: #1a1c24 !important; border-radius: 8px; width: 100%; }
    thead tr th { background-color: #2b7cff !important; color: white !important; }
    
    /* 8. Rodapé Fixo e Limpo */
    .rodape-ufo { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0E1117; color: #444; text-align: center; padding: 5px; font-size: 0.65rem; border-top: 1px solid #1A1A1A; z-index: 999; }
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
    st.error("⚠️ Erro de conexão com a planilha. Verifique as credenciais.")
    st.stop()

def get_all_clients():
    try: return planilha.get_all_records()
    except: return []

def find_client(telefone):
    registros = get_all_clients()
    for i, reg in enumerate(registros):
        if str(reg.get('Telefone', '')).strip() == str(telefone).strip():
            return reg, i + 2 
    return None, None

def add_client(telefone, nome, email):
    planilha.insert_row([str(telefone), str(nome), str(email), 0], 2)

def update_points(linha, pontos):
    planilha.update_cell(linha, 4, int(pontos)) 

# NAVEGAÇÃO
if 'pagina_atual' not in st.session_state:
    st.session_state['pagina_atual'] = 'inicio'

def mudar_pagina(nova_pagina):
    st.session_state['pagina_atual'] = nova_pagina

# ==========================================
# 3. INTERFACE GERAL (LOGO CENTRALIZADA)
# ==========================================
# Colunas para empurrar a logo perfeitamente para o centro
col_espaco_esq, col_logo, col_espaco_dir = st.columns([1.2, 1, 1.2])

with col_logo:
    try:
        # Puxando o arquivo logo.jpg que você enviou
        st.image("logo.jpg", use_container_width=True)
    except FileNotFoundError:
        pass

st.title("Cartão Fidelidade")

# ==========================================
# TELA 1: INÍCIO (Layout Lado a Lado Forçado)
# ==========================================
if st.session_state['pagina_atual'] == 'inicio':
    st.markdown("<h4>Selecione seu acesso:</h4>", unsafe_allow_html=True)
    
    col_cli, col_barb = st.columns(2)
    
    with col_cli:
        if st.button("ÁREA DO CLIENTE", type="primary"):
            mudar_pagina('cliente')
            st.rerun()
            
    with col_barb:
        if st.button("ÁREA RESTRITA", type="secondary"):
            mudar_pagina('barbeiro')
            st.rerun()

# ==========================================
# TELA 2: ÁREA DO CLIENTE
# ==========================================
elif st.session_state['pagina_atual'] == 'cliente':
    col_voltar, col_vazia = st.columns([1, 1])
    with col_voltar:
        if st.button("⬅️ Voltar", type="tertiary"):
            mudar_pagina('inicio')
            st.rerun()
        
    aba1, aba2 = st.tabs(["🔍 Meus pontos", "📝 Cadastrar"])
    
    with aba1:
        st.write("---")
        telefone_busca = st.text_input("Seu WhatsApp (apenas números):", key="busca_cli")
        
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
                        st.warning("🎉 Completou o cartão! Próximo corte GRÁTIS!")
                else:
                    st.error("Número não encontrado.")
            else:
                st.warning("Digite seu número.")

    with aba2:
        st.write("---")
        novo_nome = st.text_input("Nome:")
        novo_telefone = st.text_input("WhatsApp (com DDD):", key="cad_cli")
        novo_email = st.text_input("E-mail:") 
        
        if st.button("Criar Cartão", type="primary"):
            if novo_nome and novo_telefone and novo_email:
                cliente_existente, _ = find_client(novo_telefone)
                if cliente_existente:
                    st.error("Número já cadastrado.")
                else:
                    add_client(novo_telefone, novo_nome, novo_email)
                    st.success(f"{novo_nome}! Cadastro feito!")
                    st.balloons()
            else:
                st.warning("Preencha todos os campos.")

# ==========================================
# TELA 3: ÁREA DO BARBEIRO
# ==========================================
elif st.session_state['pagina_atual'] == 'barbeiro':
    col_voltar, col_sair = st.columns([1, 1])
    with col_voltar:
        if st.button("⬅️ Voltar", type="tertiary"):
            mudar_pagina('inicio')
            st.rerun()
            
    st.write("---")
    
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    if not st.session_state['autenticado']:
        senha = st.text_input("Senha de Acesso", type="password")
        if st.button("Entrar", type="primary"):
            if senha == "barba123":
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
                
    if st.session_state['autenticado']:
        with col_sair:
            if st.button("Sair (Logout)", type="tertiary"):
                st.session_state['autenticado'] = False
                st.rerun()
                
        acao = st.selectbox("Ação:", ["Gerenciar Pontos", "Editar/Excluir", "Ver Todos"])

        if acao == "Gerenciar Pontos":
            registros = get_all_clients()
            opcoes_clientes = [""] + [f"{reg['Nome']} - {reg['Telefone']}" for reg in registros]
            cliente_selecionado = st.selectbox("Buscar cliente:", opcoes_clientes)

            if cliente_selecionado != "":
                telefone_cli = cliente_selecionado.split(" - ")[-1]
                cliente, linha = find_client(telefone_cli)
                
                if cliente:
                    cli_nome = cliente['Nome']
                    cli_pontos = int(cliente['Pontos'])
                    st.write(f"👤 **{cli_nome}** | ⭐ **{cli_pontos}/10 Pontos**")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("➕ 1 Ponto", type="primary"):
                            novos_pontos = cli_pontos + 1
                            update_points(linha, novos_pontos)
                            st.success(f"Total: {novos_pontos}")
                            
                            msg = f"Fala {cli_nome}, beleza? Você ganhou +1 ponto no Cartão Fidelidade! ✂️\n\nFaltam só {10 - novos_pontos} para o corte GRÁTIS!" if novos_pontos < 10 else f"Parabéns {cli_nome}! 🎉 Você completou 10 pontos! Próximo corte é GRÁTIS! ✂️"
                            msg_encoded = urllib.parse.quote(msg)
                            st.markdown(f'<a href="https://wa.me/55{telefone_cli}?text={msg_encoded}" target="_blank" class="btn-zap">📱 Avisar no Whats</a>', unsafe_allow_html=True)
                            
                    with col2:
                        if st.button("🔄 Zerar", type="secondary"):
                            update_points(linha, 0)
                            st.success("Zerado!")
                            st.rerun()

        elif acao == "Editar/Excluir":
            registros = get_all_clients()
            opcoes_clientes = [""] + [f"{reg['Nome']} - {reg['Telefone']}" for reg in registros]
            cliente_selecionado = st.selectbox("Cliente:", opcoes_clientes)

            if cliente_selecionado != "":
                telefone_cli = cliente_selecionado.split(" - ")[-1]
                cliente, linha = find_client(telefone_cli)

                if cliente:
                    novo_nome = st.text_input("Nome", value=cliente['Nome'])
                    novo_telefone = st.text_input("WhatsApp", value=cliente['Telefone'])
                    novo_email = st.text_input("E-mail", value=cliente['Email'])

                    col_s, col_e = st.columns(2)
                    with col_s:
                        if st.button("💾 Salvar", type="primary"):
                            planilha.update_cell(linha, 1, str(novo_telefone))
                            planilha.update_cell(linha, 2, str(novo_nome))
                            planilha.update_cell(linha, 3, str(novo_email))
                            st.success("Atualizado!")
                    with col_e:        
                        if st.button("🗑️ Excluir", type="tertiary"):
                            planilha.delete_rows(linha)
                            st.success("Removido!")
                            st.rerun()

        elif acao == "Ver Todos":
            registros = get_all_clients()
            if registros:
                st.table(pd.DataFrame(registros))
            else:
                st.info("Nenhum cliente.")

# ==========================================
# 6. RODAPÉ 
# ==========================================
st.markdown("<br><br><br>", unsafe_allow_html=True)
st.markdown("""
    <div class="rodape-ufo">
        Desenvolvido por UFO Digital Agency<br>
        Ilton Cabeleireiro - +55 35 8702-2576
    </div>
""", unsafe_allow_html=True)