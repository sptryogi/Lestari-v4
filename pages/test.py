import streamlit as st
from supabase_helper import *
import uuid

# Layout tombol login/logout di kanan atas
def render_topbar():
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.session_state.get("user"):
            st.markdown(
                f"""
                <div style='position: fixed; top: 10px; right: 20px; z-index:9999;'>
                    👤 {st.session_state["email"]}<br>
                    <form action="?logout" method="get">
                        <button style="background:#ff4b4b;color:white;border:none;padding:4px 10px;border-radius:5px;">Logout</button>
                    </form>
                </div>
                """, unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""
                <div style='position: fixed; top: 10px; right: 20px; z-index:9999;'>
                    <form action="?login" method="get">
                        <button style="background:#4bafff;color:white;border:none;padding:6px 10px;border-radius:5px;">Login</button>
                    </form>
                </div>
                """, unsafe_allow_html=True
            )

# Auth flow
def auth_flow():
    if "register_mode" not in st.session_state:
        st.session_state.register_mode = False

    if st.session_state.register_mode:
        st.subheader("Register")
        email = st.text_input("Email")
        age = st.number_input("Umur", min_value=5, max_value=100, step=1)
        password = st.text_input("Password", type="password")
        if st.button("Buat Akun"):
            try:
                result = sign_up_with_email(email, password, age)
                st.success("Akun berhasil dibuat. Silakan login.")
                st.session_state.register_mode = False
            except Exception as e:
                st.error(f"Gagal membuat akun: {e}")
        if st.button("Sudah punya akun? Login"):
            st.session_state.register_mode = False
    else:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            try:
                result = sign_in_with_email(email, password)
                user = result.user
                if user:
                    st.session_state.user = user
                    st.session_state.email = email
                    st.experimental_rerun()
                else:
                    st.error("Login gagal.")
            except Exception as e:
                st.error(f"Login gagal: {e}")
        if st.button("Belum punya akun? Daftar"):
            st.session_state.register_mode = True

# AI logic dummy (replace with your own model call)
def get_ai_response(prompt, history):
    return f"AI menjawab berdasarkan konteks {len(history)} pesan: {prompt[::-1]}"

# Chat UI
def chat_ui():
    st.title("💬 Lestari Bahasa")
    user = st.session_state.user
    user_id = user.id

    if "room" not in st.session_state:
        st.session_state.room = "default"

    # Room selector
    room_option = st.selectbox("Pilih Room Chat", ["default", "new room"] + [f"room-{i}" for i in range(1, 4)])
    st.session_state.room = room_option

    # Fetch chat history
    history = fetch_chat_history(user_id, st.session_state.room)
    for chat in history:
        with st.chat_message("user"):
            st.markdown(chat["message"])
        with st.chat_message("assistant"):
            st.markdown(chat["response"])

    # Input new message
    prompt = st.chat_input("Ketik pesan...")
    if prompt:
        response = get_ai_response(prompt, history)
        insert_chat_history(user_id, st.session_state.room, prompt, response)
        st.rerun()

# Main
st.set_page_config(page_title="Lestari Bahasa", layout="wide")
render_topbar()

if "logout" in st.query_params:
    sign_out()
    st.session_state.clear()
    st.rerun()

if "login" in st.query_params:
    auth_flow()
elif st.session_state.get("user"):
    chat_ui()
else:
    auth_flow()
