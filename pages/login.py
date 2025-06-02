import streamlit as st
from supabase_helper import *
import uuid

# Main
st.set_page_config(page_title="Lestari Bahasa", layout="wide")

st.markdown("""
    <style>
    /* Hilangkan seluruh header (logo, GitHub, Share, Fork) */
    header {visibility: hidden !important;}
    [data-testid="stHeader"] {display: none;}

    /* Hilangkan menu titik tiga */
    #MainMenu {visibility: hidden;}
    [data-testid="collapsedControl"] {display: none;}

    /* Hilangkan footer (Made with Streamlit) */
    footer {visibility: hidden !important;}
    .st-emotion-cache-1v0mbdj {display: none !important;}
    .st-emotion-cache-164pbft {display: none !important;}
    
    /* Hilangkan semua footer */
    footer, .st-emotion-cache-1v0mbdj, .st-emotion-cache-164pbft {
        display: none !important;
        visibility: hidden !important;
    }

    /* Hilangkan elemen Fork/GitHub khusus */
    a[href*="github.com"] {display: none !important;}
    
    /* Hilangkan elemen GitHub (termasuk avatar foto) */
    a[href*="github.com"], img[src*="githubusercontent"] {
        display: none !important;
    }

    /* Ubah warna background tombol collapse sidebar ( > ) */
    button[data-testid="collapsedControl"] {
        background-color: #b0b0b0 !important;  /* abu-abu */
        color: white !important;
        border: none;
        border-radius: 0 8px 8px 0;
        padding: 8px 12px;
        margin-top: 8px;
        margin-left: -4px;
        transition: all 0.3s ease;
        box-shadow: 1px 1px 5px rgba(0,0,0,0.2);
    }

    /* Saat hover */
    button[data-testid="collapsedControl"]:hover {
        background-color: #ffc107 !important;
        color: black !important;
    }

    /* Tambahan agar ikon lebih besar */
    button[data-testid="collapsedControl"] svg {
        width: 1.2rem;
        height: 1.2rem;
    }
    .stTextArea, .stButton {
            margin-top: 0px;
        }
        div[data-testid="column"] {
            display: flex;
            align-items: center;
        }
        button[kind="primary"] {
            background-color: #25D366;  /* WhatsApp green */
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# Layout tombol login/logout di kanan atas
def render_topbar():
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.session_state.get("user"):
            st.markdown(
            f"""
            <div style='position: fixed; top: 10px; right: 20px; z-index:9999;'>
                👤 {st.session_state["email"]}<br>
                <a href="/login?logout=true" target="_self">
                    <button style="background:#ff4b4b;color:white;border:none;padding:4px 10px;border-radius:5px;">Logout</button>
                </a>
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

import requests

def get_ai_response(prompt, history):
    api_key = st.secrets["API_KEY"]
    url = "https://api.deepseek.com/v1/chat/completions"

    # Format history menjadi messages
    messages = [{"role": "system", "content": "Anda adalah asisten untuk pelajar Bahasa Sunda."}]
    for chat in history:
        messages.append({"role": "user", "content": chat["message"]})
        messages.append({"role": "assistant", "content": chat["response"]})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "deepseek-chat",  # atau deepseek-coder jika butuh reasoning lebih kuat
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        st.error(f"Gagal mengambil respons dari DeepSeek: {response.text}")
        return "⚠️ Error: Gagal menghubungi model."

    
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
                    st.switch_page("test_login.py")  # Ini yang diubah
                else:
                    st.error("Login gagal.")
            except Exception as e:
                st.error(f"Login gagal: {e}")
        if st.button("Belum punya akun? Daftar"):
            st.session_state.register_mode = True
    
# Chat UI
def chat_ui():
    st.title("💬 Lestari Bahasa")
    user = st.session_state.user
    user_id = user.id

    if "room" not in st.session_state:
        st.session_state.room = "default"

    # Room selector
    # room_option = st.selectbox("Pilih Room Chat", ["default", "new room"] + [f"room-{i}" for i in range(1, 4)])
    # st.session_state.room = room_option

    with st.sidebar:
        st.markdown("### 💬 Pilih Room Chat")
        user_id = st.session_state.user.id
        available_rooms = get_user_chat_rooms(user_id)

        # Awal: default + new room
        base_options = ["default", "new chat room"]
        room_options = base_options + [r for r in available_rooms if r not in base_options]

        # selected_room = st.selectbox("Room Chat", room_options, index=room_options.index(st.session_state.get("room", "default")))
        current_room = st.session_state.get("room", "default")
        if current_room not in room_options:
            current_room = "default"

        selected_room = st.selectbox("Room Chat", room_options, index=room_options.index(current_room))
        if selected_room != st.session_state.get("room"):
            st.session_state["room"] = selected_room
            st.rerun()

        # Kalau new chat room → beri input buat nama baru
        if selected_room == "new chat room":
            new_room_name = st.text_input("Nama Chat Room Baru", key="new_room_input")
            if st.button("Buat Room"):
                if new_room_name and new_room_name not in room_options:
                    st.session_state.room = create_chat_room(user_id, new_room_name)
                    st.rerun()

        # Tombol hapus room (kecuali default)
        elif selected_room not in ["default", "new chat room"]:
            if st.button(f"Hapus Room '{selected_room}'", key="delete_room"):
                delete_chat_room(user_id, selected_room)
                st.session_state.room = "default"
                st.rerun()

        # Simpan ke state
        if selected_room not in ["new chat room"]:
            st.session_state.room = selected_room

    history = fetch_chat_history(user_id, st.session_state.room)
    for chat in history:
        with st.chat_message("user"):
            st.markdown(chat["message"])
            col1, col2 = st.columns([1, 5])
            with col1:
                if st.button("🗑️", key=f"delete-{chat['id']}"):
                    delete_message_by_id(chat["id"])
                    st.rerun()
            with col2:
                new_text = st.text_input("Edit pesan", value=chat["message"], key=f"edit-{chat['id']}")
                if st.button("Simpan", key=f"save-edit-{chat['id']}"):
                    edit_message_by_id(chat["id"], new_text)
                    st.rerun()

        with st.chat_message("assistant"):
            st.markdown(chat["response"])

    # Input new message
    prompt = st.chat_input("Ketik pesan...")
    if prompt:
        response = get_ai_response(prompt, history)
        # insert_chat_history(user_id, st.session_state.room, prompt, response)
        supabase.table("chat_history").insert({
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "room": st.session_state.room,
            "message": prompt,
            "response": response
        }).execute()
        st.rerun()

render_topbar()

if "logout" in st.query_params:
    sign_out()
    st.session_state.clear()
    st.rerun()

if st.session_state.get("user"):
    st.switch_page("main.py")  # Redirect ke main jika sudah login
else:
    auth_flow() 
