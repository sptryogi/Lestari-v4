import streamlit as st
import pandas as pd
import re
import pybase64
from AI_chatbot import generate_text_deepseek, call_deepseek_api, kapitalisasi_awal_kalimat, bersihkan_superscript
from constraint1 import highlight_text, constraint_text, ubah_ke_lema, find_the_lema_pair, cari_arti_lema
import streamlit.components.v1 as components
from supabase_helper import *
import uuid

st.set_page_config(page_title="Lestari Bahasa", page_icon="🌐", layout="centered")  # atau "centered"
    
# UI Styling
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

    /* Sembunyikan logo SVG (dalam class _link_gzau3_10) */
    ._container_gzau3_1 _viewerBadge_nim44_23 {
        display: none !important;
    }

    /* Sembunyikan avatar profil pembuat aplikasi */
    ._profilePreview_gzau3_63 {
        display: none !important;
    }
    
    /* Hilangkan elemen GitHub (termasuk avatar foto) */
    a[href*="github.com"], img[src*="githubusercontent"] {
        display: none !important;
    }

    /* Target tombol collapse/expand sidebar */
    [data-testid="stSidebarCollapsedControl"] button {
        color: green !important;  /* ganti warna ikon */
        background-color: white !important;  /* opsional: latar belakang tombol */
        border-radius: 8px;
        padding: 6px;
    }

    /* Ganti warna saat hover juga */
    [data-testid="stSidebarCollapsedControl"] button:hover {
        background-color: #ccffcc !important;
        color: darkgreen !important;
    }

    /* Tambahan agar ikon lebih besar */
    button[data-testid="collapsedControl"] svg {
        width: 1.2rem;
        height: 1.2rem;
    }
    </style>
""", unsafe_allow_html=True)

def set_background_from_file(file_path):
    with open(file_path, "rb") as img_file:
        b64 = pybase64.b64encode(img_file.read()).decode()

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{b64}");
            background-attachment: fixed;
            background-size: cover;
            background-repeat: no-repeat;
            background-position: center;
            background-color: white;
            color: black;
            font-family: Arial, sans-serif;
        }}
        </style>
    """, unsafe_allow_html=True)

set_background_from_file("dataset/bg biru.jpg")

