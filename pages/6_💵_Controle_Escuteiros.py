import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Controle de Escuteiros", page_icon="💵", layout="wide")

st.title("💵 Controle de Pagamentos e Canhotos")

st.info("""
📋 **Fluxo de Trabalho:**
1. Escuteiro recebe bloco de rifas atribuído
2. Escuteiro vende as rifas aos compradores
3. **Escuteiro paga o dinheiro** à organização (registar aqui)
4. **Escuteiro devolve os canhotos** das rifas vendidas (registar aqui)
""")

# Initialize Supabase client
try:
    supabase = get_supabase_client()
except ValueError as e:
    st.error(f"Erro ao conectar ao Supabase: {str(e)}")
    st.stop()

# Get campaigns for filtering
try:
    campanhas_response = supabase.table('campanhas').select('*').order('created_at', desc='desc').execute()
    
    if campanhas_response.data:
        col1, col2 = st.columns([3, 1])
        with col1:
            campanhas_dict = {c['nome']: c for c in campanhas_response.data}
            
            # Set default to active campaign
            default_idx = 0
            for idx, c in enumerate(campanhas_response.data):
                if c.get('ativa', False):
                    default_idx = idx
                    break
            
            selected_campanha_name = st.selectbox(
                "🎯 Selecionar Campanha",
                options=list(campanhas_dict.keys()),
                index=default_idx
            )
            selected_campanha = campanhas_dict[selected_campanha_name]
        
        with col2:
            st.metric("", f"{'✅ Ativa' if selected_campanha.get('ativa') else '⏸️ Inativa'}")
    else:
        st.warning("⚠️ Nenhuma campanha criada.")
        st.stop()
        
except Exception as e:
    st.error(f"Erro ao carregar campanhas: {str(e)}")
    st.stop()

# Tabs
tab1, tab2 = st.tabs(["📊 Visão Geral", "✏️ Registar Pagamento/Canhotos"])

# Tab 1: Overview
with tab1:
    st.subheader(f"Estado dos Blocos - {selected_campanha['nome']}")
    
    try:
        # Get blocks with scout info
        response = supabase.table('blocos_rifas').select(
            '*, escuteiros(nome)'
        ).eq('campanha_id', selected_campanha['id']).order('numero_inicial').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Extract scout name
            df['escuteiro_nome'] = df['escuteiros'].apply(
                lambda x: x['nome'] if x else 'Não Atribuído'
            )
            
            # Calculate values
            df['total_rifas'] = df['numero_final'] - df['numero_inicial'] + 1
            df['valor_bloco'] = df['valor_a_pagar'] if 'valor_a_pagar' in df.columns else df['total_rifas'] * df['preco_unitario']
            
            # Check payment status
            if 'valor_pago' in df.columns and 'valor_a_pagar' in df.columns:
                df['status_pagamento'] = df.apply(
                    lambda row: '✅ Pago' if (row['valor_pago'] is not None and row['valor_a_pagar'] is not None and row['valor_pago'] >= row['valor_a_pagar']) 
                    else f"⏳ {row['valor_pago']:.2f}€/{row['valor_a_pagar']:.2f}€" if (row['valor_pago'] is not None and row['valor_pago'] > 0)
                    else '❌ Pendente',
                    axis=1
                )
            else:
                df['status_pagamento'] = '⏳ Pendente'
            
            # Check stub return status
            if 'canhotos_devolvidos' in df.columns:
                df['status_canhotos'] = df['canhotos_devolvidos'].apply(
                    lambda x: '✅ Devolvidos' if x else '❌ Pendente'
                )
            else:
                df['status_canhotos'] = '⏳ Pendente'
            
            # Filter only assigned blocks
            df_assigned = df[df['escuteiro_nome'] != 'Não Atribuído'].copy()
            
            if len(df_assigned) > 0:
                # Reorder columns
                colunas_ordem = [
                    'escuteiro_nome', 'numero_inicial', 'numero_final', 
                    'total_rifas', 'preco_unitario', 'valor_bloco',
                    'status_pagamento', 'status_canhotos'
                ]
                df_display = df_assigned[[col for col in colunas_ordem if col in df_assigned.columns]]
                
                st.dataframe(
                    df_display,
                    column_config={
                        "escuteiro_nome": "Escuteiro",
                        "numero_inicial": "Nº Inicial",
                        "numero_final": "Nº Final",
                        "total_rifas": st.column_config.NumberColumn("Total Rifas"),
                        "preco_unitario": st.column_config.NumberColumn(
                            "Preço/Rifa",
                            format="%.2f €"
                        ),
                        "valor_bloco": st.column_config.NumberColumn(
                            "Valor Total",
                            format="%.2f €",
                            help="Valor que o escuteiro deve pagar"
                        ),
                        "status_pagamento": "💰 Pagamento",
                        "status_canhotos": "📋 Canhotos"
                    },
                    hide_index=True,
                    use_container_width=True
                )
                
                # Summary
                total_blocos = len(df_assigned)
                total_valor = df_assigned['valor_bloco'].sum()
                
                # Calculate paid and pending
                valor_pago_total = df_assigned['valor_pago'].sum() if 'valor_pago' in df_assigned.columns else 0
                blocos_pagos = len(df_assigned[df_assigned['status_pagamento'].str.contains('✅', na=False)]) if 'status_pagamento' in df_assigned.columns else 0
                canhotos_devolvidos_total = len(df_assigned[df_assigned['status_canhotos'].str.contains('✅', na=False)]) if 'status_canhotos' in df_assigned.columns else 0
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("📦 Blocos Atribuídos", total_blocos)
                col2.metric("💰 Valor Esperado", f"{total_valor:.2f} €")
                col3.metric("✅ Blocos Pagos", f"{blocos_pagos}/{total_blocos}")
                col4.metric("📋 Canhotos OK", f"{canhotos_devolvidos_total}/{total_blocos}")
            else:
                st.info("Nenhum bloco atribuído ainda nesta campanha.")
        else:
            st.info("Nenhum bloco criado nesta campanha.")
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

