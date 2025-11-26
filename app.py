import streamlit as st


st.set_page_config(
	page_title="📒 Sistema de Gestão de Rifas — Introdução",
	page_icon="🎫",
	layout="wide",
	initial_sidebar_state="expanded",
)


st.title("📒 Sistema de Gestão de Rifas — Introdução")

with st.expander("ℹ️ Sobre o Sistema", expanded=True):
	st.markdown(
		"""
		# Bem-vindo ao Sistema de Gestão de Rifas! 🎯
		Este sistema permite gerir todos os aspetos das rifas dos escuteiros de forma simples e eficiente.

		## 🗂️ **Funcionalidades disponíveis:**
		- **👥 Escuteiros**: Gerir escuteiros que vendem rifas (criar, editar, visualizar)
		- **🎟️ Blocos de Rifas**: Criar e atribuir blocos de rifas aos escuteiros
		- **📦 Recebimento**: Registar canhotos e dinheiro recebidos dos escuteiros
		- **🔄 Devoluções**: Gerir devoluções de blocos (total ou parcial)

		## 🚀 **Como funciona:**
		1. **Registar Escuteiros**: Comece por adicionar os escuteiros na página "👥 Escuteiros"
		2. **Criar Campanha**: Crie uma campanha na página "📅 Campanhas" (cria blocos automaticamente)
		3. **Criar Blocos**: Crie blocos e atribua aos escuteiros
		4. **Registar Recebimento**: Quando escuteiro entrega canhotos + dinheiro, registe na página "📦 Recebimento"
		""",
		unsafe_allow_html=True
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
