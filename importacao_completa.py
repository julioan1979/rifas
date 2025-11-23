"""
Script de importação COMPLETA - Limpa base de dados e importa todos os dados do Excel
Execute: python importacao_completa.py
"""

from utils.supabase_client import get_supabase_client
from datetime import datetime

# Inicializar cliente Supabase
supabase = get_supabase_client()

print("🗑️  LIMPANDO BASE DE DADOS...")
print("=" * 60)

# Limpar tabelas na ordem correta (devido às foreign keys)
print("Apagando devoluções...")
supabase.table('devolucoes').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

print("Apagando pagamentos...")
supabase.table('pagamentos').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

print("Apagando vendas...")
supabase.table('vendas').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

print("Apagando blocos de rifas...")
supabase.table('blocos_rifas').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

print("Apagando escuteiros...")
supabase.table('escuteiros').delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()

print("✅ Base de dados limpa!\n")

# ============================================
# CRIAR/BUSCAR CAMPANHA
# ============================================

print("📅 CONFIGURANDO CAMPANHA...")
print("=" * 60)

campanha_nome = "Natal2025"

# Verificar se campanha existe
campanha_response = supabase.table('campanhas').select('*').eq('nome', campanha_nome).execute()

if campanha_response.data:
    campanha_id = campanha_response.data[0]['id']
    print(f"  ✅ Campanha '{campanha_nome}' já existe")
else:
    # Criar campanha
    campanha_data = {
        'nome': campanha_nome,
        'descricao': 'Campanha de rifas do Natal 2025',
        'data_inicio': '2025-11-01',
        'data_fim': '2025-12-31',
        'ativa': True
    }
    
    campanha_response = supabase.table('campanhas').insert(campanha_data).execute()
    
    if campanha_response.data:
        campanha_id = campanha_response.data[0]['id']
        print(f"  ✅ Campanha '{campanha_nome}' criada")
    else:
        print("  ❌ Erro ao criar campanha")
        exit(1)

print(f"  📌 ID da campanha: {campanha_id}\n")

# ============================================
# IMPORTAR ESCUTEIROS
# ============================================

print("👥 IMPORTANDO ESCUTEIROS...")
print("=" * 60)

escuteiros_data = {
    "Lobitos": [
        "Letícia Granjo",
        "Simão Gaspar",
        "Leonita",
        "Leonardo",
        "Doroteia Nuno Cui Tomas Cunha (pais)",
        "Pedro Monteiro + André Monteiro (pais)",
        "Bernardo Silva",
        "Miguel Rocha + Margarida (esposa)",
        "Rodrigo Semedo + Rodrigo Semedo (pais)",
        "Maria Clara",
        "Matilde Cunha",
        "Sofia Nunes",
        "Beatriz Rocha + Gabriel Rocha (Lobito)",
        "Gabriel Carmo + Gustavo Cunha (Exploradores)",
        "Inês Menino + Rita (mãe não sei o apelido)",
        "Sofia Dias",
        "Luís Marques",
        "José Dias",
        "Maria Monteiro Oliveira",
        "Luis Monteiro + Maria Monteiro (apoiadores)",
        "Luísa Duarte",
        "Leonor Ramos + Mariana Barroso (exploradores)",
        "Noa Vicente",
        "Maria Francisca E Rodrigo Barroso (exploradores)",
    ],
    "Exploradores": [
        "Rodrigo Ribeiro",
        "Afonso Silva",
        "Benedita Monteiro (Polilha)",
        "Bianca Rocha",
        "Gabriel Kenji Yamashita Quartin",
        "Vasco Natividade De Silva",
        "Alice Silva",
        "Úrsula Araújo Assumpcao",
        "Tiago Macedo de Silva Pereira",
        "Pedro Almeida Oliveira",
        "Xavier Duarte Magalhaes",
        "Gustavo Ribeiro Nanni",
        "Rodrigo Ribeiro",
        "Leonor Almeida Quintino",
        "Guilherme Miguel Francisco Silveira (Pioneiro)",
        "Ines Joel de Ramos Marianno",
        "Maria Rita Miguel Esteves (Pioneiro)",
        "Sérgio Valente",
        "Rui Tavares",
        "Marco Silva Sousa",
        "Maria Marlieiro De Sousa Caetilho (Pioneira)",
        "Martim da Silveira Sousa",
        "Leonor Ramos dos Santos",
        "Francisco Oliveira",
        "Tiago Alexandre Borges Martinho Leite",
        "Mafalda Quadros Rodrigues",
        "M Inês Moreno Barbosa",
        "Tiago Teixeira",
        "Domitinies Febias",
        "Simão Araújo",
        "Noa Vicente",
        "Serena Valente",
    ],
    "Pioneiros": [
        "Júlio (Pioneiro)",
        "Mateus",
        "Pedro Vila Pouca",
        "Gustavo",
        "Helena",
        "Henrique Bernardes",
        "Camylline Andeia",
        "Íxera Andeia",
        "Juliana Silva",
        "Sara Leite",
        "Inês Pereira",
        "Rodrigo Ribeiro",
    ],
    "Caminheiros": [
        "Noa Vicente",
        "Rodrigo Ribeiro",
    ],
}

