import streamlit as st


def require_password(password: str = "5212025") -> bool:
    """
    Exibe um prompt simples de senha (input type password).

    - Guarda o estado de autenticação em `st.session_state['authenticated']`.
    - Retorna True se o utilizador estiver autenticado.

    Uso (no topo do `app.py`):
        from utils.simple_auth import require_password
        if not require_password():
            st.stop()

    NOTA: Implementação intencionalmente simples — para uso interno somente.
    """

    # Inicializar estado
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # Se já autenticado, retorna True
    if st.session_state['authenticated']:
        # Mostrar botão de logout na barra lateral
        with st.sidebar:
            if st.button('Sair'):
                st.session_state['authenticated'] = False
                st.rerun()
        return True

    # Mostrar prompt de login central
    st.markdown("## Autenticação necessária")
    pwd = st.text_input('Senha', type='password')
    if st.button('Entrar'):
        if pwd == password:
            st.session_state['authenticated'] = True
            st.rerun()
        else:
            st.error('Senha incorreta')

    # Enquanto não autenticado, retorna False
    return False
