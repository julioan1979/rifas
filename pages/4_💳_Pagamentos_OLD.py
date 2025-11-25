# Gestão de Pagamentos
import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Pagamentos", page_icon="💳", layout="wide")

# Inicializar cliente Supabase
try:
    supabase = get_supabase_client()
except Exception as e:
    st.error(f"❌ Erro ao conectar à base de dados: {e}")
    st.stop()

st.title("💳 Gestão de Pagamentos")

st.info("Esta página regista **prestações de contas** dos escuteiros (quando os escuteiros entregam o dinheiro das rifas vendidas à organização).")

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
                help="Selecione a campanha para visualizar/registar pagamentos"
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
tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Registar Pagamento", "✏️ Editar/Eliminar"])

# Tab 1: List payments
with tab1:
    st.subheader(f"Pagamentos da Campanha: {selected_campanha['nome']}")
    
    try:
        # Fetch payments with related sales data filtered by campaign
        response = supabase.table('pagamentos').select(
            '*, vendas!inner(valor_total, escuteiros(nome), blocos_rifas!inner(numero_inicial, numero_final, campanha_id))'
        ).eq('vendas.blocos_rifas.campanha_id', selected_campanha['id']).order('data_pagamento', desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Flatten nested data
            if 'vendas' in df.columns:
                df['escuteiro_nome'] = df['vendas'].apply(
                    lambda x: x.get('escuteiros', {}).get('nome', 'N/A') if x and x.get('escuteiros') else 'N/A'
                )
                df['bloco_info'] = df['vendas'].apply(
                    lambda x: f"Rifas {x.get('blocos_rifas', {}).get('numero_inicial', '')}-{x.get('blocos_rifas', {}).get('numero_final', '')}" 
                    if x and x.get('blocos_rifas') and x.get('blocos_rifas', {}).get('numero_inicial') else 'N/A'
                )
                df['valor_venda'] = df['vendas'].apply(
                    lambda x: x.get('valor_total', 0) if x else 0
                )
            
            # Adicionar coluna de status de canhotos
            def formatar_canhotos(row):
                entregues = row.get('canhotos_entregues', 0) or 0
                esperados = row.get('canhotos_esperados', 0) or 0
                
                if esperados == 0:
                    return "N/A"
                elif entregues == esperados:
                    return f"{entregues}/{esperados} ✅"
                elif entregues > 0:
                    return f"{entregues}/{esperados} ⚠️"
                else:
                    return f"{entregues}/{esperados} ❌"
            
            df['status_canhotos'] = df.apply(formatar_canhotos, axis=1)
            
            # Formatar data (sem hora)
            if 'data_pagamento' in df.columns:
                df['data_pagamento'] = pd.to_datetime(df['data_pagamento']).dt.strftime('%d-%m-%Y')
            
            # Reordenar colunas para melhor visualização
            colunas_ordem = ['data_pagamento', 'escuteiro_nome', 'bloco_info', 'valor_pago', 'valor_venda', 'status_canhotos', 'metodo_pagamento', 'referencia', 'observacoes']
            df_display = df[[col for col in colunas_ordem if col in df.columns]]
            
            st.dataframe(
                df_display,
                column_config={
                    "data_pagamento": "Data",
                    "escuteiro_nome": "Escuteiro",
                    "bloco_info": "Bloco",
                    "valor_pago": st.column_config.NumberColumn(
                        "Valor Pago",
                        format="%.2f €",
                        help="Valor efetivamente pago pelo escuteiro"
                    ),
                    "valor_venda": st.column_config.NumberColumn(
                        "Valor Venda",
                        format="%.2f €",
                        help="Valor total da venda. Se diferente do Valor Pago, há saldo pendente."
                    ),
                    "status_canhotos": st.column_config.TextColumn(
                        "Canhotos",
                        help="Status de entrega dos canhotos: ✅ Completo | ⚠️ Parcial | ❌ Não entregue"
                    ),
                    "metodo_pagamento": "Método",
                    "referencia": "Referência",
                    "observacoes": "Observações"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Statistics
            total_pagamentos = len(df)
            total_pago = df['valor_pago'].sum() if 'valor_pago' in df.columns else 0
            total_canhotos_esperados = df['canhotos_esperados'].sum() if 'canhotos_esperados' in df.columns else 0
            total_canhotos_entregues = df['canhotos_entregues'].sum() if 'canhotos_entregues' in df.columns else 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📊 Total de Pagamentos", total_pagamentos)
            col2.metric("💰 Valor Total Recebido", f"{total_pago:.2f} €")
            col3.metric("📄 Canhotos Entregues", f"{total_canhotos_entregues}/{total_canhotos_esperados}")
            if total_canhotos_esperados > 0:
                perc_canhotos = (total_canhotos_entregues / total_canhotos_esperados) * 100
                col4.metric("✅ Taxa de Entrega", f"{perc_canhotos:.1f}%")
        else:
            st.info("Nenhum pagamento registado ainda.")
    
    except Exception as e:
        st.error(f"Erro ao carregar pagamentos: {str(e)}")

# Tab 2: Add new payment
with tab2:
    st.subheader("Registar Novo Pagamento")
    
    st.info("""
    **Como funciona:**
    - Escuteiros recebem **blocos de rifas** para vender
    - Quando vendem, devem **prestar contas** pelo bloco todo
    - Esta página regista pagamentos (parciais ou totais) por bloco
    """)
    
    # Load blocks with sales and calculate pending balance
    try:
        # Get all blocks for this campaign with their sales
        blocos_response = supabase.table('blocos_rifas').select(
            '*, escuteiros(nome), vendas(id, quantidade, valor_total)'
        ).eq('campanha_id', selected_campanha['id']).execute()
        
        if not blocos_response.data:
            st.warning("⚠️ Não há blocos de rifas atribuídos nesta campanha.")
        else:
            # Get all payments to calculate balances
            payments_response = supabase.table('pagamentos').select(
                'venda_id, valor_pago, canhotos_entregues'
            ).execute()
            
            payments_by_venda = {}
            canhotos_by_venda = {}
            if payments_response.data:
                for payment in payments_response.data:
                    venda_id = payment['venda_id']
                    if venda_id not in payments_by_venda:
                        payments_by_venda[venda_id] = 0
                        canhotos_by_venda[venda_id] = 0
                    payments_by_venda[venda_id] += float(payment['valor_pago'])
                    canhotos_by_venda[venda_id] += int(payment.get('canhotos_entregues', 0) or 0)
            
            # Build list of blocks with pending balance
            blocos_com_saldo = []
            
            for bloco in blocos_response.data:
                # Skip blocks without sales
                if not bloco.get('vendas') or len(bloco['vendas']) == 0:
                    continue
                
                escuteiro_nome = bloco.get('escuteiros', {}).get('nome', 'N/A') if bloco.get('escuteiros') else 'N/A'
                bloco_info = f"Rifas {bloco['numero_inicial']}-{bloco['numero_final']}"
                
                # Calculate total sold and paid for this block
                total_vendido = sum(float(v['valor_total']) for v in bloco['vendas'])
                total_rifas_vendidas = sum(int(v['quantidade']) for v in bloco['vendas'])
                
                total_pago = sum(payments_by_venda.get(v['id'], 0) for v in bloco['vendas'])
                total_canhotos_entregues = sum(canhotos_by_venda.get(v['id'], 0) for v in bloco['vendas'])
                
                saldo_pendente = total_vendido - total_pago
                canhotos_pendentes = total_rifas_vendidas - total_canhotos_entregues
                
                # Only show blocks with pending balance
                if saldo_pendente > 0.01:
                    label = f"{escuteiro_nome} - {bloco_info} - Vendido: {total_vendido:.2f} € | Saldo: {saldo_pendente:.2f} € | Canhotos: {total_canhotos_entregues}/{total_rifas_vendidas}"
                    blocos_com_saldo.append({
                        'label': label,
                        'bloco': bloco,
                        'saldo': saldo_pendente,
                        'total_vendido': total_vendido,
                        'total_rifas_vendidas': total_rifas_vendidas,
                        'total_canhotos_entregues': total_canhotos_entregues,
                        'canhotos_pendentes': canhotos_pendentes
                    })
            
            if not blocos_com_saldo:
                st.success("✅ Todos os blocos com vendas estão totalmente pagos!")
            else:
                st.info(f"📊 **{len(blocos_com_saldo)}** blocos com saldo pendente")
                
                with st.form("add_payment_form"):
                    # Block selection
                    blocos_dict = {b['label']: b for b in blocos_com_saldo}
                    
                    selected_bloco_label = st.selectbox(
                        "Bloco de Rifas *",
                        options=list(blocos_dict.keys()),
                        help="Mostra apenas blocos com saldo pendente"
                    )
                    
                    if selected_bloco_label:
                        bloco_data = blocos_dict[selected_bloco_label]
                        saldo_pendente = bloco_data['saldo']
                        total_vendido = bloco_data['total_vendido']
                        total_rifas_vendidas = bloco_data['total_rifas_vendidas']
                        total_canhotos_entregues = bloco_data['total_canhotos_entregues']
                        canhotos_pendentes = bloco_data['canhotos_pendentes']
                        
                        # Select which sale to associate the payment with (for DB structure)
                        # We'll use the first sale, but show block-level information
                        vendas = bloco_data['bloco']['vendas']
                        primeira_venda = vendas[0]
                        
                        st.info(f"💶 **Valor Vendido:** {total_vendido:.2f} € | **Saldo Pendente:** {saldo_pendente:.2f} €")
                        
                        # Payment amount
                        valor_pago = st.number_input(
                            "Valor a Pagar (€) *",
                            min_value=0.01,
                            max_value=float(saldo_pendente),
                            value=float(saldo_pendente),
                            step=0.10,
                            format="%.2f",
                            help="Pode fazer pagamento parcial"
                        )
                        
                        # Payment method
                        metodo_pagamento = st.selectbox(
                            "Método de Pagamento",
                            options=["Dinheiro", "Transferência Bancária", "MB Way", "Multibanco", "Cheque", "Outro"]
                        )
                        
                        # Payment date
                        data_pagamento = st.date_input(
                            "Data do Pagamento",
                            value=datetime.now()
                        )
                        
                        # Stub control section
                        st.divider()
                        st.subheader("📄 Controlo de Canhotos")
                        
                        # Show stubs status
                        st.info(f"📋 **Rifas vendidas no bloco:** {total_rifas_vendidas} | **Canhotos já entregues:** {total_canhotos_entregues} | **Canhotos pendentes:** {canhotos_pendentes}")
                        
                        # Number of stubs delivered
                        canhotos_entregues = st.number_input(
                            "Canhotos a Entregar Agora",
                            min_value=0,
                            max_value=canhotos_pendentes,
                            value=min(canhotos_pendentes, total_rifas_vendidas) if canhotos_pendentes > 0 else 0,
                            help="Quantos canhotos o escuteiro entrega nesta prestação de contas"
                        )
                        
                        # Visual feedback
                        canhotos_apos = total_canhotos_entregues + canhotos_entregues
                        if canhotos_apos == total_rifas_vendidas:
                            st.success(f"✅ Após este pagamento: {canhotos_apos}/{total_rifas_vendidas} canhotos (COMPLETO)")
                        elif canhotos_entregues > 0:
                            st.warning(f"⚠️ Após este pagamento: {canhotos_apos}/{total_rifas_vendidas} canhotos (faltam {total_rifas_vendidas - canhotos_apos})")
                        else:
                            st.error(f"❌ Nenhum canhoto será registado. Total: {canhotos_apos}/{total_rifas_vendidas}")
                        
                        # Optional notes about stubs
                        observacoes_canhotos = st.text_area(
                            "Observações sobre Canhotos (opcional)",
                            placeholder="Ex: Faltam 3 canhotos, prometeu entregar na próxima semana",
                            help="Use este campo para registar informações sobre canhotos em falta"
                        )
                        
                        submitted = st.form_submit_button("Registar Pagamento", type="primary")
                        
                        if submitted:
                            try:
                                # Associate payment with the first sale of the block
                                # (This maintains DB structure while showing block-level info)
                                data = {
                                    "venda_id": primeira_venda['id'],
                                    "valor_pago": valor_pago,
                                    "data_pagamento": data_pagamento.isoformat(),
                                    "metodo_pagamento": metodo_pagamento,
                                    "canhotos_entregues": canhotos_entregues,
                                    "canhotos_esperados": canhotos_pendentes,
                                    "data_entrega_canhotos": datetime.now().isoformat() if canhotos_entregues > 0 else None,
                                    "observacoes_canhotos": observacoes_canhotos if observacoes_canhotos else None
                                }
                                
                                response = supabase.table('pagamentos').insert(data).execute()
                                
                                if response.data:
                                    st.success(f"✅ Pagamento de {valor_pago:.2f} € registado com sucesso!")
                                    if canhotos_entregues > 0:
                                        st.success(f"📄 {canhotos_entregues} canhotos registados como entregues")
                                    st.rerun()
                                else:
                                    st.error("Erro ao registar pagamento.")
                            
                            except Exception as e:
                                st.error(f"Erro ao registar pagamento: {str(e)}")
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

# Tab 3: Edit/Delete payments
with tab3:
    st.subheader("Editar ou Eliminar Pagamento")
    
    try:
        response = supabase.table('pagamentos').select(
            '*, vendas(valor_total, escuteiros(nome), blocos_rifas(nome))'
        ).order('data_pagamento', desc=True).execute()
        
        if response.data:
            # Create a dictionary for payment selection
            payments_list = []
            for payment in response.data:
                venda = payment.get('vendas', {})
                if venda:
                    scout_name = venda.get('escuteiros', {}).get('nome', 'N/A') if venda.get('escuteiros') else 'N/A'
                    block_name = venda.get('blocos_rifas', {}).get('nome', 'N/A') if venda.get('blocos_rifas') else 'N/A'
                else:
                    scout_name = 'N/A'
                    block_name = 'N/A'
                
                label = f"{payment['data_pagamento'][:10]} - {scout_name} - {payment['valor_pago']:.2f} € ({payment['id'][:8]}...)"
                payments_list.append((label, payment))
            
            payments_dict = dict(payments_list)
            
            selected_payment_label = st.selectbox(
                "Selecione um pagamento",
                options=list(payments_dict.keys())
            )
            
            if selected_payment_label:
                payment = payments_dict[selected_payment_label]
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader("Editar Pagamento")
                    
                    with st.form("edit_payment_form"):
                        # Load sales for selection
                        sales_response = supabase.table('vendas').select(
                            '*, escuteiros(nome), blocos_rifas(nome)'
                        ).order('data_venda', desc=True).execute()
                        
                        # Create sales dictionary
                        sales_dict = {}
                        current_sale_label = None
                        for sale in sales_response.data:
                            scout_name = sale.get('escuteiros', {}).get('nome', 'N/A') if sale.get('escuteiros') else 'N/A'
                            block_name = sale.get('blocos_rifas', {}).get('nome', 'N/A') if sale.get('blocos_rifas') else 'N/A'
                            label = f"{sale['data_venda'][:10]} - {scout_name} - {block_name}"
                            sales_dict[label] = sale
                            
                            if sale['id'] == payment['venda_id']:
                                current_sale_label = label
                        
                        # Sale selection
                        sale_index = list(sales_dict.keys()).index(current_sale_label) if current_sale_label and current_sale_label in sales_dict else 0
                        new_sale_label = st.selectbox(
                            "Venda *",
                            options=list(sales_dict.keys()),
                            index=sale_index
                        )
                        
                        # Payment amount
                        new_valor_pago = st.number_input(
                            "Valor a Pagar (€) *",
                            min_value=0.01,
                            value=float(payment['valor_pago']),
                            step=0.10,
                            format="%.2f"
                        )
                        
                        # Payment method
                        metodos = ["Dinheiro", "Transferência Bancária", "MB Way", "Multibanco", "Cheque", "Outro"]
                        current_metodo = payment.get('metodo_pagamento', 'Dinheiro')
                        metodo_index = metodos.index(current_metodo) if current_metodo in metodos else 0
                        
                        new_metodo_pagamento = st.selectbox(
                            "Método de Pagamento",
                            options=metodos,
                            index=metodo_index
                        )
                        
                        # Payment date
                        current_date = datetime.fromisoformat(payment['data_pagamento'].replace('Z', '+00:00'))
                        new_data_pagamento = st.date_input(
                            "Data do Pagamento",
                            value=current_date
                        )
                        
                        # Stub control section
                        st.divider()
                        st.subheader("📄 Controlo de Canhotos")
                        
                        # Get the selected sale to know expected stubs
                        selected_sale = sales_dict[new_sale_label]
                        quantidade_vendida = selected_sale.get('quantidade', 0)
                        
                        st.info(f"📋 **Rifas vendidas:** {quantidade_vendida} | **Canhotos esperados:** {quantidade_vendida}")
                        
                        # Number of stubs delivered
                        current_canhotos_entregues = payment.get('canhotos_entregues', 0) or 0
                        new_canhotos_entregues = st.number_input(
                            "Canhotos Entregues",
                            min_value=0,
                            max_value=quantidade_vendida,
                            value=current_canhotos_entregues,
                            help="Quantos canhotos o escuteiro entregou"
                        )
                        
                        # Visual feedback
                        if new_canhotos_entregues == quantidade_vendida:
                            st.success(f"✅ Todos os {quantidade_vendida} canhotos marcados como entregues")
                        elif new_canhotos_entregues > 0:
                            st.warning(f"⚠️ Entrega parcial: {new_canhotos_entregues}/{quantidade_vendida} canhotos")
                        else:
                            st.error(f"❌ Nenhum canhoto registado como entregue")
                        
                        # Optional notes about stubs
                        current_obs_canhotos = payment.get('observacoes_canhotos', '') or ''
                        new_observacoes_canhotos = st.text_area(
                            "Observações sobre Canhotos (opcional)",
                            value=current_obs_canhotos,
                            placeholder="Ex: Faltam 3 canhotos, prometeu entregar na próxima semana"
                        )
                        
                        update_submitted = st.form_submit_button("Atualizar", type="primary")
                        
                        if update_submitted:
                            try:
                                update_data = {
                                    "venda_id": sales_dict[new_sale_label]['id'],
                                    "valor_pago": new_valor_pago,
                                    "data_pagamento": new_data_pagamento.isoformat(),
                                    "metodo_pagamento": new_metodo_pagamento,
                                    "canhotos_entregues": new_canhotos_entregues,
                                    "canhotos_esperados": quantidade_vendida,
                                    "data_entrega_canhotos": datetime.now().isoformat() if new_canhotos_entregues > 0 else None,
                                    "observacoes_canhotos": new_observacoes_canhotos if new_observacoes_canhotos else None
                                }
                                
                                response = supabase.table('pagamentos').update(update_data).eq('id', payment['id']).execute()
                                
                                if response.data:
                                    st.success("✅ Pagamento atualizado com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("Erro ao atualizar pagamento.")
                            
                            except Exception as e:
                                st.error(f"Erro ao atualizar pagamento: {str(e)}")
                
                with col2:
                    st.subheader("Eliminar")
                    st.warning("⚠️ Esta ação é irreversível!")
                    
                    if st.button("🗑️ Eliminar Pagamento", type="secondary"):
                        try:
                            response = supabase.table('pagamentos').delete().eq('id', payment['id']).execute()
                            
                            if response.data:
                                st.success("✅ Pagamento eliminado com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao eliminar pagamento.")
                        
                        except Exception as e:
                            st.error(f"Erro ao eliminar pagamento: {str(e)}")
        else:
            st.info("Nenhum pagamento disponível para editar.")
    
    except Exception as e:
        st.error(f"Erro ao carregar pagamentos: {str(e)}")
