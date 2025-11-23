import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Vendas", page_icon="💰", layout="wide")

st.title("💰 Gestão de Vendas")

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
                "🎯 Filtrar por Campanha",
                options=list(campanhas_dict.keys()),
                index=default_idx,
                help="Selecione a campanha para visualizar/registar vendas"
            )
            selected_campanha = campanhas_dict[selected_campanha_name]
        
        with col2:
            st.metric("", f"{'✅ Ativa' if selected_campanha.get('ativa') else '⏸️ Inativa'}")
    else:
        st.warning("⚠️ Nenhuma campanha criada. Crie uma campanha primeiro na página 'Campanhas'.")
        st.stop()
        
except Exception as e:
    st.error(f"Erro ao carregar campanhas: {str(e)}")
    st.stop()

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Registar Venda", "✏️ Editar/Eliminar"])

# Tab 1: List sales
with tab1:
    st.subheader(f"Vendas da Campanha: {selected_campanha['nome']}")
    
    try:
        # Fetch sales with related data filtered by campaign
        response = supabase.table('vendas').select(
            '*, escuteiros(nome), blocos_rifas!inner(numero_inicial, numero_final, preco_unitario, campanha_id)'
        ).eq('blocos_rifas.campanha_id', selected_campanha['id']).order('data_venda', desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Flatten nested data
            if 'escuteiros' in df.columns:
                df['escuteiro_nome'] = df['escuteiros'].apply(lambda x: x['nome'] if x else 'N/A')
            if 'blocos_rifas' in df.columns:
                df['bloco_info'] = df['blocos_rifas'].apply(
                    lambda x: f"Rifas {x['numero_inicial']}-{x['numero_final']}" if x and 'numero_inicial' in x else 'N/A'
                )
            
            # Formatar data (sem hora)
            if 'data_venda' in df.columns:
                df['data_venda'] = pd.to_datetime(df['data_venda']).dt.strftime('%d-%m-%Y')
            
            # Reordenar colunas para melhor visualização
            colunas_ordem = ['data_venda', 'escuteiro_nome', 'bloco_info', 'quantidade', 'valor_total', 'observacoes']
            df_display = df[[col for col in colunas_ordem if col in df.columns]]
            
            st.dataframe(
                df_display,
                column_config={
                    "data_venda": "Data",
                    "escuteiro_nome": "Escuteiro",
                    "bloco_info": "Bloco",
                    "quantidade": st.column_config.NumberColumn(
                        "Qtd",
                        help="Quantidade de rifas vendidas"
                    ),
                    "valor_total": st.column_config.NumberColumn(
                        "Valor Total",
                        format="%.2f €",
                        help="Valor total da venda (quantidade × preço unitário)"
                    ),
                    "observacoes": "Observações"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Statistics
            total_vendas = len(df)
            total_rifas = df['quantidade'].sum() if 'quantidade' in df.columns else 0
            total_valor = df['valor_total'].sum() if 'valor_total' in df.columns else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📊 Total de Vendas", total_vendas)
            col2.metric("🎟️ Total de Rifas Vendidas", int(total_rifas))
            col3.metric("💰 Valor Total", f"{total_valor:.2f} €")
        else:
            st.info("Nenhuma venda registada ainda.")
    
    except Exception as e:
        st.error(f"Erro ao carregar vendas: {str(e)}")

# Tab 2: Add new sale
with tab2:
    st.subheader("Registar Nova Venda")
    
    # Load scouts and blocks for selection
    try:
        scouts_response = supabase.table('escuteiros').select('id, nome').eq('ativo', True).order('nome').execute()
        blocks_response = supabase.table('blocos_rifas').select('id, numero_inicial, numero_final, preco_unitario, escuteiro_id, escuteiros(nome)').eq('campanha_id', selected_campanha['id']).order('numero_inicial').execute()
        
        if not scouts_response.data:
            st.warning("⚠️ Não há escuteiros registados. Por favor, adicione escuteiros primeiro.")
        elif not blocks_response.data:
            st.warning("⚠️ Não há blocos de rifas criados. Por favor, crie blocos de rifas primeiro.")
        else:
            with st.form("add_sale_form"):
                # Scout selection
                scouts_dict = {scout['nome']: scout for scout in scouts_response.data}
                
                # Prepare blocks dict with better display
                blocks_dict = {}
                for block in blocks_response.data:
                    escuteiro = block.get('escuteiros', {}).get('nome', 'Disponível') if block.get('escuteiros') else 'Disponível'
                    display_name = f"Rifas {block['numero_inicial']}-{block['numero_final']} | {escuteiro}"
                    blocks_dict[display_name] = block
                selected_scout = st.selectbox(
                    "Escuteiro *",
                    options=list(scouts_dict.keys()),
                    help="Escuteiro que realizou a venda"
                )
                
                selected_block_display = st.selectbox(
                    "Bloco de Rifas *",
                    options=list(blocks_dict.keys()),
                    help="Bloco de rifas vendido"
                )
                selected_block = blocks_dict[selected_block_display]
                
                # Quantity
                quantidade = st.number_input(
                    "Quantidade de Rifas *",
                    min_value=1,
                    value=1,
                    step=1
                )
                
                # Calculate total value
                if selected_block:
                    preco_unitario = float(selected_block['preco_unitario'])
                    valor_total = quantidade * preco_unitario
                    st.info(f"💶 Valor Total: **{valor_total:.2f} €** ({quantidade} × {preco_unitario:.2f} €)")
                
                # Sale date
                data_venda = st.date_input(
                    "Data da Venda",
                    value=datetime.now()
                )
                
                submitted = st.form_submit_button("Registar Venda", type="primary")
                
                if submitted:
                    if not selected_scout or not selected_block:
                        st.error("Por favor, selecione um escuteiro e um bloco de rifas!")
                    else:
                        try:
                            scout_id = scouts_dict[selected_scout]['id']
                            block_id = selected_block['id']
                            
                            data = {
                                "escuteiro_id": scout_id,
                                "bloco_id": block_id,
                                "quantidade": quantidade,
                                "valor_total": valor_total,
                                "data_venda": data_venda.isoformat()
                            }
                            
                            response = supabase.table('vendas').insert(data).execute()
                            
                            if response.data:
                                st.success(f"✅ Venda registada com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao registar venda.")
                        
                        except Exception as e:
                            st.error(f"Erro ao registar venda: {str(e)}")
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

# Tab 3: Edit/Delete sales
with tab3:
    st.subheader("Editar ou Eliminar Venda")
    
    try:
        response = supabase.table('vendas').select(
            '*, escuteiros(nome), blocos_rifas(nome, preco_unitario)'
        ).order('data_venda', desc=True).execute()
        
        if response.data:
            # Create a dictionary for sale selection
            sales_list = []
            for sale in response.data:
                scout_name = sale.get('escuteiros', {}).get('nome', 'N/A') if sale.get('escuteiros') else 'N/A'
                block_name = sale.get('blocos_rifas', {}).get('nome', 'N/A') if sale.get('blocos_rifas') else 'N/A'
                label = f"{sale['data_venda'][:10]} - {scout_name} - {block_name} ({sale['id'][:8]}...)"
                sales_list.append((label, sale))
            
            sales_dict = dict(sales_list)
            
            selected_sale_label = st.selectbox(
                "Selecione uma venda",
                options=list(sales_dict.keys())
            )
            
            if selected_sale_label:
                sale = sales_dict[selected_sale_label]
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader("Editar Venda")
                    
                    # Load scouts and blocks for editing
                    scouts_response = supabase.table('escuteiros').select('id, nome').order('nome').execute()
                    blocks_response = supabase.table('blocos_rifas').select('id, nome, preco_unitario').order('nome').execute()
                    
                    with st.form("edit_sale_form"):
                        # Scout selection
                        scouts_dict = {scout['nome']: scout for scout in scouts_response.data}
                        current_scout = sale.get('escuteiros', {}).get('nome', '') if sale.get('escuteiros') else ''
                        scout_index = list(scouts_dict.keys()).index(current_scout) if current_scout in scouts_dict else 0
                        
                        new_scout = st.selectbox(
                            "Escuteiro *",
                            options=list(scouts_dict.keys()),
                            index=scout_index
                        )
                        
                        # Block selection
                        blocks_dict = {block['nome']: block for block in blocks_response.data}
                        current_block = sale.get('blocos_rifas', {}).get('nome', '') if sale.get('blocos_rifas') else ''
                        block_index = list(blocks_dict.keys()).index(current_block) if current_block in blocks_dict else 0
                        
                        new_block = st.selectbox(
                            "Bloco de Rifas *",
                            options=list(blocks_dict.keys()),
                            index=block_index
                        )
                        
                        # Quantity
                        new_quantidade = st.number_input(
                            "Quantidade de Rifas *",
                            min_value=1,
                            value=sale['quantidade'],
                            step=1
                        )
                        
                        # Calculate total value
                        if new_block:
                            preco_unitario = float(blocks_dict[new_block]['preco_unitario'])
                            new_valor_total = new_quantidade * preco_unitario
                            st.info(f"💶 Valor Total: **{new_valor_total:.2f} €**")
                        
                        # Sale date
                        current_date = datetime.fromisoformat(sale['data_venda'].replace('Z', '+00:00'))
                        new_data_venda = st.date_input(
                            "Data da Venda",
                            value=current_date
                        )
                        
                        update_submitted = st.form_submit_button("Atualizar", type="primary")
                        
                        if update_submitted:
                            try:
                                update_data = {
                                    "escuteiro_id": scouts_dict[new_scout]['id'],
                                    "bloco_id": blocks_dict[new_block]['id'],
                                    "quantidade": new_quantidade,
                                    "valor_total": new_valor_total,
                                    "data_venda": new_data_venda.isoformat()
                                }
                                
                                response = supabase.table('vendas').update(update_data).eq('id', sale['id']).execute()
                                
                                if response.data:
                                    st.success("✅ Venda atualizada com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("Erro ao atualizar venda.")
                            
                            except Exception as e:
                                st.error(f"Erro ao atualizar venda: {str(e)}")
                
                with col2:
                    st.subheader("Eliminar")
                    st.warning("⚠️ Esta ação é irreversível!")
                    
                    if st.button("🗑️ Eliminar Venda", type="secondary"):
                        try:
                            response = supabase.table('vendas').delete().eq('id', sale['id']).execute()
                            
                            if response.data:
                                st.success("✅ Venda eliminada com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao eliminar venda.")
                        
                        except Exception as e:
                            st.error(f"Erro ao eliminar venda: {str(e)}")
        else:
            st.info("Nenhuma venda disponível para editar.")
    
    except Exception as e:
        st.error(f"Erro ao carregar vendas: {str(e)}")
