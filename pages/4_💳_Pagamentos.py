import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Pagamentos", page_icon="💳", layout="wide")

st.title("💳 Gestão de Pagamentos")

# Initialize Supabase client
try:
    supabase = get_supabase_client()
except ValueError as e:
    st.error(f"Erro ao conectar ao Supabase: {str(e)}")
    st.stop()

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Registar Pagamento", "✏️ Editar/Eliminar"])

# Tab 1: List payments
with tab1:
    st.subheader("Lista de Pagamentos")
    
    try:
        # Fetch payments with related sales data
        response = supabase.table('pagamentos').select(
            '*, vendas(valor_total, escuteiros(nome), blocos_rifas(nome))'
        ).order('data_pagamento', desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Flatten nested data
            if 'vendas' in df.columns:
                df['escuteiro_nome'] = df['vendas'].apply(
                    lambda x: x.get('escuteiros', {}).get('nome', 'N/A') if x and x.get('escuteiros') else 'N/A'
                )
                df['bloco_nome'] = df['vendas'].apply(
                    lambda x: x.get('blocos_rifas', {}).get('nome', 'N/A') if x and x.get('blocos_rifas') else 'N/A'
                )
                df['valor_venda'] = df['vendas'].apply(
                    lambda x: x.get('valor_total', 0) if x else 0
                )
            
            # Select and reorder columns
            display_cols = ['data_pagamento', 'escuteiro_nome', 'bloco_nome', 'valor_pago', 'valor_venda', 'metodo_pagamento', 'id']
            df_display = df[[col for col in display_cols if col in df.columns]]
            
            st.dataframe(
                df_display,
                column_config={
                    "data_pagamento": "Data do Pagamento",
                    "escuteiro_nome": "Escuteiro",
                    "bloco_nome": "Bloco",
                    "valor_pago": st.column_config.NumberColumn(
                        "Valor Pago",
                        format="%.2f €"
                    ),
                    "valor_venda": st.column_config.NumberColumn(
                        "Valor da Venda",
                        format="%.2f €"
                    ),
                    "metodo_pagamento": "Método de Pagamento",
                    "id": "ID"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Statistics
            total_pagamentos = len(df)
            total_pago = df['valor_pago'].sum() if 'valor_pago' in df.columns else 0
            
            col1, col2 = st.columns(2)
            col1.metric("Total de Pagamentos", total_pagamentos)
            col2.metric("Valor Total Recebido", f"{total_pago:.2f} €")
        else:
            st.info("Nenhum pagamento registado ainda.")
    
    except Exception as e:
        st.error(f"Erro ao carregar pagamentos: {str(e)}")

# Tab 2: Add new payment
with tab2:
    st.subheader("Registar Novo Pagamento")
    
    # Load sales for selection
    try:
        sales_response = supabase.table('vendas').select(
            '*, escuteiros(nome), blocos_rifas(nome)'
        ).order('data_venda', desc=True).execute()
        
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
            sales_list = []
            for sale in sales_response.data:
                scout_name = sale.get('escuteiros', {}).get('nome', 'N/A') if sale.get('escuteiros') else 'N/A'
                block_name = sale.get('blocos_rifas', {}).get('nome', 'N/A') if sale.get('blocos_rifas') else 'N/A'
                valor_total = float(sale['valor_total'])
                valor_pago = payments_by_sale.get(sale['id'], 0)
                saldo = valor_total - valor_pago
                
                status = "✅ Pago" if saldo <= 0 else f"⚠️ Pendente: {saldo:.2f} €"
                label = f"{sale['data_venda'][:10]} - {scout_name} - {block_name} - {valor_total:.2f} € ({status})"
                sales_list.append((label, sale, saldo))
            
            with st.form("add_payment_form"):
                # Sale selection
                sales_dict = {label: (sale, saldo) for label, sale, saldo in sales_list}
                selected_sale_label = st.selectbox(
                    "Venda *",
                    options=list(sales_dict.keys())
                )
                
                if selected_sale_label:
                    selected_sale, saldo_pendente = sales_dict[selected_sale_label]
                    valor_total = float(selected_sale['valor_total'])
                    
                    if saldo_pendente > 0:
                        st.info(f"💶 Valor da Venda: **{valor_total:.2f} €** | Saldo Pendente: **{saldo_pendente:.2f} €**")
                        default_valor = saldo_pendente
                    else:
                        st.success(f"✅ Esta venda já está totalmente paga ({valor_total:.2f} €)")
                        default_valor = 0.0
                    
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
