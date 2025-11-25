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
            '*, escuteiros(nome), blocos_rifas(nome)'
        ).order('data_devolucao', desc=True).execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Flatten nested data
            if 'escuteiros' in df.columns:
                df['escuteiro_nome'] = df['escuteiros'].apply(lambda x: x['nome'] if x else 'N/A')
            if 'blocos_rifas' in df.columns:
                df['bloco_nome'] = df['blocos_rifas'].apply(lambda x: x['nome'] if x else 'N/A')
            
            # Select and reorder columns
            display_cols = ['data_devolucao', 'escuteiro_nome', 'bloco_nome', 'quantidade', 'motivo', 'id']
            df_display = df[[col for col in display_cols if col in df.columns]]
            
            st.dataframe(
                df_display,
                column_config={
                    "data_devolucao": st.column_config.DatetimeColumn("Data da Devolução", format="DD/MM/YYYY HH:mm"),
                    "escuteiro_nome": "Escuteiro",
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
    
    # Load scouts and blocks for selection
    try:
        scouts_response = supabase.table('escuteiros').select('id, nome').order('nome').execute()
        blocks_response = supabase.table('blocos_rifas').select('id, nome, numero_inicial, numero_final').order('nome').execute()
        
        if not scouts_response.data:
            st.warning("⚠️ Não há escuteiros registados. Por favor, adicione escuteiros primeiro.")
        elif not blocks_response.data:
            st.warning("⚠️ Não há blocos de rifas criados. Por favor, crie blocos de rifas primeiro.")
        else:
            with st.form("add_return_form"):
                # Scout selection
                scouts_dict = {scout['nome']: scout for scout in scouts_response.data}
                selected_scout = st.selectbox(
                    "Escuteiro *",
                    options=list(scouts_dict.keys())
                )
                
                # Block selection
                blocks_dict = {f"{block['nome']} (Rifas {block['numero_inicial']}-{block['numero_final']})": block 
                              for block in blocks_response.data}
                selected_block = st.selectbox(
                    "Bloco de Rifas *",
                    options=list(blocks_dict.keys())
                )
                
                # Quantity
                if selected_block:
                    block = blocks_dict[selected_block]
                    total_rifas = block['numero_final'] - block['numero_inicial'] + 1
                    st.info(f"📊 Este bloco tem {total_rifas} rifas no total")
                    
                    quantidade = st.number_input(
                        "Quantidade de Rifas Devolvidas *",
                        min_value=1,
                        max_value=total_rifas,
                        value=total_rifas,
                        step=1
                    )
                else:
                    quantidade = st.number_input(
                        "Quantidade de Rifas Devolvidas *",
                        min_value=1,
                        value=1,
                        step=1
                    )
                
                # Reason
                motivo = st.text_area(
                    "Motivo da Devolução",
                    placeholder="Ex: Rifas não vendidas, mudança de escuteiro, etc.",
                    help="Opcional: descreva o motivo da devolução"
                )
                
                # Return date
                data_devolucao = st.date_input(
                    "Data da Devolução",
                    value=datetime.now()
                )
                
                submitted = st.form_submit_button("Registar Devolução", type="primary")
                
                if submitted:
                    if not selected_scout or not selected_block:
                        st.error("Por favor, selecione um escuteiro e um bloco de rifas!")
                    else:
                        try:
                            scout_id = scouts_dict[selected_scout]['id']
                            block_id = blocks_dict[selected_block]['id']
                            
                            data = {
                                "escuteiro_id": scout_id,
                                "bloco_id": block_id,
                                "quantidade": quantidade,
                                "motivo": motivo.strip() if motivo else None,
                                "data_devolucao": data_devolucao.isoformat()
                            }
                            
                            response = supabase.table('devolucoes').insert(data).execute()
                            
                            if response.data:
                                st.success(f"✅ Devolução de {quantidade} rifas registada com sucesso!")
                                
                                # Optionally update block status
                                try:
                                    supabase.table('blocos_rifas').update({
                                        'estado': 'devolvido'
                                    }).eq('id', block_id).execute()
                                except:
                                    pass  # Estado column might not exist
                                
                                st.info("🔄 A página será recarregada...")
                                import time
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error("Erro ao registar devolução.")
                        
                        except Exception as e:
                            st.error(f"Erro ao registar devolução: {str(e)}")
                            if "devolucoes" in str(e).lower():
                                st.info("Execute o schema SQL completo para criar a tabela 'devolucoes'.")
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")

# Tab 3: Edit/Delete returns
with tab3:
    st.subheader("Editar ou Eliminar Devolução")
    
    try:
        response = supabase.table('devolucoes').select(
            '*, escuteiros(nome), blocos_rifas(nome)'
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
