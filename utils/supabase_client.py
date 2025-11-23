"""
Supabase client configuration
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_supabase_client() -> Client:
    """
    Create and return a Supabase client instance
    
    Environment variables required:
    - SUPABASE_URL: Your Supabase project URL
    - SUPABASE_KEY: Your Supabase project API key
    """
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    
    if not url or not key:
        raise ValueError(
            "SUPABASE_URL and SUPABASE_KEY must be set in environment variables or .env file"
        )
    
    return create_client(url, key)
