from utils.simple_auth import require_password
import streamlit as st
if not require_password("5212025"):
	st.stop()

from src.dashboard import render_dashboard
render_dashboard()