st.markdown(
    """
    <style>
    .stApp {
        background-color: white;
        background-attachment: fixed;
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        color: black;
        font-family: Arial, sans-serif;
    }
    .chat-scroll {
        max-height: 500px;
        overflow-y: auto;
        padding: 10px;
        display: flex;
        flex-direction: column;
    }

    .chat-container {
        display: flex;
        flex-direction: column;
    }

    textarea {
        text-align: justify !important;
        resize: none !important;
    }
    .chat-container-outer {
        height: calc(100vh - 180px); /* beri ruang untuk input tetap tampil */
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        padding: 10px 20px;
        border: 1px solid #444;
        border-radius: 10px;
        margin-bottom: 10px;
        background-color: #121212;
    }

    .chat-bubble-user {
        background-color: white;
        color: black;
        padding: 10px 15px;
        border-radius: 15px 15px 0 15px;
        margin: 5px 0;
        max-width: 70%;
        align-self: flex-end;
        margin-left: auto;
        font-size: 20px;
        border: 2px solid black;
        text-align: justify;
        line-height: 20px;
    }

    .chat-bubble-bot {
        background-color: white;
        color: black;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0;
        margin: 5px 0;
        max-width: 90%;
        align-self: flex-start;
        margin-right: auto;
        font-size: 18px;
        font-family: Times New Roman;
        border: 2px solid black;
        text-align: justify;
        line-height: 20px;
    }

    .fixed-input {
        position: sticky;
        bottom: 0;
        background-color: #1E1E2F;
        padding-top: 10px;
        border-top: 1px solid #444;
    }

    .stTextInput>div>div>input {
        background-color: white;
        color: black;
        border-radius: 10px;
        border: 2px solid black;
    }

    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 5px 20px;
        font-weight: bold;
    }

    .yellow-note {
        color: #ffd700;
        font-size: 0.9em;
    }

    .scroll-to-bottom {
        position: fixed;
        bottom: 80px; /* Di atas input tetap */
        right: 30px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 50%;
        padding: 10px 14px;
        font-size: 20px;
        cursor: pointer;
        z-index: 1000;
        box-shadow: 0px 0px 8px rgba(0,0,0,0.3);
        display: none;
    }

    .scroll-to-bottom.show {
        display: block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load kamus
df_kamus = pd.read_excel("dataset/data_kamus_full_14-5-25.xlsx")
df_kamus[['ARTI EKUIVALEN 1', 'ARTI 1']] = df_kamus[['ARTI EKUIVALEN 1', 'ARTI 1']].apply(lambda col: col.str.lower())
df_idiom = pd.read_excel("dataset/data_idiom (3).xlsx")

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
                    st.rerun()
                else:
                    st.error("Login gagal.")
            except Exception as e:
                st.error(f"Login gagal: {e}")
        if st.button("Belum punya akun? Daftar"):
            st.session_state.register_mode = True
    
# Chat UI
def chat_ui():
  
    user = st.session_state.user
    user_id = user.id
    # ========== Sidebar Controls ==========
    with st.sidebar:
        st.header("⚙️ Pengaturan")
    
        option = st.selectbox(
            "Pilih Fitur",
            ["Chatbot", "Terjemah Indo → Sunda", "Terjemah Sunda → Indo"],
            key="fitur_selector"
        )
    
        fitur = "chatbot"
        if option == "Chatbot":
            fitur = "chatbot"
        elif option == "Terjemah Indo → Sunda":
            fitur = "terjemahindosunda"
        else:
            fitur = "terjemahsundaindo"
    
        chat_mode = st.selectbox(
            "Pilih Mode Chat",
            ["Ngobrol", "Belajar"],
            key="chat_mode"
        )
    
        if fitur == "chatbot":
            mode_bahasa = st.selectbox(
                "🌐 Mode Bahasa",
                ["Sunda", "Indonesia", "English"],
                key="mode_selector"
            )
        else:
            mode_bahasa = None
    
        status = st.toggle("🔍 Lihat Constraint")
        
    st.markdown("<h1 style='color:white'>Lestari Bahasa</h1>", unsafe_allow_html=True)
    bahasa_list = ["Sunda", "Indonesia", "English"]
    
    bahasa_display = []
    for bhs in bahasa_list:
        if bhs == mode_bahasa:
            bahasa_display.append(f"<span style='color:#FFD700;'><b>{bhs}</b></span>")    # italic untuk bahasa aktif
        else:
            bahasa_display.append(f"<span style='color: white;'>{bhs}</span>")
    
    bahasa_str = " ".join(bahasa_display)
    
    st.markdown(
        f"<div style='text-align:left; padding-top: 8px; font-size: 20px; margin-top:0px;'>"
        f"{bahasa_str}"
        f"</div>", 
        unsafe_allow_html=True
    )
    
    # st.markdown("<span style='color:white'>Selamat datang! Silakan ajukan pertanyaan.</span>", unsafe_allow_html=True)
    st.markdown("""
    <span style='
        color: white;
        text-shadow: 
            -1px -1px 0 #00008B,
             1px -1px 0 #00008B,
            -1px  1px 0 #00008B,
             1px  1px 0 #00008B;
        font-size: 12px;
    '>
        Selamat datang! Silakan ajukan pertanyaan.
    </span>
    """, unsafe_allow_html=True)
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    # st.markdown(f"**Hasil ekuivalen:** {user_input_ekuivalen}")
    
    # ====================================
    # # Input tanpa label karena sudah ditampilkan sebelumnya
    # user_input = st.text_input(label="", key="user_input")
    
    # Inisialisasi session state jika belum ada
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    
    # Fungsi untuk mengosongkan input
    def clear_input():
        if "user_input" in st.session_state:
            st.session_state["user_input"] = ""
    
    def handle_send():
        pasangan_cag = {}
        history_for_prompt = st.session_state.chat_history[-50:]
        user_input = st.session_state.user_input
        
        # Ambil fitur dan mode_bahasa dari session_state
        option = st.session_state.get("fitur_selector", "Chatbot")
        fitur = (
            "chatbot" if option == "Chatbot" else
            "terjemahindosunda" if option == "Terjemah Indo → Sunda" else
            "terjemahsundaindo"
        )
        mode_bahasa = st.session_state.get("mode_selector", "Sunda") if fitur == "chatbot" else None
    
        # Proses hasil seperti yang kamu punya
        if fitur == "chatbot" and mode_bahasa == "Sunda":
            bot_response = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, chat_mode, history=history_for_prompt)
            # bot_response_ekuivalen, pasangan_ganti_ekuivalen = ubah_ke_lema(bot_response, df_kamus, df_idiom)
            pasangan_ganti_ekuivalen = {}
            text_constraint, kata_terdapat, kata_tidak_terdapat, pasangan_kata, pasangan_ekuivalen = highlight_text(bot_response, df_kamus, df_idiom, fitur)
            text_constraint = kapitalisasi_awal_kalimat(text_constraint)
        elif fitur == "chatbot" and (mode_bahasa == "Indonesia" or mode_bahasa == "English"):
            bot_response = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, chat_mode, history=history_for_prompt)
            text_constraint = bot_response
            pasangan_ganti_ekuivalen = {}
            pasangan_ekuivalen = {}
            pasangan_kata = {}
    
        elif option == "Terjemah Sunda → Indo":
            fitur = "terjemahsundaindo"
            bot_response2 = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, chat_mode, history=None)
            bot_response_ekuivalen, pasangan_ganti_ekuivalen = ubah_ke_lema(bot_response2, df_kamus, df_idiom)
            #bot_response_ekuivalen = ubah_ke_lema(bot_response2, df_kamus)
            #text_constraint, kata_terdapat, kata_tidak_terdapat, pasangan_kata, pasangan_ekuivalen = highlight_text(bot_response_ekuivalen, df_kamus, df_idiom, fitur)
        elif option == "Terjemah Indo → Sunda":
            fitur = "terjemahindosunda"
            bot_response2 = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, chat_mode, history=None)
            bot_response_ekuivalen, pasangan_ganti_ekuivalen = ubah_ke_lema(bot_response2, df_kamus, df_idiom)
            text_constraint, kata_terdapat, kata_tidak_terdapat, pasangan_kata, pasangan_ekuivalen = highlight_text(bot_response_ekuivalen, df_kamus, df_idiom, fitur)
            text_constraint = kapitalisasi_awal_kalimat(text_constraint)
    
        html_block = [
            # "<p style='color: yellow;'>Kata Kata yang diganti dari Indo ke Sunda (Kamus) Setelah AI:</p>",
            # f"<p style='color: yellow;'>{pasangan_ganti_ekuivalen}</p>",
            "<p style='color: yellow;'>Kata Kata yang ada di kamus tapi tidak ada Sinonim LOMA:</p>",
            f"<p style='color: yellow;'>{pasangan_ekuivalen}</p>",
            "<p style='color: yellow;'>Kata Kata yang diganti ke Loma:</p>",
            f"<p style='color: yellow;'>{pasangan_kata}</p>",
            "<p style='color: yellow;'>CAG:</p>",
            f"<p style='color: yellow;'>{pasangan_cag}</p>",
        ]
    
        st.session_state.chat_history.append((user_input, text_constraint, html_block))
        clear_input()
        
    for user_msg, bot_msg, html_block in st.session_state.chat_history:
        st.markdown(
            f"<div class='chat-container'><div class='chat-bubble-user'>{user_msg}</div></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='chat-container'><div class='chat-bubble-bot'>{bot_msg}</div></div>",
            unsafe_allow_html=True
        )
        if status:
            for html in html_block:
                st.markdown(
                    f"<div class='chat-container'><div class='chat-bubble-bot'>{html}</div></div>",
                    unsafe_allow_html=True
                )
    
    st.markdown("</div>", unsafe_allow_html=True)  # ⬅️ END OF chat-container-outer
        
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_area(
            label="", height=80, key="user_input", placeholder="Tulis pesan...",
            label_visibility="collapsed"
        )
       
    with col2:
        st.button("➡", on_click=handle_send)
    

    if "room" not in st.session_state:
        st.session_state.room = "default"

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

if "login" in st.query_params:
    auth_flow()
elif st.session_state.get("user"):
    chat_ui()
else:
    auth_flow()
