"""
Script para importar vendas, pagamentos e devoluções da campanha Natal2025
Execute: python import_vendas_pagamentos.py
"""

from utils.supabase_client import get_supabase_client
from datetime import datetime

# Inicializar cliente Supabase
supabase = get_supabase_client()

print("🚀 Iniciando importação de vendas, pagamentos e devoluções...")

# ============================================
# DADOS COM PAGAMENTOS E DEVOLUÇÕES DO EXCEL
# ============================================

dados_com_transacoes = [
    # Lobitos
    {
        "nome": "Beatriz Rocha + Gabriel Rocha (Lobito)",
        "blocos": [(451, 460), (461, 470)],
        "data_recepcao": "19/11/2025",
        "valor_pago": 10.0,
        "rifas_devolvidas": 0
    },
    {
        "nome": "Rodrigo Ribeiro",
        "blocos": [(371, 380), (391, 400), (411, 420)],
        "data_recepcao": "19/11/2025",
        "valor_pago": 10.0,
        "rifas_devolvidas": 0
    },
    
    # Exploradores
    {
        "nome": "Rodrigo Ribeiro",
        "blocos": [(751, 760)],
        "data_recepcao": "19/11/2025",
        "valor_pago": 10.0,
        "rifas_devolvidas": 0
    },
    {
        "nome": "Rodrigo Ribeiro",
        "blocos": [(741, 750)],
        "data_recepcao": "19/11/2025",
        "valor_pago": 10.0,
        "rifas_devolvidas": 0
    },
    {
        "nome": "Sérgio Valente",
        "blocos": [(791, 800)],
        "data_recepcao": "19/11/2025",
        "valor_pago": 0.0,
        "rifas_devolvidas": 0
    },
    
    # Caminheiros
    {
        "nome": "Rodrigo Ribeiro",
        "blocos": [(941, 950)],
        "data_recepcao": "18/11/2025",
        "valor_pago": 10.0,
        "rifas_devolvidas": 0
    },
    {
        "nome": "Noa Vicente",
        "blocos": [(971, 980)],
        "data_recepcao": "18/11/2025",
        "valor_pago": 0.0,
        "rifas_devolvidas": 0
    },
]

print("\n💰 Importando vendas e pagamentos...")

# Buscar todos os blocos e escuteiros
blocos_response = supabase.table('blocos_rifas').select('*').execute()
escuteiros_response = supabase.table('escuteiros').select('*').execute()

blocos_dict = {(b['numero_inicial'], b['numero_final']): b for b in blocos_response.data}
escuteiros_dict = {e['nome']: e for e in escuteiros_response.data}

vendas_criadas = 0
pagamentos_criados = 0
devolucoes_criadas = 0

for transacao in dados_com_transacoes:
    nome = transacao['nome']
    escuteiro = escuteiros_dict.get(nome)
    
    if not escuteiro:
        print(f"  ⚠️ Escuteiro não encontrado: {nome}")
        continue
    
    for bloco_range in transacao['blocos']:
        bloco = blocos_dict.get(bloco_range)
        
        if not bloco:
            print(f"  ⚠️ Bloco não encontrado: {bloco_range}")
            continue
        
        # Calcular quantidade de rifas no bloco
        quantidade_total = bloco['numero_final'] - bloco['numero_inicial'] + 1
        rifas_devolvidas = transacao.get('rifas_devolvidas', 0)
        quantidade_vendida = quantidade_total - rifas_devolvidas
        
        if quantidade_vendida > 0:
            # Criar venda
            valor_total = quantidade_vendida * float(bloco['preco_unitario'])
            
            venda_data = {
                "escuteiro_id": escuteiro['id'],
                "bloco_id": bloco['id'],
                "quantidade": quantidade_vendida,
                "valor_total": valor_total,
                "data_venda": datetime.strptime(transacao.get('data_recepcao', '15/11/2025'), '%d/%m/%Y').isoformat(),
                "observacoes": f"Importado do Excel - Campanha Natal2025"
            }
            
            venda_response = supabase.table('vendas').insert(venda_data).execute()
            
            if venda_response.data:
                venda_id = venda_response.data[0]['id']
                vendas_criadas += 1
                print(f"  ✅ Venda: {nome[:30]} - Bloco {bloco_range[0]}-{bloco_range[1]} ({quantidade_vendida} rifas)")
                
                # Criar pagamento se houver valor pago
                valor_pago = transacao.get('valor_pago', 0)
                if valor_pago > 0:
                    pagamento_data = {
                        "venda_id": venda_id,
                        "valor_pago": valor_pago,
                        "data_pagamento": datetime.strptime(transacao['data_recepcao'], '%d/%m/%Y').isoformat(),
                        "metodo_pagamento": "Dinheiro",
                        "observacoes": "Importado do Excel"
                    }
                    
                    pagamento_response = supabase.table('pagamentos').insert(pagamento_data).execute()
                    
                    if pagamento_response.data:
                        pagamentos_criados += 1
                        print(f"    💳 Pagamento: {valor_pago:.2f} €")
        
        # Criar devolução se houver rifas devolvidas
        if rifas_devolvidas > 0:
            devolucao_data = {
                "escuteiro_id": escuteiro['id'],
                "bloco_id": bloco['id'],
                "quantidade": rifas_devolvidas,
                "motivo": "Rifas não vendidas - devolvidas",
                "data_devolucao": datetime.strptime(transacao['data_recepcao'], '%d/%m/%Y').isoformat()
            }
            
            devolucao_response = supabase.table('devolucoes').insert(devolucao_data).execute()
            
            if devolucao_response.data:
                devolucoes_criadas += 1
                print(f"    🔄 Devolução: {rifas_devolvidas} rifas")

print(f"\n✅ Importação concluída!")
print(f"\n📊 Resumo:")
print(f"   - Vendas criadas: {vendas_criadas}")
print(f"   - Pagamentos criados: {pagamentos_criados}")
print(f"   - Devoluções criadas: {devolucoes_criadas}")

# Atualizar estado dos blocos vendidos
print(f"\n🔄 Atualizando estado dos blocos...")
for transacao in dados_com_transacoes:
    for bloco_range in transacao['blocos']:
        bloco = blocos_dict.get(bloco_range)
        if bloco:
            supabase.table('blocos_rifas').update({
                'estado': 'vendido'
            }).eq('id', bloco['id']).execute()

print("✅ Estados dos blocos atualizados!")
