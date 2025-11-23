import streamlit as st
from utils.supabase_client import get_supabase_client

# Page configuration
st.set_page_config(
    page_title="Gestão de Rifas - Escuteiros",
    page_icon="🎫",
    layout="wide"
)

# Main title
st.title("🎫 Sistema de Gestão de Rifas dos Escuteiros")

# Initialize Supabase client
try:
    supabase = get_supabase_client()
    st.success("✅ Conectado ao Supabase com sucesso!")
except ValueError as e:
    st.error(f"❌ Erro ao conectar ao Supabase: {str(e)}")
    st.info("""
    **Configuração necessária:**
    
    1. Crie um ficheiro `.env` na raiz do projeto
    2. Adicione as seguintes variáveis:
    ```
    SUPABASE_URL=your_supabase_project_url
    SUPABASE_KEY=your_supabase_anon_key
    ```
    
    Ou configure estas variáveis no ficheiro `.streamlit/secrets.toml`
    """)
    st.stop()

# Welcome section
st.markdown("""
## Bem-vindo ao Sistema de Gestão de Rifas! 🎯

Este sistema permite gerir todos os aspectos das rifas dos escuteiros:

### 📋 Funcionalidades disponíveis:

- **👥 Escuteiros**: Gerir os escuteiros que vendem rifas
- **🎟️ Blocos de Rifas**: Criar e gerir blocos de rifas
- **💰 Vendas**: Registar vendas de rifas pelos escuteiros
- **💳 Pagamentos**: Controlar pagamentos recebidos

### 🚀 Como começar:

1. Use o menu lateral para navegar entre as páginas
2. Comece por registar os escuteiros
3. Crie blocos de rifas
4. Registe as vendas
5. Acompanhe os pagamentos

---

### 📊 Estatísticas Rápidas
""")

# Quick statistics
col1, col2, col3, col4 = st.columns(4)

try:
    # Count scouts
    response_scouts = supabase.table('escuteiros').select('id', count='exact').execute()
    total_scouts = response_scouts.count if hasattr(response_scouts, 'count') else 0
    
    # Count raffle blocks
    response_blocks = supabase.table('blocos_rifas').select('id', count='exact').execute()
    total_blocks = response_blocks.count if hasattr(response_blocks, 'count') else 0
    
    # Count sales
    response_sales = supabase.table('vendas').select('id', count='exact').execute()
    total_sales = response_sales.count if hasattr(response_sales, 'count') else 0
    
    # Count payments
    response_payments = supabase.table('pagamentos').select('id', count='exact').execute()
    total_payments = response_payments.count if hasattr(response_payments, 'count') else 0
    
    col1.metric("👥 Escuteiros", total_scouts)
    col2.metric("🎟️ Blocos de Rifas", total_blocks)
    col3.metric("💰 Vendas", total_sales)
    col4.metric("💳 Pagamentos", total_payments)
    
except Exception as e:
    st.warning(f"⚠️ Não foi possível carregar estatísticas: {str(e)}")
    st.info("Certifique-se de que as tabelas foram criadas na base de dados. Consulte `utils/database_schema.py` para o schema SQL.")

# Footer
st.markdown("---")
st.markdown("*Sistema desenvolvido para gestão de rifas dos escuteiros*")
