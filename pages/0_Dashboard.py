import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from utils.supabase_client import get_supabase_client


st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")


def safe_sum(iterable):
    return sum(float(x or 0) for x in iterable)


st.title("📊 Dashboard — Visão Geral")

try:
    supabase = get_supabase_client()
except Exception as e:
    st.error(f"❌ Erro ao conectar à base de dados: {e}")
    st.stop()

# Campaign selector: Todas + campanhas
campanhas_resp = supabase.table('campanhas').select('*').order('created_at', desc=True).execute()
campanhas = campanhas_resp.data or []

campanha_options = [("Todas", None)] + [(c['nome'], c['id']) for c in campanhas]

# Try to find an active campaign as default
active_camp = next((c for c in campanhas if c.get('ativa')), None)
default_idx = 0
if active_camp:
    # find its index in campanha_options
    for i, (_, cid) in enumerate(campanha_options):
        if cid == active_camp['id']:
            default_idx = i
            break

campanha_sel = st.selectbox("Selecionar Campanha", options=campanha_options, format_func=lambda x: x[0], index=default_idx)
campanha_id = campanha_sel[1]

st.markdown("---")

with st.spinner("A carregar métricas..."):
    # Fetch base data depending on selection
    # Escuteiros (global)
    esc_resp = supabase.table('escuteiros').select('*').execute()
    escuteiros = esc_resp.data or []

    # Campanhas (already have)
    total_campanhas = len(campanhas)

    # Blocos: filter by campanha if provided
    if campanha_id:
        blocos_resp = supabase.table('blocos_rifas').select('*').eq('campanha_id', campanha_id).execute()
    else:
        blocos_resp = supabase.table('blocos_rifas').select('*').execute()
    blocos = blocos_resp.data or []
    bloco_ids = [b['id'] for b in blocos]

    # Pagamentos relacionados (usados para confirmar vendas)
    pagamentos = []
    if bloco_ids:
        pag_resp = supabase.table('pagamentos').select('*').in_('bloco_id', bloco_ids).execute()
        pagamentos = pag_resp.data or []

    # Devoluções
    dev_resp = supabase.table('devolucoes').select('*').execute()
    devolucoes = dev_resp.data or []

    # KPIs
    total_escuteiros = len(escuteiros)
    total_blocos = len(blocos)
    estados = {}
    for b in blocos:
        est = b.get('estado') or 'desconhecido'
        estados[est] = estados.get(est, 0) + 1

    assigned_blocos = [b for b in blocos if (b.get('estado') or '') == 'atribuido']
    assigned_count = len(assigned_blocos)

    # rifas atribuídas
    def rifas_count(b):
        try:
            return int(b.get('numero_final', 0)) - int(b.get('numero_inicial', 0)) + 1
        except Exception:
            return 0

    rifas_atribuidas = sum(rifas_count(b) for b in assigned_blocos)

    # blocos com pagamentos (confirmados como vendidos)
    blocks_with_payments = set([p.get('bloco_id') for p in pagamentos if p.get('bloco_id')])
    confirmed_sold_blocks = len(blocks_with_payments)

    # rifas vendidas confirmadas (pela soma de quantidade_rifas ou canhotos_entregues)
    rifas_vendidas_confirmadas = 0
    for p in pagamentos:
        q = p.get('quantidade_rifas') or p.get('canhotos_entregues') or p.get('quantidade')
        try:
            rifas_vendidas_confirmadas += int(q or 0)
        except Exception:
            pass

    # Finance
    valor_total_recebido = safe_sum([p.get('valor_pago', 0) for p in pagamentos])
    receita_esperada_atribuidos = safe_sum([b.get('preco_bloco', 0) for b in assigned_blocos])
    saldo_pendente = receita_esperada_atribuidos - valor_total_recebido

    conversao_blocks = (confirmed_sold_blocks / assigned_count * 100) if assigned_count > 0 else 0

# Top metrics row
col1, col2, col3, col4 = st.columns(4)
col1.metric("👥 Escuteiros", total_escuteiros)
col2.metric("📅 Campanhas", total_campanhas)
col3.metric("🎟️ Blocos (total)", total_blocos)
col4.metric("📦 Blocos Atribuídos", assigned_count)

col5, col6, col7, col8 = st.columns(4)
col5.metric("✅ Blocos Vendidos (confirm.)", confirmed_sold_blocks)
col6.metric("🎫 Rifas Atribuídas", rifas_atribuidas)
col7.metric("💶 Recebido", f"{valor_total_recebido:.2f} €")
col8.metric("💸 Saldo Pendente", f"{saldo_pendente:.2f} €")

