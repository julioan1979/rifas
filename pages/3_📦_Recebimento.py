import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Recebimento", page_icon="📦", layout="wide")

st.title("📦 Recebimento de Canhotos e Dinheiro")

st.info("""
**Como funciona:**
1. Escuteiro recebe bloco de rifas
2. Escuteiro vende rifas aos compradores (externamente)
3. Escuteiro preenche canhotos com dados dos compradores
4. **Aqui:** Registe quando o escuteiro ENTREGA canhotos + dinheiro aos gestores
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
                "🎯 Filtrar por Campanha",
                options=list(campanhas_dict.keys()),
                index=default_idx,
                help="Selecione a campanha para visualizar/registar recebimentos"
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

# Initialize form counter for reset
if 'form_counter' not in st.session_state:
    st.session_state.form_counter = 0

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["📋 Lista de Recebimentos", "➕ Registar Recebimento", "✏️ Editar/Eliminar"])

# Tab 1: List receipts
with tab1:
    st.subheader(f"Recebimentos da Campanha: {selected_campanha['nome']}")
    
    try:
        # Fetch payments (recebimentos) with related block data filtered by campaign
        response = supabase.table('pagamentos').select(
            '*, blocos_rifas!inner(numero_inicial, numero_final, preco_bloco, campanha_id, escuteiros(nome))'
        ).eq('blocos_rifas.campanha_id', selected_campanha['id']).order('data_pagamento', desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Flatten nested data
            if 'blocos_rifas' in df.columns:
                df['escuteiro_nome'] = df['blocos_rifas'].apply(
                    lambda x: x.get('escuteiros', {}).get('nome', 'N/A') if x and x.get('escuteiros') else 'N/A'
                )
                df['bloco_info'] = df['blocos_rifas'].apply(
                    lambda x: f"Rifas {x.get('numero_inicial', '')}-{x.get('numero_final', '')}" 
                    if x and x.get('numero_inicial') else 'N/A'
                )
                df['valor_bloco'] = df['blocos_rifas'].apply(
                    lambda x: float(x.get('preco_bloco', 0)) if x else 0
                )
            
            # Formatar data (sem hora)
            if 'data_pagamento' in df.columns:
                df['data_pagamento'] = pd.to_datetime(df['data_pagamento']).dt.strftime('%d-%m-%Y')
            
            # Reordenar colunas para melhor visualização
            colunas_ordem = ['data_pagamento', 'escuteiro_nome', 'bloco_info', 'valor_bloco', 'valor_pago', 
                           'rifas_entregues', 'observacoes_canhotos', 'metodo_pagamento', 'observacoes']
            df_display = df[[col for col in colunas_ordem if col in df.columns]]
            
            st.dataframe(
                df_display,
                column_config={
                    "data_pagamento": "Data Recebimento",
                    "escuteiro_nome": "Escuteiro",
                    "bloco_info": "Bloco",
                    "valor_bloco": st.column_config.NumberColumn(
                        "Valor Bloco",
                        format="%.2f €",
                        help="Valor total do bloco"
                    ),
                    "valor_pago": st.column_config.NumberColumn(
                        "Valor Recebido",
                        format="%.2f €",
                        help="Valor efetivamente recebido do escuteiro"
                    ),
                    "rifas_entregues": st.column_config.NumberColumn(
                        "Canhotos",
                        help="Número de canhotos/rifas entregues"
                    ),
                    "observacoes_canhotos": "Obs. Canhotos",
                    "metodo_pagamento": "Método",
                    "observacoes": "Observações"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Statistics
            total_recebimentos = len(df)
            total_recebido = df['valor_pago'].sum() if 'valor_pago' in df.columns else 0
            total_canhotos = df['rifas_entregues'].sum() if 'rifas_entregues' in df.columns else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("📊 Total de Recebimentos", total_recebimentos)
            col2.metric("💰 Valor Total Recebido", f"{total_recebido:.2f} €")
            col3.metric("🎟️ Canhotos Entregues", int(total_canhotos))
        else:
            st.info("Nenhum recebimento registado ainda.")
    
    except Exception as e:
        st.error(f"Erro ao carregar recebimentos: {str(e)}")

# Tab 2: Add new receipt
with tab2:
    st.subheader("Registar Novo Recebimento")
    
    # Load assigned blocks for selection
    try:
        # Get blocks assigned to scouts (escuteiro_id not null) for this campaign
        blocks_response = supabase.table('blocos_rifas').select(
            'id, numero_inicial, numero_final, preco_bloco, escuteiro_id, escuteiros(nome)'
        ).eq('campanha_id', selected_campanha['id']).not_.is_('escuteiro_id', 'null').order('numero_inicial').execute()
        
        if not blocks_response.data:
            st.warning("⚠️ Não há blocos atribuídos a escuteiros. Por favor, atribua blocos primeiro.")
        else:
            # Check which blocks already have full payment
            payments_response = supabase.table('pagamentos').select('bloco_id, valor_pago').execute()
            payments_by_block = {}
            if payments_response.data:
                for payment in payments_response.data:
                    block_id = payment['bloco_id']
                    if block_id not in payments_by_block:
                        payments_by_block[block_id] = 0
                    payments_by_block[block_id] += float(payment['valor_pago'])
            
            # Create blocks list with payment status
            blocks_list = []
            for block in blocks_response.data:
                escuteiro = block.get('escuteiros', {})
                scout_name = escuteiro.get('nome', 'N/A') if escuteiro else 'N/A'
                total_rifas = block['numero_final'] - block['numero_inicial'] + 1
                preco_bloco = float(block.get('preco_bloco', 0))
                valor_recebido = payments_by_block.get(block['id'], 0)
                saldo = preco_bloco - valor_recebido
                
                status = "✅ Recebido" if saldo <= 0 else f"⚠️ Pendente: {saldo:.2f} €"
                label = f"{scout_name} | Rifas {block['numero_inicial']}-{block['numero_final']} | {preco_bloco:.2f} € ({status})"
                blocks_list.append((label, block, saldo, total_rifas))
            
            with st.form(f"add_receipt_form_{st.session_state.form_counter}"):
                # Block selection
                blocks_dict = {label: (block, saldo, total_rifas) for label, block, saldo, total_rifas in blocks_list}
                selected_block_label = st.selectbox(
                    "Bloco (Escuteiro) *",
                    options=list(blocks_dict.keys()),
                    help="Selecione o bloco que o escuteiro está a entregar"
                )
                
                if selected_block_label:
                    selected_block, saldo_pendente, total_rifas = blocks_dict[selected_block_label]
                    preco_bloco = float(selected_block.get('preco_bloco', 0))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if saldo_pendente > 0:
                            st.info(f"💶 Valor do Bloco: **{preco_bloco:.2f} €** | Saldo Pendente: **{saldo_pendente:.2f} €**")
                            default_valor = preco_bloco
                        else:
                            st.success(f"✅ Este bloco já está totalmente pago ({preco_bloco:.2f} €)")
                            default_valor = 0.0
                    
                    with col2:
                        st.info(f"🎟️ Total de Rifas no Bloco: **{total_rifas}**")
                    
                    # Money received
                    valor_recebido = st.number_input(
                        "💰 Valor Recebido (€) *",
                        min_value=0.0,
                        value=default_valor,
                        step=0.10,
                        format="%.2f",
                        help="Quanto dinheiro o escuteiro entregou"
                    )
                    
                    # Number of stubs received
                    rifas_entregues = st.number_input(
                        "🎟️ Canhotos Entregues *",
                        min_value=0,
                        max_value=total_rifas,
                        value=total_rifas,
                        step=1,
                        help="Quantos canhotos (rifas vendidas) o escuteiro entregou"
                    )
                    
                    # Stubs observations
                    observacoes_canhotos = st.text_area(
                        "📝 Observações sobre Canhotos",
                        placeholder="Ex: Faltam 2 canhotos (rifas perdidas), todos os canhotos preenchidos corretamente, etc.",
                        help="Registe aqui qualquer observação sobre os canhotos entregues"
                    )
                    
                    # Payment method
                    metodo_pagamento = st.selectbox(
                        "Método de Pagamento",
                        options=["Dinheiro", "Transferência Bancária", "MB Way", "Multibanco", "Cheque", "Outro"]
                    )
                    
                    # General observations
                    observacoes = st.text_area(
                        "📋 Observações Gerais",
                        placeholder="Ex: Pagamento parcial, restante na próxima semana, etc.",
                        help="Observações gerais sobre o recebimento"
                    )
                    
                    # Receipt date
                    data_recebimento = st.date_input(
                        "📅 Data do Recebimento",
                        value=datetime.now()
                    )
                    
                    submitted = st.form_submit_button("✅ Registar Recebimento", type="primary", use_container_width=True)
                    
                    if submitted:
                        try:
                            data = {
                                "bloco_id": selected_block['id'],
                                "valor_pago": valor_recebido,
                                "rifas_entregues": rifas_entregues,
                                "observacoes_canhotos": observacoes_canhotos if observacoes_canhotos else None,
                                "data_pagamento": data_recebimento.isoformat(),
                                "metodo_pagamento": metodo_pagamento,
                                "observacoes": observacoes if observacoes else None
                            }
                            
                            response = supabase.table('pagamentos').insert(data).execute()
                            
                            if response.data:
                                st.toast(f"✅ Recebimento de {valor_recebido:.2f} € registado!", icon="✅")
                                st.session_state.form_counter += 1
                                st.rerun()
                            else:
                                st.error("Erro ao registar recebimento.")
                        
                        except Exception as e:
                            st.error(f"Erro ao registar recebimento: {str(e)}")
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

# Tab 3: Edit/Delete receipts
with tab3:
    st.subheader("Editar ou Eliminar Recebimento")
    
    try:
        response = supabase.table('pagamentos').select(
            '*, blocos_rifas(numero_inicial, numero_final, preco_bloco, escuteiros(nome))'
        ).order('data_pagamento', desc=True).execute()
        
        if response.data:
            # Create a dictionary for receipt selection
            receipts_list = []
            for receipt in response.data:
                bloco = receipt.get('blocos_rifas', {})
                if bloco:
                    escuteiro = bloco.get('escuteiros', {})
                    scout_name = escuteiro.get('nome', 'N/A') if escuteiro else 'N/A'
                    bloco_info = f"Rifas {bloco.get('numero_inicial', '')}-{bloco.get('numero_final', '')}"
                else:
                    scout_name = 'N/A'
                    bloco_info = 'N/A'
                
                label = f"{receipt['data_pagamento'][:10]} - {scout_name} - {bloco_info} - {receipt['valor_pago']:.2f} €"
                receipts_list.append((label, receipt))
            
            receipts_dict = dict(receipts_list)
            
            selected_receipt_label = st.selectbox(
                "Selecione um recebimento",
                options=list(receipts_dict.keys())
            )
            
            if selected_receipt_label:
                receipt = receipts_dict[selected_receipt_label]
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader("Editar Recebimento")
                    
                    with st.form("edit_receipt_form"):
                        # Load blocks for selection
                        blocks_response = supabase.table('blocos_rifas').select(
                            'id, numero_inicial, numero_final, preco_bloco, escuteiro_id, escuteiros(nome)'
                        ).not_.is_('escuteiro_id', 'null').order('numero_inicial').execute()
                        
                        # Create blocks dictionary
                        blocks_dict = {}
                        current_block_label = None
                        for block in blocks_response.data:
                            escuteiro = block.get('escuteiros', {})
                            scout_name = escuteiro.get('nome', 'N/A') if escuteiro else 'N/A'
                            total_rifas = block['numero_final'] - block['numero_inicial'] + 1
                            label = f"{scout_name} | Rifas {block['numero_inicial']}-{block['numero_final']} | {total_rifas} rifas"
                            blocks_dict[label] = (block, total_rifas)
                            
                            if block['id'] == receipt['bloco_id']:
                                current_block_label = label
                        
                        # Block selection
                        block_index = list(blocks_dict.keys()).index(current_block_label) if current_block_label and current_block_label in blocks_dict else 0
                        new_block_label = st.selectbox(
                            "Bloco (Escuteiro) *",
                            options=list(blocks_dict.keys()),
                            index=block_index
                        )
                        
                        new_block, total_rifas = blocks_dict[new_block_label]
                        
                        # Money received
                        new_valor_recebido = st.number_input(
                            "💰 Valor Recebido (€) *",
                            min_value=0.0,
                            value=float(receipt['valor_pago']),
                            step=0.10,
                            format="%.2f"
                        )
                        
                        # Number of stubs received
                        new_rifas_entregues = st.number_input(
                            "🎟️ Canhotos Entregues *",
                            min_value=0,
                            max_value=total_rifas,
                            value=int(receipt.get('rifas_entregues', total_rifas)),
                            step=1
                        )
                        
                        # Stubs observations
                        new_observacoes_canhotos = st.text_area(
                            "📝 Observações sobre Canhotos",
                            value=receipt.get('observacoes_canhotos', '') or ''
                        )
                        
                        # Payment method
                        metodos = ["Dinheiro", "Transferência Bancária", "MB Way", "Multibanco", "Cheque", "Outro"]
                        current_metodo = receipt.get('metodo_pagamento', 'Dinheiro')
                        metodo_index = metodos.index(current_metodo) if current_metodo in metodos else 0
                        
                        new_metodo_pagamento = st.selectbox(
                            "Método de Pagamento",
                            options=metodos,
                            index=metodo_index
                        )
                        
                        # General observations
                        new_observacoes = st.text_area(
                            "📋 Observações Gerais",
                            value=receipt.get('observacoes', '') or ''
                        )
                        
                        # Receipt date
                        current_date = datetime.fromisoformat(receipt['data_pagamento'].replace('Z', '+00:00'))
                        new_data_recebimento = st.date_input(
                            "📅 Data do Recebimento",
                            value=current_date
                        )
                        
                        update_submitted = st.form_submit_button("Atualizar", type="primary")
                        
                        if update_submitted:
                            try:
                                update_data = {
                                    "bloco_id": new_block['id'],
                                    "valor_pago": new_valor_recebido,
                                    "rifas_entregues": new_rifas_entregues,
                                    "observacoes_canhotos": new_observacoes_canhotos if new_observacoes_canhotos else None,
                                    "data_pagamento": new_data_recebimento.isoformat(),
                                    "metodo_pagamento": new_metodo_pagamento,
                                    "observacoes": new_observacoes if new_observacoes else None
                                }
                                
                                response = supabase.table('pagamentos').update(update_data).eq('id', receipt['id']).execute()
                                
                                if response.data:
                                    st.toast("✅ Recebimento atualizado!", icon="✅")
                                    st.rerun()
                                else:
                                    st.error("Erro ao atualizar recebimento.")
                            
                            except Exception as e:
                                st.error(f"Erro ao atualizar recebimento: {str(e)}")
                
                with col2:
                    st.subheader("Eliminar")
                    st.warning("⚠️ Irreversível!")
                    
                    if st.button("🗑️ Eliminar", type="secondary", use_container_width=True):
                        try:
                            response = supabase.table('pagamentos').delete().eq('id', receipt['id']).execute()
                            
                            if response.data:
                                st.toast("✅ Recebimento eliminado!", icon="✅")
                                st.session_state.form_counter += 1
                                st.rerun()
                            else:
                                st.error("Erro ao eliminar recebimento.")
                        
                        except Exception as e:
                            st.error(f"Erro ao eliminar recebimento: {str(e)}")
        else:
            st.info("Nenhum recebimento disponível para editar.")
    
    except Exception as e:
        st.error(f"Erro ao carregar recebimentos: {str(e)}")