escuteiros_criados = {}

for seccao, nomes in escuteiros_data.items():
    for nome in nomes:
        # Verificar se já existe para evitar duplicados
        existing = supabase.table('escuteiros').select('id').eq('nome', nome).execute()
        
        if existing.data:
            escuteiro_id = existing.data[0]['id']
            escuteiros_criados[nome] = escuteiro_id
            print(f"  ⚠️ Já existe: {nome}")
        else:
            escuteiro_data = {
                "nome": nome,
                "email": None,
                "telefone": None,
                "ativo": True
            }
            
            response = supabase.table('escuteiros').insert(escuteiro_data).execute()
            
            if response.data:
                escuteiro_id = response.data[0]['id']
                escuteiros_criados[nome] = escuteiro_id
                print(f"  ✅ {nome}")

print(f"\n✅ {len(escuteiros_criados)} escuteiros importados!\n")

# ============================================
# IMPORTAR BLOCOS DE RIFAS
# ============================================

print("🎟️  IMPORTANDO BLOCOS DE RIFAS...")
print("=" * 60)

blocos_data = {
    # Reserva: 1-180 (sem escuteiro)
    "Reserva": {
        "escuteiros": [None] * 18,
        "ranges": [(i, i+9) for i in range(1, 180, 10)]
    },
    
    # Lobitos: 181-420
    "Lobitos": {
        "escuteiros": [
            "Letícia Granjo", None, "Simão Gaspar", "Leonita", "Leonardo",
            "Doroteia Nuno Cui Tomas Cunha (pais)", "Pedro Monteiro + André Monteiro (pais)",
            "Bernardo Silva", "Miguel Rocha + Margarida (esposa)", "Rodrigo Semedo + Rodrigo Semedo (pais)",
            "Maria Clara", "Matilde Cunha", "Sofia Nunes", None, None,
            None, "Rodrigo Ribeiro", "Rodrigo Ribeiro", "Rodrigo Ribeiro", None,
            None, None, None, "Beatriz Rocha + Gabriel Rocha (Lobito)",
        ],
        "ranges": [
            (181, 190), (191, 200), (201, 210), (211, 220), (221, 230),
            (231, 240), (241, 250), (251, 260), (261, 270), (271, 280),
            (281, 290), (291, 300), (301, 310), (311, 320), (321, 330),
            (331, 340), (341, 350), (351, 360), (361, 370), (371, 380),
            (381, 390), (391, 400), (401, 410), (411, 420),
        ]
    },
    
    # Exploradores: 421-830
    "Exploradores": {
        "escuteiros": [
            "Rodrigo Ribeiro", "Afonso Silva", 
            "Benedita Monteiro (Polilha)", "Bianca Rocha", None,
            "Gabriel Kenji Yamashita Quartin", "Vasco Natividade De Silva",
            "Alice Silva", "Úrsula Araújo Assumpcao",
            "Tiago Macedo de Silva Pereira", "Pedro Almeida Oliveira",
            "Xavier Duarte Magalhaes", "Gustavo Ribeiro Nanni",
            "Rodrigo Ribeiro", "Rodrigo Ribeiro", "Leonor Almeida Quintino",
            "Guilherme Miguel Francisco Silveira (Pioneiro)", 
            "Ines Joel de Ramos Marianno", "Maria Rita Miguel Esteves (Pioneiro)",
            "Sérgio Valente", "Rui Tavares", "Marco Silva Sousa",
            "Maria Marlieiro De Sousa Caetilho (Pioneira)", 
            "Martim da Silveira Sousa", "Leonor Ramos dos Santos",
            "Francisco Oliveira", 
            "Tiago Alexandre Borges Martinho Leite", "Mafalda Quadros Rodrigues",
            "M Inês Moreno Barbosa", None, None, None, None, None, None, None,
            "Tiago Teixeira", "Domitinies Febias", "Simão Araújo", 
            "Noa Vicente", "Serena Valente",
        ],
        "ranges": [(i, i+9) for i in range(421, 830, 10)]
    },
    
    # Pioneiros: 831-930
    "Pioneiros": {
        "escuteiros": [
            "Júlio (Pioneiro)", "Mateus", "Pedro Vila Pouca", "Gustavo",
            "Helena", "Henrique Bernardes", "Camylline Andeia", "Íxera Andeia",
            "Juliana Silva", "Rodrigo Ribeiro",
        ],
        "ranges": [(i, i+9) for i in range(831, 930, 10)]
    },
    
    # Caminheiros: 931-990
    "Caminheiros": {
        "escuteiros": [
            "Noa Vicente", None, None, "Rodrigo Ribeiro", None, None
        ],
        "ranges": [(i, i+9) for i in range(931, 990, 10)]
    },
}

