import streamlit as st
import pandas as pd
import re
import io
from datetime import datetime
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Escuteiros", page_icon="👥", layout="wide")

st.title("👥 Gestão de Escuteiros")

# Secções disponíveis
SECCOES = ['Lobitos', 'Exploradores', 'Pioneiros', 'Caminheiros', 'CPP']

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
tab1, tab2, tab3, tab4 = st.tabs(["📋 Lista", "➕ Adicionar", "✏️ Editar/Eliminar", "📤 Importar Excel"])

# Initialize session state for active tab after operations
if 'force_tab_index' not in st.session_state:
    st.session_state.force_tab_index = None

# Tab 1: List scouts
with tab1:
    st.subheader("Lista de Escuteiros")
    
    try:
        response = supabase.table('escuteiros').select('*').order('nome').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Usar secção da tabela escuteiros se existir, senão buscar dos blocos
            if 'seccao' not in df.columns:
                # Buscar secção de cada escuteiro (da tabela blocos_rifas) - legado
                escuteiro_seccoes = {}
                for escuteiro in response.data:
                    esc_id = escuteiro['id']
                    blocos_response = supabase.table('blocos_rifas').select('seccao').eq('escuteiro_id', esc_id).limit(1).execute()
                    if blocos_response.data and blocos_response.data[0].get('seccao'):
                        escuteiro_seccoes[esc_id] = blocos_response.data[0]['seccao']
                    else:
                        escuteiro_seccoes[esc_id] = '-'
                
                # Adicionar coluna secção
                df['seccao'] = df['id'].map(escuteiro_seccoes)
            else:
                # Preencher secções vazias com '-'
                df['seccao'] = df['seccao'].fillna('-')
            
            # Formatar data
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d-%m-%Y')
            
            # Criar coluna ID curto para visualização
            if 'id' in df.columns:
                df['id_curto'] = df['id'].str[:8] + '...'
            
            # Reordenar colunas
            colunas_ordem = ['id_curto', 'nome', 'seccao', 'email', 'telefone', 'ativo', 'created_at']
            df = df[[col for col in colunas_ordem if col in df.columns]]

            # Ajustar representação da coluna 'ativo' para mostrar um check verde
            if 'ativo' in df.columns:
                # Converter valores possivelmente nulos/booleanos para boolean
                df['ativo'] = df['ativo'].fillna(False).astype(bool)
                # Mostrar um ✓ para ativo ou vazio para inativo
                df['ativo'] = df['ativo'].apply(lambda v: '✅' if v else '')

                # Criar um Styler para colorir o check em verde e centralizar
                styler = df.style.applymap(
                    lambda v: 'color: #28a745; font-weight: 600; text-align: center' if v == '✅' else 'color: #6c757d; text-align: center',
                    subset=['ativo']
                ).set_properties(**{col: 'text-align: left' for col in df.columns if col != 'ativo'})

                st.dataframe(
                    styler,
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
            else:
                st.dataframe(
                    df,
                    column_config={
                        "id": None,  # Ocultar ID completo
                        "id_curto": "ID",
                        "nome": "Nome",
                        "seccao": "Secção",
                        "email": "Email",
                        "telefone": "Telefone",
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
    
    # Initialize session state apenas para preservar em caso de erro
    if 'add_error_nome' not in st.session_state:
        st.session_state.add_error_nome = ""
    if 'add_error_email' not in st.session_state:
        st.session_state.add_error_email = ""
    if 'add_error_telefone' not in st.session_state:
        st.session_state.add_error_telefone = ""
    if 'add_error_seccao' not in st.session_state:
        st.session_state.add_error_seccao = "Lobitos"
    if 'show_add_error' not in st.session_state:
        st.session_state.show_add_error = False
    
    # Secções disponíveis
    SECCOES = ['Lobitos', 'Exploradores', 'Pioneiros', 'Caminheiros', 'CPP']
    
    with st.form("add_scout_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            # Só usar value se houver erro
            nome = st.text_input(
                "Nome *", 
                value=st.session_state.add_error_nome if st.session_state.show_add_error else "",
                placeholder="Nome completo do escuteiro"
            )
            email = st.text_input(
                "Email", 
                value=st.session_state.add_error_email if st.session_state.show_add_error else "",
                placeholder="email@exemplo.com"
            )
        
        with col2:
            seccao = st.selectbox(
                "Secção *",
                options=SECCOES,
                index=SECCOES.index(st.session_state.add_error_seccao) if st.session_state.show_add_error and st.session_state.add_error_seccao in SECCOES else 0,
                help="Secção a que pertence o escuteiro"
            )
            telefone = st.text_input(
                "Telefone", 
                value=st.session_state.add_error_telefone if st.session_state.show_add_error else "",
                placeholder="+351 912 345 678"
            )
        
        submitted = st.form_submit_button("Adicionar Escuteiro", type="primary", use_container_width=True)
        
        if submitted:
            if not nome:
                st.error("O nome é obrigatório!")
                # Preservar valores para correção
                st.session_state.add_error_nome = nome
                st.session_state.add_error_email = email
                st.session_state.add_error_telefone = telefone
                st.session_state.add_error_seccao = seccao
                st.session_state.show_add_error = True
            else:
                try:
                    # Check for duplicate name
                    existing = supabase.table('escuteiros').select('nome').ilike('nome', nome).execute()
                    
                    if existing.data and len(existing.data) > 0:
                        st.error(f"⚠️ Já existe um escuteiro com o nome '{nome}'. Por favor, use um nome diferente.")
                        # Preservar valores para correção
                        st.session_state.add_error_nome = nome
                        st.session_state.add_error_email = email
                        st.session_state.add_error_telefone = telefone
                        st.session_state.add_error_seccao = seccao
                        st.session_state.show_add_error = True
                    else:
                        data = {
                            "nome": nome,
                            "email": email if email else None,
                            "telefone": telefone if telefone else None,
                            "seccao": seccao
                        }
                        
                        response = supabase.table('escuteiros').insert(data).execute()
                        
                        if response.data:
                            # Limpar estados de erro
                            st.session_state.add_error_nome = ""
                            st.session_state.add_error_email = ""
                            st.session_state.add_error_telefone = ""
                            st.session_state.add_error_seccao = "Lobitos"
                            st.session_state.show_add_error = False
                            
                            st.success(f"✅ Escuteiro '{nome}' adicionado com sucesso!")
                            st.info("🔄 A página será recarregada...")
                            
                            # Aguardar para mostrar mensagem
                            import time
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error("Erro ao adicionar escuteiro.")
                            # Preservar valores
                            st.session_state.add_error_nome = nome
                            st.session_state.add_error_email = email
                            st.session_state.add_error_telefone = telefone
                            st.session_state.add_error_seccao = seccao
                            st.session_state.show_add_error = True
                
                except Exception as e:
                    st.error(f"Erro ao adicionar escuteiro: {str(e)}")
                    # Preservar valores
                    st.session_state.add_error_nome = nome
                    st.session_state.add_error_email = email
                    st.session_state.add_error_telefone = telefone
                    st.session_state.add_error_seccao = seccao
                    st.session_state.show_add_error = True

# Tab 3: Edit/Delete scouts
with tab3:
    st.subheader("Editar ou Eliminar Escuteiro")
    
    # Initialize session state for clearing selection
    if 'clear_edit_selection' not in st.session_state:
        st.session_state.clear_edit_selection = False
    
    try:
        response = supabase.table('escuteiros').select('*').order('nome').execute()
        
        if response.data:
            # Create a dictionary for scout selection (id-based for stability)
            scouts_map = {scout['id']: scout for scout in response.data}
            scouts_display = {scout['id']: scout['nome'] for scout in response.data}
            
            # Reset selection index if needed
            if st.session_state.clear_edit_selection:
                default_index = 0
                st.session_state.clear_edit_selection = False
            else:
                default_index = 0
            
            id_list = list(scouts_map.keys())
            # Keep deterministic ordering by sorting names but keep ids aligned
            id_list = sorted(id_list, key=lambda i: scouts_display.get(i, ""))
            selected_scout_id = st.selectbox(
                "Selecione um escuteiro",
                options=id_list,
                index=default_index,
                format_func=lambda iid: scouts_display.get(iid, str(iid)),
                key="scout_selector"
            )

            if selected_scout_id:
                scout = scouts_map[selected_scout_id]
                
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
                                        # Forçar recarregar lista limpa
                                        if 'scout_selector' in st.session_state:
                                            del st.session_state['scout_selector']
                                        if 'edit_scout_form' in st.session_state:
                                            del st.session_state['edit_scout_form']
                                        
                                        st.success(f"✅ Escuteiro '{new_nome}' atualizado com sucesso!")
                                        st.info("🔄 A página será recarregada...")
                                        
                                        # Aguardar para mostrar mensagem
                                        import time
                                        time.sleep(1.5)
                                        st.rerun()
                                    else:
                                        st.error("Erro ao atualizar escuteiro.")
                                
                                except Exception as e:
                                    st.error(f"Erro ao atualizar escuteiro: {str(e)}")
                
                with col2:
                    st.subheader("Eliminar")
                    st.warning("⚠️ Esta ação é irreversível!")
                    
                    # Usar checkbox como confirmação
                    confirm_delete = st.checkbox("Confirmar eliminação", key=f"confirm_{scout['id']}")
                    
                    delete_button = st.button("🗑️ Eliminar Escuteiro", 
                                             type="secondary",
                                             disabled=not confirm_delete,
                                             key=f"delete_{scout['id']}")
                    
                    if delete_button and confirm_delete:
                        try:
                            # Tentar eliminar
                            response = supabase.table('escuteiros').delete().eq('id', scout['id']).execute()
                            
                            # Verificar se funcionou
                            if response.data and len(response.data) > 0:
                                # Limpar estados do formulário
                                if 'scout_selector' in st.session_state:
                                    del st.session_state['scout_selector']
                                if 'edit_scout_form' in st.session_state:
                                    del st.session_state['edit_scout_form']
                                    
                                st.success(f"✅ Escuteiro '{scout['nome']}' eliminado com sucesso!")
                                st.info("🔄 A página será recarregada...")
                                
                                # Aguardar um pouco antes de recarregar
                                import time
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error("⚠️ Nenhum registo foi eliminado. Possíveis causas:")
                                st.info("1. Permissões RLS (Row Level Security) bloqueando a operação")
                                st.info("2. Escuteiro tem blocos de rifas associados (foreign key constraint)")
                                st.code(f"Response: {response.data}")
                        
                        except Exception as e:
                            st.error(f"❌ Erro ao eliminar escuteiro: {str(e)}")
                            if "foreign key" in str(e).lower():
                                st.warning("⚠️ Este escuteiro tem blocos de rifas associados. Elimine os blocos primeiro.")
                            st.exception(e)
        else:
            st.info("Nenhum escuteiro disponível para editar.")
    
    except Exception as e:
        st.error(f"Erro ao carregar escuteiros: {str(e)}")

# Tab 4: Import from Excel
with tab4:
    st.subheader("📤 Importar Escuteiros via Excel")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Como importar:
        1. 📥 Faça download do modelo Excel
        2. ✏️ Preencha com os dados dos escuteiros
        3. 📤 Faça upload do arquivo preenchido
        4. ✅ Revise e confirme a importação
        """)
    
    with col2:
        # Criar modelo Excel para download
        st.markdown("### 📥 Download Modelo")
        
        # Criar DataFrame modelo
        modelo_df = pd.DataFrame({
            'Nome': ['João Silva', 'Maria Santos'],
            'Email': ['joao@exemplo.com', 'maria@exemplo.com'],
            'Telefone': ['+351 912 345 678', '+351 913 456 789'],
            'Secção': ['Lobitos', 'Exploradores']
        })
        
        # Converter para Excel em memória
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            modelo_df.to_excel(writer, index=False, sheet_name='Escuteiros')
            
            # Ajustar largura das colunas
            worksheet = writer.sheets['Escuteiros']
            worksheet.column_dimensions['A'].width = 30
            worksheet.column_dimensions['B'].width = 30
            worksheet.column_dimensions['C'].width = 20
            worksheet.column_dimensions['D'].width = 15
        
        buffer.seek(0)
        
        st.download_button(
            label="📥 Download Modelo Excel",
            data=buffer,
            file_name=f"modelo_escuteiros_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
            type="primary"
        )
        
        st.caption("💡 O modelo já vem com exemplos. Apague-os e adicione os seus dados.")
    
    st.divider()
    
    # Upload do arquivo
    st.markdown("### 📤 Upload do Arquivo")
    uploaded_file = st.file_uploader(
        "Selecione o arquivo Excel preenchido",
        type=['xlsx', 'xls'],
        help="Arquivo deve conter colunas: Nome, Email, Telefone, Secção"
    )
    
    if uploaded_file:
        try:
            # Ler arquivo Excel
            df_import = pd.read_excel(uploaded_file)
            
            # Validar colunas obrigatórias
            required_columns = ['Nome', 'Secção']
            missing_columns = [col for col in required_columns if col not in df_import.columns]
            
            if missing_columns:
                st.error(f"❌ Colunas obrigatórias faltando: {', '.join(missing_columns)}")
                st.info("O arquivo deve conter pelo menos as colunas: Nome, Secção")
            else:
                # Limpar dados
                df_import = df_import.fillna('')
                df_import['Nome'] = df_import['Nome'].astype(str).str.strip()
                df_import['Secção'] = df_import['Secção'].astype(str).str.strip()
                
                # Remover linhas vazias
                df_import = df_import[df_import['Nome'] != '']
                
                # Validar secções
                seccoes_invalidas = df_import[~df_import['Secção'].isin(SECCOES)]
                if not seccoes_invalidas.empty:
                    st.error(f"❌ Secções inválidas encontradas:")
                    st.dataframe(seccoes_invalidas[['Nome', 'Secção']], use_container_width=True)
                    st.info(f"Secções válidas: {', '.join(SECCOES)}")
                else:
                    # Preview dos dados
                    st.success(f"✅ Arquivo válido! {len(df_import)} escuteiro(s) encontrado(s)")
                    st.markdown("### 👀 Preview dos Dados")
                    st.dataframe(df_import, use_container_width=True)
                    
                    # Armazenar dados no session_state para importação
                    st.session_state['dados_para_importar'] = df_import.to_dict('records')
                    
                    # Botão de confirmação
                    col_a, col_b, col_c = st.columns([1, 1, 2])
                    
                    with col_a:
                        confirmar = st.button("✅ Confirmar Importação", type="primary", use_container_width=True)
                    
                    with col_b:
                        cancelar = st.button("❌ Cancelar", use_container_width=True)
                    
                    # Processar importação SE confirmado
                    if confirmar:
                        with st.spinner("Importando escuteiros..."):
                            importados = 0
                            erros = []
                            
                            dados = st.session_state.get('dados_para_importar', [])
                            
                            for idx, row in enumerate(dados):
                                try:
                                    # Verificar duplicados
                                    nome = row['Nome']
                                    existing = supabase.table('escuteiros').select('nome').ilike('nome', nome).execute()
                                    
                                    if existing.data and len(existing.data) > 0:
                                        erros.append(f"Linha {idx+2}: '{nome}' já existe")
                                        continue
                                    
                                    # Preparar dados
                                    data = {
                                        "nome": nome,
                                        "email": row.get('Email', '') if row.get('Email', '') else None,
                                        "telefone": row.get('Telefone', '') if row.get('Telefone', '') else None,
                                        "seccao": row['Secção']
                                    }
                                    
                                    # Inserir
                                    response = supabase.table('escuteiros').insert(data).execute()
                                    
                                    if response.data:
                                        importados += 1
                                    else:
                                        erros.append(f"Linha {idx+2}: Erro ao inserir '{nome}'")
                                
                                except Exception as e:
                                    erros.append(f"Linha {idx+2}: {str(e)}")
                            
                            # Limpar dados do session_state
                            if 'dados_para_importar' in st.session_state:
                                del st.session_state['dados_para_importar']
                            
                            # Mostrar resultados
                            if importados > 0:
                                st.success(f"✅ {importados} escuteiro(s) importado(s) com sucesso!")
                            
                            if erros:
                                st.warning(f"⚠️ {len(erros)} erro(s) encontrado(s):")
                                for erro in erros[:10]:  # Mostrar no máximo 10 erros
                                    st.text(f"• {erro}")
                                if len(erros) > 10:
                                    st.text(f"... e mais {len(erros)-10} erro(s)")
                            
                            if importados > 0:
                                st.info("🔄 A página será recarregada...")
                                import time
                                time.sleep(2)
                                st.rerun()
                    
                    if cancelar:
                        # Limpar session_state e recarregar
                        if 'dados_para_importar' in st.session_state:
                            del st.session_state['dados_para_importar']
                        st.rerun()
        
        except Exception as e:
            st.error(f"❌ Erro ao ler arquivo: {str(e)}")
            st.info("Certifique-se de que o arquivo está no formato correto (Excel .xlsx ou .xls)")
