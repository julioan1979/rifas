import streamlit as st


st.set_page_config(
	page_title="Bem-vindo — Gestão de Rifas",
	page_icon="🎫",
	layout="wide",
	initial_sidebar_state="expanded",
)


st.title("🎫 Sistema de Gestão de Rifas — Introdução")

st.markdown(
	"""
	Bem-vindo ao sistema de gestão de rifas dos Escuteiros.

	Use o menu lateral para navegar entre as páginas:

	- 👥 Escuteiros
	- 🎟️ Blocos de Rifas
	- 📦 Recebimento
	- 🔄 Devoluções
	- 📅 Campanhas
	- 📊 Dashboard

	A página `📊 Dashboard` contém as métricas e gráficos por campanha.
	"""
)

st.markdown("---")

st.header("Comece aqui")
st.write(
	"Selecione uma página no menu lateral para gerir escuteiros, blocos e registar recebimentos. "
	"Se precisa de acesso à base de dados, certifique-se de que as credenciais do Supabase estão configuradas nas secrets/env vars."
)

with st.expander("🔧 Dicas de manutenção", expanded=False):
	st.write(
		"Se o Dashboard estiver a causar problemas, pode: \n"
		"1. Abrir a página `📊 Dashboard` no menu (usa a implementação central em `src/dashboard.py`).\n"
		"2. Restaurar `app.py` do backup `app.py.bak` se precisar do comportamento antigo.\n"
	)

st.caption("Branch ativo: resource_V1.0.3")