blocos_criados = {}
campanha = "Natal2025"

for seccao, data in blocos_data.items():
    escuteiros_list = data["escuteiros"]
    ranges_list = data["ranges"]
    
    for idx, (inicio, fim) in enumerate(ranges_list):
        if idx < len(escuteiros_list):
            nome_escuteiro = escuteiros_list[idx]
            escuteiro_id = escuteiros_criados.get(nome_escuteiro) if nome_escuteiro else None
        else:
            escuteiro_id = None
        
        bloco_data = {
            "campanha_id": campanha_id,
            "nome": f"Bloco {inicio}-{fim} ({seccao})" if escuteiro_id is None else f"Bloco {inicio}-{fim} ({nome_escuteiro[:20]}...)",
            "numero_inicial": inicio,
            "numero_final": fim,
            "preco_unitario": 1.0,
            "escuteiro_id": escuteiro_id,
            "estado": "disponivel",
            "seccao": seccao
        }
        
        response = supabase.table('blocos_rifas').insert(bloco_data).execute()
        
        if response.data:
            bloco_id = response.data[0]['id']
            blocos_criados[(inicio, fim)] = bloco_id
            status = "✅" if escuteiro_id else "📦"
            print(f"  {status} Bloco {inicio}-{fim} - {seccao}" + (f" ({nome_escuteiro[:30]})" if nome_escuteiro else ""))

print(f"\n✅ {len(blocos_criados)} blocos importados!\n")

# ============================================
# IMPORTAR VENDAS E PAGAMENTOS
# ============================================

print("💰 IMPORTANDO VENDAS E PAGAMENTOS...")
print("=" * 60)

