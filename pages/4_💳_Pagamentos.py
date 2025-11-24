# Página descontinuada: Pagamentos comprador→escuteiro
import streamlit as st

st.set_page_config(page_title="Pagamentos (Descontinuado)", page_icon="💳", layout="wide")

st.title("💳 Pagamentos — Descontinuado")

st.warning(
    "A funcionalidade de registo de pagamentos comprador→escuteiro foi descontinuada.\n"
    "O fluxo oficial agora é: Escuteiro → Organização.\n\n"
    "Consulte o README e `docs/MIGRATION_PAYMENTS.md` para o processo de consolidação e as instruções para conciliação.`"
)

st.info("Se precisa de auditar ou migrar os dados históricos, utilize o script em `scripts/consolidar_pagamentos_para_blocos.sql` em ambiente de staging.")

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
            
            # Formatar data (sem hora)
            if 'data_pagamento' in df.columns:
                df['data_pagamento'] = pd.to_datetime(df['data_pagamento']).dt.strftime('%d-%m-%Y')
            
            # Reordenar colunas para melhor visualização
            colunas_ordem = ['data_pagamento', 'escuteiro_nome', 'bloco_info', 'valor_pago', 'valor_venda', 'metodo_pagamento', 'referencia', 'observacoes']
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
            
            col1, col2 = st.columns(2)
            col1.metric("📊 Total de Pagamentos", total_pagamentos)
            col2.metric("💰 Valor Total Recebido", f"{total_pago:.2f} €")
        else:
            st.info("Nenhum pagamento registado ainda.")
    
    except Exception as e:
        st.error(f"Erro ao carregar pagamentos: {str(e)}")

# Tab 2: Add new payment
with tab2:
    st.subheader("Registar Novo Pagamento")
    
    st.info("""
    **Atenção:** Esta página regista pagamentos de **vendas individuais** (comprador paga ao escuteiro).
    
    Para registar pagamentos do **escuteiro à organização**, use a página **💵 Controle Escuteiros**.
    """)
    
    # Load sales for selection
    try:
        sales_response = supabase.table('vendas').select(
            '*, escuteiros(nome), blocos_rifas!inner(numero_inicial, numero_final, campanha_id)'
        ).eq('blocos_rifas.campanha_id', selected_campanha['id']).order('data_venda', desc=True).execute()
        
        if not sales_response.data:
            st.warning("⚠️ Não há vendas registadas. Por favor, registe vendas primeiro.")
        else:
            # Check which sales already have payments
            payments_response = supabase.table('pagamentos').select('venda_id, valor_pago').execute()
            payments_by_sale = {}
            if payments_response.data:
                for payment in payments_response.data:
                    sale_id = payment['venda_id']
                    if sale_id not in payments_by_sale:
                        payments_by_sale[sale_id] = 0
                    payments_by_sale[sale_id] += float(payment['valor_pago'])
            
            # Create sales list with payment status
            sales_list_pendentes = []
            sales_list_pagas = []
            
            for sale in sales_response.data:
                scout_name = sale.get('escuteiros', {}).get('nome', 'N/A') if sale.get('escuteiros') else 'N/A'
                block_info = f"Rifas {sale.get('blocos_rifas', {}).get('numero_inicial', '')}-{sale.get('blocos_rifas', {}).get('numero_final', '')}"
                valor_total = float(sale['valor_total'])
                valor_pago = payments_by_sale.get(sale['id'], 0)
                saldo = valor_total - valor_pago
                
                if saldo > 0.01:  # Tem saldo pendente
                    status = f"⏳ Pendente: {saldo:.2f} €"
                    label = f"{sale['data_venda'][:10]} - {scout_name} - {block_info} - {valor_total:.2f} € ({status})"
                    sales_list_pendentes.append((label, sale, saldo))
                else:  # Já pago
                    status = "✅ Pago"
                    label = f"{sale['data_venda'][:10]} - {scout_name} - {block_info} - {valor_total:.2f} € ({status})"
                    sales_list_pagas.append((label, sale, saldo))
            
            # Show filter option
            mostrar_todas = st.checkbox(
                "Mostrar também vendas já pagas",
                value=False,
                help="Por padrão, mostra apenas vendas com pagamento pendente"
            )
            
            if mostrar_todas:
                sales_list = sales_list_pendentes + sales_list_pagas
            else:
                sales_list = sales_list_pendentes
            
            if not sales_list:
                if mostrar_todas:
                    st.info("Não há vendas registadas nesta campanha.")
                else:
                    st.success("✅ Todas as vendas desta campanha estão pagas!")
                    st.info("Active a opção 'Mostrar também vendas já pagas' para ver todas as vendas.")
            else:
                st.info(f"📊 **{len(sales_list_pendentes)}** vendas com pagamento pendente | **{len(sales_list_pagas)}** vendas pagas")
            
            with st.form("add_payment_form"):
                # Sale selection
                sales_dict = {label: (sale, saldo) for label, sale, saldo in sales_list}
                
                if not sales_dict:
                    st.warning("⚠️ Não há vendas disponíveis para registar pagamento.")
                    st.form_submit_button("Registar Pagamento", type="primary", disabled=True)
                else:
                    selected_sale_label = st.selectbox(
                        "Venda *",
                        options=list(sales_dict.keys()),
                        help="Vendas pendentes aparecem primeiro"
                    )
                
                if selected_sale_label:
                    selected_sale, saldo_pendente = sales_dict[selected_sale_label]
                    valor_total = float(selected_sale['valor_total'])
                    
                    if saldo_pendente > 0.01:
                        st.info(f"💶 Valor da Venda: **{valor_total:.2f} €** | Saldo Pendente: **{saldo_pendente:.2f} €**")
                        default_valor = saldo_pendente
                    else:
                        st.warning(f"⚠️ Esta venda já está totalmente paga ({valor_total:.2f} €)")
                        default_valor = 0.01
                    
                    # Payment amount
                    valor_pago = st.number_input(
                        "Valor a Pagar (€) *",
                        min_value=0.01,
                        value=default_valor,
                        step=0.10,
                        format="%.2f"
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
                    
                    submitted = st.form_submit_button("Registar Pagamento", type="primary")
                    
                    if submitted:
                        try:
                            data = {
                                "venda_id": selected_sale['id'],
                                "valor_pago": valor_pago,
                                "data_pagamento": data_pagamento.isoformat(),
                                "metodo_pagamento": metodo_pagamento
                            }
                            
                            response = supabase.table('pagamentos').insert(data).execute()
                            
                            if response.data:
                                st.success(f"✅ Pagamento de {valor_pago:.2f} € registado com sucesso!")
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
                        
                        update_submitted = st.form_submit_button("Atualizar", type="primary")
                        
                        if update_submitted:
                            try:
                                update_data = {
                                    "venda_id": sales_dict[new_sale_label]['id'],
                                    "valor_pago": new_valor_pago,
                                    "data_pagamento": new_data_pagamento.isoformat(),
                                    "metodo_pagamento": new_metodo_pagamento
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
