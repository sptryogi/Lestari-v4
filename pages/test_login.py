import streamlit as st
import pandas as pd
import re
import pybase64
from AI_chatbot import kapitalisasi_awal_kalimat, bersihkan_superscript
from constraint1 import highlight_text, constraint_text, ubah_ke_lema, find_the_lema_pair, cari_arti_lema
import streamlit.components.v1 as components
from supabase_helper import *  # Pastikan modul ini berisi semua fungsi yang diperlukan
import uuid
import requests

# Inisialisasi Supabase (pastikan ini ada di supabase_helper.py)
# supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Lestari Bahasa", page_icon="🌐", layout="centered")

# ========== FUNGSI BANTU ==========
def set_background_from_file(file_path):
    """Set background dari file lokal"""
    try:
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
    except Exception as e:
        st.error(f"Gagal memuat background: {str(e)}")

@st.cache_data
def load_data():
    """Load data kamus dengan caching"""
    try:
        df_kamus = pd.read_excel("dataset/data_kamus_full_14-5-25.xlsx")
        df_kamus[['ARTI EKUIVALEN 1', 'ARTI 1']] = df_kamus[['ARTI EKUIVALEN 1', 'ARTI 1']].apply(lambda col: col.str.lower())
        df_idiom = pd.read_excel("dataset/data_idiom (3).xlsx")
        return df_kamus, df_idiom
    except Exception as e:
        st.error(f"Gagal memuat data: {str(e)}")
        return pd.DataFrame(), pd.DataFrame()  # Return empty DataFrames sebagai fallback

def get_age_by_id(user_id):
    """Mendapatkan usia pengguna dari database"""
    if not user_id:
        return None
    
    try:
        response = supabase.table("profiles").select("age").eq("id", user_id).single().execute()
        return response.data.get("age") if response.data else None
    except Exception as e:
        st.error(f"Error getting user age: {e}")
        return None

def get_ai_response(prompt, history):
    """Mendapatkan respons dari API DeepSeek"""
    try:
        api_key = st.secrets.get("API_KEY")
        if not api_key:
            raise ValueError("API_KEY tidak ditemukan di st.secrets")
        
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

        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()  # Akan memunculkan exception untuk status code 4xx/5xx
        
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        st.error(f"Gagal menghubungi API DeepSeek: {str(e)}")
        return "⚠️ Error: Gagal menghubungi model."
    except Exception as e:
        st.error(f"Terjadi kesalahan: {str(e)}")
        return "⚠️ Error: Terjadi kesalahan saat memproses respons."

# ========== FUNGSI UTAMA ==========
def auth_flow():
    """Menangani alur autentikasi pengguna"""
    if "register_mode" not in st.session_state:
        st.session_state.register_mode = False

    if st.session_state.register_mode:
        # Tampilan registrasi
        with st.form("register_form"):
            st.subheader("Register")
            email = st.text_input("Email")
            age = st.number_input("Umur", min_value=5, max_value=100, step=1)
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Buat Akun"):
                try:
                    result = sign_up_with_email(email, password, age)
                    if result:
                        st.success("Akun berhasil dibuat. Silakan login.")
                        st.session_state.register_mode = False
                        st.rerun()
                except Exception as e:
                    st.error(f"Gagal membuat akun: {e}")
        
        if st.button("Sudah punya akun? Login"):
            st.session_state.register_mode = False
            st.rerun()
    else:
        # Tampilan login
        with st.form("login_form"):
            st.subheader("Login")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.form_submit_button("Login"):
                try:
                    result = sign_in_with_email(email, password)
                    if result and hasattr(result, 'user'):
                        st.session_state.user = result.user
                        st.session_state.email = email
                        st.rerun()
                    else:
                        st.error("Login gagal.")
                except Exception as e:
                    st.error(f"Login gagal: {e}")
        
        if st.button("Belum punya akun? Daftar"):
            st.session_state.register_mode = True
            st.rerun()

