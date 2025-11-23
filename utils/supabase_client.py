"""
Supabase client configuration with automatic environment detection
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file (for local development)
load_dotenv()

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance
    
    Automatically detects credentials from:
    1. Streamlit Cloud: st.secrets
    2. GitHub Codespaces / Local: environment variables
    
    Environment variables required:
    - SUPABASE_URL: Your Supabase project URL
    - SUPABASE_KEY: Your Supabase project API key (anon/public key)
    """
    supabase_url = None
    supabase_key = None
    
    # Try to get credentials from Streamlit secrets first (for Streamlit Cloud)
    try:
        import streamlit as st
        if hasattr(st, 'secrets') and 'supabase' in st.secrets:
            supabase_url = st.secrets["supabase"]["url"]
            supabase_key = st.secrets["supabase"]["key"]
    except (ImportError, KeyError, FileNotFoundError):
        # Streamlit not available or secrets not configured
        pass
    
    # If not found in Streamlit secrets, try environment variables
    if not supabase_url or not supabase_key:
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
    
    # Validate that we have the required credentials
    if not supabase_url or not supabase_key:
        raise ValueError(
            "❌ Credenciais do Supabase não encontradas!\n\n"
            "Por favor, configure as credenciais:\n\n"
            "📌 Para Streamlit Cloud:\n"
            "   - Adicione em 'App settings' → 'Secrets':\n"
            "   [supabase]\n"
            "   url = \"sua_url_do_supabase\"\n"
            "   key = \"sua_chave_do_supabase\"\n\n"
            "📌 Para GitHub Codespaces / Local:\n"
            "   - Configure as variáveis de ambiente:\n"
            "   export SUPABASE_URL='sua_url_do_supabase'\n"
            "   export SUPABASE_KEY='sua_chave_do_supabase'\n\n"
            "   - Ou crie um ficheiro .env na raiz do projeto:\n"
            "   SUPABASE_URL=sua_url_do_supabase\n"
            "   SUPABASE_KEY=sua_chave_do_supabase"
        )
    
    # Create and return the Supabase client
    return create_client(supabase_url, supabase_key)
