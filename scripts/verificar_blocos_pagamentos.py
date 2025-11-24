#!/usr/bin/env python3
"""
Script para verificar status de blocos e pagamentos
"""

import sys
sys.path.append('/workspaces/rifas')

from utils.supabase_client import get_supabase_client

def verificar_blocos():
    supabase = get_supabase_client()
    
    print("=" * 80)
    print("ANÁLISE DE BLOCOS E PAGAMENTOS")
    print("=" * 80)
    
    # Get all blocks with sales
    blocos_response = supabase.table('blocos_rifas').select(
        '*, escuteiros(nome), vendas(id, quantidade, valor_total), campanhas(nome)'
    ).execute()
    
    # Get all payments
    payments_response = supabase.table('pagamentos').select(
        'venda_id, valor_pago, canhotos_entregues'
    ).execute()
    
    # Build payment map
    payments_by_venda = {}
    canhotos_by_venda = {}
    if payments_response.data:
        for payment in payments_response.data:
            venda_id = payment['venda_id']
            if venda_id not in payments_by_venda:
                payments_by_venda[venda_id] = 0
                canhotos_by_venda[venda_id] = 0
            payments_by_venda[venda_id] += float(payment['valor_pago'])
            canhotos_by_venda[venda_id] += int(payment.get('canhotos_entregues', 0) or 0)
    
    blocos_sem_vendas = 0
    blocos_com_vendas = 0
    blocos_pendentes = 0
    blocos_pagos_completo = 0
    blocos_pagos_parcial = 0
    
    print("\n📊 BLOCOS COM VENDAS:\n")
    
    for bloco in blocos_response.data:
        vendas = bloco.get('vendas', [])
        
        if not vendas or len(vendas) == 0:
            blocos_sem_vendas += 1
            continue
        
        blocos_com_vendas += 1
        
        escuteiro_nome = bloco.get('escuteiros', {}).get('nome', 'N/A') if bloco.get('escuteiros') else 'N/A'
        campanha_nome = bloco.get('campanhas', {}).get('nome', 'N/A') if bloco.get('campanhas') else 'N/A'
        bloco_info = f"Rifas {bloco['numero_inicial']}-{bloco['numero_final']}"
        
        # Calculate totals
        total_vendido = sum(float(v['valor_total']) for v in vendas)
        total_rifas_vendidas = sum(int(v['quantidade']) for v in vendas)
        
        total_pago = sum(payments_by_venda.get(v['id'], 0) for v in vendas)
        total_canhotos_entregues = sum(canhotos_by_venda.get(v['id'], 0) for v in vendas)
        
        saldo_pendente = total_vendido - total_pago
        canhotos_pendentes = total_rifas_vendidas - total_canhotos_entregues
        
        # Classify
        if saldo_pendente > 0.01:
            if total_pago > 0:
                status = "⚠️  PAGO PARCIAL"
                blocos_pagos_parcial += 1
            else:
                status = "❌ PENDENTE"
                blocos_pendentes += 1
        else:
            status = "✅ PAGO COMPLETO"
            blocos_pagos_completo += 1
        
        print(f"{status}")
        print(f"  Campanha: {campanha_nome}")
        print(f"  Escuteiro: {escuteiro_nome}")
        print(f"  Bloco: {bloco_info}")
        print(f"  Vendido: {total_vendido:.2f}€ | Pago: {total_pago:.2f}€ | Saldo: {saldo_pendente:.2f}€")
        print(f"  Rifas vendidas: {total_rifas_vendidas} | Canhotos entregues: {total_canhotos_entregues}")
        print()
    
    print("=" * 80)
    print("RESUMO:")
    print("=" * 80)
    print(f"📦 Total de blocos: {len(blocos_response.data)}")
    print(f"   ├─ Sem vendas: {blocos_sem_vendas}")
    print(f"   └─ Com vendas: {blocos_com_vendas}")
    print()
    print(f"💰 Status de pagamento:")
    print(f"   ├─ ✅ Pagos completo: {blocos_pagos_completo}")
    print(f"   ├─ ⚠️  Pagos parcial: {blocos_pagos_parcial}")
    print(f"   └─ ❌ Pendentes: {blocos_pendentes}")
    print()
    print(f"🎯 Blocos que aparecem no formulário: {blocos_pendentes + blocos_pagos_parcial}")
    print("=" * 80)

if __name__ == "__main__":
    verificar_blocos()