def chat_ui():
    """Tampilan utama chat"""
    user = st.session_state.get("user")
    if not user:
        st.error("Pengguna tidak terautentikasi")
        return
    
    user_id = user.id
    
    # Inisialisasi chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
        # Ambil history dari database
        try:
            db_history = fetch_chat_history(user_id, st.session_state.get("room", "default"))
            for item in db_history:
                st.session_state.chat_history.append(
                    (item['message'], item['response'], [])
                )
        except Exception as e:
            st.error(f"Gagal memuat riwayat chat: {str(e)}")
    
    # Sidebar untuk pengaturan
    with st.sidebar:
        st.header("⚙️ Pengaturan")
        
        # Pilihan fitur
        option = st.selectbox(
            "Pilih Fitur",
            ["Chatbot", "Terjemah Indo → Sunda", "Terjemah Sunda → Indo"],
            key="fitur_selector"
        )
        
        fitur = {
            "Chatbot": "chatbot",
            "Terjemah Indo → Sunda": "terjemahindosunda", 
            "Terjemah Sunda → Indo": "terjemahsundaindo"
        }.get(option, "chatbot")
        
        # Mode chat
        chat_mode = st.selectbox(
            "Pilih Mode Chat",
            ["Ngobrol", "Belajar"],
            key="chat_mode"
        )
        
        # Mode bahasa (hanya untuk fitur chatbot)
        if fitur == "chatbot":
            mode_bahasa = st.selectbox(
                "🌐 Mode Bahasa",
                ["Sunda", "Indonesia", "English"],
                key="mode_selector"
            )
        else:
            mode_bahasa = None
        
        # Toggle untuk constraint
        status = st.toggle("🔍 Lihat Constraint")
        
        # Manajemen room chat
        st.markdown("### 💬 Pilih Room Chat")
        try:
            available_rooms = get_user_chat_rooms(user_id)
        except Exception as e:
            st.error(f"Gagal memuat room chat: {str(e)}")
            available_rooms = ["default"]
            
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
                    try:
                        st.session_state.room = create_chat_room(user_id, new_room_name)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Gagal membuat room: {str(e)}")

        elif selected_room not in ["default", "new chat room"]:
            if st.button(f"Hapus Room '{selected_room}'", key="delete_room"):
                try:
                    delete_chat_room(user_id, selected_room)
                    st.session_state.room = "default"
                    st.rerun()
                except Exception as e:
                    st.error(f"Gagal menghapus room: {str(e)}")
    
    # Tampilan utama chat
    st.markdown("<h1 style='text-align: left; color: white;'>Lestari Bahasa</h1>", unsafe_allow_html=True)
    
    # Tampilkan mode bahasa yang aktif
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
    
    # Pesan selamat datang
    st.markdown("""
    <p style='
        color: white;
        text-align: left;
        font-size: 14px;
    '>
        Selamat datang! Silakan ajukan pertanyaan.
    </p>
    """, unsafe_allow_html=True)
    
    # Input area
    def clear_input():
        st.session_state.user_input = ""
    
    def handle_send():
        if not st.session_state.get("user_input", "").strip():
            return
            
        pasangan_cag = {}
        user_input = st.session_state.user_input
        
        try:
            # Tentukan fitur dan mode bahasa
            option = st.session_state.get("fitur_selector", "Chatbot")
            fitur = {
                "Chatbot": "chatbot",
                "Terjemah Indo → Sunda": "terjemahindosunda", 
                "Terjemah Sunda → Indo": "terjemahsundaindo"
            }.get(option, "chatbot")
            
            mode_bahasa = st.session_state.get("mode_selector", "Sunda") if fitur == "chatbot" else None
            
            # Siapkan history untuk API
            api_history = []
            for user_msg, bot_msg, _ in st.session_state.chat_history:
                api_history.append({"message": user_msg, "response": bot_msg})
            
            # Proses berdasarkan fitur
            if fitur == "chatbot":
                bot_response = generate_text_deepseek(
                    user_input, 
                    fitur, 
                    pasangan_cag, 
                    mode_bahasa, 
                    chat_mode, 
                    api_history
                )
                
                if mode_bahasa == "Sunda":
                    text_constraint, _, _, pasangan_kata, pasangan_ekuivalen = highlight_text(
                        bot_response, 
                        df_kamus, 
                        df_idiom, 
                        fitur
                    )
                    text_constraint = kapitalisasi_awal_kalimat(text_constraint)
                else:
                    text_constraint = bot_response
                    pasangan_kata = {}
                    pasangan_ekuivalen = {}
                    
            elif fitur == "terjemahsundaindo":
                bot_response2 = generate_text_deepseek(
                    user_input, 
                    fitur, 
                    pasangan_cag, 
                    mode_bahasa, 
                    chat_mode, 
                    api_history
                )
                bot_response_ekuivalen, pasangan_ganti_ekuivalen = ubah_ke_lema(bot_response2, df_kamus, df_idiom)
                text_constraint = bot_response_ekuivalen
                
            elif fitur == "terjemahindosunda":
                bot_response2 = generate_text_deepseek(
                    user_input, 
                    fitur, 
                    pasangan_cag, 
                    mode_bahasa, 
                    chat_mode, 
                    api_history
                )
                bot_response_ekuivalen, pasangan_ganti_ekuivalen = ubah_ke_lema(bot_response2, df_kamus, df_idiom)
                text_constraint, _, _, pasangan_kata, pasangan_ekuivalen = highlight_text(
                    bot_response_ekuivalen, 
                    df_kamus, 
                    df_idiom, 
                    fitur
                )
                text_constraint = kapitalisasi_awal_kalimat(text_constraint)
            
            # Simpan ke database
            try:
                supabase.table("chat_history").insert({
                    "id": str(uuid.uuid4()),
                    "user_id": user_id,
                    "room": st.session_state.get("room", "default"),
                    "message": user_input,
                    "response": text_constraint
                }).execute()
            except Exception as e:
                st.error(f"Gagal menyimpan riwayat chat: {str(e)}")
            
            # Update chat history
            html_block = [
                f"<p style='color: yellow;'>Kata yang diganti ke Loma: {pasangan_kata}</p>",
                f"<p style='color: yellow;'>Kata yang ada di kamus: {pasangan_ekuivalen}</p>",
            ] if status else []
            
            st.session_state.chat_history.append((user_input, text_constraint, html_block))
            clear_input()
            st.rerun()
            
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")
    
    # Tampilkan chat history
    for user_msg, bot_msg, html_block in st.session_state.get("chat_history", []):
        st.markdown(
            f"<div class='chat-container'><div class='chat-bubble-user'>{user_msg}</div></div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='chat-container'><div class='chat-bubble-bot'>{bot_msg}</div></div>",
            unsafe_allow_html=True
        )
        
        if status and html_block:
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

# ========== MAIN APP ==========
# Load data dan set background
try:
    df_kamus, df_idiom = load_data()
    set_background_from_file("dataset/bg biru.jpg")
except Exception as e:
    st.error(f"Gagal memulai aplikasi: {str(e)}")

# Render top bar
def render_topbar():
    col1, col2 = st.columns([8, 1])
    with col2:
        if st.session_state.get("user"):
            st.markdown(
                f"""
                <div style='position: fixed; top: 10px; right: 20px; z-index:9999;'>
                    👤 {st.session_state.get("email", "User")}<br>
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

# Handle query parameters
if "logout" in st.query_params:
    try:
        sign_out()
        st.session_state.clear()
        st.rerun()
    except Exception as e:
        st.error(f"Gagal logout: {str(e)}")

# Main flow
render_topbar()

if "login" in st.query_params:
    auth_flow()
elif st.session_state.get("user"):
    chat_ui()
else:
    auth_flow()
