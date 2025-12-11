# login.py
import streamlit as st
import app_principal  # importa o arquivo da app principal
import hashlib

# DICIONÁRIO DE USUÁRIOS (exemplo simples)
# ⚠ Em produção, o ideal é NÃO deixar isso hardcoded no código.
USERS = {
    "835d6dc88b708bc646d6db82c853ef4182fabbd4a8de59c213f2b5ab3ae7d9be": "218d033a33e37ad0f4208cda5c28143aeac99bb9e234eda3c06b720134cc24c2",
    "2838901e9c6354dcbef7a8fd5134633465c67c1c353a24f2c84c65ee61f8fc10": "d0b26502e9ae93f461ee345bf11a405dcbcf82d066d5c93d49f67f91fa68e98b",
}
def SHA216(input_string):
     # Encode the string to bytes
    encoded_string = input_string.encode('utf-8')

    # Create a SHA-256 hash object and compute the hash
    sha256_hash_object = hashlib.sha256(encoded_string)

    # Get the hexadecimal representation of the hash
    hex_digest = sha256_hash_object.hexdigest()
    return hex_digest

def login_screen():
    st.title("Login")

    # Campos de login
    usuario=st.text_input("Usuário")
    username = SHA216(usuario)
    password = SHA216(st.text_input("Senha", type="password"))

    # Mensagem de erro (se já tiver tentado e falhado)
    if st.session_state.get("login_failed"):
        st.error("Usuário ou senha inválidos.")

    # Botão de login
    if st.button("Entrar"):
        if username in USERS and password == USERS[username]:
            st.session_state.logged_in = True
            st.session_state.username = usuario
            st.session_state.login_failed = False
            #st.experimental_rerun()
            st.rerun()
        else:
            st.session_state.logged_in = False
            st.session_state.login_failed = True

def main():
    # Verifica se já está logado
    if not st.session_state.get("logged_in"):
        login_screen()
        # Impede que o resto do código rode enquanto não logar
        st.stop()
    else:
        st.sidebar.success(f"Logado como {st.session_state.username}")
        app_principal.main()

if __name__ == "__main__":
    main()