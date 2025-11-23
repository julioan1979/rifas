"""
Análise das secções REAIS do Excel para corrigir importação
Baseado na análise visual do ficheiro Excel fornecido
"""

# SECÇÕES CORRETAS DO EXCEL (observação visual):
secções_reais = {
    # Reserva: 1-180 (azul escuro no Excel)
    "Reserva": {
        "inicio": 1,
        "fim": 180,
        "cor": "azul escuro"
    },
    
    # Lobitos: 181-310 (amarelo no Excel)
    "Lobitos": {
        "inicio": 181,
        "fim": 310,
        "cor": "amarelo",
        "escuteiros_visiveis": [
            "Letícia Granjo", "Simão Gaspar", "Leonita", "Leonardo",
            "Doroteia/Tomas", "Pedro/André", "Bernardo Silva",
            "Miguel Rocha", "Rodrigo Semedo", "Maria Clara",
            "Matilde Cunha", "Sofia Nunes", "Mateus"
        ]
    },
    
    # Pioneiros: 311-420 (vermelho no Excel) 
    "Pioneiros": {
        "inicio": 311,
        "fim": 420,
        "cor": "vermelho",
        "escuteiros_visiveis": [
            "Pedro Vila Pouca", "Gustavo", "Helena", 
            "Henrique Bernardes", "Camylline Andeia", "Íxera Andeia",
            "Juliana Silva", "Sara Leite", "Inês Pereira",
            "Júlio (Pioneiro)", "Beatriz Rocha + Gabriel Rocha"
        ]
    },
    
    # Exploradores: 421-990 (verde no Excel)
    "Exploradores": {
        "inicio": 421,
        "fim": 990,
        "cor": "verde",
        "nota": "Maior secção, inclui a maioria dos escuteiros"
    }
}

print("📊 SECÇÕES CORRETAS BASEADAS NO EXCEL:")
print("=" * 60)
for seccao, dados in secções_reais.items():
    print(f"\n{seccao}: {dados['inicio']}-{dados['fim']}")
    print(f"  Cor no Excel: {dados['cor']}")
    total_rifas = dados['fim'] - dados['inicio'] + 1
    print(f"  Total rifas: {total_rifas}")
    if 'escuteiros_visiveis' in dados:
        print(f"  Escuteiros: {len(dados['escuteiros_visiveis'])}")
