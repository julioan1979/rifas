"""
Script para importar dados do Excel para a campanha Natal 2025
"""

from utils.supabase_client import get_supabase_client
from datetime import datetime
import pandas as pd

# Mapeamento de cores para secções
COLOR_TO_SECTION = {
    'FFC000': 'Lobitos',      # Amarelo/Laranja
    '00B0F0': 'Exploradores', # Azul claro
    '92D050': 'Pioneiros',    # Verde
    'FF0000': 'Caminheiros',  # Vermelho
}

def parse_date(date_str):
    """Converte string de data para formato ISO"""
    if pd.isna(date_str) or date_str == '':
        return None
    try:
        # Tentar formato DD/M/YYYY
        if isinstance(date_str, str) and '/' in date_str:
            parts = date_str.split('/')
            day = int(parts[0])
            month = int(parts[1])
            year = int(parts[2])
            return f"{year:04d}-{month:02d}-{day:02d}"
        return None
    except:
        return None

def importar_dados():
    """Importa dados do Excel para o Supabase"""
    
    supabase = get_supabase_client()
    
    print("=" * 70)
    print("📦 IMPORTAÇÃO DE DADOS - NATAL 2025")
    print("=" * 70)
    print()
    
    # Dados dos escuteiros extraídos da imagem
    escuteiros_data = [
        # Exploradores (Azul)
        {'nome': 'Afonso Marrafes', 'seccao': 'Exploradores', 'data_nascimento': '15/1/2012'},
        {'nome': 'Afonso', 'seccao': 'Exploradores', 'data_nascimento': '23/3/2012'},
        {'nome': 'Eduardo', 'seccao': 'Exploradores', 'data_nascimento': '20/3/2012'},
        {'nome': 'Filipa', 'seccao': 'Exploradores', 'data_nascimento': '30/1/2012'},
        {'nome': 'Francisco', 'seccao': 'Exploradores', 'data_nascimento': '27/3/2012'},
        {'nome': 'Gonçalo', 'seccao': 'Exploradores', 'data_nascimento': '17/1/2012'},
        {'nome': 'Henrique Magalhães', 'seccao': 'Exploradores', 'data_nascimento': '30/1/2012'},
        {'nome': 'Inês Cardoso', 'seccao': 'Exploradores', 'data_nascimento': '14/10/2012'},
        {'nome': 'Isabel', 'seccao': 'Exploradores', 'data_nascimento': '20/11/2012'},
        {'nome': 'João Pedro', 'seccao': 'Exploradores', 'data_nascimento': '7/3/2012'},
        {'nome': 'José', 'seccao': 'Exploradores', 'data_nascimento': '30/3/2012'},
        {'nome': 'Lourenço', 'seccao': 'Exploradores', 'data_nascimento': '4/8/2012'},
        {'nome': 'Maria', 'seccao': 'Exploradores', 'data_nascimento': '27/3/2012'},
        {'nome': 'Maria Inês', 'seccao': 'Exploradores', 'data_nascimento': '7/6/2012'},
        {'nome': 'Martim', 'seccao': 'Exploradores', 'data_nascimento': '11/6/2012'},
        {'nome': 'Diogo', 'seccao': 'Exploradores', 'data_nascimento': '29/11/2011'},
        {'nome': 'Hugo', 'seccao': 'Exploradores', 'data_nascimento': '27/3/2012'},
        
        # Lobitos (Amarelo)
        {'nome': 'Afonso', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Afonso Ribeiro', 'seccao': 'Lobitos', 'data_nascimento': '14/10/2014'},
        {'nome': 'Artur', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Beatriz (Ana Carolina)', 'seccao': 'Lobitos', 'data_nascimento': '11/3/2015'},
        {'nome': 'Carolina', 'seccao': 'Lobitos', 'data_nascimento': '11/1/2015'},
        {'nome': 'Duarte', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Eduardo (Marques)', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Francisco (Dias)', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Francisco (Neves)', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Guilherme', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Guilherme (Oliveira)', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Henrique', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'João', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'José Maria', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Lourenço (Sara)', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Margarida (costa)', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Margarida (joao)', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Maria', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Maria Couto', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Martim', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Rodrigo', 'seccao': 'Lobitos', 'data_nascimento': '11/7/2015'},
        {'nome': 'Tomás', 'seccao': 'Lobitos', 'data_nascimento': '26/1/2015'},
        {'nome': 'Xavier', 'seccao': 'Lobitos', 'data_nascimento': '29/7/2015'},
        
        # Pioneiros (Verde)
        {'nome': 'Afonso', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Ana', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'Beatriz', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'Benedita', 'seccao': 'Pioneiros', 'data_nascimento': '20/3/2009'},
        {'nome': 'Catarina', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'Diogo (Pedro)', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Duarte', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'Eduardo', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Filipe', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Francisco', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Gonçalo Rodrigues', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Guilherme', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Inês', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'João', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'João Matos', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'João Paulo', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'José', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Lourenço', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Mafalda', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'Manuel', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Margarida', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'Maria', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'Maria (Sara)', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'Maria Constança', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'Maria Francisca', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'Matilde', 'seccao': 'Pioneiros', 'data_nascimento': '29/3/2010'},
        {'nome': 'Miguel', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Pedro', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Rafael', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Rodrigo', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Rui', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Salvador', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Santiago', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Tomás', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        {'nome': 'Vicente', 'seccao': 'Pioneiros', 'data_nascimento': '12/1/2010'},
        
        # Caminheiros (Vermelho)
        {'nome': 'Afonso', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
        {'nome': 'Beatriz', 'seccao': 'Caminheiros', 'data_nascimento': '11/7/2007'},
        {'nome': 'Bernardo', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
        {'nome': 'Carolina', 'seccao': 'Caminheiros', 'data_nascimento': '11/7/2007'},
        {'nome': 'Diogo', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
        {'nome': 'Francisco', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
        {'nome': 'Gonçalo', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
        {'nome': 'João', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
        {'nome': 'Lourenço', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
        {'nome': 'Mariana', 'seccao': 'Caminheiros', 'data_nascimento': '11/7/2007'},
        {'nome': 'Matilde', 'seccao': 'Caminheiros', 'data_nascimento': '11/7/2007'},
        {'nome': 'Miguel', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
        {'nome': 'Pedro', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
        {'nome': 'Rafael', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
        {'nome': 'Rodrigo', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
        {'nome': 'Tiago', 'seccao': 'Caminheiros', 'data_nascimento': '30/3/2007'},
    ]
    
    # 1. Criar campanha Natal 2025
    print("📅 Criando campanha Natal 2025...")
    try:
        campanha_response = supabase.table('campanhas').insert({
            'nome': 'Natal 2025',
            'descricao': 'Campanha de rifas de Natal 2025',
            'data_inicio': '2025-11-01',
            'data_fim': '2025-12-31',
            'ativa': True
        }).execute()
        
        campanha_id = campanha_response.data[0]['id']
        print(f"   ✅ Campanha criada (ID: {campanha_id})")
    except Exception as e:
        print(f"   ❌ Erro ao criar campanha: {e}")
        return
    
    # 2. Criar escuteiros
    print()
    print(f"👥 Criando {len(escuteiros_data)} escuteiros...")
    escuteiros_criados = 0
    escuteiros_map = {}  # nome -> id
    
    for esc in escuteiros_data:
        try:
            esc_response = supabase.table('escuteiros').insert({
                'nome': esc['nome'],
                'ativo': True
            }).execute()
            
            escuteiro_id = esc_response.data[0]['id']
            escuteiros_map[esc['nome']] = escuteiro_id
            escuteiros_criados += 1
            
        except Exception as e:
            print(f"   ❌ Erro ao criar {esc['nome']}: {e}")
    
    print(f"   ✅ {escuteiros_criados} escuteiros criados")
    
    # 3. Criar blocos de rifas (99 blocos de 10 rifas cada)
    print()
    print("🎟️  Criando 99 blocos de rifas...")
    
    # Ranges por secção
    seccao_ranges = {
        'Exploradores': (421, 990),  # 57 blocos
        'Lobitos': (181, 420),       # 24 blocos  
        'Pioneiros': (311, 420),     # 11 blocos (overlap com Lobitos nas últimas)
        'Caminheiros': (1, 100),     # 10 blocos
    }
    
    blocos_criados = 0
    
    # Criar blocos sem atribuir a escuteiros
    for i in range(1, 100):  # 99 blocos
        rifa_inicio = (i - 1) * 10 + 1
        rifa_fim = i * 10
        
        # Determinar secção baseada no range
        seccao = None
        for sec, (start, end) in seccao_ranges.items():
            if rifa_inicio >= start and rifa_inicio <= end:
                seccao = sec
                break
        
        if not seccao:
            seccao = 'Exploradores'  # Default
        
        try:
            supabase.table('blocos_rifas').insert({
                'campanha_id': campanha_id,
                'nome': f'Bloco {i}',
                'numero_inicial': rifa_inicio,
                'numero_final': rifa_fim,
                'preco_unitario': 1.0,
                'seccao': seccao,
                'escuteiro_id': None,  # Não atribuído inicialmente
                'data_atribuicao': None,
                'estado': 'disponivel'
            }).execute()
            
            blocos_criados += 1
            
        except Exception as e:
            print(f"   ❌ Erro ao criar bloco {i}: {e}")
    
    print(f"   ✅ {blocos_criados} blocos criados")
    
    # Resumo final
    print()
    print("=" * 70)
    print("✅ IMPORTAÇÃO CONCLUÍDA")
    print("=" * 70)
    print(f"  📅 Campanha: Natal 2025")
    print(f"  👥 Escuteiros: {escuteiros_criados}")
    print(f"  🎟️  Blocos: {blocos_criados}")
    print(f"  🎫 Total de rifas: {blocos_criados * 10}")
    print("=" * 70)

if __name__ == "__main__":
    importar_dados()