# Tab 2: Register payment/stubs
with tab2:
    st.subheader("Registar Pagamento e Devolução de Canhotos")
    
    try:
        # Get assigned blocks for this campaign
        blocks_response = supabase.table('blocos_rifas').select(
            '*, escuteiros(nome)'
        ).eq('campanha_id', selected_campanha['id']).not_.is_('escuteiro_id', 'null').order('numero_inicial').execute()
        
        if not blocks_response.data:
            st.warning("⚠️ Nenhum bloco atribuído nesta campanha.")
        else:
            # Create block selection
            blocks_dict = {}
            for block in blocks_response.data:
                esc_nome = block.get('escuteiros', {}).get('nome', 'N/A') if block.get('escuteiros') else 'N/A'
                total_rifas = block['numero_final'] - block['numero_inicial'] + 1
                valor_bloco = total_rifas * float(block['preco_unitario'])
                display = f"{esc_nome} | Rifas {block['numero_inicial']}-{block['numero_final']} | {valor_bloco:.2f} €"
                blocks_dict[display] = block
            
            selected_block_display = st.selectbox(
                "1️⃣ Selecione o Bloco",
                options=list(blocks_dict.keys()),
                help="Escolha o bloco do escuteiro"
            )
            
            if selected_block_display:
                block = blocks_dict[selected_block_display]
                escuteiro_nome = block.get('escuteiros', {}).get('nome', 'N/A') if block.get('escuteiros') else 'N/A'
                total_rifas = block['numero_final'] - block['numero_inicial'] + 1
                valor_bloco = total_rifas * float(block['preco_unitario'])
                
                # Show block info
                st.info(f"""
                **Escuteiro:** {escuteiro_nome}  
                **Rifas:** {block['numero_inicial']} a {block['numero_final']} ({total_rifas} rifas)  
                **Preço por Rifa:** {float(block['preco_unitario']):.2f} €  
                **Valor Total do Bloco:** {valor_bloco:.2f} €
                """)
                
                st.divider()
                
                # Payment section
                st.subheader("💰 Registar Pagamento")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    valor_pago = st.number_input(
                        "Valor Pago (€)",
                        min_value=0.0,
                        max_value=float(valor_bloco),
                        value=float(valor_bloco),
                        step=0.10,
                        format="%.2f",
                        help="Quanto o escuteiro pagou"
                    )
                
                with col2:
                    data_pagamento = st.date_input(
                        "Data do Pagamento",
                        value=datetime.now()
                    )
                
                metodo_pagamento = st.selectbox(
                    "Método de Pagamento",
                    options=["Dinheiro", "Transferência Bancária", "MB Way", "Multibanco", "Outro"]
                )
                
                obs_pagamento = st.text_input(
                    "Observações sobre Pagamento",
                    placeholder="Ex: Pagamento parcial, referência, etc."
                )
                
                st.divider()
                
                # Stubs section
                st.subheader("📋 Devolução de Canhotos")
                
                st.info("""
                **Importante:** Os canhotos das rifas contêm:
                - Nome e contacto de quem comprou a rifa
                - Número da rifa vendida
                - Estes dados são essenciais para o sorteio!
                """)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    rifas_vendidas = st.number_input(
                        "Quantas rifas foram vendidas?",
                        min_value=0,
                        max_value=total_rifas,
                        value=0,
                        step=1,
                        help="Número de rifas que o escuteiro conseguiu vender"
                    )
                
                with col2:
                    canhotos_devolvidos = st.checkbox(
                        "Canhotos foram devolvidos?",
                        help="Marque se o escuteiro já entregou os canhotos das rifas vendidas"
                    )
                
                if canhotos_devolvidos:
                    data_devolucao = st.date_input(
                        "Data da Devolução dos Canhotos",
                        value=datetime.now()
                    )
                else:
                    data_devolucao = None
                
                obs_canhotos = st.text_area(
                    "Observações sobre Canhotos",
                    placeholder="Ex: Faltam 2 canhotos, alguns ilegíveis, etc."
                )
                
                st.divider()
                
                if st.button("💾 Guardar Informação", type="primary", use_container_width=True):
                    try:
                        update_data = {
                            "valor_pago": float(valor_pago),
                            "data_pagamento": data_pagamento.isoformat() if valor_pago > 0 else None,
                            "metodo_pagamento": metodo_pagamento if valor_pago > 0 else None,
                            "rifas_vendidas": int(rifas_vendidas),
                            "canhotos_devolvidos": canhotos_devolvidos,
                            "data_devolucao_canhotos": data_devolucao.isoformat() if canhotos_devolvidos and data_devolucao else None,
                            "observacoes_pagamento": obs_pagamento.strip() if obs_pagamento else None,
                            "observacoes_canhotos": obs_canhotos.strip() if obs_canhotos else None
                        }
                        
                        response = supabase.table('blocos_rifas').update(update_data).eq('id', block['id']).execute()
                        
                        if response.data:
                            st.success("✅ Informação registada com sucesso!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("Erro ao guardar informação.")
                    
                    except Exception as e:
                        st.error(f"Erro ao guardar: {str(e)}")
                        st.info("Verifique se o SQL de atualização foi executado corretamente no Supabase.")
    
    except Exception as e:
        st.error(f"Erro: {str(e)}")
