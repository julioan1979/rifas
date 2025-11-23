import streamlit as st
import pandas as pd
from utils.supabase_client import get_supabase_client

st.set_page_config(page_title="Blocos de Rifas", page_icon="🎟️", layout="wide")

st.title("🎟️ Gestão de Blocos de Rifas")

st.info("💡 **Nota:** Os blocos de rifas são criados automaticamente na página 'Campanhas'. Aqui pode atribuir blocos aos escuteiros.")

# Initialize Supabase client
try:
    supabase = get_supabase_client()
except ValueError as e:
    st.error(f"Erro ao conectar ao Supabase: {str(e)}")
    st.stop()

# Get campaigns for filtering
try:
    campanhas_response = supabase.table('campanhas').select('*').order('created_at', desc='desc').execute()
    
    if campanhas_response.data:
        # Create campaign selector
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
                index=default_idx
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
tab1, tab2, tab3 = st.tabs(["📋 Lista de Blocos", "🏷️ Reservar por Secção", "➕ Atribuir a Escuteiro"])

# Tab 1: List raffle blocks
with tab1:
    st.subheader(f"Blocos da Campanha: {selected_campanha['nome']}")
    
    try:
        response = supabase.table('blocos_rifas').select('*').eq('campanha_id', selected_campanha['id']).order('numero_inicial').execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Formatar data (sem hora)
            if 'data_atribuicao' in df.columns:
                df['data_atribuicao'] = pd.to_datetime(df['data_atribuicao'], errors='coerce').dt.strftime('%d-%m-%Y')
                df['data_atribuicao'] = df['data_atribuicao'].replace('NaT', '')
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%d-%m-%Y')
            
            # Buscar nomes dos escuteiros
            if 'escuteiro_id' in df.columns:
                escuteiros_ids = df['escuteiro_id'].dropna().unique().tolist()
                if escuteiros_ids:
                    esc_response = supabase.table('escuteiros').select('id, nome').in_('id', escuteiros_ids).execute()
                    esc_dict = {e['id']: e['nome'] for e in esc_response.data}
                    df['escuteiro_nome'] = df['escuteiro_id'].map(esc_dict).fillna('')
                else:
                    df['escuteiro_nome'] = ''
            else:
                df['escuteiro_nome'] = ''
            
            # Calculate total tickets per block
            if 'numero_inicial' in df.columns and 'numero_final' in df.columns:
                df['total_rifas'] = df['numero_final'] - df['numero_inicial'] + 1
            
            # Criar indicador de atribuição
            df['atribuido'] = df['escuteiro_nome'].apply(lambda x: '✅' if x else '⬜')
            
            # Reordenar colunas
            colunas_ordem = ['atribuido', 'numero_inicial', 'numero_final', 'total_rifas', 'seccao', 'escuteiro_nome', 'preco_unitario', 'data_atribuicao']
            df_display = df[[col for col in colunas_ordem if col in df.columns]]
            
            st.dataframe(
                df_display,
                column_config={
                    "atribuido": st.column_config.TextColumn(
                        "Atrib.",
                        help="✅ Atribuído | ⬜ Disponível"
                    ),
                    "numero_inicial": "Nº Inicial",
                    "numero_final": "Nº Final",
                    "total_rifas": st.column_config.NumberColumn(
                        "Total",
                        help="Total de rifas no bloco"
                    ),
                    "seccao": "Secção",
                    "escuteiro_nome": "Escuteiro",
                    "preco_unitario": st.column_config.NumberColumn(
                        "Preço Unit.",
                        format="%.2f €"
                    ),
                    "data_atribuicao": "Data Atribuição"
                },
                hide_index=True,
                use_container_width=True
            )
            
            # Estatísticas
            total_blocos = len(df)
            blocos_atribuidos = len(df[df['escuteiro_nome'] != ''])
            blocos_disponiveis = total_blocos - blocos_atribuidos
            total_rifas_all = df['total_rifas'].sum() if 'total_rifas' in df.columns else 0
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("📦 Total de Blocos", total_blocos)
            col2.metric("✅ Atribuídos", blocos_atribuidos)
            col3.metric("⬜ Disponíveis", blocos_disponiveis)
            col4.metric("🎟️ Total de Rifas", int(total_rifas_all))
        else:
            st.info("Nenhum bloco de rifas criado ainda.")
    
    except Exception as e:
        st.error(f"Erro ao carregar blocos de rifas: {str(e)}")

