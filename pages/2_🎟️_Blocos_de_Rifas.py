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
tab1, tab2, tab3 = st.tabs(["📋 Lista de Blocos", "🏷️ Atribuição de Secção", "➕ Atribuir a Escuteiro"])

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

# Tab 2: Assign section to blocks (individual or batch)
with tab2:
    st.subheader("🏷️ Atribuição de Secção")
    st.info("""
    Atribua uma secção a um ou mais blocos completos de rifas de uma só vez. Basta escolher o bloco inicial e final para definir o intervalo (ou o mesmo bloco para apenas um).
    Blocos atribuídos a uma secção podem depois ser atribuídos a escuteiros na tab "Atribuir a Escuteiro".
    """)
    try:
        # Get blocks from selected campaign
        blocos_response = supabase.table('blocos_rifas').select('*').eq('campanha_id', selected_campanha['id']).order('numero_inicial').execute()
        if blocos_response.data:
            blocos_disponiveis = [b for b in blocos_response.data if not b.get('escuteiro_id')]
            if blocos_disponiveis:
                blocos_opcoes = []
                for b in blocos_disponiveis:
                    blocos_opcoes.append({
                        'numero_inicial': b['numero_inicial'],
                        'numero_final': b['numero_final'],
                        'label': f"Rifas {b['numero_inicial']}-{b['numero_final']}",
                        'bloco': b
                    })
                blocos_opcoes = sorted(blocos_opcoes, key=lambda x: x['numero_inicial'])
                
                # --- Seletores fora do form para atualização instantânea ---
                col1, col2, col3 = st.columns(3)
                with col1:
                    bloco_inicial_idx = st.selectbox(
                        "Bloco Inicial",
                        options=range(len(blocos_opcoes)),
                        format_func=lambda x: blocos_opcoes[x]['label'],
                        help="Selecione o primeiro bloco do intervalo",
                        key="bloco_inicial_select"
                    )
                    bloco_inicial = blocos_opcoes[bloco_inicial_idx]['numero_inicial']
                with col2:
                    blocos_finais_opcoes = [i for i, b in enumerate(blocos_opcoes) if b['numero_inicial'] >= bloco_inicial]
                    bloco_final_idx = st.selectbox(
                        "Bloco Final",
                        options=blocos_finais_opcoes,
                        format_func=lambda x: blocos_opcoes[x]['label'],
                        help="Selecione o último bloco do intervalo",
                        key="bloco_final_select"
                    )
                    bloco_final = blocos_opcoes[bloco_final_idx]['numero_inicial']
                with col3:
                    seccao_lote = st.selectbox(
                        "Secção",
                        options=['Lobitos', 'Exploradores', 'Pioneiros', 'Caminheiros', '-- Remover Secção --'],
                        key="seccao_lote_select"
                    )
                # Corrigir o cálculo do intervalo exibido
                bloco_inicial_num = blocos_opcoes[bloco_inicial_idx]['numero_inicial']
                bloco_final_num = blocos_opcoes[bloco_final_idx]['numero_final']
                intervalo_inicio = min(bloco_inicial_num, bloco_final_num)
                intervalo_fim = max(bloco_inicial_num, bloco_final_num)
                blocos_a_atribuir = [
                    b for b in blocos_disponiveis
                    if b['numero_inicial'] >= intervalo_inicio and b['numero_inicial'] <= intervalo_fim
                ]
                st.info(f"📊 Serão atribuídos até **{len(blocos_a_atribuir)} bloco(s)** completo(s) (Rifas {intervalo_inicio}-{intervalo_fim})")
                if len(blocos_a_atribuir) == 0:
                    st.warning("⚠️ Nenhum bloco disponível para atribuição neste intervalo.")
                # --- Botão de confirmação dentro do form ---
                with st.form("atribuir_secao_form"):
                    submitted = st.form_submit_button("🏷️ Atribuir Secção", type="primary", use_container_width=True)
                    if submitted:
                        try:
                            if blocos_a_atribuir:
                                if seccao_lote == '-- Remover Secção --':
                                    nova_seccao = None
                                    msg_acao = "com secção removida"
                                else:
                                    nova_seccao = seccao_lote
                                    msg_acao = f"atribuído(s) à secção **{seccao_lote}**"
                                blocos_atualizados = 0
                                for bloco in blocos_a_atribuir:
                                    response = supabase.table('blocos_rifas').update({
                                        "seccao": nova_seccao
                                    }).eq('id', bloco['id']).execute()
                                    if response.data:
                                        blocos_atualizados += 1
                                st.success(f"✅ {blocos_atualizados} bloco(s) completo(s) {msg_acao}!")
                                st.info("🔄 A página será recarregada...")
                                import time
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.warning(f"⚠️ Nenhum bloco disponível no intervalo selecionado")
                        except Exception as e:
                            st.error(f"Erro: {str(e)}")
            else:
                st.info("📭 Nenhum bloco disponível para atribuição de secção.")
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
    if opcao_atribuicao == "👥 Irmãos (divisão automática)":
        st.info("ℹ️ Se o número de rifas não for divisível igualmente, as rifas extra serão atribuídas ao primeiro irmão da lista.")
        # Seleção de bloco
        blocos_response = supabase.table('blocos_rifas').select('*').eq('campanha_id', selected_campanha['id']).is_('escuteiro_id', 'null').order('numero_inicial').execute()
        if not blocos_response.data:
            st.warning("⚠️ Nenhum bloco disponível para divisão.")
        else:
            blocks_dict = {}
            for block in blocos_response.data:
                rifa_range = f"{block['numero_inicial']:03d}-{block['numero_final']:03d}"
                total_rifas = block['numero_final'] - block['numero_inicial'] + 1
                display_name = f"Rifas {rifa_range} | {block.get('seccao', 'N/A')} | {total_rifas} rifas"
                blocks_dict[display_name] = block
            if blocks_dict and len(blocks_dict) > 0:
                selected_block_name = st.selectbox(
                    "1️⃣ Selecione o bloco de rifas",
                    options=list(blocks_dict.keys()),
                    help="Escolha o bloco a dividir entre irmãos"
                )
                block = blocks_dict[selected_block_name]
                total_rifas_bloco = block['numero_final'] - block['numero_inicial'] + 1
                st.info(f"Bloco selecionado: Rifas {block['numero_inicial']} - {block['numero_final']} ({total_rifas_bloco} rifas)")
                # Seleção de irmãos
                escuteiros_response = supabase.table('escuteiros').select('id, nome, ativo').eq('ativo', True).order('nome').execute()
                if not escuteiros_response.data or len(escuteiros_response.data) < 2:
                    st.warning("⚠️ É necessário pelo menos 2 escuteiros ativos para divisão entre irmãos.")
                else:
                    escuteiros_dict = {e['nome']: e['id'] for e in escuteiros_response.data}
                    selected_irmaos = st.multiselect(
                        "2️⃣ Selecione os irmãos",
                        options=list(escuteiros_dict.keys()),
                        help="Selecione 2 ou mais irmãos para dividir o bloco"
                    )
                    if len(selected_irmaos) >= 2:
                        n_irmaos = len(selected_irmaos)
                        base = total_rifas_bloco // n_irmaos
                        extra = total_rifas_bloco % n_irmaos
                        partes = [base + (1 if i == 0 and extra > 0 else 0) for i in range(n_irmaos)]
                        # Calcular intervalos
                        intervalos = []
                        inicio = block['numero_inicial']
                        for p in partes:
                            fim = inicio + p - 1
                            intervalos.append((inicio, fim))
                            inicio = fim + 1
                        # Preview
                        st.markdown("### Pré-visualização da divisão:")
                        for idx, nome in enumerate(selected_irmaos):
                            st.write(f"{nome}: Rifas {intervalos[idx][0]} - {intervalos[idx][1]} ({partes[idx]} rifas){' (recebe extra)' if idx == 0 and extra > 0 else ''}")
                        # Botão de confirmação
                        if st.button("➗ Dividir e atribuir bloco aos irmãos", type="primary", use_container_width=True):
                            try:
                                # 1. Atribuir bloco original ao primeiro irmão
                                id_primeiro = escuteiros_dict[selected_irmaos[0]]
                                update_data = {
                                    "escuteiro_id": id_primeiro,
                                    "numero_inicial": intervalos[0][0],
                                    "numero_final": intervalos[0][1],
                                    "observacoes": f"Divisão automática entre irmãos: {', '.join(selected_irmaos)}"
                                }
                                supabase.table('blocos_rifas').update(update_data).eq('id', block['id']).execute()
                                # 2. Criar blocos para os outros irmãos (sem preco_unitario)
                                for idx in range(1, n_irmaos):
                                    novo_bloco = {
                                        "campanha_id": block['campanha_id'],
                                        "nome": f"Bloco {intervalos[idx][0]}-{intervalos[idx][1]}",
                                        "numero_inicial": intervalos[idx][0],
                                        "numero_final": intervalos[idx][1],
                                        "preco_bloco": block.get('preco_bloco'),
                                        "estado": "atribuido",
                                        "escuteiro_id": escuteiros_dict[selected_irmaos[idx]],
                                        "seccao": block.get('seccao'),
                                        "data_atribuicao": pd.Timestamp.now().isoformat(),
                                        "observacoes": f"Divisão automática entre irmãos: {', '.join(selected_irmaos)} (original {block['numero_inicial']}-{block['numero_final']})"
                                    }
                                    supabase.table('blocos_rifas').insert(novo_bloco).execute()
                                st.success("✅ Bloco dividido e atribuído aos irmãos com sucesso!")
                                st.info("🔄 A página será recarregada...")
                                import time
                                time.sleep(1.5)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao dividir bloco: {str(e)}")
            elif not blocks_dict or len(blocks_dict) == 0:
                st.warning("⚠️ Nenhum bloco disponível para atribuição nesta campanha. Crie ou libere blocos na aba 'Lista de Blocos'.")
    
    try:
        # Get blocks from selected campaign - ONLY UNASSIGNED
        blocos_response = supabase.table('blocos_rifas').select('*').eq('campanha_id', selected_campanha['id']).is_('escuteiro_id', 'null').order('numero_inicial').execute()
        blocks_dict = {}  # Garante existência
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
                    for block in blocos_response.data:
                        rifa_range = f"{block['numero_inicial']:03d}-{block['numero_final']:03d}"
                        total_rifas = block['numero_final'] - block['numero_inicial'] + 1
                        status = "⬜"
                        display_name = f"{status} Rifas {rifa_range} | {block.get('seccao', 'N/A')} | {total_rifas} rifas"
                        blocks_dict[display_name] = block
                    if not blocks_dict:
                        st.warning("⚠️ Nenhum bloco disponível para atribuição nesta campanha. Crie ou libere blocos na aba 'Lista de Blocos'.")
                    else:
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
                            preco = block.get('preco_unitario')
                            try:
                                preco_str = f"{float(preco):.2f} €/rifa" if preco is not None else "N/A"
                            except Exception:
                                preco_str = "N/A"
                            col4.metric("Preço", preco_str)
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
                                submitted = col_btn1.form_submit_button("💾 Guardar", type="primary", use_container_width=True)
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
                                            if response.data:
                                                st.success(f"✅ Bloco (rifas {block['numero_inicial']}-{block['numero_final']}) atribuído a **{selected_escuteiro_name}** com sucesso!")
                                            else:
                                                st.success("✅ Atribuição removida com sucesso!")
                                            st.info("🔄 A página será recarregada...")
                                            import time
                                            time.sleep(1.5)
                                            st.rerun()
                                        else:
                                            st.error("Erro ao atualizar atribuição.")
                                    except Exception as e:
                                        st.error(f"Erro ao atualizar atribuição: {str(e)}")
        else:
            st.info("📭 Nenhum bloco disponível nesta campanha. Crie blocos na página 'Campanhas'.")
    
    except Exception as e:
        st.error(f"Erro ao carregar dados: {str(e)}")
