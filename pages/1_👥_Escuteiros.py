import streamlit as st
import pandas as pd
import re
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Escuteiros", page_icon="👥", layout="wide")

st.title("👥 Gestão de Escuteiros")

# Helper functions
def validate_email(email):
    """Validate email format"""
    if not email:
        return True  # Email is optional
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    """Validate phone format (Portuguese format)"""
    if not phone:
        return True  # Phone is optional
    # Remove spaces and common separators
    phone_clean = phone.replace(' ', '').replace('-', '').replace('+', '')
    # Check if it's a valid Portuguese number (9 digits starting with 9, or with country code)
    return len(phone_clean) >= 9 and phone_clean.isdigit()

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
            
            # Buscar todas as secções de uma vez (1 query apenas!)
            blocos_response = supabase.table('blocos_rifas').select('escuteiro_id, seccao').not_.is_('escuteiro_id', 'null').execute()
            
            # Criar mapa escuteiro -> secção (pega a primeira secção do escuteiro)
            escuteiro_seccoes = {}
            if blocos_response.data:
                for bloco in blocos_response.data:
                    esc_id = bloco['escuteiro_id']
                    if esc_id not in escuteiro_seccoes and bloco.get('seccao'):
                        escuteiro_seccoes[esc_id] = bloco['seccao']
            
            # Adicionar coluna secção
            df['seccao'] = df['id'].map(lambda x: escuteiro_seccoes.get(x, '-'))
            
            # Formatar data
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d-%m-%Y')
            
            # Criar coluna ID curto para visualização
            if 'id' in df.columns:
                df['id_curto'] = df['id'].str[:8] + '...'
            
            # Reordenar colunas
            colunas_ordem = ['id_curto', 'nome', 'seccao', 'email', 'telefone', 'ativo', 'created_at']
            df = df[[col for col in colunas_ordem if col in df.columns]]
            
            st.dataframe(
                df,
                column_config={
                    "id": None,  # Ocultar ID completo
                    "id_curto": "ID",
                    "nome": "Nome",
                    "seccao": "Secção",
                    "email": "Email",
                    "telefone": "Telefone",
                    "ativo": "Ativo",
                    "created_at": "Data de Registo"
                },
                hide_index=True,
                use_container_width=True
            )
            st.info(f"📊 Total de escuteiros: {len(df)}")
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
            # Create a dictionary for scout selection (apenas nome, sem ID)
            scouts_dict = {scout['nome']: scout for scout in response.data}
            
            selected_scout_name = st.selectbox(
                "Selecione um escuteiro",
                options=sorted(scouts_dict.keys())
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
