python import_vendas_pagamentos.py"""
Script para importar dados da campanha Natal2025 para Supabase
Execute: python import_data.py
"""

from utils.supabase_client import get_supabase_client
from datetime import datetime

# Inicializar cliente Supabase
supabase = get_supabase_client()

print("🚀 Iniciando importação de dados da campanha Natal2025...")

# ============================================
# DADOS EXTRAÍDOS DA IMAGEM
# ============================================

# Mapeamento: Secção -> Nome do Escuteiro -> Blocos
dados_campanha = {
    # Reserva (1-170)
    "Reserva": {
        "blocos": [(1, 10), (11, 20), (21, 30), (31, 40), (41, 50), (51, 60), (61, 70), (71, 80), (81, 90), (91, 100), (101, 110), (111, 120), (121, 130), (131, 140), (141, 150), (151, 160), (161, 170), (171, 180)]
    },
    
    # Lobitos (181-420)
    "Lobitos": [
        {"nome": "Le'a Granja", "data_entrega": "15/11/2025", "blocos": [(181, 190)]},
        {"nome": "Duarte Silva", "data_entrega": "15/11/2025", "blocos": [(191, 200)]},
        {"nome": "Leonor", "data_entrega": "15/11/2025", "blocos": [(201, 210)]},
        {"nome": "Júlio (Pioneiro)", "data_entrega": "15/11/2025", "blocos": [(211, 220)]},
        {"nome": "Leonardo", "data_entrega": "15/11/2025", "blocos": [(221, 230)]},
        {"nome": "Benedita Nuno Gil Teresa Cunha (pais)", "data_entrega": "15/11/2025", "blocos": [(231, 240)]},
        {"nome": "Pedro Monteiro + André Monteiro (pai)", "data_entrega": "15/11/2025", "blocos": [(241, 250)]},
        {"nome": "Vasco Ribeiro", "data_entrega": "15/11/2025", "blocos": [(251, 260)]},
        {"nome": "Miguel Rocha + Margarida (mãe)", "data_entrega": "15/11/2025", "blocos": [(261, 270)]},
        {"nome": "Rodrigo Barreto + Rodrigo Barreto (pai)", "data_entrega": "15/11/2025", "blocos": [(271, 280)]},
        {"nome": "Maria Clara", "data_entrega": "15/11/2025", "blocos": [(281, 290)]},
        {"nome": "Gonçalo Cunha", "data_entrega": "15/11/2025", "blocos": [(291, 300)]},
        {"nome": "Teresa Longa", "data_entrega": "15/11/2025", "blocos": [(301, 310)]},
        {"nome": "Mateus", "data_entrega": "15/11/2025", "blocos": [(311, 320)]},
        {"nome": "Rodrigo", "data_entrega": "18/11/2025", "blocos": [(321, 330)]},
        {"nome": "Duarte", "data_entrega": "18/11/2025", "blocos": [(331, 340)]},
        {"nome": "Beatriz", "data_entrega": "18/11/2025", "blocos": [(341, 350)]},
        {"nome": "Rodrigo Ribeiro", "data_entrega": "19/11/2025", "blocos": [(351, 360)]},
        {"nome": "Afonso Silva", "data_entrega": "19/11/2025", "blocos": [(361, 370)]},
        {"nome": "Rodrigo Ribeiro", "data_entrega": "19/11/2025", "blocos": [(371, 380), (391, 400), (411, 420)]},
    ],
    
    # Exploradores (421-830)
    "Exploradores": [
        {"nome": "Afonso Silva", "blocos": [(421, 430)]},
        {"nome": "Henriette Sousa", "blocos": [(431, 440)]},
        {"nome": "Beatriz Rocha + Gabriel Rocha (Lobito)", "data_entrega": "19/11/2025", "data_recepcao": "19/11/2025", "valor": 10, "rifas": 0, "blocos": [(451, 460), (461, 470)]},
        {"nome": "Rodrigo Ribeiro", "blocos": [(471, 480)]},
        {"nome": "Francisco Carmo + Rodrigo Barreto (exploradores)", "blocos": [(481, 490)]},
        {"nome": "Gabriel Cunha + Gustavo Cunha (Exploradores)", "blocos": [(491, 500)]},
        {"nome": "Inês Pereira + Rita (mal sabe no inicio)", "blocos": [(501, 510)]},
        {"nome": "João Dias", "blocos": [(511, 520)]},
        {"nome": "José Maria", "blocos": [(521, 530)]},
        {"nome": "Joana Oliveira", "blocos": [(531, 540)]},
        {"nome": "Luis Monteiro + Maria Monteiro (exploradora)", "blocos": [(541, 550)]},
        {"nome": "Luisa Duarte", "blocos": [(551, 560)]},
        {"nome": "Maria Branco + Mariano Branco (explorador)", "blocos": [(561, 570)]},
        {"nome": "Noa Vicente", "data_entrega": "19/11/2025", "blocos": [(571, 580)]},
        {"nome": "Maria Francisca E Rodrigo Barreto (explorador)", "blocos": [(581, 590)]},
        {"nome": "Maria Luisa Elhe", "blocos": [(591, 600)]},
        {"nome": "Maria Rita Moreira", "blocos": [(601, 610)]},
        {"nome": "Rodrigo Silva + Tiago Teixeira (explorador)", "blocos": [(611, 620)]},
        {"nome": "João Maes", "blocos": [(621, 630)]},
        {"nome": "Pedro Pereira", "blocos": [(631, 640)]},
        {"nome": "Joao Reves", "blocos": [(641, 650)]},
        {"nome": "Vitoria Costa", "blocos": [(651, 660)]},
        {"nome": "Francisco João", "blocos": [(661, 670)]},
        {"nome": "Gabriel Kenji Yamanaka Quines", "data_entrega": "19/11/2025", "blocos": [(671, 680)]},
        {"nome": "Vasco Natividade de Silva", "data_entrega": "19/11/2025", "blocos": [(681, 690)]},
        {"nome": "Diogo Santos Mesquita Moreira (Pioneira)", "blocos": [(691, 700)]},
        {"nome": "Ursula Araujo Assumpcao", "blocos": [(701, 710)]},
        {"nome": "Samuel Macedo de Silva Pereira", "blocos": [(711, 720)]},
        {"nome": "Pedro Almeida Oliveira", "blocos": [(721, 730)]},
        {"nome": "Manuel Duarte Magalhaes", "blocos": [(731, 740)]},
        {"nome": "Bernardo Ferreira Coelho Moroni", "data_entrega": "19/11/2025", "blocos": [(741, 750)]},
        {"nome": "Rodrigo Ribeiro", "data_entrega": "19/11/2025", "data_recepcao": "19/11/2025", "valor": 10, "rifas": 0, "blocos": [(751, 760)]},
        {"nome": "Júlia Almeida Quintino", "blocos": [(761, 770)]},
        {"nome": "Guilherme Miguel Francisco Silveira (Pioneiro)", "blocos": [(771, 780)]},
        {"nome": "Luís Gil Homens Maximiano", "blocos": [(781, 790)]},
        {"nome": "Helena Tavares Mukai (Pioneira)", "data_entrega": "19/11/2025", "blocos": [(791, 800)]},
        {"nome": "Sérgio Valente", "data_entrega": "19/11/2025", "blocos": [(801, 810)]},
        {"nome": "Rita Tavares", "data_entrega": "17/11/2025", "blocos": [(811, 820)]},
        {"nome": "Marcos Silva Sousa", "blocos": [(821, 830)]},
    ],
    
    # Pioneiros (831-930)
    "Pioneiros": [
        {"nome": "Maria Mariana 72 Ioana Castilho (Pioneira)", "blocos": [(831, 840)]},
        {"nome": "Constança Andrés Seabra Fonsa", "blocos": [(841, 850)]},
        {"nome": "Leonor Ramos dos Santos", "blocos": [(851, 860)]},
        {"nome": "Francisco Oliveira Filipe Oliveira", "blocos": [(861, 870)]},
        {"nome": "José Pedro Amaral Saraiva Marinho Lage", "blocos": [(871, 880)]},
        {"nome": "Matilde Guedes Rodrigues", "blocos": [(881, 890)]},
        {"nome": "M Bia Moreno Barbosa", "blocos": [(891, 900)]},
        {"nome": "Maria Leonor", "blocos": [(901, 910)]},
        {"nome": "Inês Ramos", "blocos": [(911, 920)]},
        {"nome": "André Silva", "blocos": [(921, 930)]},
    ],
    
    # Caminheiros (931-990)
    "Caminheiros": [
        {"nome": "Pedro Marques", "blocos": [(931, 940)]},
        {"nome": "Rodrigo Ribeiro", "data_entrega": "18/11/2025", "data_recepcao": "18/11/2025", "valor": 10, "rifas": 0, "blocos": [(941, 950)]},
        {"nome": "Tiago Teixeira", "blocos": [(951, 960)]},
        {"nome": "Constança Fonseca", "blocos": [(961, 970)]},
        {"nome": "Joao Gomes", "blocos": [(971, 980)]},
        {"nome": "Noa Vicente", "data_entrega": "18/11/2025", "blocos": [(981, 990)]},
    ]
}

