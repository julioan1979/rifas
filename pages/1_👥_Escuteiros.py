import streamlit as st
import pandas as pd
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Escuteiros", page_icon="👥", layout="wide")

st.title("👥 Gestão de Escuteiros")

# Initialize Supabase client
try:
    supabase = get_supabase_client()
except ValueError as e:
    st.error(f"Erro ao conectar ao Supabase: {str(e)}")
    st.stop()

# Tabs for different operations
tab1, tab2, tab3 = st.tabs(["📋 Lista", "➕ Adicionar", "✏️ Editar/Eliminar"])

# Tab 1: List scouts
with tab1:
    st.subheader("Lista de Escuteiros")
    
    try:
        response = supabase.table('escuteiros').select('*').order('nome').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            # Reorder columns for better display
            columns = ['nome', 'email', 'telefone', 'created_at', 'id']
            df = df[[col for col in columns if col in df.columns]]
            
            st.dataframe(
                df,
                column_config={
                    "nome": "Nome",
                    "email": "Email",
                    "telefone": "Telefone",
                    "created_at": "Data de Registo",
                    "id": "ID"
                },
                hide_index=True,
                use_container_width=True
            )
            st.info(f"Total de escuteiros: {len(df)}")
        else:
            st.info("Nenhum escuteiro registado ainda.")
    
    except Exception as e:
        st.error(f"Erro ao carregar escuteiros: {str(e)}")

# Tab 2: Add new scout
with tab2:
    st.subheader("Adicionar Novo Escuteiro")
    
    with st.form("add_scout_form"):
        nome = st.text_input("Nome *", placeholder="Nome completo do escuteiro")
        email = st.text_input("Email", placeholder="email@exemplo.com")
        telefone = st.text_input("Telefone", placeholder="+351 912 345 678")
        
        submitted = st.form_submit_button("Adicionar Escuteiro", type="primary")
        
        if submitted:
            if not nome:
                st.error("O nome é obrigatório!")
            else:
                try:
                    data = {
                        "nome": nome,
                        "email": email if email else None,
                        "telefone": telefone if telefone else None
                    }
                    
                    response = supabase.table('escuteiros').insert(data).execute()
                    
                    if response.data:
                        st.success(f"✅ Escuteiro '{nome}' adicionado com sucesso!")
                        st.rerun()
                    else:
                        st.error("Erro ao adicionar escuteiro.")
                
                except Exception as e:
                    st.error(f"Erro ao adicionar escuteiro: {str(e)}")

# Tab 3: Edit/Delete scouts
with tab3:
    st.subheader("Editar ou Eliminar Escuteiro")
    
    try:
        response = supabase.table('escuteiros').select('*').order('nome').execute()
        
        if response.data:
            # Create a dictionary for scout selection
            scouts_dict = {f"{scout['nome']} ({scout['id'][:8]}...)": scout for scout in response.data}
            
            selected_scout_name = st.selectbox(
                "Selecione um escuteiro",
                options=list(scouts_dict.keys())
            )
            
            if selected_scout_name:
                scout = scouts_dict[selected_scout_name]
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.subheader("Editar Dados")
                    with st.form("edit_scout_form"):
                        new_nome = st.text_input("Nome *", value=scout['nome'])
                        new_email = st.text_input("Email", value=scout.get('email', '') or '')
                        new_telefone = st.text_input("Telefone", value=scout.get('telefone', '') or '')
                        
                        update_submitted = st.form_submit_button("Atualizar", type="primary")
                        
                        if update_submitted:
                            if not new_nome:
                                st.error("O nome é obrigatório!")
                            else:
                                try:
                                    update_data = {
                                        "nome": new_nome,
                                        "email": new_email if new_email else None,
                                        "telefone": new_telefone if new_telefone else None
                                    }
                                    
                                    response = supabase.table('escuteiros').update(update_data).eq('id', scout['id']).execute()
                                    
                                    if response.data:
                                        st.success("✅ Escuteiro atualizado com sucesso!")
                                        st.rerun()
                                    else:
                                        st.error("Erro ao atualizar escuteiro.")
                                
                                except Exception as e:
                                    st.error(f"Erro ao atualizar escuteiro: {str(e)}")
                
                with col2:
                    st.subheader("Eliminar")
                    st.warning("⚠️ Esta ação é irreversível!")
                    
                    if st.button("🗑️ Eliminar Escuteiro", type="secondary"):
                        try:
                            response = supabase.table('escuteiros').delete().eq('id', scout['id']).execute()
                            
                            if response.data:
                                st.success("✅ Escuteiro eliminado com sucesso!")
                                st.rerun()
                            else:
                                st.error("Erro ao eliminar escuteiro.")
                        
                        except Exception as e:
                            st.error(f"Erro ao eliminar escuteiro: {str(e)}")
        else:
            st.info("Nenhum escuteiro disponível para editar.")
    
    except Exception as e:
        st.error(f"Erro ao carregar escuteiros: {str(e)}")
