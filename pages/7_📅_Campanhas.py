import streamlit as st
import pandas as pd
from datetime import datetime, date
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Campanhas", page_icon="📅", layout="wide")

# Inicializar cliente Supabase
try:
    supabase = get_supabase_client()
except Exception as e:
    st.error(f"❌ Erro ao conectar à base de dados: {e}")
    st.stop()

st.title("📅 Gestão de Campanhas")

# Tabs para diferentes ações
tab_list, tab_add, tab_create_blocos, tab_edit = st.tabs(["📋 Lista", "➕ Adicionar Campanha", "🎟️ Criar Blocos de Rifas", "✏️ Editar/Eliminar"])

# ============================================
# TAB: LISTA DE CAMPANHAS
# ============================================
with tab_list:
    st.subheader("Lista de Campanhas")
    
    # Buscar campanhas
    response = supabase.table('campanhas').select('*').order('created_at', desc=True).execute()
    
    if response.data:
        campanhas_df = pd.DataFrame(response.data)
        
        # Buscar estatísticas de cada campanha
        stats_list = []
        for _, campanha in campanhas_df.iterrows():
            campanha_id = campanha['id']
            
            # Contar blocos
            blocos_response = supabase.table('blocos_rifas').select('id, numero_inicial, numero_final, estado').eq('campanha_id', campanha_id).execute()
            
            total_blocos = len(blocos_response.data) if blocos_response.data else 0
            total_rifas = sum(b['numero_final'] - b['numero_inicial'] + 1 for b in blocos_response.data) if blocos_response.data else 0
            blocos_vendidos = sum(1 for b in blocos_response.data if b['estado'] == 'vendido') if blocos_response.data else 0
            
            stats_list.append({
                'Campanha': campanha['nome'],
                'Descrição': campanha['descricao'] or '-',
                'Data Início': campanha['data_inicio'],
                'Data Fim': campanha['data_fim'],
                'Ativa': '✅ Sim' if campanha['ativa'] else '❌ Não',
                'Total Blocos': total_blocos,
                'Total Rifas': total_rifas,
                'Blocos Vendidos': blocos_vendidos
            })
        
        stats_df = pd.DataFrame(stats_list)
        
        # Formatar datas
        if 'Data Início' in stats_df.columns:
            stats_df['Data Início'] = pd.to_datetime(stats_df['Data Início']).dt.strftime('%d-%m-%Y')
        if 'Data Fim' in stats_df.columns:
            stats_df['Data Fim'] = pd.to_datetime(stats_df['Data Fim']).dt.strftime('%d-%m-%Y')
        
        st.dataframe(
            stats_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Métricas das campanhas ativas
        campanhas_ativas = campanhas_df[campanhas_df['ativa'] == True]
        if not campanhas_ativas.empty:
            nomes_ativas = ', '.join(campanhas_ativas['nome'].tolist())
            st.info(f"📌 **Campanha(s) Ativa(s):** {nomes_ativas}")
        else:
            st.warning("⚠️ Nenhuma campanha ativa no momento")
    else:
        st.info("ℹ️ Nenhuma campanha cadastrada ainda")

# ============================================
# TAB: ADICIONAR CAMPANHA
# ============================================
with tab_add:
    st.subheader("➕ Adicionar Nova Campanha")
    
    # Mostrar mensagem de sucesso se houver
    if 'campanha_criada' in st.session_state:
        st.success(f"✅ Campanha '{st.session_state.campanha_criada}' criada com sucesso!")
        del st.session_state['campanha_criada']
    
    with st.form("form_adicionar_campanha", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome da Campanha *", placeholder="Ex: Natal2025, Pascoa2026")
            data_inicio = st.date_input("Data de Início *", value=date.today())
            ativa = st.checkbox("Campanha Ativa", value=False, help="Pode ter múltiplas campanhas ativas simultaneamente")
        
        with col2:
            descricao = st.text_area("Descrição", placeholder="Descrição opcional da campanha")
            data_fim = st.date_input("Data de Fim *", value=date.today())
        
        submitted = st.form_submit_button("✅ Criar Campanha", use_container_width=True)
        
        if submitted:
            if not nome:
                st.error("❌ O nome da campanha é obrigatório")
            elif data_fim < data_inicio:
                st.error("❌ A data de fim deve ser posterior à data de início")
            else:
                try:
                    # Inserir nova campanha
                    campanha_data = {
                        'nome': nome,
                        'descricao': descricao,
                        'data_inicio': data_inicio.isoformat(),
                        'data_fim': data_fim.isoformat(),
                        'ativa': ativa
                    }
                    
                    response = supabase.table('campanhas').insert(campanha_data).execute()
                    
                    if response.data:
                        # Guardar mensagem de sucesso e fazer rerun para limpar formulário
                        st.session_state['campanha_criada'] = nome
                        st.rerun()
                    else:
                        st.error("❌ Erro ao criar campanha")
                except Exception as e:
                    if "duplicate key" in str(e).lower():
                        st.error(f"❌ Já existe uma campanha com o nome '{nome}'")
                    else:
                        st.error(f"❌ Erro ao criar campanha: {e}")

# ============================================
# TAB: CRIAR BLOCOS DE RIFAS
# ============================================
with tab_create_blocos:
    st.subheader("🎟️ Criar Blocos de Rifas Automaticamente")
    
    # Buscar campanhas
    campanhas_response = supabase.table('campanhas').select('*').order('created_at', desc=True).execute()
    
    if campanhas_response.data:
        st.info("💡 **Dica:** Crie blocos de rifas automaticamente para uma campanha. Os blocos ficarão disponíveis para atribuição posterior aos escuteiros.")
        
        with st.form("form_criar_blocos"):
            # Selecionar campanha
            campanhas_dict = {c['nome']: c['id'] for c in campanhas_response.data}
            campanha_selecionada = st.selectbox(
                "Campanha *",
                options=list(campanhas_dict.keys()),
                help="Selecione a campanha para criar os blocos de rifas"
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_rifas = st.number_input(
                    "Total de Rifas *",
                    min_value=10,
                    value=1000,
                    step=10,
                    help="Número total de rifas a criar"
                )
            
            with col2:
                rifas_por_bloco = st.number_input(
                    "Rifas por Bloco *",
                    min_value=1,
                    value=10,
                    step=1,
                    help="Quantas rifas em cada bloco"
                )
            
            with col3:
                preco_bloco = st.number_input(
                    "Preço por Bloco (€) *",
                    min_value=0.01,
                    value=10.00,
                    step=0.10,
                    format="%.2f",
                    help="Preço total de cada bloco"
                )
            
            # Calcular blocos
            if total_rifas > 0 and rifas_por_bloco > 0:
                num_blocos = total_rifas // rifas_por_bloco
                rifas_sobra = total_rifas % rifas_por_bloco
                
                if rifas_sobra > 0:
                    st.warning(f"⚠️ Com {total_rifas} rifas e blocos de {rifas_por_bloco}, terá {num_blocos} blocos completos e {rifas_sobra} rifas sobrando. Ajuste os números para não haver sobras.")
                else:
                    st.success(f"✅ Serão criados **{num_blocos} blocos** de {rifas_por_bloco} rifas cada, totalizando {total_rifas} rifas. Preço por bloco: {preco_bloco:.2f}€")
            
            submitted = st.form_submit_button("🎟️ Criar Blocos de Rifas", type="primary", use_container_width=True)
            
            if submitted:
                if rifas_sobra > 0:
                    st.error("❌ Ajuste o total de rifas ou rifas por bloco para não haver sobras!")
                else:
                    try:
                        campanha_id = campanhas_dict[campanha_selecionada]
                        
                        # Criar blocos
                        blocos_criados = 0
                        numero_atual = 1
                        
                        with st.spinner(f"Criando {num_blocos} blocos..."):
                            for i in range(num_blocos):
                                numero_inicial = numero_atual
                                numero_final = numero_atual + rifas_por_bloco - 1
                                
                                bloco_data = {
                                    "campanha_id": campanha_id,
                                    "nome": f"Bloco {numero_inicial}-{numero_final}",
                                    "numero_inicial": numero_inicial,
                                    "numero_final": numero_final,
                                    "preco_bloco": preco_bloco,
                                    "estado": "disponivel",
                                    "escuteiro_id": None,
                                    "seccao": None
                                }
                                
                                response = supabase.table('blocos_rifas').insert(bloco_data).execute()
                                
                                if response.data:
                                    blocos_criados += 1
                                
                                numero_atual = numero_final + 1
                        
                        if blocos_criados == num_blocos:
                            st.success(f"✅ {blocos_criados} blocos criados com sucesso para a campanha '{campanha_selecionada}'!")
                            st.info("💡 Agora pode atribuir os blocos aos escuteiros na página 'Blocos de Rifas'.")
                            st.rerun()
                        else:
                            st.warning(f"⚠️ Apenas {blocos_criados} de {num_blocos} blocos foram criados.")
                    
                    except Exception as e:
                        st.error(f"❌ Erro ao criar blocos: {e}")
    else:
        st.warning("⚠️ Crie primeiro uma campanha antes de criar blocos de rifas!")

# ============================================
# TAB: EDITAR/ELIMINAR CAMPANHA
# ============================================
with tab_edit:
    st.subheader("✏️ Editar ou Eliminar Campanha")
    
    # Buscar campanhas
    response = supabase.table('campanhas').select('*').order('created_at', desc=True).execute()
    
    if response.data:
        campanhas_list = [(c['nome'], c['id']) for c in response.data]
        campanha_selecionada = st.selectbox(
            "Selecione a Campanha",
            options=campanhas_list,
            format_func=lambda x: x[0]
        )
        
        if campanha_selecionada:
            campanha_id = campanha_selecionada[1]
            campanha_data = next(c for c in response.data if c['id'] == campanha_id)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                with st.form("form_editar_campanha"):
                    st.markdown("### Editar Dados")
                    
                    novo_nome = st.text_input("Nome", value=campanha_data['nome'])
                    nova_descricao = st.text_area("Descrição", value=campanha_data['descricao'] or "")
                    
                    col_a, col_b = st.columns(2)
                    with col_a:
                        nova_data_inicio = st.date_input("Data Início", value=datetime.fromisoformat(campanha_data['data_inicio']).date())
                    with col_b:
                        nova_data_fim = st.date_input("Data Fim", value=datetime.fromisoformat(campanha_data['data_fim']).date())
                    
                    nova_ativa = st.checkbox("Campanha Ativa", value=campanha_data['ativa'])
                    
                    submitted = st.form_submit_button("💾 Guardar Alterações", use_container_width=True)
                    
                    if submitted:
                        try:
                            # Atualizar campanha
                            update_data = {
                                'nome': novo_nome,
                                'descricao': nova_descricao,
                                'data_inicio': nova_data_inicio.isoformat(),
                                'data_fim': nova_data_fim.isoformat(),
                                'ativa': nova_ativa
                            }
                            
                            supabase.table('campanhas').update(update_data).eq('id', campanha_id).execute()
                            
                            st.success("✅ Campanha atualizada com sucesso!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Erro ao atualizar: {e}")
            
            with col2:
                st.markdown("### Eliminar")
                st.warning("⚠️ **Atenção!** Ao eliminar uma campanha, todos os blocos, vendas e pagamentos associados serão também eliminados.")
                
                if st.button("🗑️ Eliminar Campanha", type="secondary", use_container_width=True):
                    # Confirmar eliminação
                    st.session_state['confirmar_eliminacao'] = campanha_id
                
                if st.session_state.get('confirmar_eliminacao') == campanha_id:
                    st.error("**Tem certeza?**")
                    col_sim, col_nao = st.columns(2)
                    
                    with col_sim:
                        if st.button("✅ Sim", use_container_width=True):
                            try:
                                supabase.table('campanhas').delete().eq('id', campanha_id).execute()
                                st.success("✅ Campanha eliminada!")
                                del st.session_state['confirmar_eliminacao']
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Erro: {e}")
                    
                    with col_nao:
                        if st.button("❌ Não", use_container_width=True):
                            del st.session_state['confirmar_eliminacao']
                            st.rerun()
    else:
        st.info("ℹ️ Nenhuma campanha disponível para editar")