st.markdown("---")

# Charts: block state pie, payments over time, top escuteiros
chart_col1, chart_col2 = st.columns([2, 3])

with chart_col1:
    st.subheader("Estado dos Blocos")
    if estados:
        df_est = pd.DataFrame([{'Estado': k, 'Quantidade': v} for k, v in estados.items()])
        fig = px.pie(df_est, names='Estado', values='Quantidade', title='Distribuição de Estados')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Sem blocos para mostrar")

with chart_col2:
    st.subheader("Recebimentos ao Longo do Tempo")
    if pagamentos:
        df_pag = pd.DataFrame(pagamentos)
        if 'data_pagamento' in df_pag.columns:
            df_pag['data_pagamento'] = pd.to_datetime(df_pag['data_pagamento']).dt.date
            daily = df_pag.groupby('data_pagamento').agg({'valor_pago': lambda s: safe_sum(s)}).reset_index()
            fig = px.line(daily, x='data_pagamento', y='valor_pago', markers=True, title='Recebimentos diários')
            fig.update_layout(yaxis_title='Valor (€)')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Coluna 'data_pagamento' não encontrada nos pagamentos")
    else:
        st.info("Sem pagamentos registados ainda")

st.markdown("---")

# Top escuteiros by received
st.subheader("Top Escuteiros — Recebimentos")
if pagamentos:
    # join pagamentos -> blocos -> escuteiro
    df_pag = pd.DataFrame(pagamentos)
    df_blocos = pd.DataFrame(blocos)
    if 'bloco_id' in df_pag.columns and not df_blocos.empty:
        df_merged = df_pag.merge(df_blocos[['id', 'escuteiro_id']], left_on='bloco_id', right_on='id', how='left')
        # bring escuteiro names
        esc_df = pd.DataFrame(escuteiros)
        if not esc_df.empty:
            df_merged = df_merged.merge(esc_df[['id', 'nome']], left_on='escuteiro_id', right_on='id', how='left', suffixes=('', '_esc'))
            df_merged['nome'] = df_merged['nome'].fillna('Desconhecido')
        else:
            df_merged['nome'] = 'Desconhecido'

        top = df_merged.groupby('nome').agg({'valor_pago': lambda s: safe_sum(s), 'quantidade_rifas': lambda s: safe_sum(s)}).reset_index()
        top = top.sort_values('valor_pago', ascending=False).head(10)
        if not top.empty:
            fig = px.bar(top, x='nome', y='valor_pago', title='Top Escuteiros por Valor Recebido', labels={'nome':'Escuteiro','valor_pago':'Valor (€)'})
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(top.rename(columns={'nome':'Escuteiro','valor_pago':'Valor Recebido (€)','quantidade_rifas':'Rifas Confirmadas'}), use_container_width=True, hide_index=True)
        else:
            st.info('Sem dados agregados por escuteiro')
    else:
        st.info('Dados insuficientes para agregar top escuteiros')
else:
    st.info('Ainda não há pagamentos para calcular top escuteiros')

st.markdown('---')

st.subheader('Tabelas e detalhes')
with st.expander('Lista de Blocos (detalhada)', expanded=False):
    if blocos:
        df_blocos = pd.DataFrame(blocos)
        # add computed columns
        df_blocos['rifas_total'] = df_blocos.apply(rifas_count, axis=1)
        df_blocos['preco_bloco'] = df_blocos['preco_bloco'].fillna(0)
        st.dataframe(df_blocos[['id','nome','numero_inicial','numero_final','rifas_total','escuteiro_id','seccao','estado','preco_bloco']], use_container_width=True)
    else:
        st.info('Sem blocos para listar')

with st.expander('Pagamentos recentes', expanded=False):
    if pagamentos:
        df_pag = pd.DataFrame(pagamentos)
        # format date if present
        if 'data_pagamento' in df_pag.columns:
            df_pag['data_pagamento'] = pd.to_datetime(df_pag['data_pagamento']).dt.strftime('%Y-%m-%d')
        st.dataframe(df_pag.sort_values('data_pagamento', ascending=False).head(50), use_container_width=True)
    else:
        st.info('Sem pagamentos registados')

st.markdown('---')
st.caption('Dashboard provisório — se concordares eu refino visual e métricas, adiciono export CSV e alertas configuráveis.')
