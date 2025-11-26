import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Devoluções", page_icon="🔄", layout="wide")

st.title("🔄 Gestão de Devoluções")

# Initialize Supabase client
try:
    supabase = get_supabase_client()
except ValueError as e:
    st.error(f"Erro ao conectar ao Supabase: {str(e)}")
    st.stop()

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Registar Devolução", "✏️ Editar/Eliminar"])

# Tab 1: List returns
with tab1:
    st.subheader("Lista de Devoluções")
    
    try:
        # Check if table exists
        response = supabase.table('devolucoes').select(
            '*, escuteiros(nome), blocos_rifas(id, nome, campanha_id)'
        ).order('data_devolucao', desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)

            # Flatten nested data
            if 'escuteiros' in df.columns:
                df['escuteiro_nome'] = df['escuteiros'].apply(lambda x: x['nome'] if x else 'N/A')
            if 'blocos_rifas' in df.columns:
                df['bloco_nome'] = df['blocos_rifas'].apply(lambda x: x['nome'] if x else 'N/A')

                # Try to extract campanha_id from nested bloco and fetch campaign names
                try:
                    df['campanha_id'] = df['blocos_rifas'].apply(lambda x: x.get('campanha_id') if x and 'campanha_id' in x else None)
                    campanha_ids = df['campanha_id'].dropna().unique().tolist()
                    if campanha_ids:
                        campanhas_resp = supabase.table('campanhas').select('id, nome').in_('id', campanha_ids).execute()
                        campanhas_map = {c['id']: c['nome'] for c in (campanhas_resp.data or [])}
                        df['campanha_nome'] = df['campanha_id'].map(campanhas_map).fillna('N/A')
                    else:
                        df['campanha_nome'] = 'N/A'
                except Exception:
                    df['campanha_nome'] = 'N/A'

            # Select and reorder columns (include campanha)
            display_cols = ['data_devolucao', 'escuteiro_nome', 'campanha_nome', 'bloco_nome', 'quantidade', 'motivo', 'id']
            df_display = df[[col for col in display_cols if col in df.columns]]

            st.dataframe(
                df_display,
                column_config={
                    "data_devolucao": st.column_config.DatetimeColumn("Data da Devolução", format="DD/MM/YYYY HH:mm"),
                    "escuteiro_nome": "Escuteiro",
                    "campanha_nome": "Campanha",
                    "bloco_nome": "Bloco de Rifas",
                    "quantidade": "Quantidade Devolvida",
                    "motivo": "Motivo",
                    "id": "ID"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Statistics
            total_devolucoes = len(df)
            total_rifas_devolvidas = df['quantidade'].sum() if 'quantidade' in df.columns else 0
            
            col1, col2 = st.columns(2)
            col1.metric("Total de Devoluções", total_devolucoes)
            col2.metric("Total de Rifas Devolvidas", int(total_rifas_devolvidas))
            # If a new devolução was just created, show a highlighted box with details
            if 'last_devolucao' in st.session_state and st.session_state.get('last_devolucao'):
                ld = st.session_state['last_devolucao']
                try:
                    esc_nome = ld.get('escuteiros', {}).get('nome') if ld.get('escuteiros') else None
                except Exception:
                    esc_nome = None
                try:
                    bloco_nome = ld.get('blocos_rifas', {}).get('nome') if ld.get('blocos_rifas') else None
                except Exception:
                    bloco_nome = None
                st.success(f"Última devolução registada: {ld.get('quantidade')} rifas | Escuteiro: {esc_nome or 'N/A'} | Bloco: {bloco_nome or 'N/A'} | ID: {ld.get('id')}")
                if st.button("Marcar como lida / Remover destaque"):
                    del st.session_state['last_devolucao']
        else:
            st.info("Nenhuma devolução registada ainda.")
    
    except Exception as e:
        st.warning(f"⚠️ Tabela 'devolucoes' não encontrada ou erro ao carregar: {str(e)}")
        st.info("""
        Para usar esta funcionalidade, execute o SQL completo do ficheiro `utils/database_schema.py` 
        no Supabase SQL Editor para criar a tabela de devoluções.
        """)

# Tab 2: Add new return
with tab2:
    st.subheader("Registar Nova Devolução")
    
    # Load campaigns, scouts and blocks for selection
    try:
        # Load campaigns to allow filtering by campanha
        campanhas_response = supabase.table('campanhas').select('*').order('created_at', desc='desc').execute()

        # Default: no campanha selected
        selected_campanha = None
        if campanhas_response.data:
            campanhas_dict = {c['nome']: c for c in campanhas_response.data}

            # choose default index as active campaign when available
            default_idx = 0
            for idx, c in enumerate(campanhas_response.data):
                if c.get('ativa', False):
                    default_idx = idx
                    break

            col1, col2 = st.columns([3, 1])
            with col1:
                selected_campanha_name = st.selectbox(
                    "🎯 Filtrar por Campanha",
                    options=list(campanhas_dict.keys()),
                    index=default_idx,
                    help="Escolha a campanha para filtrar os blocos de rifas"
                )
                selected_campanha = campanhas_dict[selected_campanha_name]
            with col2:
                st.metric("", f"{'✅ Ativa' if selected_campanha.get('ativa') else '⏸️ Inativa'}")
        else:
            st.warning("⚠️ Nenhuma campanha criada. Crie uma campanha primeiro na página 'Campanhas'.")
            st.stop()

        scouts_response = supabase.table('escuteiros').select('id, nome').order('nome').execute()

        # Fetch blocks only for the selected campaign
        blocks_response = supabase.table('blocos_rifas').select('id, nome, numero_inicial, numero_final, escuteiro_id, campanha_id').eq('campanha_id', selected_campanha['id']).order('nome').execute()

        if not scouts_response.data:
            st.warning("⚠️ Não há escuteiros registados. Por favor, adicione escuteiros primeiro.")
        elif not blocks_response.data:
            st.warning("⚠️ Não há blocos de rifas criados para a campanha selecionada. Por favor, crie blocos na página de Campanhas.")
        else:
            # Build selection data outside the form so selection updates immediately
            blocks_dict = {}
            display_labels = []
            id_list = []
            for block in blocks_response.data:
                escuteiro_id = block.get('escuteiro_id')
                if not escuteiro_id:
                    continue
                esc = next((s for s in scouts_response.data if s['id'] == escuteiro_id), None)
                escuteiro_nome = esc['nome'] if esc else 'N/A'
                display_name = f"{block['nome']} (Rifas {block['numero_inicial']}-{block['numero_final']}) | Escuteiro: {escuteiro_nome}"
                blocks_dict[block['id']] = block
                display_labels.append(display_name)
                id_list.append(block['id'])

            display_map = {bid: lbl for bid, lbl in zip(id_list, display_labels)}

            # Cleanup stale session state value if it doesn't match current options
            if 'select_bloco_id' in st.session_state and st.session_state.get('select_bloco_id') not in id_list and st.session_state.get('select_bloco_id') is not None:
                try:
                    del st.session_state['select_bloco_id']
                except Exception:
                    pass

            selected_block_id = None
            total_rifas = 1
            if id_list:
                # include a placeholder None option so nothing is selected by default after submit
                select_options = [None] + id_list
                selected_block_id = st.selectbox(
                    "Bloco de Rifas *",
                    options=select_options,
                    format_func=lambda bid: "-- Selecione um bloco --" if bid is None else display_map.get(bid, str(bid)),
                    key="select_bloco_id"
                )

                # Compute block totals immediately so we can sync number_input via session_state
                if selected_block_id:
                    block_response = supabase.table('blocos_rifas').select('numero_inicial, numero_final').eq('id', selected_block_id).single().execute()
                    if block_response.data:
                        block_tmp = {**blocks_dict[selected_block_id], **block_response.data}
                    else:
                        block_tmp = blocks_dict[selected_block_id]
                    try:
                        total_rifas = int(block_tmp['numero_final']) - int(block_tmp['numero_inicial']) + 1
                    except Exception:
                        total_rifas = 1

                    # If the user changed the selected block, update a stable session_state key for the number input
                    if st.session_state.get('_last_selected_bloco') != selected_block_id:
                        st.session_state['qtd_rifas'] = total_rifas
                        st.session_state['_last_selected_bloco'] = selected_block_id

            with st.form("add_return_form"):
                # The selection widget is outside the form; read selected id from session_state inside the form
                # (selected_block_id will still be available from the variable above)

                # Buscar sempre o bloco atualizado do banco (para registrar)
                block = None
                if selected_block_id:
                    block_response = supabase.table('blocos_rifas').select('numero_inicial, numero_final').eq('id', selected_block_id).single().execute()
                    if block_response.data:
                        block = {**blocks_dict[selected_block_id], **block_response.data}
                    else:
                        block = blocks_dict[selected_block_id]

                # Quantity
                if block:
                    st.info(f"📊 Este bloco tem {total_rifas} rifas no total")

                # Ensure the initial value never exceeds the computed max (to avoid Streamlit ValueError)
                initial_qtd = st.session_state.get('qtd_rifas', total_rifas)
                try:
                    initial_qtd = int(initial_qtd)
                except Exception:
                    initial_qtd = total_rifas
                initial_qtd = min(max(1, total_rifas if total_rifas is None else total_rifas), max(1, initial_qtd))

                quantidade = st.number_input(
                    "Quantidade de Rifas Devolvidas *",
                    min_value=1,
                    max_value=total_rifas,
                    value=min(initial_qtd, total_rifas),
                    step=1,
                    key='qtd_rifas'
                )

                motivo = st.text_area(
                    "Motivo da Devolução",
                    placeholder="Ex: Rifas não vendidas, mudança de escuteiro, etc.",
                    help="Opcional: descreva o motivo da devolução",
                    key='motivo_devolucao'
                )

                data_devolucao = st.date_input(
                    "Data da Devolução",
                    value=st.session_state.get('data_devolucao', datetime.now().date()),
                    key='data_devolucao'
                )

                submitted = st.form_submit_button("Registar Devolução", type="primary")

                if submitted:
                    if not selected_block_id:
                        st.error("Por favor, selecione um bloco de rifas!")
                    else:
                        block = blocks_dict[selected_block_id]
                        escuteiro_id = block.get('escuteiro_id')
                        if not escuteiro_id:
                            st.error("Este bloco não está atribuído a nenhum escuteiro. Não é possível registar devolução.")
                        else:
                            try:
                                block_id = block['id']
                                payload = {
                                    "escuteiro_id": escuteiro_id,
                                    "bloco_id": block_id,
                                    "quantidade": quantidade,
                                    "motivo": motivo.strip() if motivo else None,
                                    "data_devolucao": data_devolucao.isoformat()
                                }
                                response = supabase.table('devolucoes').insert(payload).execute()
                            except Exception as e:
                                st.error(f"Erro ao registar devolução: {str(e)}")
                                if "devolucoes" in str(e).lower():
                                    st.info("Execute o schema SQL completo para criar a tabela 'devolucoes'.")
                            else:
                                if response.data:
                                    # capture the inserted record (supabase returns a list)
                                    inserted = None
                                    try:
                                        if isinstance(response.data, list) and len(response.data) > 0:
                                            inserted = response.data[0]
                                        else:
                                            inserted = response.data
                                    except Exception:
                                        inserted = None

                                    st.success(f"✅ Devolução de {quantidade} rifas registada com sucesso!")
                                    # Optionally update block status
                                    try:
                                        supabase.table('blocos_rifas').update({
                                            'estado': 'devolvido'
                                        }).eq('id', block_id).execute()
                                    except Exception:
                                        pass  # Estado column might not exist

                                    # store the last inserted devolucao in session_state so Lista pode destacar
                                    if inserted:
                                        st.session_state['last_devolucao'] = inserted

                                    # Clear form-related session state to avoid leaving old values in the UI
                                    try:
                                        st.session_state['qtd_rifas'] = 1
                                    except Exception:
                                        pass
                                    try:
                                        st.session_state['motivo_devolucao'] = ''
                                    except Exception:
                                        pass
                                    try:
                                        st.session_state['data_devolucao'] = datetime.now().date()
                                    except Exception:
                                        pass

                                    # Remove selection caches so selectbox reinitializes (optional)
                                    for k in ['_last_selected_bloco']:
                                        if k in st.session_state:
                                            try:
                                                del st.session_state[k]
                                            except Exception:
                                                pass

                                    # Also clear the bloco select so dropdown shows no selection
                                    try:
                                        st.session_state['select_bloco_id'] = None
                                    except Exception:
                                        try:
                                            del st.session_state['select_bloco_id']
                                        except Exception:
                                            pass

                                    # Show an explicit action to go view the list (no immediate rerun)
                                    if st.button("🔎 Ver na Lista / Recarregar página"):
                                        st.experimental_rerun()
                                else:
                                    st.error("Erro ao registar devolução.")

            # Show a clear summary of the last created devolução in this tab to avoid confusion
            if 'last_devolucao' in st.session_state and st.session_state.get('last_devolucao'):
                ld = st.session_state['last_devolucao']
                try:
                    df_ld = pd.DataFrame([{
                        'data_devolucao': ld.get('data_devolucao'),
                        'escuteiro': (ld.get('escuteiros') or {}).get('nome') if isinstance(ld.get('escuteiros'), dict) else None,
                        'bloco': (ld.get('blocos_rifas') or {}).get('nome') if isinstance(ld.get('blocos_rifas'), dict) else None,
                        'quantidade': ld.get('quantidade'),
                        'motivo': ld.get('motivo'),
                        'id': ld.get('id')
                    }])
                    st.markdown("---")
                    st.success("Devolução registada — resumo abaixo:")
                    st.dataframe(df_ld, hide_index=True, use_container_width=True)
                    col_a, col_b = st.columns([1, 1])
                    with col_a:
                        if st.button("Ir para Lista (ver destaque)"):
                            st.experimental_rerun()
                    with col_b:
                        if st.button("Limpar resumo"):
                            try:
                                del st.session_state['last_devolucao']
                                st.experimental_rerun()
                            except Exception:
                                pass
                except Exception:
                    st.info("Devolução registada com sucesso.")

    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

# Tab 3: Edit/Delete returns
with tab3:
    st.subheader("Editar ou Eliminar Devolução")
    
    try:
        response = supabase.table('devolucoes').select(
            '*, escuteiros(nome), blocos_rifas(id, nome, campanha_id)'
        ).order('data_devolucao', desc=True).execute()
        
        if response.data:
            # Create a dictionary for return selection
            returns_list = []
            for ret in response.data:
                scout_name = ret.get('escuteiros', {}).get('nome', 'N/A') if ret.get('escuteiros') else 'N/A'
                block_name = ret.get('blocos_rifas', {}).get('nome', 'N/A') if ret.get('blocos_rifas') else 'N/A'
                label = f"{ret['data_devolucao'][:10]} - {scout_name} - {block_name} - {ret['quantidade']} rifas ({ret['id'][:8]}...)"
                returns_list.append((label, ret))
            
            returns_dict = dict(returns_list)
            
            selected_return_label = st.selectbox(
                "Selecione uma devolução",
                options=list(returns_dict.keys())
            )
            
            if selected_return_label:
                ret = returns_dict[selected_return_label]
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader("Detalhes da Devolução")
                    st.info(f"""
                    **Escuteiro:** {ret.get('escuteiros', {}).get('nome', 'N/A') if ret.get('escuteiros') else 'N/A'}  
                    **Bloco:** {ret.get('blocos_rifas', {}).get('nome', 'N/A') if ret.get('blocos_rifas') else 'N/A'}  
                    **Quantidade:** {ret['quantidade']} rifas  
                    **Data:** {ret['data_devolucao'][:10]}  
                    **Motivo:** {ret.get('motivo', 'Não especificado')}
                    """)
                
                with col2:
                    st.subheader("Eliminar")
                    st.warning("⚠️ Esta ação é irreversível!")
                    
                    if st.button("🗑️ Eliminar Devolução", type="secondary"):
                        try:
                            response = supabase.table('devolucoes').delete().eq('id', ret['id']).execute()
                            
                            if response.data:
                                st.success("✅ Devolução eliminada com sucesso!")
                                st.info("🔄 A página será recarregada...")
                                import time
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error("Erro ao eliminar devolução.")
                        
                        except Exception as e:
                            st.error(f"Erro ao eliminar devolução: {str(e)}")
        else:
            st.info("Nenhuma devolução disponível para editar.")
    
    except Exception as e:
        st.warning(f"Erro ao carregar devoluções: {str(e)}")
        st.info("Certifique-se de que a tabela 'devolucoes' foi criada na base de dados.")
