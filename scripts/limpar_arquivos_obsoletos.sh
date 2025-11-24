#!/bin/bash
# Script para remover arquivos obsoletos do repositório

echo "🧹 Limpando arquivos obsoletos do repositório..."
echo ""

# Arquivos obsoletos identificados:

# 1. SQL da página 6 (removida)
echo "❌ Removendo: sql_update_blocos_controle.sql (página 6 removida)"
git rm -f sql_update_blocos_controle.sql

# 2. Scripts obsoletos em scripts/
echo "❌ Removendo: scripts/consolidar_pagamentos_para_blocos.sql (não usado)"
git rm -f scripts/consolidar_pagamentos_para_blocos.sql

echo "❌ Removendo: scripts/importar_natal_2025_corrigido.py (já executado)"
git rm -f scripts/importar_natal_2025_corrigido.py

echo "❌ Removendo: scripts/limpar_base_dados.py (não usado)"
git rm -f scripts/limpar_base_dados.py

echo "❌ Removendo: scripts/restore_page6.sh (já usado)"
git rm -f scripts/restore_page6.sh

# 3. Arquivos de documentação antiga
echo "❌ Removendo: docs/MIGRATION_PAYMENTS.md (não aplicável)"
git rm -f docs/MIGRATION_PAYMENTS.md

echo "❌ Removendo: scripts/docs_archive/ (documentação obsoleta)"
git rm -rf scripts/docs_archive/

echo "❌ Removendo: scripts/sql_archive/ (SQLs antigos não usados)"
git rm -rf scripts/sql_archive/

echo ""
echo "✅ Limpeza concluída!"
echo ""
echo "📝 Arquivos mantidos (em uso):"
echo "   - scripts/setup_completo_supabase.sql (setup DB)"
echo "   - scripts/verificar_e_ajustar_supabase.py (verificação)"
echo "   - scripts/executar_limpeza_supabase.py (limpeza)"
echo "   - scripts/limpar_campos_extras_blocos.sql (limpeza)"
echo ""
echo "⚠️  Execute 'git status' para ver as alterações"
echo "⚠️  Execute 'git commit -m \"chore: Remover arquivos obsoletos\"' para commitar"
