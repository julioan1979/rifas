"""
Script para limpar completamente a base de dados do Supabase
ATENÇÃO: Este script vai DELETAR TODOS OS DADOS!
"""

from utils.supabase_client import get_supabase_client

def limpar_base_dados():
    """Limpa todas as tabelas da base de dados"""
    
    supabase = get_supabase_client()
    
    print("=" * 60)
    print("⚠️  LIMPEZA COMPLETA DA BASE DE DADOS")
    print("=" * 60)
    print()
    
    # Ordem de deleção (respeitar foreign keys)
    tabelas_ordem = [
        'devolucoes',
        'pagamentos',
        'vendas',
        'blocos_rifas',
        'escuteiros',
        'campanhas'
    ]
    
    resultados = {}
    
    for tabela in tabelas_ordem:
        try:
            print(f"🗑️  Limpando tabela: {tabela}...", end=" ")
            
            # Get count before delete
            response_count = supabase.table(tabela).select('id', count='exact').execute()
            count_antes = response_count.count if hasattr(response_count, 'count') else len(response_count.data) if response_count.data else 0
            
            # Delete all records
            # Supabase requires a filter, so we use a condition that matches all
            response = supabase.table(tabela).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            
            resultados[tabela] = count_antes
            print(f"✅ {count_antes} registos eliminados")
            
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
            resultados[tabela] = f"ERRO: {str(e)}"
    
    print()
    print("=" * 60)
    print("📊 RESUMO DA LIMPEZA")
    print("=" * 60)
    
    for tabela, resultado in resultados.items():
        if isinstance(resultado, int):
            print(f"  {tabela:20s}: {resultado:>6} registos eliminados")
        else:
            print(f"  {tabela:20s}: {resultado}")
    
    print()
    print("✅ Limpeza concluída!")
    print("=" * 60)

if __name__ == "__main__":
    import sys
    
    print()
    resposta = input("⚠️  TEM CERTEZA que deseja LIMPAR TODA A BASE DE DADOS? (escreva 'SIM' em maiúsculas): ")
    
    if resposta == "SIM":
        limpar_base_dados()
    else:
        print("❌ Operação cancelada. Nenhum dado foi eliminado.")
        sys.exit(0)
