import streamlit as st
import pandas as pd
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Blocos de Rifas", page_icon="🎟️", layout="wide")

st.title("🎟️ Gestão de Blocos de Rifas")

# Initialize Supabase client
try:
    supabase = get_supabase_client()
except ValueError as e:
    st.error(f"Erro ao conectar ao Supabase: {str(e)}")
    st.stop()

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Adicionar", "✏️ Editar/Eliminar"])

# Tab 1: List raffle blocks
with tab1:
    st.subheader("Lista de Blocos de Rifas")
    
    try:
        response = supabase.table('blocos_rifas').select('*').order('nome').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Reorder columns for better display
            columns = ['nome', 'numero_inicial', 'numero_final', 'preco_unitario', 'created_at', 'id']
            df = df[[col for col in columns if col in df.columns]]
            
            # Calculate total tickets per block
            if 'numero_inicial' in df.columns and 'numero_final' in df.columns:
                df['total_rifas'] = df['numero_final'] - df['numero_inicial'] + 1
            
            st.dataframe(
                df,
                column_config={
                    "nome": "Nome do Bloco",
                    "numero_inicial": "Número Inicial",
                    "numero_final": "Número Final",
                    "preco_unitario": st.column_config.NumberColumn(
                        "Preço Unitário",
                        format="%.2f €"
                    ),
                    "total_rifas": "Total de Rifas",
                    "created_at": "Data de Criação",
                    "id": "ID"
                },
                hide_index=True,
                use_container_width=True
            )
            st.info(f"Total de blocos: {len(df)}")
        else:
            st.info("Nenhum bloco de rifas criado ainda.")
    
    except Exception as e:
        st.error(f"Erro ao carregar blocos de rifas: {str(e)}")

# Tab 2: Add new raffle block
with tab2:
    st.subheader("Adicionar Novo Bloco de Rifas")
    
    with st.form("add_block_form"):
        nome = st.text_input("Nome do Bloco *", placeholder="Ex: Bloco A, Bloco Janeiro 2024")
        
        col1, col2 = st.columns(2)
        with col1:
            numero_inicial = st.number_input("Número Inicial *", min_value=1, value=1, step=1)
        with col2:
            numero_final = st.number_input("Número Final *", min_value=1, value=100, step=1)
        
        preco_unitario = st.number_input("Preço Unitário (€) *", min_value=0.01, value=1.00, step=0.10, format="%.2f")
        
        # Calculate and show total tickets
        if numero_final >= numero_inicial:
            total_rifas = numero_final - numero_inicial + 1
            st.info(f"📊 Este bloco terá **{total_rifas} rifas** no total")
        else:
            st.warning("⚠️ O número final deve ser maior ou igual ao número inicial!")
        
        submitted = st.form_submit_button("Criar Bloco de Rifas", type="primary")
        
        if submitted:
            if not nome:
                st.error("O nome do bloco é obrigatório!")
            elif numero_final < numero_inicial:
                st.error("O número final deve ser maior ou igual ao número inicial!")
            else:
                try:
                    data = {
                        "nome": nome,
                        "numero_inicial": numero_inicial,
                        "numero_final": numero_final,
                        "preco_unitario": preco_unitario
                    }
                    
                    response = supabase.table('blocos_rifas').insert(data).execute()
                    
                    if response.data:
                        st.success(f"✅ Bloco '{nome}' criado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao criar bloco de rifas.")
                
                except Exception as e:
                    st.error(f"Erro ao criar bloco de rifas: {str(e)}")

# Tab 3: Edit/Delete raffle blocks
with tab3:
    st.subheader("Editar ou Eliminar Bloco de Rifas")
    
    try:
        response = supabase.table('blocos_rifas').select('*').order('nome').execute()
        
        if response.data:
            # Create a dictionary for block selection
            blocks_dict = {f"{block['nome']} ({block['id'][:8]}...)": block for block in response.data}
            
            selected_block_name = st.selectbox(
                "Selecione um bloco",
                options=list(blocks_dict.keys())
            )
            
            if selected_block_name:
                block = blocks_dict[selected_block_name]
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader("Editar Dados")
                    with st.form("edit_block_form"):
                        new_nome = st.text_input("Nome do Bloco *", value=block['nome'])
                        
                        col_a, col_b = st.columns(2)
                        with col_a:
                            new_numero_inicial = st.number_input(
                                "Número Inicial *", 
                                min_value=1, 
                                value=block['numero_inicial'], 
                                step=1
                            )
                        with col_b:
                            new_numero_final = st.number_input(
                                "Número Final *", 
                                min_value=1, 
                                value=block['numero_final'], 
                                step=1
                            )
                        
                        new_preco_unitario = st.number_input(
                            "Preço Unitário (€) *", 
                            min_value=0.01, 
                            value=float(block['preco_unitario']), 
                            step=0.10, 
                            format="%.2f"
                        )
                        
                        # Show total tickets
                        if new_numero_final >= new_numero_inicial:
                            total_rifas = new_numero_final - new_numero_inicial + 1
                            st.info(f"📊 Este bloco terá **{total_rifas} rifas** no total")
                        
                        update_submitted = st.form_submit_button("Atualizar", type="primary")
                        
                        if update_submitted:
                            if not new_nome:
                                st.error("O nome do bloco é obrigatório!")
                            elif new_numero_final < new_numero_inicial:
                                st.error("O número final deve ser maior ou igual ao número inicial!")
                            else:
                                try:
                                    update_data = {
                                        "nome": new_nome,
                                        "numero_inicial": new_numero_inicial,
                                        "numero_final": new_numero_final,
                                        "preco_unitario": new_preco_unitario
                                    }
                                    
                                    response = supabase.table('blocos_rifas').update(update_data).eq('id', block['id']).execute()
                                    
                                    if response.data:
                                        st.success("✅ Bloco atualizado com sucesso!")
                                        st.rerun()
                                    else:
                                        st.error("Erro ao atualizar bloco.")
                                
                                except Exception as e:
                                    st.error(f"Erro ao atualizar bloco: {str(e)}")
                
                with col2:
                    st.subheader("Eliminar")
                    st.warning("⚠️ Esta ação é irreversível!")
                    
                    if st.button("🗑️ Eliminar Bloco", type="secondary"):
                        try:
                            response = supabase.table('blocos_rifas').delete().eq('id', block['id']).execute()
                            
                            if response.data:
                                st.success("✅ Bloco eliminado com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao eliminar bloco.")
                        
                        except Exception as e:
                            st.error(f"Erro ao eliminar bloco: {str(e)}")
        else:
            st.info("Nenhum bloco disponível para editar.")
    
    except Exception as e:
        st.error(f"Erro ao carregar blocos: {str(e)}")