transacoes = [
    # Lobitos
    {"nome": "Beatriz Rocha + Gabriel Rocha (Lobito)", "blocos": [(451, 460), (461, 470)], 
     "data": "19/11/2025", "pago": 10.0, "devolvidas": 0},
    {"nome": "Rodrigo Ribeiro", "blocos": [(371, 380), (391, 400), (411, 420)], 
     "data": "19/11/2025", "pago": 10.0, "devolvidas": 0},
    
    # Exploradores
    {"nome": "Rodrigo Ribeiro", "blocos": [(741, 750), (751, 760)], 
     "data": "19/11/2025", "pago": 10.0, "devolvidas": 0},
    {"nome": "Sérgio Valente", "blocos": [(791, 800)], 
     "data": "19/11/2025", "pago": 0.0, "devolvidas": 0},
    
    # Caminheiros
    {"nome": "Rodrigo Ribeiro", "blocos": [(941, 950)], 
     "data": "18/11/2025", "pago": 10.0, "devolvidas": 0},
    {"nome": "Noa Vicente", "blocos": [(971, 980)], 
     "data": "18/11/2025", "pago": 0.0, "devolvidas": 0},
]

vendas_count = 0
pagamentos_count = 0

for trans in transacoes:
    nome = trans["nome"]
    escuteiro_id = escuteiros_criados.get(nome)
    
    if not escuteiro_id:
        print(f"  ⚠️ Escuteiro não encontrado: {nome}")
        continue
    
    for bloco_range in trans["blocos"]:
        bloco_id = blocos_criados.get(bloco_range)
        
        if not bloco_id:
            print(f"  ⚠️ Bloco não encontrado: {bloco_range}")
            continue
        
        quantidade = bloco_range[1] - bloco_range[0] + 1 - trans["devolvidas"]
        
        if quantidade > 0:
            valor_total = quantidade * 1.0
            
            venda_data = {
                "escuteiro_id": escuteiro_id,
                "bloco_id": bloco_id,
                "quantidade": quantidade,
                "valor_total": valor_total,
                "data_venda": datetime.strptime(trans["data"], '%d/%m/%Y').isoformat(),
                "observacoes": "Importado do Excel"
            }
            
            venda_response = supabase.table('vendas').insert(venda_data).execute()
            
            if venda_response.data:
                venda_id = venda_response.data[0]['id']
                vendas_count += 1
                print(f"  ✅ Venda: {nome[:30]} - Bloco {bloco_range[0]}-{bloco_range[1]}")
                
                # Atualizar estado do bloco
                supabase.table('blocos_rifas').update({'estado': 'vendido'}).eq('id', bloco_id).execute()
                
                # Criar pagamento se houver
                if trans["pago"] > 0:
                    pagamento_data = {
                        "venda_id": venda_id,
                        "valor_pago": trans["pago"],
                        "data_pagamento": datetime.strptime(trans["data"], '%d/%m/%Y').isoformat(),
                        "metodo_pagamento": "Dinheiro",
                        "observacoes": "Importado do Excel"
                    }
                    
                    supabase.table('pagamentos').insert(pagamento_data).execute()
                    pagamentos_count += 1
                    print(f"    💳 Pagamento: {trans['pago']:.2f} €")
        
        # Devoluções
        if trans["devolvidas"] > 0:
            devolucao_data = {
                "escuteiro_id": escuteiro_id,
                "bloco_id": bloco_id,
                "quantidade": trans["devolvidas"],
                "motivo": "Rifas não vendidas",
                "data_devolucao": datetime.strptime(trans["data"], '%d/%m/%Y').isoformat()
            }
            
            supabase.table('devolucoes').insert(devolucao_data).execute()
            print(f"    🔄 Devolução: {trans['devolvidas']} rifas")

print(f"\n✅ Importação concluída!")
print("=" * 60)
print(f"📊 RESUMO FINAL:")
print(f"   👥 Escuteiros: {len(escuteiros_criados)}")
print(f"   🎟️  Blocos: {len(blocos_criados)}")
print(f"   💰 Vendas: {vendas_count}")
print(f"   💳 Pagamentos: {pagamentos_count}")
print("=" * 60)
