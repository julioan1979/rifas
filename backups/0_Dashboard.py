# Backup copy of pages/0_Dashboard.py
# Moved out of `pages/` to avoid Streamlit multiple-pages conflict.
from src.dashboard import render_dashboard


def _backup_render():
    """Backup wrapper; not executed by Streamlit as it's outside pages/"""
    render_dashboard()


# End of backup
