import streamlit as st
import pandas as pd
import time
import random
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json

# Configuração da página
st.set_page_config(
    page_title="Demo - Integração RD Station × CIGAM ERP | AddLife Diagnósticos",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado com cores da AddLife
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #E53E3E 0%, #C53030 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .addlife-logo {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        text-align: center;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .logo-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
    }
    .logo-icon {
        width: 50px;
        height: 50px;
        background: linear-gradient(135deg, #E53E3E 0%, #C53030 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    .logo-icon::before {
        content: "💧";
        color: white;
        font-size: 24px;
        transform: rotate(-20deg);
    }
    .logo-text {
        font-family: 'Arial', sans-serif;
        font-size: 28px;
        font-weight: bold;
        color: #666;
    }
    .logo-add {
        color: #666;
    }
    .logo-life {
        color: #E53E3E;
        font-style: italic;
    }
    .logo-subtitle {
        font-size: 12px;
        color: #999;
        margin-left: 5px;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #E53E3E;
    }
    .sync-success {
        background: #d4edda;
        color: #155724;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    .sync-error {
        background: #f8d7da;
        color: #721c24;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    .sync-info {
        background: #d1ecf1;
        color: #0c5460;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }
    .client-card {
        background: #fef2f2;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #E53E3E;
    }
</style>
""", unsafe_allow_html=True)

# Header principal com logotipo AddLife
st.markdown("""
<div class="main-header">
    <div class="addlife-logo">
        <div class="logo-container">
            <div>
                <img src="https://images.tcdn.com.br/files/1172397/themes/7/img/settings/logo.png" 
             alt="AddLife Diagnósticos" 
             style="max-width: 200px; height: auto;">
            </div>
        </div>
    </div>
    <h1>🔄 Integração RD Station × CIGAM ERP</h1>
    <p>Demonstração Personalizada dos Fluxos de Sincronização para Laboratórios</p>
</div>
""", unsafe_allow_html=True)

# Dados fictícios específicos para AddLife (laboratórios e hospitais como clientes)
@st.cache_data
def gerar_dados_addlife():
    # Leads do RD Station - Laboratórios e Hospitais
    leads_rd = [
        {"id": "RD001", "nome": "Laboratório Santa Clara", "email": "compras@labsantaclara.com.br", "telefone": "(31) 98765-4321", "status": "Oportunidade", "cnpj": "12.345.678/0001-90", "interesse": "Equipamento Hematologia"},
        {"id": "RD002", "nome": "Hospital das Clínicas BH", "email": "suprimentos@hcbh.org.br", "telefone": "(31) 91234-5678", "status": "Lead Qualificado", "cnpj": "98.765.432/0001-10", "interesse": "Reagentes Bioquímica"},
        {"id": "RD003", "nome": "Lab Diagnose Premium", "email": "contato@diagnose.com.br", "telefone": "(31) 99988-7766", "status": "Oportunidade", "cnpj": "11.222.333/0001-44", "interesse": "Gasometria + Point of Care"},
        {"id": "RD004", "nome": "Centro Médico Mater Dei", "email": "compras@materdei.com.br", "telefone": "(31) 95555-4444", "status": "Negociação", "cnpj": "55.666.777/0001-88", "interesse": "Kit Hemoglobina Glicada"},
        {"id": "RD005", "nome": "Laboratório Biocenter", "email": "gerencia@biocenter.com.br", "telefone": "(31) 94444-3333", "status": "Lead Qualificado", "cnpj": "77.888.999/0001-22", "interesse": "Uroanálise Automatizada"},
    ]
    
    # Clientes no CIGAM ERP
    clientes_cigam = [
        {"id": "CLI001", "codigo": "12.345.678/0001-90", "nome": "Laboratório Santa Clara", "limite_credito": 180000, "saldo_devedor": 45000, "status": "Ativo", "tipo": "Laboratório Privado"},
        {"id": "CLI002", "codigo": "98.765.432/0001-10", "nome": "Hospital das Clínicas BH", "limite_credito": 500000, "saldo_devedor": 0, "status": "Ativo", "tipo": "Hospital Público"},
        {"id": "CLI003", "codigo": "11.222.333/0001-44", "nome": "Lab Diagnose Premium", "limite_credito": 220000, "saldo_devedor": 32000, "status": "Ativo", "tipo": "Laboratório Premium"},
    ]
    
    # Pedidos específicos da área médica
    pedidos = [
        {"id": "PED001", "cliente_id": "CLI001", "rd_deal_id": "RD001", "valor": 95000, "status": "Entregue", "data": "2025-06-10", "equipamento": "Analisador Hematológico XL-640"},
        {"id": "PED002", "cliente_id": "CLI002", "rd_deal_id": "RD002", "valor": 12500, "status": "Em Trânsito", "data": "2025-06-12", "equipamento": "Kit Reagentes Bioquímica (50 testes)"},
        {"id": "PED003", "cliente_id": "CLI003", "rd_deal_id": "RD003", "valor": 165000, "status": "Instalação Agendada", "data": "2025-06-14", "equipamento": "Sistema Gasometria + Point of Care"},
    ]
    
    # Produtos/Equipamentos específicos AddLife
    produtos = [
        {"codigo": "HEMA-XL640", "nome": "Analisador Hematológico XL-640", "estoque": 8, "preco": 95000, "categoria": "Hematologia", "fabricante": "Erba Mannheim"},
        {"codigo": "BIO-KIT50", "nome": "Kit Reagentes Bioquímica (50 testes)", "estoque": 150, "preco": 2500, "categoria": "Bioquímica", "fabricante": "Kovalent"},
        {"codigo": "GASO-POC", "nome": "Sistema Gasometria + Point of Care", "estoque": 3, "preco": 165000, "categoria": "Gasometria", "fabricante": "Siemens Healthineers"},
        {"codigo": "HBA1C-KIT", "nome": "Kit Hemoglobina Glicada", "estoque": 45, "preco": 1800, "categoria": "Marcador Cardíaco", "fabricante": "Afias"},
        {"codigo": "URIN-AUTO", "nome": "Analisador Uroanálise Automatizada", "estoque": 12, "preco": 75000, "categoria": "Uroanálise", "fabricante": "Erba Mannheim"},
        {"codigo": "COAG-XL", "nome": "Analisador Coagulação XL-200", "estoque": 6, "preco": 120000, "categoria": "Coagulação", "fabricante": "Erba Brasil"},
    ]
    
    return leads_rd, clientes_cigam, pedidos, produtos

# Inicializar dados específicos AddLife
if 'dados_addlife_inicializados' not in st.session_state:
    st.session_state.leads_rd, st.session_state.clientes_cigam, st.session_state.pedidos, st.session_state.produtos = gerar_dados_addlife()
    st.session_state.logs = []
    st.session_state.metricas = {
        'sincronizacoes_hoje': 28,
        'equipamentos_vendidos': 7,
        'leads_laboratorios': 15,
        'assistencias_agendadas': 5
    }
    st.session_state.dados_addlife_inicializados = True

# Sidebar - Controles específicos AddLife
st.sidebar.header("🎛️ Controles da Demonstração AddLife")

# Informações da AddLife
st.sidebar.markdown("""
### 🏥 AddLife Diagnósticos
**Fundada:** 2002 • **Sede:** Belo Horizonte/MG  
**Diretor:** Robson Resende Pereira  
**Atuação:** Minas Gerais e regiões  
""")

# Seleção do fluxo específico para negócio de equipamentos médicos
fluxo_demo = st.sidebar.selectbox(
    "Escolha o Fluxo para Demonstrar:",
    [
        "1. 🏥 Laboratório Lead → Cliente ERP",
        "2. 📋 Orçamento Equipamento → Pedido ERP",
        "3. 📊 Status Entrega → Atualizar CRM",
        "4. 💰 Situação Financeira → CRM",
        "5. 📦 Consulta Estoque Equipamentos",
        "6. 📈 Histórico Compras Laboratório",
        "7. 💲 Tabela Preços por Categoria"
    ]
)

# Botão para executar demonstração
if st.sidebar.button("▶️ Executar Demonstração", type="primary"):
    st.session_state.executar_demo = True

# Configurações
st.sidebar.header("⚙️ Configurações")
velocidade_demo = st.sidebar.slider("Velocidade da Demo (segundos)", 0.5, 3.0, 1.5)
mostrar_logs_detalhados = st.sidebar.checkbox("Mostrar Logs Detalhados", True)
simular_erro = st.sidebar.checkbox("Simular Erro de Conexão", False)

# Layout principal
col1, col2 = st.columns([2, 1])

with col1:
    st.header("📊 Dashboard de Vendas e Operações")
    
    # Métricas específicas AddLife
    met_col1, met_col2, met_col3, met_col4 = st.columns(4)
    
    with met_col1:
        st.metric(
            "Sincronizações Hoje", 
            st.session_state.metricas['sincronizacoes_hoje'],
            delta="↗️ +8 vs ontem"
        )
    
    with met_col2:
        st.metric(
            "Equipamentos Vendidos", 
            st.session_state.metricas['equipamentos_vendidos'],
            delta="🎯 Meta: 10/mês"
        )
    
    with met_col3:
        st.metric(
            "Leads Laboratórios", 
            st.session_state.metricas['leads_laboratorios'],
            delta="↗️ +4 esta semana"
        )
    
    with met_col4:
        st.metric(
            "Assistências Agendadas", 
            st.session_state.metricas['assistencias_agendadas'],
            delta="🔧 Preventivas"
        )

with col2:
    st.header("🔄 Status Sistema AddLife")
    
    # Status das conexões
    st.markdown("**Integrações Ativas:**")
    st.success("🟢 RD Station Marketing - Conectado")
    st.success("🟢 RD Station CRM - Conectado") 
    st.success("🟢 CIGAM ERP - Conectado")
    st.info("🔵 Sistema Assistência Técnica - OK")
    
    # Última sincronização
    st.markdown("**Última Sincronização:**")
    st.info(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
    
    # Próximas tarefas
    st.markdown("**Próximas Atividades:**")
    st.warning("📅 Instalação Lab Diagnose - 16/06")
    st.warning("🔧 Manutenção HC BH - 17/06")

# Função para simular API calls específicas AddLife
def simular_api_call_addlife(sistema, endpoint, metodo="GET", dados=None):
    """Simula chamadas API específicas para o negócio AddLife"""
    time.sleep(random.uniform(0.8, 2.0))  # Tempo mais realista
    
    if simular_erro and random.random() < 0.15:  # 15% chance erro quando ativado
        return {"status": "error", "message": "Timeout na conexão com servidor"}
    
    return {
        "status": "success", 
        "data": dados or {"message": f"Operação {metodo} em {endpoint} concluída"},
        "timestamp": datetime.now().isoformat()
    }

# Função para adicionar log específico AddLife
def adicionar_log_addlife(tipo, sistema, mensagem):
    """Adiciona log com contexto específico AddLife"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "tipo": tipo,
        "sistema": sistema,
        "mensagem": mensagem
    }
    st.session_state.logs.insert(0, log_entry)
    
    if len(st.session_state.logs) > 50:
        st.session_state.logs = st.session_state.logs[:50]

# Demonstrações específicas AddLife
if 'executar_demo' in st.session_state and st.session_state.executar_demo:
    
    demo_container = st.container()
    
    with demo_container:
        st.header(f"🎬 Demonstração AddLife: {fluxo_demo}")
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        if fluxo_demo.startswith("1."):
            # Fluxo 1: Laboratório Lead → Cliente ERP
            status_text.text("Processando novo lead de laboratório...")
            progress_bar.progress(10)
            time.sleep(velocidade_demo)
            
            adicionar_log_addlife("INFO", "RD Station", "Webhook: Lead 'Laboratório Santa Clara' marcado como oportunidade - Interesse: Equipamento Hematologia")
            status_text.text("📥 Webhook recebido - Laboratório interessado em equipamento...")
            progress_bar.progress(25)
            time.sleep(velocidade_demo)
            
            status_text.text("🔍 Consultando histórico do laboratório...")
            resultado_rd = simular_api_call_addlife("RD Station", "/platform/contacts/RD001", "GET")
            
            if resultado_rd["status"] == "success":
                adicionar_log_addlife("SUCCESS", "RD Station", "Dados completos do laboratório recuperados")
                progress_bar.progress(50)
                time.sleep(velocidade_demo)
                
                status_text.text("🏥 Classificando tipo de laboratório (Privado/Público)...")
                progress_bar.progress(65)
                time.sleep(velocidade_demo)
                
                status_text.text("📤 Criando cadastro no CIGAM ERP...")
                dados_lab = {
                    "razao_social": "Laboratório Santa Clara",
                    "cnpj": "12.345.678/0001-90",
                    "email": "compras@labsantaclara.com.br",
                    "telefone": "(31) 98765-4321",
                    "tipo_cliente": "Laboratório Privado",
                    "segmento": "Diagnóstico Clínico",
                    "limite_credito": 180000
                }
                
                resultado_cigam = simular_api_call_addlife("CIGAM", "/api/clientes", "POST", dados_lab)
                
                if resultado_cigam["status"] == "success":
                    adicionar_log_addlife("SUCCESS", "CIGAM", "Laboratório cadastrado - ID: CLI004 | Limite R$ 180.000")
                    progress_bar.progress(85)
                    time.sleep(velocidade_demo)
                    
                    status_text.text("🎯 Criando oportunidade para equipamento hematologia...")
                    progress_bar.progress(100)
                    adicionar_log_addlife("SUCCESS", "Sistema", "Lead → Cliente: RD001 → CLI004 | Produto sugerido: Analisador XL-640")
                    
                    st.success("✅ Laboratório convertido em cliente com sucesso!")
                    
                    # Card do novo cliente
                    st.markdown("""
                    <div class="client-card">
                        <h4>🏥 Novo Cliente Cadastrado</h4>
                        <p><strong>Laboratório:</strong> Santa Clara<br>
                        <strong>Tipo:</strong> Laboratório Privado<br>
                        <strong>Interesse:</strong> Analisador Hematológico XL-640<br>
                        <strong>Limite Crédito:</strong> R$ 180.000<br>
                        <strong>Próximo Passo:</strong> Agendamento visita técnica</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
        elif fluxo_demo.startswith("2."):
            # Fluxo 2: Orçamento Equipamento → Pedido ERP
            status_text.text("Processando orçamento de equipamento médico...")
            progress_bar.progress(15)
            
            adicionar_log_addlife("INFO", "RD Station CRM", "Orçamento aprovado: Sistema Gasometria POC - R$ 165.000")
            time.sleep(velocidade_demo)
            
            status_text.text("🔍 Verificando disponibilidade do equipamento...")
            progress_bar.progress(30)
            time.sleep(velocidade_demo)
            
            status_text.text("💳 Consultando limite de crédito do laboratório...")
            progress_bar.progress(50)
            adicionar_log_addlife("SUCCESS", "CIGAM", "Limite aprovado: R$ 165.000 disponível de R$ 220.000")
            time.sleep(velocidade_demo)
            
            status_text.text("📋 Gerando pedido no ERP...")
            pedido_data = {
                "cliente_id": "CLI003",
                "equipamento": "Sistema Gasometria + Point of Care",
                "codigo": "GASO-POC",
                "valor_unitario": 165000,
                "quantidade": 1,
                "instalacao_inclusa": True,
                "treinamento_incluso": True,
                "garantia_meses": 24
            }
            resultado = simular_api_call_addlife("CIGAM", "/api/pedidos", "POST", pedido_data)
            
            progress_bar.progress(80)
            adicionar_log_addlife("SUCCESS", "CIGAM", "Pedido PED004 criado | Instalação agendada para 20/06")
            time.sleep(velocidade_demo)
            
            status_text.text("📅 Agendando instalação e treinamento...")
            progress_bar.progress(100)
            adicionar_log_addlife("SUCCESS", "Sistema", "Instalação agendada | Equipe técnica notificada")
            
            st.success("✅ Pedido de equipamento processado com sucesso!")
            
            # Detalhes do pedido
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Valor do Pedido", "R$ 165.000")
                st.metric("Prazo Entrega", "5 dias úteis")
            with col_b:
                st.metric("Garantia", "24 meses")
                st.metric("Instalação", "✅ Incluída")
                
        elif fluxo_demo.startswith("3."):
            # Fluxo 3: Status Entrega → CRM
            status_text.text("Atualizando status de entrega no CRM...")
            progress_bar.progress(20)
            
            adicionar_log_addlife("INFO", "CIGAM", "Equipamento XL-640 entregue e instalado no Lab Santa Clara")
            time.sleep(velocidade_demo)
            
            status_text.text("✅ Confirmando instalação e treinamento...")
            progress_bar.progress(40)
            time.sleep(velocidade_demo)
            
            status_text.text("📞 Sincronizando com equipe comercial...")
            progress_bar.progress(70)
            resultado = simular_api_call_addlife("RD Station CRM", "/deals/RD001", "PUT", 
                                               {"status": "Equipamento Instalado", "proxima_acao": "Follow-up pós-venda"})
            time.sleep(velocidade_demo)
            
            progress_bar.progress(100)
            adicionar_log_addlife("SUCCESS", "RD Station CRM", "Status atualizado | Follow-up pós-venda agendado para 7 dias")
            st.success("✅ Status sincronizado com equipe comercial!")
            
            st.info("📋 **Próximas Ações:** Follow-up em 7 dias • Treinamento adicional se necessário • Apresentação novos produtos")
            
        elif fluxo_demo.startswith("4."):
            # Fluxo 4: Situação Financeira → CRM
            status_text.text("Consultando situação financeira dos laboratórios...")
            progress_bar.progress(25)
            
            adicionar_log_addlife("INFO", "CIGAM", "Analisando situação financeira - Hospital das Clínicas BH")
            time.sleep(velocidade_demo)
            
            status_text.text("💰 Calculando limite disponível...")
            progress_bar.progress(50)
            time.sleep(velocidade_demo)
            
            status_text.text("📊 Verificando histórico de pagamentos...")
            progress_bar.progress(75)
            
            info_financeira = {
                "limite_credito": 500000,
                "credito_disponivel": 500000,
                "inadimplente": False,
                "categoria_pagador": "Excelente",
                "prazo_medio_pagto": 30,
                "ultima_compra": "2025-05-15"
            }
            
            resultado = simular_api_call_addlife("RD Station CRM", "/contacts/update_financial", "PUT", info_financeira)
            progress_bar.progress(100)
            adicionar_log_addlife("SUCCESS", "RD Station CRM", "Situação financeira atualizada - Cliente Premium")
            st.success("✅ Informações financeiras sincronizadas!")
            
            # Dashboard financeiro
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Limite Total", "R$ 500.000", "🏛️ Público")
                st.metric("Disponível", "R$ 500.000", "💚 100%")
            with col_b:
                st.metric("Categoria", "Excelente", "⭐ Premium")
                st.metric("Prazo Médio", "30 dias", "📅 Pontual")
            with col_c:
                st.metric("Status", "✅ Adimplente", "🟢 Liberado")
                st.metric("Risco", "Baixo", "🛡️ Seguro")
                
        elif fluxo_demo.startswith("5."):
            # Fluxo 5: Consulta Estoque Equipamentos
            status_text.text("Consultando estoque de equipamentos médicos...")
            progress_bar.progress(25)
            
            adicionar_log_addlife("INFO", "Sistema", "Solicitação de consulta - Equipamentos Hematologia")
            time.sleep(velocidade_demo)
            
            status_text.text("📦 Verificando disponibilidade por categoria...")
            progress_bar.progress(60)
            
            resultado = simular_api_call_addlife("CIGAM", "/api/produtos/estoque", "GET")
            progress_bar.progress(85)
            time.sleep(velocidade_demo)
            
            status_text.text("🚚 Calculando prazos de entrega...")
            progress_bar.progress(100)
            adicionar_log_addlife("SUCCESS", "CIGAM", "Estoque consultado - 6 categorias disponíveis")
            st.success("✅ Estoque atualizado em tempo real!")
            
            # Mostrar estoque por categoria
            df_estoque = pd.DataFrame(st.session_state.produtos)
            
            # Gráfico de estoque por categoria
            fig_estoque = px.bar(
                df_estoque, 
                x='categoria', 
                y='estoque',
                color='categoria',
                title="Estoque Disponível por Categoria",
                labels={'estoque': 'Unidades', 'categoria': 'Categoria'}
            )
            st.plotly_chart(fig_estoque, use_container_width=True)
            
        elif fluxo_demo.startswith("6."):
            # Fluxo 6: Histórico Compras Laboratório
            status_text.text("Analisando histórico de compras do laboratório...")
            progress_bar.progress(30)
            
            adicionar_log_addlife("INFO", "CIGAM", "Consultando histórico - Laboratório Santa Clara")
            time.sleep(velocidade_demo)
            
            status_text.text("📈 Calculando padrões de consumo...")
            progress_bar.progress(70)
            time.sleep(velocidade_demo)
            
            progress_bar.progress(100)
            adicionar_log_addlife("SUCCESS", "RD Station CRM", "Histórico sincronizado - Insights de venda gerados")
            st.success("✅ Análise de histórico concluída!")
            
            # Dados do histórico
            historico_data = {
                "primeira_compra": "2023-03-15",
                "ultima_compra": "2025-05-20", 
                "total_investido": 340000,
                "equipamentos_adquiridos": 4,
                "categoria_preferida": "Hematologia",
                "frequencia_compra": "Trimestral",
                "ticket_medio": 85000
            }
            
            col_hist1, col_hist2, col_hist3 = st.columns(3)
            with col_hist1:
                st.metric("Total Investido", "R$ 340.000", "💰 Cliente VIP")
                st.metric("Equipamentos", "4 unidades", "🔬 Diversos")
            with col_hist2:
                st.metric("Frequência", "Trimestral", "📅 Regular")
                st.metric("Ticket Médio", "R$ 85.000", "💎 Premium")
            with col_hist3:
                st.metric("Categoria Preferida", "Hematologia", "🩸 Especialidade")
                st.metric("Próxima Compra", "Prevista Set/2025", "🎯 Prospecção")
                
        # Resetar flag
        st.session_state.executar_demo = False

# Seção de Logs específicos AddLife
st.header("📝 Logs de Operação AddLife")

if mostrar_logs_detalhados and st.session_state.logs:
    with st.container():
        for log in st.session_state.logs[:8]:  # Mostrar 8 mais recentes
            if log["tipo"] == "SUCCESS":
                st.markdown(f'<div class="sync-success">✅ {log["timestamp"]} | {log["sistema"]} | {log["mensagem"]}</div>', unsafe_allow_html=True)
            elif log["tipo"] == "ERROR":
                st.markdown(f'<div class="sync-error">❌ {log["timestamp"]} | {log["sistema"]} | {log["mensagem"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="sync-info">ℹ️ {log["timestamp"]} | {log["sistema"]} | {log["mensagem"]}</div>', unsafe_allow_html=True)

# Analytics específicos AddLife
st.header("📈 Analytics de Vendas AddLife")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    # Vendas por categoria de equipamento
    categorias = ["Hematologia", "Bioquímica", "Gasometria", "Uroanálise", "Coagulação", "Marcador Cardíaco"]
    vendas = [450000, 280000, 520000, 180000, 340000, 95000]
    
    fig_vendas = px.bar(
        x=categorias, 
        y=vendas,
        title="Faturamento por Categoria (Últimos 6 meses)",
        labels={"x": "Categoria", "y": "Faturamento (R$)"},
        color=vendas,
        color_continuous_scale="Blues"
    )
    fig_vendas.update_layout(height=350)
    st.plotly_chart(fig_vendas, use_container_width=True)

with col_graf2:
    # Pipeline de vendas
    pipeline_data = {
        "Estágio": ["Prospecção", "Qualificação", "Proposta", "Negociação", "Fechamento"],
        "Valor": [1200000, 850000, 520000, 380000, 165000]
    }
    
    fig_pipeline = px.funnel(
        pipeline_data,
        x="Valor",
        y="Estágio",
        title="Pipeline de Vendas AddLife"
    )
    fig_pipeline.update_layout(height=350)
    st.plotly_chart(fig_pipeline, use_container_width=True)

# Dados das tabelas específicos AddLife
st.header("🗃️ Base de Dados AddLife")

tab1, tab2, tab3 = st.tabs(["🏥 Laboratórios/Hospitais", "📋 Pedidos Equipamentos", "🔬 Produtos/Estoque"])

with tab1:
    st.subheader("Clientes - Laboratórios e Hospitais")
    df_clientes = pd.DataFrame(st.session_state.clientes_cigam)
    st.dataframe(df_clientes, use_container_width=True)

with tab2:
    st.subheader("Pedidos de Equipamentos e Reagentes")
    df_pedidos = pd.DataFrame(st.session_state.pedidos)
    st.dataframe(df_pedidos, use_container_width=True)

with tab3:
    st.subheader("Catálogo de Produtos AddLife")
    df_produtos = pd.DataFrame(st.session_state.produtos)
    st.dataframe(df_produtos, use_container_width=True)

# Footer específico AddLife
st.markdown("---")
st.markdown("""
### 🎯 Benefícios da Integração para AddLife Diagnósticos

- ⚡ **Gestão Automatizada de Leads**: Laboratórios e hospitais são automaticamente cadastrados
- 🔄 **Sincronização de Pedidos**: Orçamentos viram pedidos sem retrabalho manual
- 🎯 **Segmentação Inteligente**: Laboratórios privados vs hospitais públicos
- 📊 **Análise de Consumo**: Padrões de compra por tipo de equipamento
- 🔧 **Gestão de Assistência**: Integração com agenda de manutenções
- 💰 **Controle Financeiro**: Limites específicos por tipo de cliente

#### 🏥 Específico para o Setor de Diagnósticos:
- **Rastreamento de Equipamentos**: Por número de série e localização
- **Gestão de Garantias**: Controle automático de vencimentos
- **Alertas de Manutenção**: Preventivas baseadas em uso
- **Relatórios Regulatórios**: Para ANVISA e vigilância sanitária

*Demo personalizada para AddLife Diagnósticos - Tecnologia em Diagnósticos desde 2002*
""")

# Auto-refresh opcional
if st.sidebar.checkbox("Auto-refresh (10s)", False):
    time.sleep(10)
    st.rerun()