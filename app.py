import streamlit as st
import pandas as pd
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E CSS HACKER (MOBILE APP NATIVO)
# ==========================================
st.set_page_config(page_title="Ilton Fidelidade Digital", page_icon="✂️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800&display=swap');
    
    /* ANIQUILAR MARCAS DO STREAMLIT DE VEZ */
    header, footer, [data-testid="stToolbar"], .viewerBadge_container, #viewerBadge { 
        display: none !important; 
        visibility: hidden !important; 
    }
    
    /* A GRANDE SACADA: FORÇAR FORMATO DE CELULAR ATÉ NO PC */
    .block-container {
        max-width: 450px !important; /* Trava a largura máxima! */
        margin: 0 auto !important;   /* Centraliza o app inteiro na tela */
        padding-top: 1.5rem !important;
        padding-bottom: 5rem !important;
    }
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    /* LOGO 100% CENTRALIZADA NATIVA */
    [data-testid="stImage"] {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-bottom: 0px !important;
    }
    [data-testid="stImage"] img {
        max-width: 200px !important; /* Tamanho harmonioso */
    }
    
    /* NOVO TÍTULO PROPORCIONAL E ELEGANTE */
    .titulo-app {
        font-family: 'Montserrat', sans-serif;
        color: #D4AF37;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 1.6rem;
        font-weight: 800;
        line-height: 1.2;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    
    /* TEXTOS GERAIS */
    h2, h3, h4, label, p { text-align: center !important; color: #C0C0C0 !important; font-family: 'Montserrat', sans-serif; }
    p { margin-bottom: 20px !important; }
    
    /* BOTÕES GORDOS E PREMIUM (TIRANDO O ASPECTO ACHATADO) */
    div[data-testid="stButton"] button {
        width: 100% !important;
        height: 60px !important; /* Botão com altura de app moderno */
        border-radius: 12px !important; /* Arredondamento suave */
        font-weight: 800 !important;
        text-transform: uppercase !important;
        font-size: 1rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
        margin-bottom: 10px !important;
    }
    
    /* Botão Principal (Vermelho Vivo com Sombra) */
    div[data-testid="stButton"] button[kind="primary"] { 
        background: linear-gradient(135deg, #ff1a1a 0%, #cc0000 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255, 26, 26, 0.3) !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 26, 26, 0.5) !important;
    }

    /* Botão Secundário (Escuro com Borda Dourada) */
    div[data-testid="stButton"] button[kind="secondary"] { 
        background-color: #1a1c24 !important;  
        color: #D4AF37 !important; 
        border: 1px solid #D4AF37 !important; 
    }
    
    /* HACK NAS ABAS (TABS) PARA PARECEREM BOTÕES DE APP */
    [data-baseweb="tabs"] { width: 100%; margin-top: 10px; }
    [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 10px;
        background-color: transparent !important;
        border-bottom: none !important;
        margin-bottom: 20px;
    }
    [data-baseweb="tab"] {
        background-color: #1a1c24 !important;
        border-radius: 10px !important;
        padding: 12px 15px !important;
        color: #888 !important;
        font-weight: 600 !important;
        font-family: 'Montserrat', sans-serif;
        border: 1px solid #333 !important;
        transition: 0.3s;
    }
    [aria-selected="true"] {
        background: linear-gradient(135deg, #ff1a1a 0%, #cc0000 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(255, 26, 26, 0.3) !important;
    }
    [data-baseweb="tab-highlight"] { display: none !important; } /* Tira a linha azul feia embaixo */
    
    /* CAIXAS DE TEXTO MAIS ALTAS E CENTRALIZADAS */
    [data-testid="stTextInput"] input, [data-testid="stSelectbox"] > div > div { 
        height: 55px !important; 
        border-radius: 12px !important; 
        background-color: #1a1c24 !important; 
        color: white !important; 
        border: 1px solid #333 !important; 
        text-align: center !important; 
        font-size: 1rem !important; 
    }
    [data-testid="stTextInput"] input:focus { border-color: #ff1a1a !important; box-shadow: 0 0 8px rgba(255,26,26,0.4) !important;}
    
    /* LINK WHATSAPP */
    .btn-zap { background-color: #25D366 !important; color: white !important; border-radius: 12px; border: none; padding: 18px; font-weight: 800; font-family: 'Montserrat', sans-serif; width: 100%; text-transform: uppercase; text-align: center; display: block; text-decoration: none; margin-top: 15px; box-shadow: 0 4px 15px rgba(37, 211, 102, 0.3); transition: 0.3s;}
    .btn-zap:hover { background-color: #1ebe57 !important; transform: translateY(-2px);}
    
    /* TABELAS */
    table { color: #FAFAFA !important; background-color: #1a1c24 !important; border-radius: 8px; width: 100%; text-align: center; }
    thead tr th { background-color: #ff1a1a !important; color: white !important; text-align: center !important;}
    
    /* RODAPÉ LIMPO */
    .rodape-ufo { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #0E1117; color: #444; text-align: center; padding: 10px; font-size: 0.65rem; border-top: 1px solid #1a1c24; z-index: 999; }
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

# NAVEGAÇÃO
if 'pagina_atual' not in st.session_state:
    st.session_state['pagina_atual'] = 'inicio'

def mudar_pagina(nova_pagina):
    st.session_state['pagina_atual'] = nova_pagina

# ==========================================
# 3. INTERFACE GERAL (LOGO E TÍTULO)
# ==========================================
# A logo agora entra sozinha, sem colunas, pois o CSS centraliza perfeitamente!
try:
    st.image("logo.png")
except Exception:
    pass

st.markdown("<div class='titulo-app'>CARTÃO<br>FIDELIDADE</div>", unsafe_allow_html=True)

# ==========================================
# TELA 1: INÍCIO 
# ==========================================
if st.session_state['pagina_atual'] == 'inicio':
    st.markdown("<p style='font-size: 1.1rem; color: #aaa;'>Selecione seu acesso:</p>", unsafe_allow_html=True)
    
    # Botões empilhados naturalmente, soltos na tela, usando 100% do container
    if st.button("💇‍♂️ ÁREA DO CLIENTE", type="primary", use_container_width=True):
        mudar_pagina('cliente')
        st.rerun()
        
    if st.button("🔒 ÁREA RESTRITA", type="secondary", use_container_width=True):
        mudar_pagina('barbeiro')
        st.rerun()

# ==========================================
# TELA 2: ÁREA DO CLIENTE
# ==========================================
elif st.session_state['pagina_atual'] == 'cliente':
    if st.button("⬅️ VOLTAR AO INÍCIO", type="secondary", use_container_width=True):
        mudar_pagina('inicio')
        st.rerun()
        
    st.write("") # Espaço
    
    aba1, aba2 = st.tabs(["🔍 MEUS PONTOS", "📝 CADASTRAR"])
    
    with aba1:
        st.markdown("<br><p>Digite seu número para ver seus pontos</p>", unsafe_allow_html=True)
        telefone_busca = st.text_input("", placeholder="Ex: 35999999999", label_visibility="collapsed", key="busca_cli")
        
        if st.button("BUSCAR MEUS PONTOS", type="primary", use_container_width=True):
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
        st.markdown("<br><p>Crie seu cartão agora mesmo</p>", unsafe_allow_html=True)
        novo_nome = st.text_input("Qual seu nome?", placeholder="Seu Nome")
        novo_telefone = st.text_input("WhatsApp (com DDD):", placeholder="Ex: 3588888888", key="cad_cli")
        novo_email = st.text_input("Seu E-mail:", placeholder="email@exemplo.com") 
        
        st.write("")
        if st.button("CRIAR MEU CARTÃO", type="primary", use_container_width=True):
            if novo_nome and novo_telefone and novo_email:
                cliente_existente, _ = find_client(novo_telefone)
                if cliente_existente:
                    st.error("Opa! Número já cadastrado.")
                else:
                    add_client(novo_telefone, novo_nome, novo_email)
                    st.success(f"{novo_nome}! Cadastro feito com sucesso!")
                    st.balloons()
            else:
                st.warning("Preencha todos os campos.")

# ==========================================
# TELA 3: ÁREA DO BARBEIRO
# ==========================================
elif st.session_state['pagina_atual'] == 'barbeiro':
    
    if st.button("⬅️ VOLTAR AO INÍCIO", type="secondary", use_container_width=True):
        mudar_pagina('inicio')
        st.rerun()
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    if not st.session_state['autenticado']:
        st.markdown("<p>Acesso Exclusivo Ilton</p>", unsafe_allow_html=True)
        senha = st.text_input("Senha", type="password", placeholder="Digite a senha", label_visibility="collapsed")
        if st.button("ENTRAR NO PAINEL", type="primary", use_container_width=True):
            if senha == "barba123":
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
                
    if st.session_state['autenticado']:
        
        acao = st.selectbox("Selecione a ação:", ["Gerenciar Pontos", "Editar/Excluir", "Ver Todos"])
        st.markdown("<br>", unsafe_allow_html=True)

        if acao == "Gerenciar Pontos":
            registros = get_all_clients()
            registros_validos = [r for r in registros if str(r.get('Telefone', '')).strip() != '']
            opcoes_clientes = [""] + [f"{reg.get('Nome', 'Sem Nome')} - {reg.get('Telefone', '')}" for reg in registros_validos]
            
            cliente_selecionado = st.selectbox("Buscar cliente:", opcoes_clientes)

            if cliente_selecionado != "":
                telefone_cli = cliente_selecionado.split(" - ")[-1]
                cliente, linha = find_client(telefone_cli)
                
                if cliente:
                    cli_nome = cliente.get('Nome', 'Sem Nome')
                    cli_pontos = int(cliente.get('Pontos', 0))
                    
                    st.info(f"👤 {cli_nome} | ⭐ {cli_pontos}/10 Pontos")
                    
                    if st.button("➕ ADICIONAR 1 PONTO", type="primary", use_container_width=True):
                        novos_pontos = cli_pontos + 1
                        update_points(linha, novos_pontos)
                        st.success(f"Ponto Adicionado! Total: {novos_pontos}")
                        
                        msg = f"Fala {cli_nome}, beleza? Você ganhou +1 ponto no Cartão Fidelidade! ✂️\n\nFaltam só {10 - novos_pontos} para o corte GRÁTIS!" if novos_pontos < 10 else f"Parabéns {cli_nome}! 🎉 Você completou 10 pontos! Próximo corte é GRÁTIS! ✂️"
                        msg_encoded = urllib.parse.quote(msg)
                        st.markdown(f'<a href="https://wa.me/55{telefone_cli}?text={msg_encoded}" target="_blank" class="btn-zap">📱 AVISAR NO WHATSAPP</a>', unsafe_allow_html=True)
                        
                    st.write("")
                    if st.button("🔄 ZERAR PONTOS", type="secondary", use_container_width=True):
                        update_points(linha, 0)
                        st.success("Pontos Zerados!")
                        st.rerun()

        elif acao == "Editar/Excluir":
            registros = get_all_clients()
            registros_validos = [r for r in registros if str(r.get('Telefone', '')).strip() != '']
            opcoes_clientes = [""] + [f"{reg.get('Nome', 'Sem Nome')} - {reg.get('Telefone', '')}" for reg in registros_validos]
            cliente_selecionado = st.selectbox("Cliente:", opcoes_clientes)

            if cliente_selecionado != "":
                telefone_cli = cliente_selecionado.split(" - ")[-1]
                cliente, linha = find_client(telefone_cli)

                if cliente:
                    novo_nome = st.text_input("Nome", value=str(cliente.get('Nome', '')))
                    novo_telefone = st.text_input("WhatsApp", value=str(cliente.get('Telefone', '')))
                    novo_email = st.text_input("E-mail", value=str(cliente.get('Email', '')))

                    st.write("")
                    if st.button("💾 SALVAR", type="primary", use_container_width=True):
                        planilha.update_cell(linha, 1, str(novo_telefone))
                        planilha.update_cell(linha, 2, str(novo_nome))
                        planilha.update_cell(linha, 3, str(novo_email))
                        st.success("Atualizado com sucesso!")
                            
                    if st.button("🗑️ EXCLUIR", type="secondary", use_container_width=True):
                        planilha.delete_rows(linha)
                        st.success("Cliente Removido!")
                        st.rerun()

        elif acao == "Ver Todos":
            registros = get_all_clients()
            if registros:
                st.table(pd.DataFrame(registros))
            else:
                st.info("Nenhum cliente cadastrado.")
                
        st.markdown("<hr style='border:1px solid #333'>", unsafe_allow_html=True)
        if st.button("SAIR DO SISTEMA", type="secondary", use_container_width=True):
            st.session_state['autenticado'] = False
            st.rerun()

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
