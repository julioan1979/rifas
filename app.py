import streamlit as st


st.set_page_config(page_title="App Temporariamente Desativado", page_icon="⚠️", layout="centered")


st.title("🛠️ App Temporariamente Desativado")

st.info(
	"O aplicativo principal foi desativado temporariamente para manutenção/depuração.\n"
	"Se precisar reativá-lo, restaure `app.py` a partir do backup `app.py.bak` ou consulte o histórico do Git."
)

st.caption("Branch: resource_V1.0.3 — página principal desativada por segurança")

# Stop further rendering to avoid executing dashboard code while troubleshooting
st.stop()
