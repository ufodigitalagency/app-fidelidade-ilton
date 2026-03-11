import streamlit as st
import pandas as pd
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials
import base64

# ==========================================
# 1. CONFIGURAÇÃO E CSS HACKER (APP NATIVO)
# ==========================================
st.set_page_config(page_title="Sistema Fidelidade", page_icon="✂️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800&display=swap');
    
    /* REMOÇÃO SEGURA DA ESTRUTURA DO STREAMLIT */
    header { visibility: hidden !important; display: none !important; }
    footer { visibility: hidden !important; display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    
    /* TRAVA O FORMATO DE CELULAR E CENTRALIZA O APP INTEIRO */
    .block-container {
        max-width: 480px !important; 
        margin: 0 auto !important;   
        padding-top: 1.5rem !important;
        padding-bottom: 7rem !important; 
    }
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    /* TÍTULO DA HOME */
    .titulo-app {
        font-family: 'Montserrat', sans-serif;
        color: #D4AF37;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 1.6rem;
        font-weight: 800;
        line-height: 1.3;
        margin-top: 15px;
        margin-bottom: 30px;
    }
    
    /* TEXTOS GERAIS */
    h2, h3, h4, label, p { text-align: center !important; color: #C0C0C0 !important; font-family: 'Montserrat', sans-serif; }
    p { margin-bottom: 10px !important; }
    
    /* --- DESIGN DOS BOTÕES --- */
    div[data-testid="stButton"] button {
        border-radius: 8px !important; 
        font-weight: 800 !important;
        text-transform: uppercase !important;
        font-size: 0.95rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    div[data-testid="stButton"] button p { margin: 0 !important; padding: 0 !important; line-height: 1 !important; }
    
    /* Botão Principal (Vermelho) */
    div[data-testid="stButton"] button[kind="primary"] { 
        min-height: 55px !important;
        background: linear-gradient(135deg, #ff1a1a 0%, #cc0000 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255, 26, 26, 0.2) !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover { transform: translateY(-2px); opacity: 0.9; }

    /* Botão Secundário (Preto/Dourado) */
    div[data-testid="stButton"] button[kind="secondary"] { 
        min-height: 55px !important;
        background-color: #1a1c24 !important;  
        color: #D4AF37 !important; 
        border: 1px solid #D4AF37 !important; 
    }
    
    /* Botão Terciário (Discreto para o "VOLTAR") */
    div[data-testid="stButton"] button[kind="tertiary"] { 
        background-color: transparent !important;  
        color: #888888 !important; 
        border: 1px solid #333 !important; 
        min-height: 40px !important;
        border-radius: 6px !important;
        font-size: 0.75rem !important;
        padding: 5px 15px !important;
        margin-bottom: 20px !important;
        width: auto !important;
    }
    
    /* ABAS (TABS) OTIMIZADAS */
    [data-baseweb="tabs"] { width: 100%; margin-top: 5px; }
    [data-baseweb="tab-list"] { display: flex; justify-content: center; gap: 10px; background-color: transparent !important; border-bottom: none !important; margin-bottom: 25px; }
    [data-baseweb="tab"] { background-color: #1a1c24 !important; border-radius: 8px !important; padding: 12px !important; color: #888 !important; font-weight: 600 !important; font-family: 'Montserrat', sans-serif; border: 1px solid #333 !important; transition: 0.3s; flex: 1; text-align: center; }
    [aria-selected="true"] { background: linear-gradient(135deg, #ff1a1a 0%, #cc0000 100%) !important; color: white !important; border: none !important; box-shadow: 0 4px 10px rgba(255, 26, 26, 0.3) !important; }
    [data-baseweb="tab-highlight"] { display: none !important; } 
    
    /* CAIXAS DE TEXTO E BUSCA */
    div[data-baseweb="input"] { border-radius: 8px !important; background-color: #1a1c24 !important; border: 1px solid #333 !important; min-height: 50px !important; }
    div[data-baseweb="input"] input { color: white !important; text-align: center !important; font-size: 1rem !important; background-color: transparent !important; }
    div[data-baseweb="input"]:focus-within { border-color: #ff1a1a !important; box-shadow: 0 0 8px rgba(255,26,26,0.4) !important;}

    /* MENUS SUSPENSOS (SELECTBOX) EM AZUL */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] > div { background-color: #0d1f3d !important; border: 1px solid #2b7cff !important; border-radius: 8px !important; min-height: 50px !important; }
    div[data-testid="stSelectbox"] div[data-baseweb="select"] * { color: white !important; font-weight: 600 !important; }
    
    /* LINK WHATSAPP */
    .btn-zap { background-color: #25D366 !important; color: white !important; border-radius: 8px; border: none; padding: 15px; font-weight: 800; font-family: 'Montserrat', sans-serif; width: 100%; text-transform: uppercase; text-align: center; display: flex; justify-content: center; text-decoration: none; margin: 10px auto; box-shadow: 0 4px 15px rgba(37, 211, 102, 0.3); transition: 0.3s;}
    
    /* CARD DA LISTA DE CLIENTES (Design Inspirado no seu Print) */
    .lista-card { 
        background-color: #1a1c24; 
        border-radius: 12px; 
        padding: 15px; 
        margin-bottom: 15px; 
        border-left: 6px solid #ff1a1a; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); 
    }
    .lista-card h4 { color: white !important; margin: 0 0 10px 0 !important; text-align: left !important; font-size: 1.1rem; text-transform: uppercase;}
    .lista-card .pontos { color: #D4AF37 !important; margin: 0 0 5px 0 !important; text-align: left !important; font-weight: 800; font-size: 1.1rem; }
    .lista-card .contato { color: #888 !important; margin: 0 !important; text-align: left !important; font-size: 0.8rem; }
    
    /* RODAPÉS */
    .rodape-container { position: fixed; left: 0; width: 100%; background-color: transparent; text-align: center; padding: 10px; z-index: 999; pointer-events: none;}
    .rodape-container p, .rodape-container a { pointer-events: auto; }
    .rodape-container p { margin: 0 !important; line-height: 1.4 !important; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONEXÃO COM GOOGLE SHEETS
# ==========================================
scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

try:
    cred_dict = dict(st.secrets["gcp_service_account"])
    credentials = Credentials.from_service_account_info(cred_dict, scopes=scopes)
    gc = gspread.authorize(credentials)
    planilha = gc.open("Barbearia_Fidelidade").sheet1
except Exception as e:
    st.error(f"⚠️ Erro de conexão com a planilha.")
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

# FUNÇÃO DA LOGO BLINDADA
def exibir_logo_blindada():
    try:
        with open("logo.png", "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f'<div style="display: flex; justify-content: center; width: 100%;">'
            f'<img src="data:image/png;base64,{encoded_string}" style="max-width: 220px; width: 100%;">'
            f'</div>', 
            unsafe_allow_html=True
        )
    except Exception:
        pass 

# FUNÇÕES DE RODAPÉ
def exibir_rodape_home():
    st.markdown("""
        <div class="rodape-container" style="bottom: 10px;">
            <p style="font-size: 0.65rem; color: #666;">Desenvolvido por <strong>UFO Digital Agency</strong></p>
            <a href="http://www.instagram.com/mkt.ufo" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/1384/1384063.png" alt="Instagram" style="width: 18px; opacity: 0.5; margin-top: 5px; transition: 0.3s;" onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.5'">
            </a>
        </div>
    """, unsafe_allow_html=True)

def exibir_rodape_interno():
    st.markdown("""
        <div class="rodape-container" style="bottom: 25px;">
            <p style="font-size: 0.75rem; color: #777; font-weight: 600;">Ilton Cabeleireiro - +55 35 8702-2576</p>
        </div>
    """, unsafe_allow_html=True)

# NAVEGAÇÃO E ESTADOS
if 'pagina_atual' not in st.session_state:
    st.session_state['pagina_atual'] = 'inicio'

def mudar_pagina(nova_pagina):
    st.session_state['pagina_atual'] = nova_pagina

# ==========================================
# TELA 1: INÍCIO (COM AS COLUNAS QUE FUNCIONARAM)
# ==========================================
if st.session_state['pagina_atual'] == 'inicio':
    exibir_logo_blindada()
    
    st.markdown("<div class='titulo-app'>SISTEMA<br>FIDELIDADE</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1rem; color: #aaa; margin-bottom: 20px !important;'>Selecione seu acesso:</p>", unsafe_allow_html=True)
    
    # RESTAURADO: A gaiola de colunas que você elogiou e que manteve tudo no centro!
    col_esq, col_meio, col_dir = st.columns([1, 8, 1])
    with col_meio:
        if st.button("💇‍♂️ ÁREA DO CLIENTE", type="primary", use_container_width=True):
            mudar_pagina('cliente')
            st.rerun()
            
        st.write("") 
        
        if st.button("🔒 ÁREA RESTRITA", type="secondary", use_container_width=True):
            mudar_pagina('barbeiro')
            st.rerun()
        
    exibir_rodape_home()

# ==========================================
# TELA 2: ÁREA DO CLIENTE
# ==========================================
elif st.session_state['pagina_atual'] == 'cliente':
    
    if st.button("⬅️ Voltar", type="tertiary"):
        mudar_pagina('inicio')
        st.rerun()
            
    aba1, aba2 = st.tabs(["🔍 MEUS PONTOS", "📝 CADASTRAR"])
    
    with aba1:
        st.markdown("<p style='margin-top: 10px;'>Digite seu número para ver seus pontos</p>", unsafe_allow_html=True)
        telefone_busca = st.text_input("", placeholder="Ex: 35999999999", label_visibility="collapsed", key="busca_cli")
        
        st.write("")
        if st.button("BUSCAR PONTOS", type="primary", use_container_width=True):
            if telefone_busca:
                cliente, _ = find_client(telefone_busca)
                if cliente:
                    nome = cliente.get('Nome', 'Cliente')
                    pontos = int(cliente.get('Pontos', 0))
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
        st.markdown("<p style='margin-top: 10px;'>Crie seu cartão agora mesmo</p>", unsafe_allow_html=True)
        novo_nome = st.text_input("", placeholder="Qual seu nome?", label_visibility="collapsed")
        novo_telefone = st.text_input("", placeholder="WhatsApp com DDD (Ex: 3588888888)", label_visibility="collapsed", key="cad_cli")
        novo_email = st.text_input("", placeholder="Seu e-mail", label_visibility="collapsed") 
        
        st.write("")
        if st.button("CRIAR CARTÃO", type="primary", use_container_width=True):
            if novo_nome and novo_telefone and novo_email:
                cliente_existente, _ = find_client(novo_telefone)
                if cliente_existente:
                    st.error("Opa! Número já cadastrado.")
                else:
                    add_client(novo_telefone, novo_nome, novo_email)
                    st.success(f"Cadastro feito com sucesso!")
                    st.balloons()
            else:
                st.warning("Preencha todos os campos.")
                
    exibir_rodape_interno()

# ==========================================
# TELA 3: ÁREA DO BARBEIRO (FEED DE CLIENTES)
# ==========================================
elif st.session_state['pagina_atual'] == 'barbeiro':
    
    if st.button("⬅️ Voltar", type="tertiary"):
        mudar_pagina('inicio')
        st.rerun()
            
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    if not st.session_state['autenticado']:
        st.markdown("<h3 style='color: #D4AF37 !important;'>Painel do Barbeiro</h3><p>Acesso exclusivo Ilton</p>", unsafe_allow_html=True)
        senha = st.text_input("", type="password", placeholder="Digite a senha", label_visibility="collapsed")
        
        st.write("")
        if st.button("ENTRAR", type="primary", use_container_width=True):
            # A NOVA SENHA ATUALIZADA
            if senha == "Adm@Ilton2576":
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
                
    if st.session_state['autenticado']:
        
        st.markdown("<p style='color: #888 !important; text-align: left !important; font-size: 0.8rem !important; margin-bottom: 5px !important;'>Selecione o menu:</p>", unsafe_allow_html=True)
        acao = st.selectbox("Selecione a ação:", ["Adicionar Pontos", "Editar/Excluir", "Ver Todos"], label_visibility="collapsed")
        st.write("---")

        registros = get_all_clients()
        registros_validos = [r for r in registros if str(r.get('Telefone', '')).strip() != '']

        # ==========================================
        # ABA: ADICIONAR PONTOS (Estilo Feed de Instagram)
        # ==========================================
        if acao == "Adicionar Pontos":
            st.markdown("<p style='color: white; text-align:left !important; margin-bottom:10px;'>🔍 Buscar Cliente:</p>", unsafe_allow_html=True)
            busca = st.text_input("", placeholder="Nome ou telefone...", label_visibility="collapsed", key="busca_add")
            st.markdown("<br>", unsafe_allow_html=True)
            
            encontrou = False
            for i, reg in enumerate(registros):
                tel = str(reg.get('Telefone', '')).strip()
                if not tel: continue
                nome = str(reg.get('Nome', 'Sem Nome')).upper()
                email = str(reg.get('Email', '-'))
                pontos = int(reg.get('Pontos', 0))
                
                # Sistema de Filtro
                if busca.lower() in nome.lower() or busca in tel:
                    encontrou = True
                    
                    with st.container():
                        st.markdown(f"""
                            <div class="lista-card">
                                <h4>👤 {nome}</h4>
                                <p class="pontos">⭐ Pontos: {pontos} / 10</p>
                                <p class="contato">📱 {tel} &nbsp;|&nbsp; ✉️ {email}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Botões perfeitamente alinhados embaixo do card
                        c1, c2 = st.columns([1, 1])
                        with c1:
                            if st.button("➕ ADD+ PONTO", type="primary", use_container_width=True, key=f"add_{i}"):
                                update_points(i + 2, pontos + 1)
                                st.success("Ponto Adicionado!")
                                st.rerun()
                        with c2:
                            if st.button("🔄 ZERAR", type="secondary", use_container_width=True, key=f"zerar_{i}"):
                                update_points(i + 2, 0)
                                st.success("Pontos Zerados!")
                                st.rerun()
                                
                        st.markdown("<hr style='border:1px solid #1a1c24; margin: 15px 0;'>", unsafe_allow_html=True)

            if not encontrou:
                st.info("Nenhum cliente encontrado com essa busca.")

        # ==========================================
        # ABA: EDITAR / EXCLUIR (Estilo Feed Interativo)
        # ==========================================
        elif acao == "Editar/Excluir":
            st.markdown("<p style='color: white; text-align:left !important; margin-bottom:10px;'>🔍 Buscar para Editar:</p>", unsafe_allow_html=True)
            busca = st.text_input("", placeholder="Nome ou telefone...", label_visibility="collapsed", key="busca_edit")
            st.markdown("<br>", unsafe_allow_html=True)
            
            encontrou = False
            for i, reg in enumerate(registros):
                tel = str(reg.get('Telefone', '')).strip()
                if not tel: continue
                nome = str(reg.get('Nome', 'Sem Nome')).upper()
                email = str(reg.get('Email', '-'))
                pontos = int(reg.get('Pontos', 0))
                
                if busca.lower() in nome.lower() or busca in tel:
                    encontrou = True
                    
                    with st.container():
                        st.markdown(f"""
                            <div class="lista-card">
                                <h4>👤 {nome}</h4>
                                <p class="pontos">⭐ Pontos: {pontos} / 10</p>
                                <p class="contato">📱 {tel} &nbsp;|&nbsp; ✉️ {email}</p>
                            </div>
                        """, unsafe_allow_html=True)

                        c1, c2 = st.columns([1, 1])
                        with c1:
                            # Quando clica, ele muda o estado para "editando"
                            if st.button("✏️ EDITAR", type="secondary", use_container_width=True, key=f"btn_edit_{i}"):
                                st.session_state[f"edit_mode_{i}"] = not st.session_state.get(f"edit_mode_{i}", False)
                                st.rerun()
                        with c2:
                            if st.button("🗑️ DELETAR", type="primary", use_container_width=True, key=f"btn_del_{i}"):
                                planilha.delete_rows(i + 2)
                                st.success("Cliente removido!")
                                st.rerun()
                                
                        # Mostra os campos apenas se estiver no modo "Editar"
                        if st.session_state.get(f"edit_mode_{i}", False):
                            st.markdown("<p style='color: #D4AF37; font-size:0.8rem; margin-top:10px;'>Alterando dados:</p>", unsafe_allow_html=True)
                            novo_nome = st.text_input("Novo Nome", value=nome.title(), key=f"nome_{i}", label_visibility="collapsed")
                            novo_telefone = st.text_input("Novo WhatsApp", value=tel, key=f"tel_{i}", label_visibility="collapsed")
                            novo_email = st.text_input("Novo E-mail", value=email, key=f"email_{i}", label_visibility="collapsed")

                            if st.button("💾 SALVAR", type="primary", use_container_width=True, key=f"save_{i}"):
                                planilha.update_cell(i + 2, 1, str(novo_telefone))
                                planilha.update_cell(i + 2, 2, str(novo_nome))
                                planilha.update_cell(i + 2, 3, str(novo_email))
                                st.session_state[f"edit_mode_{i}"] = False
                                st.success("Atualizado!")
                                st.rerun()
                                
                        st.markdown("<hr style='border:1px solid #1a1c24; margin: 15px 0;'>", unsafe_allow_html=True)
                    
            if not encontrou:
                st.info("Nenhum cliente encontrado com essa busca.")

        # ==========================================
        # ABA: VER TODOS (Apenas Leitura)
        # ==========================================
        elif acao == "Ver Todos":
            if registros_validos:
                st.markdown("<p style='color: #888 !important; text-align: left !important; font-size: 0.8rem !important; margin-bottom: 10px !important;'>Lista de Clientes Cadastrados:</p>", unsafe_allow_html=True)
                for reg in registros_validos:
                    nome = str(reg.get('Nome', 'Sem Nome')).upper()
                    telefone = str(reg.get('Telefone', 'Sem Número'))
                    email = str(reg.get('Email', '-'))
                    pontos = int(reg.get('Pontos', 0))
                    
                    st.markdown(f"""
                        <div class="lista-card">
                            <h4>👤 {nome}</h4>
                            <p class="pontos">⭐ Pontos: {pontos} / 10</p>
                            <p class="contato">📱 {telefone} &nbsp;|&nbsp; ✉️ {email}</p>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum cliente cadastrado no momento.")
                
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("SAIR DO SISTEMA", type="tertiary"):
            st.session_state['autenticado'] = False
            st.rerun()
            
    exibir_rodape_interno()