print("\n📝 Importando escuteiros únicos...")

# Coletar todos os nomes únicos de escuteiros
escuteiros_map = {}

for seccao, dados in dados_campanha.items():
    if seccao == "Reserva":
        continue  # Reserva não tem nome individual
    
    if isinstance(dados, list):
        for escuteiro in dados:
            nome = escuteiro["nome"]
            if nome not in escuteiros_map:
                # Inserir escuteiro
                response = supabase.table('escuteiros').insert({
                    "nome": nome,
                    "ativo": True
                }).execute()
                
                if response.data:
                    escuteiro_id = response.data[0]['id']
                    escuteiros_map[nome] = escuteiro_id
                    print(f"  ✅ {nome} (ID: {escuteiro_id[:8]}...)")

print(f"\n✅ {len(escuteiros_map)} escuteiros importados")

print("\n📦 Importando blocos de rifas...")

# Preço unitário (assumindo 1€ por rifa)
preco_unitario = 1.00

blocos_criados = 0

for seccao, dados in dados_campanha.items():
    if seccao == "Reserva":
        # Blocos de reserva (sem escuteiro atribuído)
        for inicio, fim in dados["blocos"]:
            response = supabase.table('blocos_rifas').insert({
                "nome": f"Bloco {inicio}-{fim} (Reserva)",
                "numero_inicial": inicio,
                "numero_final": fim,
                "preco_unitario": preco_unitario,
                "estado": "disponivel"
            }).execute()
            
            if response.data:
                blocos_criados += 1
                print(f"  ✅ Bloco {inicio}-{fim} (Reserva)")
    
    elif isinstance(dados, list):
        for escuteiro in dados:
            nome = escuteiro["nome"]
            escuteiro_id = escuteiros_map.get(nome)
            
            for inicio, fim in escuteiro["blocos"]:
                response = supabase.table('blocos_rifas').insert({
                    "nome": f"Bloco {inicio}-{fim} - {nome[:30]}",
                    "numero_inicial": inicio,
                    "numero_final": fim,
                    "preco_unitario": preco_unitario,
                    "escuteiro_id": escuteiro_id,
                    "estado": "atribuido",
                    "data_atribuicao": datetime.now().isoformat()
                }).execute()
                
                if response.data:
                    blocos_criados += 1
                    print(f"  ✅ Bloco {inicio}-{fim} → {nome[:40]}")

print(f"\n✅ {blocos_criados} blocos de rifas importados")

print("\n🎉 Importação concluída com sucesso!")
print("\n📊 Resumo:")
print(f"   - Escuteiros: {len(escuteiros_map)}")
print(f"   - Blocos de rifas: {blocos_criados}")
print(f"   - Total de rifas: 990")
print(f"   - Campanha: Natal2025")
