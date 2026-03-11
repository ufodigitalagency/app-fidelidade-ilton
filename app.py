import streamlit as st
import pandas as pd
import urllib.parse
import gspread
from google.oauth2.service_account import Credentials

# ==========================================
# 1. CONFIGURAÇÃO E CSS HACKER (APP NATIVO)
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
    
    /* TRAVA O FORMATO DE CELULAR E CENTRALIZA TUDO */
    .block-container {
        max-width: 450px !important; /* Trava na largura de um iPhone Max */
        margin: 0 auto !important;   /* Centraliza a div inteira na tela */
        padding-top: 2rem !important;
        padding-bottom: 6rem !important; 
    }
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    /* LOGO 100% CENTRALIZADA NATIVA */
    [data-testid="stImage"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        margin-bottom: 10px !important;
    }
    [data-testid="stImage"] img {
        max-width: 220px !important; 
        margin: 0 auto !important;
    }
    
    /* TÍTULO DA HOME (EM PILHA) */
    .titulo-app {
        font-family: 'Montserrat', sans-serif;
        color: #D4AF37;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        font-size: 1.6rem;
        font-weight: 800;
        line-height: 1.3;
        margin-top: 5px;
        margin-bottom: 40px;
    }
    
    /* TEXTOS GERAIS */
    h2, h3, h4, label, p { text-align: center !important; color: #C0C0C0 !important; font-family: 'Montserrat', sans-serif; }
    
    /* --- BOTÕES - ESTRUTURA BLINDADA --- */
    div[data-testid="stButton"] {
        display: flex;
        justify-content: center;
        width: 100%;
    }
    
    div[data-testid="stButton"] button {
        border-radius: 12px !important; 
        font-weight: 800 !important;
        font-family: 'Montserrat', sans-serif !important;
        text-transform: uppercase !important;
        font-size: 0.95rem !important;
        border: none !important;
        transition: all 0.3s ease !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    /* Centraliza o texto dentro do botão perfeitamente */
    div[data-testid="stButton"] button p { margin: 0 !important; padding: 0 !important; line-height: 1 !important; color: inherit !important;}
    
    /* Botão Principal (Vermelho) */
    div[data-testid="stButton"] button[kind="primary"] { 
        width: 100% !important;
        min-height: 60px !important;
        background: linear-gradient(135deg, #ff1a1a 0%, #cc0000 100%) !important;
        color: white !important;
        box-shadow: 0 4px 15px rgba(255, 26, 26, 0.3) !important;
        margin-bottom: 10px !important;
    }

    /* Botão Secundário (Preto/Dourado) */
    div[data-testid="stButton"] button[kind="secondary"] { 
        width: 100% !important;
        min-height: 60px !important;
        background-color: #1a1c24 !important;  
        color: #D4AF37 !important; 
        border: 1px solid #D4AF37 !important; 
        margin-bottom: 10px !important;
    }
    
    /* Botão Terciário (Discreto para o "VOLTAR" no topo) */
    div[data-testid="stButton"] button[kind="tertiary"] { 
        background-color: transparent !important;  
        color: #888888 !important; 
        border: 1px solid #333 !important; 
        min-height: 35px !important;
        height: 35px !important;
        border-radius: 8px !important;
        font-size: 0.75rem !important;
        padding: 5px 15px !important;
        margin-bottom: 25px !important;
        width: auto !important; /* Não toma a tela toda */
    }
    
    /* ABAS (TABS) OTIMIZADAS */
    [data-baseweb="tabs"] { width: 100%; margin-top: 5px; }
    [data-baseweb="tab-list"] {
        display: flex;
        justify-content: center;
        gap: 10px;
        background-color: transparent !important;
        border-bottom: none !important;
        margin-bottom: 25px;
    }
    [data-baseweb="tab"] {
        background-color: #1a1c24 !important;
        border-radius: 10px !important;
        padding: 12px !important;
        color: #888 !important;
        font-weight: 600 !important;
        font-family: 'Montserrat', sans-serif;
        border: 1px solid #333 !important;
        transition: 0.3s;
        flex: 1; /* Estica igual para os dois lados */
        text-align: center;
    }
    [aria-selected="true"] {
        background: linear-gradient(135deg, #ff1a1a 0%, #cc0000 100%) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(255, 26, 26, 0.3) !important;
    }
    [data-baseweb="tab-highlight"] { display: none !important; } 
    
    /* CAIXAS DE TEXTO */
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
    .btn-zap { background-color: #25D366 !important; color: white !important; border-radius: 12px; border: none; padding: 18px; font-weight: 800; font-family: 'Montserrat', sans-serif; width: 100%; text-transform: uppercase; text-align: center; display: block; text-decoration: none; margin-top: 15px; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(37, 211, 102, 0.3); transition: 0.3s;}
    
    /* CARD DASHBOARD DO CLIENTE NO BARBEIRO */
    .client-card {
        background: #1a1c24;
        border-radius: 15px;
        padding: 25px 20px;
        border: 1px solid #333;
        text-align: center;
        margin-top: 15px;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    .client-card h3 { color: white; margin: 0 0 10px 0; font-size: 1.3rem; }
    .client-card h1 { color: #D4AF37; margin: 0; font-size: 2.5rem; text-shadow: 0 2px 10px rgba(212, 175, 55, 0.2); }
    .client-card p { color: #888; font-size: 0.9rem; margin-top: 5px !important; }

    /* TABELAS */
    table { color: #FAFAFA !important; background-color: #1a1c24 !important; border-radius: 8px; width: 100%; text-align: center; }
    thead tr th { background-color: #ff1a1a !important; color: white !important; text-align: center !important;}
    
    /* RODAPÉ NO FIM DA TELA */
    .rodape-ufo { position: fixed; left: 0; bottom: 20px; width: 100%; background-color: transparent; color: #555; text-align: center; padding: 10px; font-size: 0.65rem; z-index: 999; }
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
# TELA 1: INÍCIO (COM LOGO E TÍTULO)
# ==========================================
if st.session_state['pagina_atual'] == 'inicio':
    try: st.image("logo.png")
    except Exception: pass
    
    st.markdown("<div class='titulo-app'>CARTÃO<br>FIDELIDADE</div>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.1rem; color: #aaa; margin-bottom: 25px !important;'>Selecione seu acesso:</p>", unsafe_allow_html=True)
    
    if st.button("💇‍♂️ ÁREA DO CLIENTE", type="primary", use_container_width=True):
        mudar_pagina('cliente')
        st.rerun()
        
    if st.button("🔒 ÁREA RESTRITA", type="secondary", use_container_width=True):
        mudar_pagina('barbeiro')
        st.rerun()

# ==========================================
# TELA 2: ÁREA DO CLIENTE (CLEAN E FOCADA)
# ==========================================
elif st.session_state['pagina_atual'] == 'cliente':
    
    # Botão de voltar discreto (Tertiary)
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

# ==========================================
# TELA 3: ÁREA DO BARBEIRO (PAINEL MODERNO)
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
            if senha == "barba123":
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
                
    if st.session_state['autenticado']:
        
        acao = st.selectbox("Selecione a ação:", ["Adicionar Pontos", "Editar/Excluir", "Ver Todos"])
        st.write("---")

        if acao == "Adicionar Pontos":
            registros = get_all_clients()
            registros_validos = [r for r in registros if str(r.get('Telefone', '')).strip() != '']
            
            # USO DO GET() PARA EVITAR O ERRO KEYERROR: 'NOME'
            opcoes_clientes = [""] + [f"{reg.get('Nome', 'Sem Nome')} - {reg.get('Telefone', '')}" for reg in registros_validos]
            
            cliente_selecionado = st.selectbox("Buscar cliente:", opcoes_clientes)

            if cliente_selecionado != "":
                telefone_cli = cliente_selecionado.split(" - ")[-1]
                cliente, linha = find_client(telefone_cli)
                
                if cliente:
                    cli_nome = cliente.get('Nome', 'Sem Nome')
                    cli_pontos = int(cliente.get('Pontos', 0))
                    
                    # CARD DASHBOARD PREMIUM EM HTML
                    st.markdown(f"""
                        <div class="client-card">
                            <h3>{cli_nome}</h3>
                            <h1>{cli_pontos} / 10</h1>
                            <p>Pontos Atuais</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("➕ ADICIONAR 1 PONTO", type="primary", use_container_width=True):
                        novos_pontos = cli_pontos + 1
                        update_points(linha, novos_pontos)
                        st.success(f"Ponto Adicionado!")
                        
                        msg = f"Fala {cli_nome}, beleza? Você ganhou +1 ponto no Cartão Fidelidade! ✂️\n\nFaltam só {10 - novos_pontos} para o corte GRÁTIS!" if novos_pontos < 10 else f"Parabéns {cli_nome}! 🎉 Você completou 10 pontos! Próximo corte é GRÁTIS! ✂️"
                        msg_encoded = urllib.parse.quote(msg)
                        st.markdown(f'<a href="https://wa.me/55{telefone_cli}?text={msg_encoded}" target="_blank" class="btn-zap">📱 AVISAR NO WHATSAPP</a>', unsafe_allow_html=True)
                        
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
                    st.markdown("<br>", unsafe_allow_html=True)
                    novo_nome = st.text_input("Nome", value=str(cliente.get('Nome', '')))
                    novo_telefone = st.text_input("WhatsApp", value=str(cliente.get('Telefone', '')))
                    novo_email = st.text_input("E-mail", value=str(cliente.get('Email', '')))

                    st.write("")
                    if st.button("💾 SALVAR", type="primary", use_container_width=True):
                        planilha.update_cell(linha, 1, str(novo_telefone))
                        planilha.update_cell(linha, 2, str(novo_nome))
                        planilha.update_cell(linha, 3, str(novo_email))
                        st.success("Atualizado!")
                            
                    if st.button("🗑️ EXCLUIR CLIENTE", type="secondary", use_container_width=True):
                        planilha.delete_rows(linha)
                        st.success("Removido!")
                        st.rerun()

        elif acao == "Ver Todos":
            registros = get_all_clients()
            if registros:
                st.table(pd.DataFrame(registros))
            else:
                st.info("Nenhum cliente cadastrado.")
                
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("SAIR DO SISTEMA", type="tertiary"):
            st.session_state['autenticado'] = False
            st.rerun()

# ==========================================
# 6. RODAPÉ 
# ==========================================
st.markdown("""
    <div class="rodape-ufo">
        Desenvolvido por UFO Digital Agency<br>
        Ilton Cabeleireiro - +55 35 8702-2576
    </div>
""", unsafe_allow_html=True)
