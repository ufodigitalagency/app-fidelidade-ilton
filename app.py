import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import urllib.parse

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E CSS REFINADO
# ==========================================
st.set_page_config(page_title="Ilton Fidelidade Digital", page_icon="✂️", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800&display=swap');

    /* Ocultar elementos padrão do Streamlit */
    [data-testid="collapsedControl"] {display: none;}
    [data-testid="stToolbar"] {visibility: hidden;}

    /* Fundo principal escuro */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Fonte moderna e robusta para o título */
    h1 {
        font-family: 'Montserrat', sans-serif !important;
        color: #D4AF37 !important; 
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: -30px;
        font-size: 2.8rem !important;
    }
    
    h2, h3 {
        color: #C0C0C0 !important; 
    }
    
    /* ANIMAÇÃO DE PULSO PARA BOTÕES PRINCIPAIS */
    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 51, 51, 0.6); }
        70% { box-shadow: 0 0 0 12px rgba(255, 51, 51, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255, 51, 51, 0); }
    }

    /* Botões Primários (Ação, Salvar, Buscar) com Efeito Chamativo */
    div[data-testid="stButton"] button[kind="primary"] {
        background: linear-gradient(45deg, #ff1a1a, #e60000) !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
        animation: pulse 2s infinite; /* Aplica o efeito pulsante */
        transition: transform 0.2s ease-in-out !important;
        padding: 10px !important;
    }
    div[data-testid="stButton"] button[kind="primary"]:hover {
        transform: scale(1.03); /* Dá um leve zoom ao passar o mouse */
        background: linear-gradient(45deg, #ff4d4d, #ff0000) !important;
    }

    /* Botões Secundários (Voltar, Sair) */
    div[data-testid="stButton"] button[kind="secondary"] {
        background-color: #2A2A2A !important;
        color: #AAAAAA !important;
        border: 1px solid #444 !important;
        border-radius: 8px !important;
        font-weight: bold !important;
        text-transform: uppercase;
        transition: 0.3s !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        background-color: #333 !important;
        color: #FFF !important;
        border-color: #666 !important;
    }
    
    /* Botão Verde para o WhatsApp */
    .btn-zap {
        background-color: #25D366 !important;
        color: white !important;
        border-radius: 8px;
        border: none;
        padding: 10px;
        font-weight: bold;
        width: 100%;
        text-transform: uppercase;
        text-align: center;
        display: block;
        text-decoration: none;
        margin-top: 15px;
        transition: 0.3s;
    }
    .btn-zap:hover {
        background-color: #1ebe57 !important;
    }
    
    /* Caixas de texto */
    .stTextInput>div>div>input, .stSelectbox>div>div>div {
        background-color: #1a1c24 !important;
        color: white !important;
        border: 1px solid #444 !important;
        transition: 0.3s;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #2b7cff !important;
        box-shadow: 0 0 8px rgba(255, 51, 51, 0.6) !important;
    }
    
    /* Tabelas */
    table {
        color: #FAFAFA !important;
        background-color: #1a1c24 !important;
        border-radius: 8px;
        width: 100%;
    }
    thead tr th {
        background-color: #2b7cff !important;
        color: white !important;
    }
    
    /* Rodapé */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #111;
        color: #666;
        text-align: center;
        padding: 12px;
        font-size: 0.75rem;
        border-top: 1px solid #222;
        z-index: 999;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CONTROLE DE NAVEGAÇÃO E BANCO DE DADOS
# ==========================================
if 'pagina_atual' not in st.session_state:
    st.session_state['pagina_atual'] = 'inicio'

def mudar_pagina(nova_pagina):
    st.session_state['pagina_atual'] = nova_pagina

conn = sqlite3.connect('barbearia.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS clientes (telefone TEXT PRIMARY KEY, nome TEXT, email TEXT, pontos INTEGER)')
conn.commit()

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
# TELA 1: INÍCIO (Escolha de Perfil)
# ==========================================
if st.session_state['pagina_atual'] == 'inicio':
    st.write("<br><h4 style='text-align: center; color: #C0C0C0;'>Selecione seu acesso:</h4><br>", unsafe_allow_html=True)
    
    # Criamos 4 colunas para empurrar os botões para o centro perfeitamente
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
        
        # Agora usando type="primary" para ficar com o efeito vermelho
        if st.button("Buscar meus pontos", type="primary"):
            if telefone_busca:
                c.execute('SELECT nome, pontos FROM clientes WHERE telefone=?', (telefone_busca,))
                resultado = c.fetchone()
                
                if resultado:
                    nome, pontos = resultado
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
                try:
                    c.execute('INSERT INTO clientes (telefone, nome, email, pontos) VALUES (?, ?, ?, 0)', (novo_telefone, novo_nome, novo_email))
                    conn.commit()
                    st.success(f"Show, {novo_nome}! Seu cadastro foi feito. Você já pode avisar o barbeiro no seu próximo corte!")
                    st.balloons()
                except sqlite3.IntegrityError:
                    st.error("Opa! Esse número de WhatsApp já está cadastrado. Vá na aba 'Ver meus pontos'.")
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
            c.execute("SELECT telefone, nome FROM clientes")
            todos_clientes = c.fetchall()
            
            opcoes_clientes = [""] + [f"{nome} - {tel}" for tel, nome in todos_clientes]
            cliente_selecionado = st.selectbox("Digite ou selecione o Nome/WhatsApp do cliente:", opcoes_clientes)

            if cliente_selecionado != "":
                telefone_cli = cliente_selecionado.split(" - ")[-1]
                
                c.execute('SELECT nome, pontos, email FROM clientes WHERE telefone=?', (telefone_cli,))
                resultado = c.fetchone()
                
                if resultado:
                    cli_nome = resultado[0]
                    cli_pontos = resultado[1]
                    cli_email = resultado[2]
                    
                    st.write("---")
                    st.write(f"👤 **Cliente:** {cli_nome} | 📧 **E-mail:** {cli_email}")
                    st.write(f"⭐ **Pontos Atuais:** {cli_pontos} de 10")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("➕ Adicionar 1 Ponto", type="primary"):
                            novos_pontos = cli_pontos + 1
                            c.execute('UPDATE clientes SET pontos=? WHERE telefone=?', (novos_pontos, telefone_cli))
                            conn.commit()
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
                            c.execute('UPDATE clientes SET pontos=0 WHERE telefone=?', (telefone_cli,))
                            conn.commit()
                            st.success("Pontos zerados. Novo ciclo iniciado!")
                            st.rerun()

        elif acao == "Ver Todos os Clientes":
            df = pd.read_sql_query("SELECT nome as Nome, telefone as WhatsApp, email as Email, pontos as Pontos FROM clientes", conn)
            st.table(df)

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