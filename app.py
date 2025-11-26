import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.supabase_client import get_supabase_client

# Page configuration
st.set_page_config(
    page_title="Gestão de Rifas - Escuteiros",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.markdown('<h1 class="main-header">🎫 Sistema de Gestão de Rifas dos Escuteiros</h1>', unsafe_allow_html=True)

# Initialize Supabase client
try:
    supabase = get_supabase_client()
    
    # Buscar todas as campanhas e definir seleção (inclui opção 'Todas Campanhas')
    campanhas_resp = supabase.table('campanhas').select('*').order('created_at', desc='desc').execute()
    campanhas_list = campanhas_resp.data if campanhas_resp.data else []

    if not campanhas_list:
        st.warning("⚠️ Nenhuma campanha criada. Por favor, crie uma campanha na página 'Campanhas'.")
        campanha_id = None
    else:
        # construir dict nome->campanha e identificar campanha ativa
        campanhas_dict = {c['nome']: c for c in campanhas_list}
        default_idx = 0
        for idx, c in enumerate(campanhas_list):
            if c.get('ativa', False):
                default_idx = idx
                break

        # inserir opção para todas as campanhas
        options = ['Todas Campanhas'] + [c['nome'] for c in campanhas_list]
        # determine selected name defaulting to active
        default_name = campanhas_list[default_idx]['nome'] if campanhas_list else None
        selected_name = st.selectbox("🎯 Selecionar Campanha", options=options, index=0 if default_name is None else options.index(default_name))

        if selected_name == 'Todas Campanhas':
            selected_campanha = None
            campanha_id = None
            st.success(f"✅ Conectado | 📅 Visualizando: Todas as Campanhas")
        else:
            selected_campanha = campanhas_dict[selected_name]
            campanha_id = selected_campanha['id']
            st.success(f"✅ Conectado | 📅 Campanha: **{selected_campanha['nome']}**")
except ValueError as e:
    st.error(f"❌ Erro ao conectar ao Supabase")
    st.error(str(e))
    campanha_id = None
    st.stop()

# Welcome section
with st.expander("ℹ️ Sobre o Sistema", expanded=False):
    st.markdown("""
    ## Bem-vindo ao Sistema de Gestão de Rifas! 🎯

    Este sistema permite gerir todos os aspectos das rifas dos escuteiros de forma simples e eficiente.

    ### 📋 Funcionalidades disponíveis:

    - **👥 Escuteiros**: Gerir escuteiros que vendem rifas (criar, editar, visualizar)
    - **🎟️ Blocos de Rifas**: Criar e atribuir blocos de rifas aos escuteiros
    - **📦 Recebimento**: Registar canhotos e dinheiro recebidos dos escuteiros
    - **🔄 Devoluções**: Gerir devoluções de blocos (total ou parcial)

    ### 🚀 Como funciona:

    1. **Registar Escuteiros**: Comece por adicionar os escuteiros na página "👥 Escuteiros"
    2. **Criar Campanha**: Crie uma campanha na página "📅 Campanhas" (cria blocos automaticamente)
    3. **Atribuir Blocos**: Atribua blocos aos escuteiros na página "🎟️ Blocos de Rifas"
    4. **Escuteiros Vendem**: Escuteiros vendem rifas aos compradores (externamente)
    5. **Registar Recebimento**: Quando escuteiro entrega canhotos + dinheiro, registe na página "📦 Recebimento"
    """)

st.markdown("---")

# Dashboard Statistics
st.subheader("📊 Dashboard - Visão Geral")

# Nota: campanha_id == None significa 'Todas Campanhas' (ou nenhuma campanha criada).

try:
    # Fetch data filtered by selected campaign (or all campaigns)
    # Blocks
    if campanha_id:
        blocos_response = supabase.table('blocos_rifas').select('*').eq('campanha_id', campanha_id).execute()
    else:
        blocos_response = supabase.table('blocos_rifas').select('*').execute()

    # Escuteiros: if a campaign is selected, count only escuteiros who have blocks in that campaign
    if campanha_id:
        # collect escuteiro ids from blocks
        escuteiro_ids = [b.get('escuteiro_id') for b in (blocos_response.data or []) if b.get('escuteiro_id')]
        if escuteiro_ids:
            escuteiros_response = supabase.table('escuteiros').select('*', count='exact').in_('id', escuteiro_ids).execute()
        else:
            # no escuteiros assigned in this campaign
            escuteiros_response = type('obj', (object,), {'data': []})()
    else:
        escuteiros_response = supabase.table('escuteiros').select('*', count='exact').execute()

    # Vendas
    if campanha_id:
        vendas_response = supabase.table('vendas').select('*, blocos_rifas!inner(campanha_id)').eq('blocos_rifas.campanha_id', campanha_id).execute()
    else:
        vendas_response = supabase.table('vendas').select('*').execute()

    # Recebimentos (pagamentos)
    if campanha_id:
        if blocos_response.data:
            bloco_ids = [b['id'] for b in blocos_response.data]
            recebimentos_response = supabase.table('pagamentos').select('*').in_('bloco_id', bloco_ids).execute()
        else:
            recebimentos_response = type('obj', (object,), {'data': []})()
    else:
        recebimentos_response = supabase.table('pagamentos').select('*').execute()
    total_escuteiros = len(escuteiros_response.data) if escuteiros_response.data else 0
    total_blocos = len(blocos_response.data) if blocos_response.data else 0
    total_vendas = len(vendas_response.data) if vendas_response.data else 0
    total_recebimentos = len(recebimentos_response.data) if recebimentos_response.data else 0
    
    # Calculate financial data
    valor_total_vendas = sum(float(v.get('valor_total', 0)) for v in vendas_response.data) if vendas_response.data else 0
    valor_total_recebido = sum(float(p.get('valor_pago', 0)) for p in recebimentos_response.data) if recebimentos_response.data else 0
    saldo_pendente = valor_total_vendas - valor_total_recebido
    
    # Calculate total raffle tickets
    total_rifas_vendidas = sum(int(v.get('quantidade', 0)) for v in vendas_response.data) if vendas_response.data else 0
    
    # Display main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Escuteiros Ativos",
            value=total_escuteiros,
            help="Total de escuteiros registados no sistema"
        )
    
    with col2:
        st.metric(
            label="🎟️ Blocos de Rifas",
            value=total_blocos,
            help="Total de blocos de rifas criados"
        )
    
    with col3:
        st.metric(
            label="💰 Vendas Registadas",
            value=total_vendas,
            delta=f"{total_rifas_vendidas} rifas vendidas",
            help="Total de vendas registadas no sistema"
        )
    
    with col4:
        st.metric(
            label="📦 Recebimentos Registados",
            value=total_recebimentos,
            help="Total de recebimentos (canhotos + dinheiro) registados"
        )
    
    # Financial summary
    st.markdown("### 💶 Resumo Financeiro")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="Valor Total de Vendas",
            value=f"{valor_total_vendas:.2f} €",
            help="Valor total de todas as vendas registadas"
        )
    
    with col2:
        st.metric(
            label="Total Recebido",
            value=f"{valor_total_recebido:.2f} €",
            help="Valor total já recebido dos escuteiros"
        )
    
    with col3:
        delta_color = "inverse" if saldo_pendente > 0 else "normal"
        st.metric(
            label="Saldo Pendente",
            value=f"{saldo_pendente:.2f} €",
            delta=f"{(valor_total_recebido/valor_total_vendas*100):.1f}% recebido" if valor_total_vendas > 0 else "0% recebido",
            help="Valor ainda por receber dos escuteiros"
        )
    
    # Charts section
    if vendas_response.data and len(vendas_response.data) > 0:
        st.markdown("---")
        st.subheader("📈 Análise de Dados")
        
        tab1, tab2, tab3 = st.tabs(["Vendas por Escuteiro", "Evolução Temporal", "Estado dos Blocos"])
        
        with tab1:
            # Sales by scout
            try:
                if campanha_id:
                    vendas_detalhadas = supabase.table('vendas').select('*, escuteiros(nome), blocos_rifas!inner(campanha_id)').eq('blocos_rifas.campanha_id', campanha_id).execute()
                else:
                    vendas_detalhadas = supabase.table('vendas').select('*, escuteiros(nome)').execute()

                if vendas_detalhadas.data:
                    df_vendas = pd.DataFrame(vendas_detalhadas.data)
                    df_vendas['escuteiro_nome'] = df_vendas['escuteiros'].apply(
                        lambda x: x['nome'] if x else 'Desconhecido'
                    )

                    # Group by scout
                    vendas_por_escuteiro = df_vendas.groupby('escuteiro_nome').agg({
                        'valor_total': 'sum',
                        'quantidade': 'sum'
                    }).reset_index()
                    vendas_por_escuteiro.columns = ['Escuteiro', 'Valor Total (€)', 'Rifas Vendidas']
                    vendas_por_escuteiro = vendas_por_escuteiro.sort_values('Valor Total (€)', ascending=False)

                    # Create bar chart
                    fig = px.bar(
                        vendas_por_escuteiro,
                        x='Escuteiro',
                        y='Valor Total (€)',
                        text='Rifas Vendidas',
                        title='Vendas por Escuteiro',
                        color='Valor Total (€)',
                        color_continuous_scale='Blues'
                    )
                    fig.update_traces(texttemplate='%{text} rifas', textposition='outside')
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)

                    # Show table
                    st.dataframe(
                        vendas_por_escuteiro,
                        hide_index=True,
                        use_container_width=True
                    )
            except Exception as e:
                st.warning(f"Não foi possível carregar o gráfico de vendas: {str(e)}")
        
        with tab2:
            # Sales over time
            try:
                df_vendas_tempo = pd.DataFrame(vendas_response.data)
                df_vendas_tempo['data_venda'] = pd.to_datetime(df_vendas_tempo['data_venda'])
                df_vendas_tempo['data'] = df_vendas_tempo['data_venda'].dt.date
                
                vendas_diarias = df_vendas_tempo.groupby('data').agg({
                    'valor_total': 'sum',
                    'quantidade': 'sum'
                }).reset_index()
                
                # Create line chart
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=vendas_diarias['data'],
                    y=vendas_diarias['valor_total'],
                    mode='lines+markers',
                    name='Valor (€)',
                    line=dict(color='#1f77b4', width=3)
                ))
                fig.update_layout(
                    title='Evolução das Vendas ao Longo do Tempo',
                    xaxis_title='Data',
                    yaxis_title='Valor Total (€)',
                    height=400,
                    hovermode='x unified'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Show summary table
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Média Diária", f"{vendas_diarias['valor_total'].mean():.2f} €")
                with col2:
                    st.metric("Melhor Dia", f"{vendas_diarias['valor_total'].max():.2f} €")
            except Exception as e:
                st.warning(f"Não foi possível carregar o gráfico temporal: {str(e)}")
        
        with tab3:
            # Block status
            try:
                if blocos_response.data:
                    df_blocos = pd.DataFrame(blocos_response.data)
                    
                    # Check if 'estado' column exists
                    if 'estado' in df_blocos.columns:
                        status_count = df_blocos['estado'].value_counts().reset_index()
                        status_count.columns = ['Estado', 'Quantidade']
                        
                        # Create pie chart
                        fig = px.pie(
                            status_count,
                            values='Quantidade',
                            names='Estado',
                            title='Distribuição do Estado dos Blocos',
                            color_discrete_sequence=px.colors.qualitative.Set3
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("A coluna 'estado' não existe na tabela blocos_rifas. Execute o schema SQL atualizado.")
            except Exception as e:
                st.warning(f"Não foi possível carregar o gráfico de estados: {str(e)}")
    
    else:
        st.info("📝 Ainda não há dados suficientes para mostrar gráficos. Comece por registar vendas!")
    
except Exception as e:
    st.error(f"⚠️ Erro ao carregar dados do dashboard: {str(e)}")
    st.info("""
    **Possíveis soluções:**
    
    1. Verifique se as tabelas foram criadas na base de dados Supabase
    2. Consulte o ficheiro `utils/database_schema.py` para o schema SQL completo
    3. Execute o SQL no Supabase SQL Editor
    4. Verifique se as credenciais estão corretas
    """)

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>💙 Sistema desenvolvido para gestão de rifas dos escuteiros</p>
        <p><small>Use o menu lateral para navegar entre as páginas</small></p>
    </div>
    """, unsafe_allow_html=True)
