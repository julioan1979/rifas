#!/usr/bin/env python3
"""Script para substituir o arquivo corrompido pelo arquivo limpo"""

import os
import shutil

pages_dir = "/workspaces/rifas/pages"
corrupted_file = os.path.join(pages_dir, "2_🎟️_Blocos_de_Rifas.py")
clean_file = os.path.join(pages_dir, "2_🎟️_Blocos_de_Rifas_CLEAN.py")
backup_file = os.path.join(pages_dir, "2_🎟️_Blocos_de_Rifas_CORRUPTED.py.bak")

try:
    # 1. Backup do arquivo corrompido
    print(f"1. Fazendo backup do arquivo corrompido...")
    shutil.copy2(corrupted_file, backup_file)
    print(f"   ✅ Backup criado: {backup_file}")
    
    # 2. Remover arquivo corrompido
    print(f"2. Removendo arquivo corrompido...")
    os.remove(corrupted_file)
    print(f"   ✅ Arquivo corrompido removido")
    
    # 3. Renomear arquivo limpo
    print(f"3. Renomeando arquivo limpo...")
    shutil.move(clean_file, corrupted_file)
    print(f"   ✅ Arquivo limpo renomeado para: {corrupted_file}")
    
    print("\n✨ Sucesso! O arquivo foi substituído com sucesso!")
    print(f"📁 Backup disponível em: {backup_file}")
    
except Exception as e:
    print(f"\n❌ Erro: {e}")
    exit(1)