# Tab 2: Reserve blocks by section
with tab2:
    st.subheader("🏷️ Reservar Blocos por Secção")
    
    st.info("""
    **Sistema de Reserva:**
    - Reserve blocos para uma secção específica (Reserva, Lobitos, Exploradores, Pioneiros, Caminheiros)
    - Blocos reservados ficam marcados com a secção mas ainda sem escuteiro atribuído
    - Posteriormente pode atribuir escuteiros específicos na tab "Atribuir a Escuteiro"
    """)
    
    try:
        # Get blocks from selected campaign
        blocos_response = supabase.table('blocos_rifas').select('*').eq('campanha_id', selected_campanha['id']).order('numero_inicial').execute()
        
        if blocos_response.data:
            # Estatísticas por secção
            df_blocos = pd.DataFrame(blocos_response.data)
            
            st.markdown("### 📊 Distribuição Atual")
            
            seccoes_info = []
            for seccao in ['Reserva', 'Lobitos', 'Exploradores', 'Pioneiros', 'Caminheiros']:
                blocos_seccao = df_blocos[df_blocos['seccao'] == seccao]
                total_blocos = len(blocos_seccao)
                blocos_atribuidos = len(blocos_seccao[blocos_seccao['escuteiro_id'].notna()])
                blocos_reservados = total_blocos - blocos_atribuidos
                
                seccoes_info.append({
                    'Secção': seccao,
                    'Total Blocos': total_blocos,
                    'Reservados (sem escuteiro)': blocos_reservados,
                    'Atribuídos (com escuteiro)': blocos_atribuidos
                })
            
            st.dataframe(
                pd.DataFrame(seccoes_info),
                hide_index=True,
                use_container_width=True
            )
            
            st.divider()
            
            # Formulário para reservar blocos
            st.markdown("### 🏷️ Reservar ou Alterar Secção")
            
            with st.form("reserve_section_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    # Filtrar blocos disponíveis ou já com secção
                    blocos_opcoes = []
                    for bloco in blocos_response.data:
                        rifa_range = f"{bloco['numero_inicial']:03d}-{bloco['numero_final']:03d}"
                        seccao_atual = bloco.get('seccao', 'Sem secção')
                        esc_id = bloco.get('escuteiro_id')
                        
                        if esc_id:
                            status = "👤 Atribuído"
                        elif seccao_atual and seccao_atual != 'Sem secção':
                            status = "🏷️ Reservado"
                        else:
                            status = "⬜ Disponível"
                        
                        display = f"{status} | Rifas {rifa_range} | {seccao_atual}"
                        blocos_opcoes.append((display, bloco))
                    
                    if blocos_opcoes:
                        bloco_selecionado_display = st.selectbox(
                            "Selecione o Bloco",
                            options=[b[0] for b in blocos_opcoes],
                            help="Escolha o bloco para reservar/alterar secção"
                        )
                        
                        # Find selected block
                        bloco_selecionado = None
                        for display, bloco in blocos_opcoes:
                            if display == bloco_selecionado_display:
                                bloco_selecionado = bloco
                                break
                    else:
                        st.warning("Nenhum bloco disponível")
                        bloco_selecionado = None
                
                with col2:
                    nova_seccao = st.selectbox(
                        "Secção",
                        options=['Reserva', 'Lobitos', 'Exploradores', 'Pioneiros', 'Caminheiros', '-- Remover Reserva --'],
                        help="Secção para reservar este bloco"
                    )
                
                if bloco_selecionado:
                    total_rifas = bloco_selecionado['numero_final'] - bloco_selecionado['numero_inicial'] + 1
                    st.info(f"📊 **Bloco:** Rifas {bloco_selecionado['numero_inicial']}-{bloco_selecionado['numero_final']} | **Total:** {total_rifas} rifas")
                    
                    if bloco_selecionado.get('escuteiro_id'):
                        st.warning("⚠️ Este bloco já está atribuído a um escuteiro. A alteração da secção será aplicada mas o escuteiro permanecerá atribuído.")
                
                col_btn1, col_btn2 = st.columns([1, 3])
                with col_btn1:
                    submitted = st.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
                with col_btn2:
                    st.caption("💡 Use '-- Remover Reserva --' para desmarcar a secção")
                
                if submitted and bloco_selecionado:
                    try:
                        # Determine new section value
                        if nova_seccao == '-- Remover Reserva --':
                            update_data = {"seccao": None}
                            msg = "Reserva removida"
                        else:
                            update_data = {"seccao": nova_seccao}
                            msg = f"Bloco reservado para secção **{nova_seccao}**"
                        
                        response = supabase.table('blocos_rifas').update(update_data).eq('id', bloco_selecionado['id']).execute()
                        
                        if response.data:
                            st.success(f"✅ {msg} com sucesso!")
                            st.rerun()
                        else:
                            st.error("Erro ao atualizar bloco.")
                    
                    except Exception as e:
                        st.error(f"Erro: {str(e)}")
            
            st.divider()
            
            # Ação em lote
            st.markdown("### 📦 Reserva em Lote")
            st.caption("Reserve múltiplos blocos sequenciais para uma secção de uma vez")
            
            with st.form("batch_reserve_form"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    num_inicial_lote = st.number_input(
                        "Número Inicial da Rifa",
                        min_value=1,
                        value=1,
                        help="Primeira rifa do intervalo"
                    )
                
                with col2:
                    num_final_lote = st.number_input(
                        "Número Final da Rifa",
                        min_value=1,
                        value=10,
                        help="Última rifa do intervalo"
                    )
                
                with col3:
                    seccao_lote = st.selectbox(
                        "Secção para o Lote",
                        options=['Reserva', 'Lobitos', 'Exploradores', 'Pioneiros', 'Caminheiros']
                    )
                
                submitted_lote = st.form_submit_button("🏷️ Reservar Lote", type="secondary", use_container_width=True)
                
                if submitted_lote:
                    try:
                        # Find all blocks in range
                        blocos_no_intervalo = [
                            b for b in blocos_response.data
                            if b['numero_inicial'] >= num_inicial_lote and b['numero_final'] <= num_final_lote
                        ]
                        
                        if blocos_no_intervalo:
                            # Update all blocks
                            blocos_atualizados = 0
                            for bloco in blocos_no_intervalo:
                                response = supabase.table('blocos_rifas').update({
                                    "seccao": seccao_lote
                                }).eq('id', bloco['id']).execute()
                                
                                if response.data:
                                    blocos_atualizados += 1
                            
                            st.success(f"✅ {blocos_atualizados} bloco(s) reservado(s) para **{seccao_lote}**!")
                            st.rerun()
                        else:
                            st.warning(f"⚠️ Nenhum bloco encontrado no intervalo {num_inicial_lote}-{num_final_lote}")
                    
                    except Exception as e:
                        st.error(f"Erro: {str(e)}")
        else:
            st.info("📭 Nenhum bloco criado nesta campanha. Crie blocos na página 'Campanhas'.")
    
    except Exception as e:
        st.error(f"Erro: {str(e)}")

# Tab 3: Assign blocks to escuteiros
with tab3:
    st.subheader("Atribuir Bloco a Escuteiro")
    
    # Option selector
    opcao_atribuicao = st.radio(
        "Tipo de Atribuição",
        options=["👤 Individual", "👥 Irmãos (divisão automática)"],
        horizontal=True
    )
    
    try:
        # Get blocks from selected campaign - ONLY UNASSIGNED
        blocos_response = supabase.table('blocos_rifas').select('*').eq('campanha_id', selected_campanha['id']).is_('escuteiro_id', 'null').order('numero_inicial').execute()
        
        if blocos_response.data:
            # Get all escuteiros
            escuteiros_response = supabase.table('escuteiros').select('id, nome, ativo').eq('ativo', True).order('nome').execute()
            
            if not escuteiros_response.data:
                st.warning("⚠️ Nenhum escuteiro ativo disponível. Ative escuteiros na página 'Escuteiros'.")
            else:
                if opcao_atribuicao == "👤 Individual":
                    # ===== ATRIBUIÇÃO INDIVIDUAL =====
                    st.markdown("### Atribuição Individual")
                    
                    escuteiros_dict = {e['id']: e['nome'] for e in escuteiros_response.data}
                    
                    # Create block selection dropdown (only unassigned)
                    blocks_dict = {}
                    for block in blocos_response.data:
                        rifa_range = f"{block['numero_inicial']:03d}-{block['numero_final']:03d}"
                        total_rifas = block['numero_final'] - block['numero_inicial'] + 1
                        status = "⬜"
                        
                        display_name = f"{status} Rifas {rifa_range} | {block.get('seccao', 'N/A')} | {total_rifas} rifas"
                        blocks_dict[display_name] = block
                    status = "✅" if block.get('escuteiro_id') else "⬜"
                    
                    display_name = f"{status} Rifas {rifa_range} | {block.get('seccao', 'N/A')} | {total_rifas} rifas | {esc_nome}"
                    blocks_dict[display_name] = block
                
                selected_block_name = st.selectbox(
                    "1️⃣ Selecione o bloco de rifas",
                    options=list(blocks_dict.keys()),
                    help="Escolha o bloco que deseja atribuir a um escuteiro"
                )
                
                if selected_block_name:
                    block = blocks_dict[selected_block_name]
                    total_rifas_bloco = block['numero_final'] - block['numero_inicial'] + 1
                    
                    # Show block info
                    col1, col2, col3, col4 = st.columns(4)
                    col1.metric("Rifas", f"{block['numero_inicial']} - {block['numero_final']}")
                    col2.metric("Total", f"{total_rifas_bloco} rifas")
                    col3.metric("Secção", block.get('seccao', 'N/A'))
                    col4.metric("Preço", f"{float(block['preco_unitario']):.2f} €/rifa")
                    
                    st.divider()
                    
                    with st.form("assign_block_form"):
                        # Escuteiro selection (allow None for unassignment)
                        escuteiro_options = ["-- Sem atribuição --"] + [e['nome'] for e in escuteiros_response.data]
                        
                        # Get current assignment
                        current_idx = 0
                        if block.get('escuteiro_id'):
                            current_name = escuteiros_dict.get(block['escuteiro_id'])
                            if current_name in escuteiro_options:
                                current_idx = escuteiro_options.index(current_name)
                        
                        selected_escuteiro_name = st.selectbox(
                            "2️⃣ Atribuir a Escuteiro",
                            options=escuteiro_options,
                            index=current_idx,
                            help="Selecione o escuteiro que ficará responsável por este bloco"
                        )
                        
                        # Show current assignment info if exists
                        if block.get('data_atribuicao'):
                            st.caption(f"ℹ️ Última atribuição: {pd.to_datetime(block['data_atribuicao']).strftime('%d-%m-%Y')}")
                        
                        col_btn1, col_btn2 = st.columns([1, 4])
                        with col_btn1:
                            submitted = st.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
                        with col_btn2:
                            if block.get('escuteiro_id'):
                                st.caption("💡 Para remover atribuição, selecione '-- Sem atribuição --'")
                        
                        if submitted:
                            try:
                                # Find escuteiro ID or set to None
                                escuteiro_id = None
                                if selected_escuteiro_name != "-- Sem atribuição --":
                                    for e in escuteiros_response.data:
                                        if e['nome'] == selected_escuteiro_name:
                                            escuteiro_id = e['id']
                                            break
                                
                                update_data = {
                                    "escuteiro_id": escuteiro_id
                                }
                                
                                # Add/update assignment date if assigning
                                if escuteiro_id:
                                    from datetime import datetime
                                    update_data["data_atribuicao"] = datetime.now().isoformat()
                                else:
                                    # Clear assignment date if removing assignment
                                    update_data["data_atribuicao"] = None
                                
                                response = supabase.table('blocos_rifas').update(update_data).eq('id', block['id']).execute()
                                
                                if response.data:
                                    if escuteiro_id:
                                        st.success(f"✅ Bloco (rifas {block['numero_inicial']}-{block['numero_final']}) atribuído a **{selected_escuteiro_name}** com sucesso!")
                                    else:
                                        st.success("✅ Atribuição removida com sucesso!")
                                    st.rerun()
                                else:
                                    st.error("Erro ao atualizar atribuição.")
                            
                            except Exception as e:
                                st.error(f"Erro ao atualizar atribuição: {str(e)}")
        else:
            st.info("📭 Nenhum bloco disponível nesta campanha. Crie blocos na página 'Campanhas'.")
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
