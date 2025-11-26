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
            
            # Buscar nomes dos escuteiros e preencher secção se estiver vazia no bloco
            if 'escuteiro_id' in df.columns:
                escuteiros_ids = df['escuteiro_id'].dropna().unique().tolist()
                if escuteiros_ids:
                    # trazer também a seccao dos escuteiros
                    esc_response = supabase.table('escuteiros').select('id, nome, seccao').in_('id', escuteiros_ids).execute()
                    esc_dict = {e['id']: e['nome'] for e in (esc_response.data or [])}
                    esc_seccao = {e['id']: e.get('seccao') for e in (esc_response.data or [])}
                    df['escuteiro_nome'] = df['escuteiro_id'].map(esc_dict).fillna('')

                    # preencher a coluna 'seccao' do bloco com a seccao do escuteiro quando estiver vazia
                    if 'seccao' in df.columns:
                        df['seccao'] = df['seccao'].fillna(df['escuteiro_id'].map(esc_seccao).fillna(''))
                    else:
                        df['seccao'] = df['escuteiro_id'].map(esc_seccao).fillna('')
                else:
                    df['escuteiro_nome'] = ''
                    if 'seccao' not in df.columns:
                        df['seccao'] = ''
            else:
                df['escuteiro_nome'] = ''
                if 'seccao' not in df.columns:
                    df['seccao'] = ''
            
            # Calculate total tickets per block
            if 'numero_inicial' in df.columns and 'numero_final' in df.columns:
                df['total_rifas'] = df['numero_final'] - df['numero_inicial'] + 1
            
            # Criar indicador de atribuição
            df['atribuido'] = df['escuteiro_nome'].apply(lambda x: '✅' if x else '⬜')
            
            # Reordenar colunas (mostrar o preço total do bloco como coluna principal)
            # garante coluna de observações e reordena
            if 'observacoes' not in df.columns:
                df['observacoes'] = ''

            # truncar observações para apresentação na grid (mantemos o texto original na coluna)
            def _truncate(s, n=80):
                try:
                    s = str(s)
                except Exception:
                    return ''
                return s if len(s) <= n else s[:n-1] + '…'

            df['observacoes_display'] = df['observacoes'].fillna('').apply(lambda x: _truncate(x, 80))

            colunas_ordem = ['atribuido', 'numero_inicial', 'numero_final', 'total_rifas', 'seccao', 'escuteiro_nome', 'preco_bloco', 'data_atribuicao', 'observacoes_display']
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
                    "preco_bloco": st.column_config.NumberColumn(
                        "Preço Bloco",
                        format="%.2f €",
                        help="Valor total do bloco (preço unitário × quantidade de rifas)"
                    ),
                    "data_atribuicao": "Data Atribuição",
                    # mostrar observações truncadas na grid; o utilizador pode selecionar o bloco para ver a nota completa
                    "observacoes_display": st.column_config.TextColumn(
                        "Observações",
                        help="Observações (texto truncado). Selecione o bloco para ver a observação completa.",
                        width="large"
                    )
                },
                hide_index=True,
                width='stretch'
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
                # Build id-based maps for stable selectbox options
                id_list = [opt['bloco']['id'] for opt in blocos_opcoes]
                display_map = {opt['bloco']['id']: opt['label'] for opt in blocos_opcoes}
                blocks_map = {opt['bloco']['id']: opt['bloco'] for opt in blocos_opcoes}

                with col1:
                    selected_bloco_inicial_id = st.selectbox(
                        "Bloco Inicial",
                        options=id_list,
                        format_func=lambda bid: display_map.get(bid, str(bid)),
                        help="Selecione o primeiro bloco do intervalo",
                        key="bloco_inicial_select"
                    )
                    bloco_inicial = blocks_map[selected_bloco_inicial_id]['numero_inicial']

                with col2:
                    # final options are ids where numero_inicial >= selected initial
                    blocos_finais_ids = [opt['bloco']['id'] for opt in blocos_opcoes if opt['numero_inicial'] >= bloco_inicial]
                    selected_bloco_final_id = st.selectbox(
                        "Bloco Final",
                        options=blocos_finais_ids,
                        format_func=lambda bid: display_map.get(bid, str(bid)),
                        help="Selecione o último bloco do intervalo",
                        key="bloco_final_select"
                    )
                    bloco_final = blocks_map[selected_bloco_final_id]['numero_inicial']

                with col3:
                    seccao_lote = st.selectbox(
                        "Secção",
                        options=['Lobitos', 'Exploradores', 'Pioneiros', 'Caminheiros', '-- Remover Secção --'],
                        key="seccao_lote_select"
                    )

                # Corrigir o cálculo do intervalo exibido
                bloco_inicial_num = blocks_map[selected_bloco_inicial_id]['numero_inicial']
                bloco_final_num = blocks_map[selected_bloco_final_id]['numero_final']
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
                # Use id-based selection to avoid label/index desync
                id_list = [b['id'] for b in blocos_response.data]
                display_map = {}
                blocks_map = {}
                for b in blocos_response.data:
                    rifa_range = f"{b['numero_inicial']:03d}-{b['numero_final']:03d}"
                    total_rifas = b['numero_final'] - b['numero_inicial'] + 1
                    display_name = f"Rifas {rifa_range} | {b.get('seccao', 'N/A')} | {total_rifas} rifas"
                    display_map[b['id']] = display_name
                    blocks_map[b['id']] = b

                selected_block_id = st.selectbox(
                    "1️⃣ Selecione o bloco de rifas",
                    options=id_list,
                    format_func=lambda bid: display_map.get(bid, str(bid)),
                    help="Escolha o bloco a dividir entre irmãos",
                    key="dividir_bloco_select"
                )
                block = blocks_map[selected_block_id]
                total_rifas_bloco = block['numero_final'] - block['numero_inicial'] + 1
                st.info(f"Bloco selecionado: Rifas {block['numero_inicial']} - {block['numero_final']} ({total_rifas_bloco} rifas)")
                # Seleção de irmãos
                escuteiros_response = supabase.table('escuteiros').select('id, nome, ativo, seccao').eq('ativo', True).order('nome').execute()
                if not escuteiros_response.data or len(escuteiros_response.data) < 2:
                    st.warning("⚠️ É necessário pelo menos 2 escuteiros ativos para divisão entre irmãos.")
                else:
                    # escuteiros: use id-based multiselect to avoid name->id mapping issues
                    esc_ids = [e['id'] for e in escuteiros_response.data]
                    esc_display = {e['id']: e['nome'] for e in escuteiros_response.data}
                    esc_seccao = {e['id']: e.get('seccao') for e in escuteiros_response.data}
                    selected_irmaos = st.multiselect(
                        "2️⃣ Selecione os irmãos",
                        options=esc_ids,
                        format_func=lambda eid: esc_display.get(eid, str(eid)),
                        help="Selecione 2 ou mais irmãos para dividir o bloco",
                        key="dividir_irmaos_select"
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
                                # 1. Determinar preco_unitario (preferir campo existente, senão derivar)
                                total_rifas_original = total_rifas_bloco
                                preco_unitario = block.get('preco_unitario')
                                try:
                                    if preco_unitario is None:
                                        preco_unitario = float(block.get('preco_bloco', 0)) / float(total_rifas_original) if total_rifas_original and total_rifas_original > 0 else 0.0
                                except Exception:
                                    preco_unitario = 0.0

                                # 2. Atualizar bloco original para o primeiro irmão com novo intervalo e preços
                                id_primeiro = selected_irmaos[0]
                                quantidade_primeiro = intervalos[0][1] - intervalos[0][0] + 1
                                preco_bloco_primeiro = round(preco_unitario * quantidade_primeiro, 2)

                                # copy seccao from the assigned escuteiro if available
                                seccao_primeiro = esc_seccao.get(id_primeiro)
                                update_data = {
                                    "escuteiro_id": id_primeiro,
                                    "numero_inicial": intervalos[0][0],
                                    "numero_final": intervalos[0][1],
                                    "preco_unitario": preco_unitario,
                                    "preco_bloco": preco_bloco_primeiro,
                                    "seccao": seccao_primeiro,
                                    "observacoes": f"Divisão automática entre irmãos: {', '.join([esc_display[eid] for eid in selected_irmaos])}"
                                }
                                supabase.table('blocos_rifas').update(update_data).eq('id', block['id']).execute()

                                # 3. Criar blocos para os outros irmãos com preços recalculados
                                for idx in range(1, n_irmaos):
                                    inicio, fim = intervalos[idx]
                                    quantidade = fim - inicio + 1
                                    novo_preco_bloco = round(preco_unitario * quantidade, 2)

                                    # assign seccao from the escuteiro when creating the new block
                                    seccao_novo = esc_seccao.get(selected_irmaos[idx]) or block.get('seccao')
                                    novo_bloco = {
                                        "campanha_id": block['campanha_id'],
                                        "nome": f"Bloco {inicio}-{fim}",
                                        "numero_inicial": inicio,
                                        "numero_final": fim,
                                        "preco_unitario": preco_unitario,
                                        "preco_bloco": novo_preco_bloco,
                                        "estado": "atribuido",
                                        "escuteiro_id": selected_irmaos[idx],
                                        "seccao": seccao_novo,
                                        "data_atribuicao": pd.Timestamp.now().isoformat(),
                                        "observacoes": f"Divisão automática entre irmãos: {', '.join([esc_display[eid] for eid in selected_irmaos])} (original {block['numero_inicial']}-{block['numero_final']})"
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
            # Get all escuteiros (including seccao)
            escuteiros_response = supabase.table('escuteiros').select('id, nome, ativo, seccao').eq('ativo', True).order('nome').execute()
            if not escuteiros_response.data:
                st.warning("⚠️ Nenhum escuteiro ativo disponível. Ative escuteiros na página 'Escuteiros'.")
            else:
                if opcao_atribuicao == "👤 Individual":
                    # ===== ATRIBUIÇÃO INDIVIDUAL =====
                    st.markdown("### Atribuição Individual")
                    escuteiros_dict = {e['id']: e['nome'] for e in escuteiros_response.data}
                    esc_seccao = {e['id']: e.get('seccao') for e in escuteiros_response.data}

                    # Create block selection dropdown (only unassigned)
                    id_list = [b['id'] for b in blocos_response.data]
                    display_map = {
                        b['id']: f"⬜ Rifas {b['numero_inicial']:03d}-{b['numero_final']:03d} | {b.get('seccao', 'N/A')} | {b['numero_final']-b['numero_inicial']+1} rifas"
                        for b in blocos_response.data
                    }
                    blocks_map = {b['id']: b for b in blocos_response.data}

                    if not id_list:
                        st.warning("⚠️ Nenhum bloco disponível para atribuição nesta campanha. Crie ou libere blocos na aba 'Lista de Blocos'.")
                    else:
                        selected_block_id = st.selectbox(
                            "1️⃣ Selecione o bloco de rifas",
                            options=id_list,
                            format_func=lambda bid: display_map.get(bid, str(bid)),
                            help="Escolha o bloco que deseja atribuir a um escuteiro",
                            key="assign_block_select"
                        )
                        if selected_block_id:
                            block = blocks_map[selected_block_id]
                            total_rifas_bloco = block['numero_final'] - block['numero_inicial'] + 1

                            # Show block info
                            col1, col2, col3, col4 = st.columns(4)
                            col1.metric("Rifas", f"{block['numero_inicial']} - {block['numero_final']}")
                            col2.metric("Total", f"{total_rifas_bloco} rifas")
                            col3.metric("Secção", block.get('seccao', 'N/A'))
                            # Mostrar o preço total do bloco (preco_bloco). Se não existir, derivar a partir do preco_unitario.
                            preco_unitario = block.get('preco_unitario')
                            preco_bloco_val = None
                            try:
                                if block.get('preco_bloco') is not None:
                                    preco_bloco_val = float(block.get('preco_bloco'))
                                elif preco_unitario is not None:
                                    preco_bloco_val = float(preco_unitario) * float(total_rifas_bloco)
                            except Exception:
                                preco_bloco_val = None

                            try:
                                preco_str = f"{preco_bloco_val:.2f} €" if preco_bloco_val is not None else "N/A"
                            except Exception:
                                preco_str = "N/A"

                            col4.metric("Preço", preco_str)
                            st.divider()

                            with st.form("assign_block_form"):
                                # Escuteiro selection (allow None for unassignment)
                                esc_ids = [e['id'] for e in escuteiros_response.data]
                                esc_display = {e['id']: e['nome'] for e in escuteiros_response.data}
                                options = [None] + esc_ids

                                # determine default index based on current assignment
                                default_index = 0
                                if block.get('escuteiro_id'):
                                    try:
                                        default_index = options.index(block.get('escuteiro_id'))
                                    except ValueError:
                                        default_index = 0

                                selected_escuteiro_id = st.selectbox(
                                    "2️⃣ Atribuir a Escuteiro",
                                    options=options,
                                    index=default_index,
                                    format_func=lambda eid: "-- Sem atribuição --" if eid is None else esc_display.get(eid, str(eid)),
                                    help="Selecione o escuteiro que ficará responsável por este bloco",
                                    key="assign_escuteiro_select"
                                )
                                
                                # Observations / notes field
                                observacoes_text = st.text_area(
                                    "3️⃣ Observações",
                                    value=block.get('observacoes', '') or '',
                                    help="Registo de notas ou observações para este bloco (ex: contacto, estado, detalhes).",
                                    key="assign_observacoes_text",
                                    height=100
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
                                        # selected_escuteiro_id is either None or an id
                                        escuteiro_id = selected_escuteiro_id
                                        update_data = {"escuteiro_id": escuteiro_id}
                                        
                                        # include observações (save empty string as NULL)
                                        obs_val = observacoes_text.strip() if observacoes_text and isinstance(observacoes_text, str) else None
                                        update_data["observacoes"] = obs_val

                                        # Add/update assignment date if assigning
                                        if escuteiro_id:
                                            from datetime import datetime
                                            update_data["data_atribuicao"] = datetime.now().isoformat()
                                            # copy the escuteiro's seccao into the block
                                            update_data["seccao"] = esc_seccao.get(escuteiro_id)
                                        else:
                                            # Clear assignment date if removing assignment
                                            update_data["data_atribuicao"] = None

                                        response = supabase.table('blocos_rifas').update(update_data).eq('id', block['id']).execute()
                                        if response.data:
                                            # Determine name for success message
                                            if escuteiro_id:
                                                nome_esc = esc_display.get(escuteiro_id, str(escuteiro_id))
                                                st.success(f"✅ Bloco (rifas {block['numero_inicial']}-{block['numero_final']}) atribuído a **{nome_esc}** com sucesso!")
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
