#!/usr/bin/env bash
# Script para restaurar (reverter) o commit que criou pages/6_💵_Controle_Escuteiros.py
# Uso: bash scripts/restore_page6.sh
# Teste em branch e faça backup antes.

set -euo pipefail

BRANCH="restore-page6-from-create-commit"
FILEPATH="pages/6_💵_Controle_Escuteiros.py"

echo "1) Criando branch de trabalho: $BRANCH"
git checkout -b "$BRANCH"

echo "2) Comitando alterações locais (se existirem)"
if git diff --quiet --; then
  echo "   Sem alterações locais a commitar."
else
  git add -A
  git commit -m "chore: preserve workspace changes before restoring page6" || true
fi

echo "3) Procurando commit que adicionou $FILEPATH"
CREATOR=$(git log --diff-filter=A --follow --pretty=format:"%H %ad %an %s" --date=short -- "$FILEPATH" | head -n 1 || true)
if [ -z "$CREATOR" ]; then
  echo "Não foi encontrado commit de adição com --diff-filter=A. Listando commits que tocaram o ficheiro:" 
  git log --oneline --follow -- "$FILEPATH" || true
  exit 0
fi

echo "Commit encontrado:"
echo "$CREATOR"
SHA=$(echo "$CREATOR" | awk '{print $1}')

echo "Mostrando resumo do commit $SHA"
git show --stat --pretty=fuller $SHA | sed -n '1,200p'

read -p "Deseja reverter este commit? (y/N): " yn
yn=${yn:-N}
if [ "$yn" != "y" ]; then
  echo "Abortando sem reverter."
  exit 0
fi

echo "Executando git revert $SHA ..."
if git revert "$SHA" --no-edit; then
  echo "Revert concluído com sucesso."
  git status --short
  echo "Commit de revert criado. Faça push da branch e abra PR para revisão."
else
  echo "Revert encontrou conflitos. Verifique git status, resolva conflitos e depois execute: git revert --continue" >&2
  git status
  exit 1
fi

echo "Fim do script."
