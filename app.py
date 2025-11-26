import streamlit as st

from src.dashboard import render_dashboard


st.set_page_config(page_title="Gestão de Rifas - Escuteiros", page_icon="🎫", layout="wide")


# Delegate rendering to the centralized dashboard renderer
render_dashboard(show_instructions=True)
