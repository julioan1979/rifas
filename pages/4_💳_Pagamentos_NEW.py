# Gestão de Pagamentos - Fluxo Direto por Bloco
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
        # Fetch payments with blocks (new flow) and legacy vendas
        response = supabase.table('pagamentos').select(
            '*, blocos_rifas(numero_inicial, numero_final, campanha_id, escuteiros(nome)), vendas(blocos_rifas(numero_inicial, numero_final, campanha_id, escuteiros(nome)))'
        ).order('data_pagamento', desc=True).execute()
        
        if response.data:
            # Filter by campaign
            pagamentos_campanha = []
            for pag in response.data:
                # Check if it's new flow (bloco_id) or legacy (venda_id)
                if pag.get('blocos_rifas') and pag['blocos_rifas'].get('campanha_id') == selected_campanha['id']:
                    pagamentos_campanha.append(pag)
                elif pag.get('vendas') and pag['vendas'].get('blocos_rifas', {}).get('campanha_id') == selected_campanha['id']:
                    pagamentos_campanha.append(pag)
            
            if pagamentos_campanha:
                df = pd.DataFrame(pagamentos_campanha)
                
                # Flatten nested data (supports both flows)
                def get_escuteiro_nome(row):
                    if row.get('blocos_rifas'):
                        return row['blocos_rifas'].get('escuteiros', {}).get('nome', 'N/A')
                    elif row.get('vendas'):
                        return row['vendas'].get('blocos_rifas', {}).get('escuteiros', {}).get('nome', 'N/A')
                    return 'N/A'
                
                def get_bloco_info(row):
                    if row.get('blocos_rifas'):
                        b = row['blocos_rifas']
                        return f"Rifas {b.get('numero_inicial', '')}-{b.get('numero_final', '')}"
                    elif row.get('vendas'):
                        b = row['vendas'].get('blocos_rifas', {})
                        return f"Rifas {b.get('numero_inicial', '')}-{b.get('numero_final', '')}"
                    return 'N/A'
                
                df['escuteiro_nome'] = df.apply(get_escuteiro_nome, axis=1)
                df['bloco_info'] = df.apply(get_bloco_info, axis=1)
                
                # Add stub status column
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
                
                # Format date
                if 'data_pagamento' in df.columns:
                    df['data_pagamento'] = pd.to_datetime(df['data_pagamento']).dt.strftime('%d-%m-%Y')
                
                # Reorder columns
                colunas_ordem = ['data_pagamento', 'escuteiro_nome', 'bloco_info', 'valor_pago', 'quantidade_rifas', 'status_canhotos', 'metodo_pagamento', 'referencia', 'observacoes']
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
                        "quantidade_rifas": st.column_config.NumberColumn(
                            "Rifas Vendidas",
                            help="Quantidade de rifas vendidas do bloco"
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
                st.info("Nenhum pagamento registado nesta campanha.")
        else:
            st.info("Nenhum pagamento registado ainda.")
    
    except Exception as e:
        st.error(f"Erro ao carregar pagamentos: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# Tab 2: Add new payment (NOVO FLUXO DIRETO)
with tab2:
    st.subheader("Registar Novo Pagamento")
    
    st.info("""
    **Fluxo Simplificado:**
    1. Escolha o bloco atribuído ao escuteiro
    2. Indique quantas rifas vendeu
    3. Registe o valor e canhotos entregues
    """)
    
    try:
        # Get blocks for this campaign with assigned scouts
        blocos_response = supabase.table('blocos_rifas').select(
            '*, escuteiros(nome)'
        ).eq('campanha_id', selected_campanha['id']).not_.is_('escuteiro_id', 'null').order('numero_inicial').execute()
        
        if not blocos_response.data:
            st.warning("⚠️ Não há blocos atribuídos a escuteiros nesta campanha.")
        else:
            # Get existing payments to calculate pending balance
            pagamentos_response = supabase.table('pagamentos').select(
                'bloco_id, valor_pago, quantidade_rifas, canhotos_entregues'
            ).not_.is_('bloco_id', 'null').execute()
            
            payments_by_bloco = {}
            canhotos_by_bloco = {}
            rifas_by_bloco = {}
            if pagamentos_response.data:
                for payment in pagamentos_response.data:
                    bloco_id = payment['bloco_id']
                    if bloco_id not in payments_by_bloco:
                        payments_by_bloco[bloco_id] = 0
                        canhotos_by_bloco[bloco_id] = 0
                        rifas_by_bloco[bloco_id] = 0
                    payments_by_bloco[bloco_id] += float(payment['valor_pago'])
                    canhotos_by_bloco[bloco_id] += int(payment.get('canhotos_entregues', 0) or 0)
                    rifas_by_bloco[bloco_id] += int(payment.get('quantidade_rifas', 0) or 0)
            
            # Build list of blocks with pending balance
            blocos_dict = {}
            for bloco in blocos_response.data:
                escuteiro_nome = bloco.get('escuteiros', {}).get('nome', 'N/A') if bloco.get('escuteiros') else 'N/A'
                bloco_info = f"Rifas {bloco['numero_inicial']}-{bloco['numero_final']}"
                total_rifas_bloco = bloco['numero_final'] - bloco['numero_inicial'] + 1
                valor_total_bloco = total_rifas_bloco * float(bloco['preco_unitario'])
                
                total_pago = payments_by_bloco.get(bloco['id'], 0)
                rifas_reportadas = rifas_by_bloco.get(bloco['id'], 0)
                canhotos_entregues = canhotos_by_bloco.get(bloco['id'], 0)
                
                saldo_pendente = valor_total_bloco - total_pago
                rifas_pendentes = total_rifas_bloco - rifas_reportadas
                canhotos_pendentes = rifas_reportadas - canhotos_entregues
                
                label = f"{escuteiro_nome} - {bloco_info} ({total_rifas_bloco} rifas) | Reportado: {rifas_reportadas} | Pago: {total_pago:.2f}€ | Canhotos: {canhotos_entregues}"
                
                blocos_dict[label] = {
                    'bloco': bloco,
                    'saldo_pendente': saldo_pendente,
                    'valor_total_bloco': valor_total_bloco,
                    'total_rifas_bloco': total_rifas_bloco,
                    'rifas_reportadas': rifas_reportadas,
                    'rifas_pendentes': rifas_pendentes,
                    'canhotos_entregues': canhotos_entregues,
                    'canhotos_pendentes': canhotos_pendentes
                }
            
            with st.form("add_payment_form"):
                if not blocos_dict:
                    st.warning("⚠️ Todos os blocos já foram totalmente processados.")
                    st.form_submit_button("Registar Pagamento", type="primary", disabled=True)
                else:
                    selected_bloco_label = st.selectbox(
                        "Bloco de Rifas *",
                        options=list(blocos_dict.keys()),
                        help="Escolha o bloco para registar prestação de contas"
                    )
                    
                    if selected_bloco_label:
                        bloco_data = blocos_dict[selected_bloco_label]
                        bloco = bloco_data['bloco']
                        
                        st.info(f"📊 **Bloco:** {bloco['numero_inicial']}-{bloco['numero_final']} ({bloco_data['total_rifas_bloco']} rifas) | **Valor total:** {bloco_data['valor_total_bloco']:.2f}€")
                        st.info(f"💰 **Já reportado:** {bloco_data['rifas_reportadas']} rifas | **Já pago:** {bloco_data['saldo_pendente']:.2f}€ pendente")
                        
                        # Quantity sold
                        quantidade_rifas = st.number_input(
                            "Quantas rifas vendeu agora? *",
                            min_value=0,
                            max_value=bloco_data['rifas_pendentes'],
                            value=0,
                            help=f"Máximo: {bloco_data['rifas_pendentes']} rifas ainda não reportadas"
                        )
                        
                        if quantidade_rifas > 0:
                            valor_esperado = quantidade_rifas * float(bloco['preco_unitario'])
                            st.success(f"💶 Valor esperado: {valor_esperado:.2f}€ ({quantidade_rifas} × {bloco['preco_unitario']:.2f}€)")
                            
                            # Payment amount
                            valor_pago = st.number_input(
                                "Valor a Pagar (€) *",
                                min_value=0.01,
                                value=float(valor_esperado),
                                step=0.10,
                                format="%.2f",
                                help="Pode ser diferente se houver desconto ou problema"
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
                            
                            st.info(f"📋 **Rifas a reportar agora:** {quantidade_rifas} | **Canhotos esperados:** {quantidade_rifas}")
                            
                            # Number of stubs delivered
                            canhotos_entregues = st.number_input(
                                "Canhotos a Entregar Agora",
                                min_value=0,
                                max_value=quantidade_rifas,
                                value=quantidade_rifas,
                                help="Quantos canhotos o escuteiro entrega com este pagamento"
                            )
                            
                            # Visual feedback
                            if canhotos_entregues == quantidade_rifas:
                                st.success(f"✅ Todos os {quantidade_rifas} canhotos serão marcados como entregues")
                            elif canhotos_entregues > 0:
                                st.warning(f"⚠️ Entrega parcial: {canhotos_entregues}/{quantidade_rifas} canhotos")
                            else:
                                st.error(f"❌ Nenhum canhoto registado")
                            
                            # Optional notes about stubs
                            observacoes_canhotos = st.text_area(
                                "Observações sobre Canhotos (opcional)",
                                placeholder="Ex: Faltam 3 canhotos, prometeu entregar na próxima semana"
                            )
                            
                            submitted = st.form_submit_button("Registar Pagamento", type="primary")
                            
                            if submitted:
                                try:
                                    data = {
                                        "bloco_id": bloco['id'],
                                        "quantidade_rifas": quantidade_rifas,
                                        "valor_pago": valor_pago,
                                        "data_pagamento": data_pagamento.isoformat(),
                                        "metodo_pagamento": metodo_pagamento,
                                        "canhotos_entregues": canhotos_entregues,
                                        "canhotos_esperados": quantidade_rifas,
                                        "data_entrega_canhotos": datetime.now().isoformat() if canhotos_entregues > 0 else None,
                                        "observacoes_canhotos": observacoes_canhotos if observacoes_canhotos else None
                                    }
                                    
                                    response = supabase.table('pagamentos').insert(data).execute()
                                    
                                    if response.data:
                                        st.success(f"✅ Pagamento de {valor_pago:.2f}€ registado com sucesso!")
                                        if canhotos_entregues > 0:
                                            st.success(f"📄 {canhotos_entregues} canhotos registados como entregues")
                                        st.rerun()
                                    else:
                                        st.error("Erro ao registar pagamento.")
                                
                                except Exception as e:
                                    st.error(f"Erro ao registar pagamento: {str(e)}")
                        else:
                            st.form_submit_button("Registar Pagamento", type="primary", disabled=True)
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
        import traceback
        st.code(traceback.format_exc())

# Tab 3: Edit/Delete payments
with tab3:
    st.subheader("Editar ou Eliminar Pagamento")
    st.warning("⚠️ Funcionalidade de edição será implementada após migração completa.")
    st.info("Por agora, use o SQL Editor do Supabase para editar pagamentos manualmente se necessário.")
