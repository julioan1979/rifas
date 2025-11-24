"""
Script para verificar e ajustar a estrutura do banco de dados no Supabase
Verifica se todas as tabelas e campos existem conforme o projeto
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.supabase_client import get_supabase_client
from dotenv import load_dotenv

# Carregar variáveis de ambiente do .env.supabase
load_dotenv('.env.supabase')

def verificar_tabelas():
    """Verifica quais tabelas existem no Supabase"""
    print("🔍 Verificando tabelas no Supabase...\n")
    
    supabase = get_supabase_client()
    
    tabelas_esperadas = [
        'campanhas',
        'escuteiros', 
        'blocos_rifas',
        'vendas',
        'pagamentos',
        'devolucoes'
    ]
    
    tabelas_existentes = {}
    
    for tabela in tabelas_esperadas:
        try:
            response = supabase.table(tabela).select('*').limit(1).execute()
            tabelas_existentes[tabela] = True
            print(f"✅ Tabela '{tabela}' existe")
        except Exception as e:
            tabelas_existentes[tabela] = False
            print(f"❌ Tabela '{tabela}' NÃO existe - Erro: {str(e)}")
    
    return tabelas_existentes

def verificar_campos_blocos_rifas():
    """Verifica se os campos necessários existem em blocos_rifas"""
    print("\n🔍 Verificando campos da tabela 'blocos_rifas'...\n")
    
    supabase = get_supabase_client()
    
    campos_esperados = [
        'id',
        'campanha_id',
        'nome',
        'numero_inicial',
        'numero_final',
        'preco_unitario',
        'escuteiro_id',
        'seccao',
        'data_atribuicao',
        'estado',
        'created_at'
    ]
    
    try:
        response = supabase.table('blocos_rifas').select('*').limit(1).execute()
        
        if response.data:
            campos_existentes = list(response.data[0].keys()) if response.data else []
            
            for campo in campos_esperados:
                if campo in campos_existentes:
                    print(f"✅ Campo '{campo}' existe")
                else:
                    print(f"❌ Campo '{campo}' NÃO existe")
            
            # Verificar campos extras não esperados
            campos_extras = set(campos_existentes) - set(campos_esperados)
            if campos_extras:
                print(f"\n⚠️  Campos extras encontrados: {', '.join(campos_extras)}")
        else:
            print("⚠️  Tabela vazia, não foi possível verificar campos")
            
    except Exception as e:
        print(f"❌ Erro ao verificar campos: {str(e)}")

def gerar_sql_ajustes():
    """Gera o SQL necessário para ajustar a estrutura"""
    print("\n" + "="*60)
    print("📝 SQL PARA AJUSTAR A ESTRUTURA DO SUPABASE")
    print("="*60 + "\n")
    
    sql_completo = """
-- Execute este SQL no Supabase SQL Editor para ajustar a estrutura

-- 1. Criar tabela campanhas (se não existir)
CREATE TABLE IF NOT EXISTS campanhas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    data_inicio DATE NOT NULL,
    data_fim DATE NOT NULL,
    ativa BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT check_datas CHECK (data_fim >= data_inicio)
);

CREATE INDEX IF NOT EXISTS idx_campanhas_ativa ON campanhas(ativa);
CREATE INDEX IF NOT EXISTS idx_campanhas_nome ON campanhas(nome);

-- 2. Adicionar campos em blocos_rifas (se não existirem)
ALTER TABLE blocos_rifas 
ADD COLUMN IF NOT EXISTS campanha_id UUID REFERENCES campanhas(id) ON DELETE CASCADE;

ALTER TABLE blocos_rifas 
ADD COLUMN IF NOT EXISTS seccao TEXT;

-- 3. Criar índices adicionais
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_campanha ON blocos_rifas(campanha_id);
CREATE INDEX IF NOT EXISTS idx_blocos_rifas_seccao ON blocos_rifas(seccao);

-- 4. Habilitar RLS para campanhas
ALTER TABLE campanhas ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Enable all for authenticated users" ON campanhas;
CREATE POLICY "Enable all for authenticated users" ON campanhas FOR ALL USING (true);

-- 5. Criar views para relatórios
CREATE OR REPLACE VIEW vw_blocos_por_campanha AS
SELECT 
    c.id as campanha_id,
    c.nome as campanha_nome,
    c.ativa as campanha_ativa,
    COUNT(b.id) as total_blocos,
    SUM(b.numero_final - b.numero_inicial + 1) as total_rifas,
    COUNT(CASE WHEN b.estado = 'atribuido' THEN 1 END) as blocos_atribuidos,
    COUNT(CASE WHEN b.estado = 'vendido' THEN 1 END) as blocos_vendidos,
    COUNT(CASE WHEN b.estado = 'disponivel' THEN 1 END) as blocos_disponiveis,
    COUNT(CASE WHEN b.estado = 'devolvido' THEN 1 END) as blocos_devolvidos
FROM campanhas c
LEFT JOIN blocos_rifas b ON c.id = b.campanha_id
GROUP BY c.id, c.nome, c.ativa;

CREATE OR REPLACE VIEW vw_vendas_por_campanha AS
SELECT 
    c.id as campanha_id,
    c.nome as campanha_nome,
    COUNT(DISTINCT v.id) as total_vendas,
    COALESCE(SUM(v.quantidade), 0) as total_rifas_vendidas,
    COALESCE(SUM(v.valor_total), 0) as valor_total_vendas,
    COALESCE(SUM(p.valor_pago), 0) as total_pago,
    COALESCE(SUM(v.valor_total) - SUM(p.valor_pago), 0) as saldo_pendente
FROM campanhas c
LEFT JOIN blocos_rifas b ON c.id = b.campanha_id
LEFT JOIN vendas v ON b.id = v.bloco_id
LEFT JOIN pagamentos p ON v.id = p.venda_id
GROUP BY c.id, c.nome;

-- Verificação
SELECT 'Ajustes aplicados com sucesso! ✅' as status;
"""
    
    print(sql_completo)
    print("\n" + "="*60)
    print("📋 INSTRUÇÕES:")
    print("="*60)
    print("1. Copie o SQL acima")
    print("2. Acesse https://app.supabase.com/project/_/sql")
    print("3. Cole o SQL no editor e clique em 'RUN'")
    print("4. Execute este script novamente para verificar")
    print("="*60 + "\n")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔧 VERIFICAÇÃO DA ESTRUTURA DO SUPABASE")
    print("="*60 + "\n")
    
    try:
        # Verificar tabelas
        tabelas = verificar_tabelas()
        
        # Verificar campos de blocos_rifas se a tabela existir
        if tabelas.get('blocos_rifas'):
            verificar_campos_blocos_rifas()
        
        # Gerar SQL de ajustes
        gerar_sql_ajustes()
        
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        print("\nVerifique se as credenciais do Supabase estão corretas no arquivo .env.supabase")
