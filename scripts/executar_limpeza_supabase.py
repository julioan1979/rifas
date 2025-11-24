"""
Script para executar a limpeza de campos extras no Supabase via API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.supabase_client import get_supabase_client
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env.supabase
load_dotenv('.env.supabase')

def executar_limpeza():
    """Executa os comandos SQL para remover campos extras"""
    print("\n" + "="*60)
    print("🧹 LIMPANDO CAMPOS EXTRAS DE blocos_rifas")
    print("="*60 + "\n")
    
    supabase = get_supabase_client()
    
    campos_a_remover = [
        'data_pagamento',
        'valor_a_pagar',
        'observacoes_canhotos',
        'canhotos_devolvidos',
        'metodo_pagamento',
        'rifas_vendidas',
        'data_devolucao_canhotos',
        'observacoes_pagamento',
        'valor_pago'
    ]
    
    print("⚠️  ATENÇÃO: Esta operação irá remover permanentemente os seguintes campos:")
    for campo in campos_a_remover:
        print(f"   - {campo}")
    
    print("\n📋 SQL gerado:")
    print("-" * 60)
    
    sql_commands = []
    for campo in campos_a_remover:
        sql = f"ALTER TABLE blocos_rifas DROP COLUMN IF EXISTS {campo};"
        sql_commands.append(sql)
        print(sql)
    
    print("-" * 60)
    print("\n❗ IMPORTANTE:")
    print("   O Supabase Python client não suporta ALTER TABLE diretamente.")
    print("   Você precisa executar o SQL manualmente no Supabase SQL Editor.")
    print("\n📝 INSTRUÇÕES:")
    print("   1. Acesse: https://app.supabase.com/project/_/sql")
    print("   2. Copie o conteúdo do arquivo: scripts/limpar_campos_extras_blocos.sql")
    print("   3. Cole no SQL Editor e clique em 'RUN'")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        executar_limpeza()
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
