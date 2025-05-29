import streamlit as st
import pandas as pd
import re
import pybase64
from AI_chatbot import kapitalisasi_awal_kalimat, bersihkan_superscript
from constraint1 import highlight_text, constraint_text, ubah_ke_lema, find_the_lema_pair, cari_arti_lema
import streamlit.components.v1 as components
from supabase_helper import *
import uuid

st.set_page_config(page_title="Lestari Bahasa", page_icon="🌐", layout="centered")

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

    /* Sembunyikan logo SVG */
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
        color: green !important;
        background-color: white !important;
        border-radius: 8px;
        padding: 6px;
    }

    /* Ganti warna saat hover */
    [data-testid="stSidebarCollapsedControl"] button:hover {
        background-color: #ccffcc !important;
        color: darkgreen !important;
    }

    /* Tambahan agar ikon lebih besar */
    button[data-testid="collapsedControl"] svg {
        width: 1.2rem;
        height: 1.2rem;
    }
    
    /* Gaya untuk chat bubble */
    .chat-bubble-user {
        background-color: white;
        color: black;
        padding: 10px 15px;
        border-radius: 15px 15px 0 15px;
        margin: 5px 0;
        max-width: 70%;
        align-self: flex-end;
        margin-left: auto;
        font-size: 16px;
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
        font-size: 16px;
        font-family: Times New Roman;
        border: 2px solid black;
        text-align: justify;
        line-height: 20px;
    }
    
    /* Container untuk chat */
    .chat-container {
        display: flex;
        flex-direction: column;
        margin-bottom: 15px;
    }
    
    /* Area input */
    .stTextArea>div>div>textarea {
        text-align: justify !important;
        resize: none !important;
        font-size: 16px !important;
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

# Load kamus
@st.cache_data
def load_data():
    df_kamus = pd.read_excel("dataset/data_kamus_full_14-5-25.xlsx")
    df_kamus[['ARTI EKUIVALEN 1', 'ARTI 1']] = df_kamus[['ARTI EKUIVALEN 1', 'ARTI 1']].apply(lambda col: col.str.lower())
    df_idiom = pd.read_excel("dataset/data_idiom (3).xlsx")
    return df_kamus, df_idiom

df_kamus, df_idiom = load_data()

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

def get_age_by_id(user_id):
    if not user_id:
        return None  # atau return default age
    
    try:
        response = supabase.table("profiles").select("age").eq("id", user_id).single().execute()
        return response.data.get("age") if response.data else None
        
    except Exception as e:
        st.error(f"Error getting user age: {e}")
        return None

def get_ai_response(prompt, history):
    api_key = st.secrets["API_KEY"]
    url = "https://api.deepseek.com/v1/chat/completions"

    messages = [{"role": "system", "content": "Anda adalah asisten untuk pelajar Bahasa Sunda."}]
    for chat in history:
        messages.append({"role": "user", "content": chat["message"]})
        messages.append({"role": "assistant", "content": chat["response"]})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024
    }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            st.error(f"Gagal mengambil respons dari DeepSeek: {response.text}")
            return "⚠️ Error: Gagal menghubungi model."
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")
        return "⚠️ Error: Terjadi kesalahan saat menghubungi API."

def call_deepseek_api(history, prompt):
    # Fungsi ini memanggil get_ai_response dengan parameter yang sesuai
    return get_ai_response(prompt, history)

def generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa="Sunda", chat_mode="Ngobrol", history=None):
    if "user" not in st.session_state:
        raise ValueError("User not logged in")
    
    user_id = st.session_state.user.id
    # Mendapatkan usia pengguna dari database
    age = get_age_by_id(user_id)
    
    # Jika tidak dapat mendapatkan usia, gunakan default 30
    if age is None:
        age = 30
    
    klasifikasi_bahasa = "LOMA"
    
    if age >= 30:
        klasifikasi_bahasa = "HALUS"
    elif age < 30:
        klasifikasi_bahasa = "LOMA"
    
    # Instruksi berdasarkan fitur dan mode bahasa
    if fitur == "chatbot":
        if mode_bahasa == "Sunda":
            instruksi_bahasa = f"Jawablah hanya dalam Bahasa Sunda {klasifikasi_bahasa}. Jawab pertanyaannya mau itu Bahasa Sunda, Bahasa Indonesia atau English tapi tetap jawab pakai Bahasa Sunda Loma. Gunakan tata bahasa sunda yang baik dan benar."
        elif mode_bahasa == "Indonesia":
            instruksi_bahasa = "Jawablah hanya dalam Bahasa Indonesia. Jawab pertanyaannya mau itu Bahasa Indonesia, Bahasa Sunda atau English tapi tetap jawab pakai Bahasa Indonesia."
        elif mode_bahasa == "English":
            instruksi_bahasa = "Please respond only in British English. Answer the questions whether it is in Indonesian, Sundanese or English but always answer in English"
        else:
            instruksi_bahasa = ""

        final_prompt = f"""
        {instruksi_bahasa}
        Anda adalah Lestari, chatbot yang interaktif membantu pengguna belajar bahasa Indonesia, English, dan Sunda serta menjawab pertanyaan secara ramah dan jelas informasinya.
        Anda berumur 30 tahun. Jika anda ditanya "Kumaha damang?" tolong jawab "Sae, anjeun kumaha?" tapi selain ditanya itu jangan jawab "Sae, anjeun kumaha?".
        Lawan bicara anda berumur {age} tahun. tolong sesuaikan gaya bicara anda dengan umur lawan bicara anda.        
        Jangan memberikan informasi yang tidak tentu kebenarannya.
        Jangan gunakan huruf-huruf aneh seperti kanji korea, kanji jepang, atau kanji china.
        Kenali format paragraf kalimat teks dari user.
        Gunakan huruf kapital pada awal kalimat dan setelah tanda titik serta setelah petik dua atau setelah paragraf.
        Gunakan huruf kapital pada awal nama orang dan nama tempat.
        Gunakan huruf kapital yang sama jika pada kalimat atau kata pada input user menggunakan huruf kapital.
        Jika diperintahkan untuk terjemahkan atau translate, jaga format paragrafnya. Tiap paragraf dalam teks asli harus menjadi paragraf yang terpisah dalam hasil terjemahan.
        Jangan menggabungkan paragraf.
        Selalu akhiri dengan pertanyaan. 
        Pertanyaan dari pengguna: "{user_input}"
        """

    elif fitur == "terjemahindosunda":
        final_prompt = f"""Kamu adalah penerjemah yang ahli bahasa sunda dan bahasa indonesia.
        Terjemahkan kalimat berikut ke dalam Bahasa Sunda LOMA secara alami seperti digunakan dalam kehidupan sehari-hari.
        Kenali format paragraf kalimat teks dari pengguna.
        Jaga agar format paragraf dan barisnya tetap sama persis seperti teks asli atau input user.
        Jangan menggabungkan paragraf.
        Gunakan huruf kapital yang sama jika pada kalimat atau kata pada input user menggunakan huruf kapital.
        Jangan mengajak mengobrol seperti fitur chatbot. anda hanya menterjemahkan input dari user seperti google translater.
        Jangan menambahkan kata bahasa sunda yang memang bukan arti dari kalimat bahasa indonesia tersebut.
        Sesuaikan gaya bahasanya agar cocok dengan konteks relasi antarpenutur dalam hal ini teman sebaya anak-anak umur 7 - 10 tahun.
        Perintah anda hanya terjemahkan dari input user, bukan menjawab hal lain. Jangan menggunakan kata awalan atau sapaan sebagai tambahan jawaban.
        Jangan beri penjelasan atau keterangan tambahan, langsung berikan hasil terjemahannya saja. 
        Jangan jadikan semua huruf pada awal kata huruf kapital kecuali nama tempat dan nama orang.
        Huruf pada awal kalimat dan setelah titik serta setelah petik dua atau setelah paragraf harus huruf kapital.
        Nama orang dan nama tempat juga harus berawalan huruf kapital.
        Kalimat: {user_input}"""
        
    elif fitur == "terjemahsundaindo":
        final_prompt = f"""Kamu adalah penerjemah yang ahli bahasa indonesia dan bahasa sunda.
        Terjemahkan kalimat berikut ke dalam Bahasa Indonesia yang baku dan mudah dimengerti.
        Jaga agar format paragraf dan barisnya tetap sama persis seperti teks asli atau input user.
        Jangan menggabungkan paragraf.
        Gunakan huruf kapital yang sama jika pada kalimat atau kata pada input user menggunakan huruf kapital.
        Jangan mengajak mengobrol seperti fitur chatbot, anda hanya menterjemahkan input dari user seperti google translate.
        Jangan tambahkan penjelasan atau keterangan apa pun. Langsung tampilkan hasil terjemahannya.
        Jangan jadikan semua huruf pada awal kata huruf kapital, kecuali nama orang dan nama tempat.
        Huruf pada awal kalimat dan setelah titik serta setelah petik dua atau setelah paragraf harus huruf kapital.
        Nama orang dan nama tempat juga harus berawalan huruf kapital.
        Kalimat: {user_input}"""

    else:
        # fallback
        final_prompt = f"Jawablah dengan sopan dan informatif: {user_input}"

    # Panggil LLM Deepseek API
    response = call_deepseek_api(history=history, prompt=final_prompt)
    return response

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
    
    # Inisialisasi chat history dari database
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
        # Ambil history dari database
        db_history = fetch_chat_history(user_id, st.session_state.room)
        
        # Konversi format history dari database ke format yang digunakan aplikasi
        for item in db_history:
            st.session_state.chat_history.append(
                (item['message'], item['response'], [])
            )
    
    with st.sidebar:
        st.header("⚙️ Pengaturan")
    
        option = st.selectbox(
            "Pilih Fitur",
            ["Chatbot", "Terjemah Indo → Sunda", "Terjemah Sunda → Indo"],
            key="fitur_selector"
        )
    
        fitur = "chatbot" if option == "Chatbot" else "terjemahindosunda" if option == "Terjemah Indo → Sunda" else "terjemahsundaindo"
    
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
        
    st.markdown("<h1 style='text-align: left; color: white;'>Lestari Bahasa</h1>", unsafe_allow_html=True)
    
    bahasa_list = ["Sunda", "Indonesia", "English"]
    bahasa_display = []
    for bhs in bahasa_list:
        if bhs == mode_bahasa if mode_bahasa else "Sunda":
            bahasa_display.append(f"<span style='color:#FFD700;'><b>{bhs}</b></span>")
        else:
            bahasa_display.append(f"<span style='color: white;'>{bhs}</span>")
    
    st.markdown(
        f"<div style='text-align:left; padding-top: 8px; font-size: 20px; margin-top:0px;'>"
        f"{' '.join(bahasa_display)}"
        f"</div>", 
        unsafe_allow_html=True
    )
    
    st.markdown("""
    <p style='
        color: white;
        text-align: left;
        font-size: 14px;
    '>
        Selamat datang! Silakan ajukan pertanyaan.
    </p>
    """, unsafe_allow_html=True)
    
    
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    
    def clear_input():
        st.session_state.user_input = ""
    
    def handle_send():
        if not st.session_state.user_input.strip():
            return
            
        pasangan_cag = {}
        user_input = st.session_state.user_input
        
        option = st.session_state.get("fitur_selector", "Chatbot")
        fitur = (
            "chatbot" if option == "Chatbot" else
            "terjemahindosunda" if option == "Terjemah Indo → Sunda" else
            "terjemahsundaindo"
        )
        mode_bahasa = st.session_state.get("mode_selector", "Sunda") if fitur == "chatbot" else None
        
        try:
            # Dalam fungsi handle_send(), perbaiki pemanggilan generate_text_deepseek
            if fitur == "chatbot" and mode_bahasa == "Sunda":
                api_history = []
                for user_msg, bot_msg, _ in st.session_state.chat_history:
                    api_history.append({"message": user_msg, "response": bot_msg})
                
                bot_response = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, chat_mode, api_history)
                pasangan_ganti_ekuivalen = {}
                text_constraint, _, _, pasangan_kata, pasangan_ekuivalen = highlight_text(bot_response, df_kamus, df_idiom, fitur)
                text_constraint = kapitalisasi_awal_kalimat(text_constraint)
                supabase.table("chat_history").insert({
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "room": st.session_state.room,
                    "message": user_input,
                    "response": text_constraint
                }).execute()
            elif fitur == "chatbot" and (mode_bahasa == "Indonesia" or mode_bahasa == "English"):
                api_history = []
                for user_msg, bot_msg, _ in st.session_state.chat_history:
                    api_history.append({"message": user_msg, "response": bot_msg})
                text_constraint = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, chat_mode, api_history)
                supabase.table("chat_history").insert({
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "room": st.session_state.room,
                    "message": user_input,
                    "response": text_constraint
                }).execute()
                pasangan_ganti_ekuivalen = {}
                pasangan_ekuivalen = {}
                pasangan_kata = {}
            elif option == "Terjemah Sunda → Indo":
                api_history = []
                for user_msg, bot_msg, _ in st.session_state.chat_history:
                    api_history.append({"message": user_msg, "response": bot_msg})
                bot_response2 = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, chat_mode, api_history)
                bot_response_ekuivalen, pasangan_ganti_ekuivalen = ubah_ke_lema(bot_response2, df_kamus, df_idiom)
                text_constraint = bot_response_ekuivalen
                supabase.table("chat_history").insert({
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "room": st.session_state.room,
                    "message": user_input,
                    "response": text_constraint
                }).execute()
            elif option == "Terjemah Indo → Sunda":
                api_history = []
                for user_msg, bot_msg, _ in st.session_state.chat_history:
                    api_history.append({"message": user_msg, "response": bot_msg})
                bot_response2 = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, chat_mode, api_history)
                bot_response_ekuivalen, pasangan_ganti_ekuivalen = ubah_ke_lema(bot_response2, df_kamus, df_idiom)
                text_constraint, _, _, pasangan_kata, pasangan_ekuivalen = highlight_text(bot_response_ekuivalen, df_kamus, df_idiom, fitur)
                text_constraint = kapitalisasi_awal_kalimat(text_constraint)
                supabase.table("chat_history").insert({
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "room": st.session_state.room,
                    "message": user_input,
                    "response": text_constraint
                }).execute()
            
            html_block = [
                f"<p style='color: yellow;'>Kata yang diganti ke Loma: {pasangan_kata}</p>",
                f"<p style='color: yellow;'>Kata yang ada di kamus: {pasangan_ekuivalen}</p>",
            ]
            
            st.session_state.chat_history.append((user_input, text_constraint, html_block))
            clear_input()
            st.rerun()
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")
    
    # Tampilkan chat history
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
    
    # Input area
    col1, col2 = st.columns([6, 1])
    with col1:
        user_input = st.text_area(
            label="", 
            height=80, 
            key="user_input", 
            placeholder="Tulis pesan...",
            label_visibility="collapsed"
        )
       
    with col2:
        st.button("➡", on_click=handle_send, use_container_width=True)
            

    # Room management
    if "room" not in st.session_state:
        st.session_state.room = "default"

    with st.sidebar:
        st.markdown("### 💬 Pilih Room Chat")
        available_rooms = get_user_chat_rooms(user_id)
        room_options = ["default", "new chat room"] + [r for r in available_rooms if r not in ["default", "new chat room"]]
        
        current_room = st.session_state.get("room", "default")
        if current_room not in room_options:
            current_room = "default"

        selected_room = st.selectbox("Room Chat", room_options, index=room_options.index(current_room))
        
        if selected_room != st.session_state.get("room"):
            st.session_state.room = selected_room
            st.rerun()

        if selected_room == "new chat room":
            new_room_name = st.text_input("Nama Chat Room Baru", key="new_room_input")
            if st.button("Buat Room") and new_room_name:
                if new_room_name not in room_options:
                    st.session_state.room = create_chat_room(user_id, new_room_name)
                    st.rerun()

        elif selected_room not in ["default", "new chat room"]:
            if st.button(f"Hapus Room '{selected_room}'", key="delete_room"):
                delete_chat_room(user_id, selected_room)
                st.session_state.room = "default"
                st.rerun()

# Main app flow
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
