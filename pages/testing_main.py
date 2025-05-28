import streamlit as st
import pandas as pd
import re
import pybase64
from AI_chatbot import generate_text_deepseek, call_deepseek_api, kapitalisasi_awal_kalimat, bersihkan_superscript
from constraint1_test import highlight_text, constraint_text, ubah_ke_lema, find_the_lema_pair, cari_arti_lema, filter_ucapan_langsung
import streamlit.components.v1 as components
from supabase_helper import sign_in_with_email, get_user_session, insert_chat_history, sign_out, fetch_chat_history

st.set_page_config(page_title="Lestari Bahasa", page_icon="🌐", layout="centered")  # atau "centered"
# Session State
if "user" not in st.session_state:
    st.session_state.user = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Floating Login/Logout Button UI
login_placeholder = st.empty()

with login_placeholder.container():
    if st.session_state.user:
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("Logout"):
                st.session_state.user = None
                st.session_state.chat_history = []
                st.rerun()
        with col1:
            st.markdown(f"<div style='text-align:right;font-weight:bold;'>{st.session_state.user['email']}</div>", unsafe_allow_html=True)
    else:
        with st.expander("Login", expanded=True):
            st.markdown("### Login to Lestari Bahasa")
            email = st.text_input("Email")
            umur = st.text_input("Umur")  # Umur bisa digunakan nanti untuk kebutuhan personalisasi
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                auth_response = sign_in_with_email(email, umur, password)
                if auth_response.user:
                    st.session_state.user = {"email": email, "id": auth_response.user.id, "umur": umur}
                    history = fetch_chat_history(auth_response.user.id)
                    st.session_state.chat_history = history or []
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Login failed. Please check your credentials.")

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

    .stChatInputContainer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background-color: #1E1E2F;
        padding: 10px 20px;
        z-index: 999;
        border-top: 1px solid #444;
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
        line-height: 20px;
    }

    .chat-bubble-bot {
        background-color: white;
        color: black;
        padding: 10px 15px;
        border-radius: 15px 15px 15px 0;
        margin: 5px 0;
        max-width: 70%;
        align-self: flex-start;
        margin-right: auto;
        font-size: 18px;
        font-family: Times New Roman;
        border: 2px solid black;
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
# df_paribasa = pd.read_excel("dataset/paribasa 27-3-25.xlsx")
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
        
# # Cetak hasil input sebelum dihapus
# if st.session_state.user_input != "":
#     st.write("Teks:", st.session_state.user_input)

# ====================================

# user_input_ekuivalen = ubah_ke_lema(user_input, df_kamus)

# ========== Sidebar Controls ==========
# with st.sidebar:
#     st.header("⚙️ Pengaturan")

#     option = st.selectbox(
#         "Pilih Fitur",
#         ["Chatbot", "Terjemah Indo → Sunda", "Terjemah Sunda → Indo"],
#         key="fitur_selector"
#     )

#     fitur = "chatbot"
#     if option == "Chatbot":
#         fitur = "chatbot"
#     elif option == "Terjemah Indo → Sunda":
#         fitur = "terjemahindosunda"
#     else:
#         fitur = "terjemahsundaindo"

#     if fitur == "chatbot":
#         mode_bahasa = st.selectbox(
#             "🌐 Mode Bahasa",
#             ["Sunda", "Indonesia", "English"],
#             key="mode_selector"
#         )
#     else:
#         mode_bahasa = None

#     status = st.toggle("🔍 Lihat Constraint")

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
        bot_response = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, history=history_for_prompt)
        bot_response_ekuivalen, pasangan_ganti_ekuivalen = ubah_ke_lema(bot_response, df_kamus, df_idiom)
        text_constraint, kata_terdapat, kata_tidak_terdapat, pasangan_kata, pasangan_ekuivalen = highlight_text(bot_response_ekuivalen, df_kamus, df_idiom, fitur)
        text_constraint = kapitalisasi_awal_kalimat(text_constraint)
    elif fitur == "chatbot" and (mode_bahasa == "Indonesia" or mode_bahasa == "English"):
        bot_response = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, history=history_for_prompt)
        text_constraint = bot_response
        pasangan_ganti_ekuivalen = {}
        pasangan_ekuivalen = {}
        pasangan_kata = {}

    elif option == "Terjemah Sunda → Indo":
        fitur = "terjemahsundaindo"
        bot_response2 = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, history=None)
        bot_response_ekuivalen, pasangan_ganti_ekuivalen = ubah_ke_lema(bot_response2, df_kamus, df_idiom)
        #bot_response_ekuivalen = ubah_ke_lema(bot_response2, df_kamus)
        #text_constraint, kata_terdapat, kata_tidak_terdapat, pasangan_kata, pasangan_ekuivalen = highlight_text(bot_response_ekuivalen, df_kamus, df_idiom, fitur)
    elif option == "Terjemah Indo → Sunda":
        fitur = "terjemahindosunda"
        bot_response2 = generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa, history=None)
        bot_response_ekuivalen, pasangan_ganti_ekuivalen = ubah_ke_lema(bot_response2, df_kamus, df_idiom)
        text_constraint, kata_terdapat, kata_tidak_terdapat, pasangan_kata, pasangan_ekuivalen = highlight_text(bot_response_ekuivalen, df_kamus, df_idiom, fitur)
        text_constraint = kapitalisasi_awal_kalimat(text_constraint)
        text_constraint = filter_ucapan_langsung(bot_response_ekuivalen, text_constraint)

    html_block = [
        "<p style='color: yellow;'>Kata Kata yang diganti dari Indo ke Sunda (Kamus) Setelah AI:</p>",
        f"<p style='color: yellow;'>{pasangan_ganti_ekuivalen}</p>",
        "<p style='color: yellow;'>Kata Kata yang ada di kamus tapi tidak ada Sinonim LOMA:</p>",
        f"<p style='color: yellow;'>{pasangan_ekuivalen}</p>",
        "<p style='color: yellow;'>Kata Kata yang diganti ke Loma:</p>",
        f"<p style='color: yellow;'>{pasangan_kata}</p>",
        "<p style='color: yellow;'>CAG:</p>",
        f"<p style='color: yellow;'>{pasangan_cag}</p>",
    ]

    st.session_state.chat_history.append((user_input, text_constraint, html_block))
    clear_input()
    
# CHAT HISTORY WRAPPER
#st.markdown("<div class='chat-container-outer'>", unsafe_allow_html=True)

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

# FIXED INPUT DI BAWAH
st.markdown('<div class="stChatInputContainer">', unsafe_allow_html=True)
    
col1, col2 = st.columns([6, 1])
with col1:
    user_input = st.text_area(
        label="", height=80, key="user_input", placeholder="Tulis pesan...",
        label_visibility="collapsed"
    )
   
with col2:
    st.button("➡", on_click=handle_send, use_container_width=True)
# components.html(
#     """
#     <style>
#     .chat-wrapper {
#         position: relative;
#         width: 100%;
#     }
#     .chat-input {
#         width: 100%;
#         height: 100px;
#         padding: 12px 48px 12px 12px;
#         font-size: 16px;
#         resize: none;
#         border-radius: 8px;
#         border: 1px solid #ccc;
#         box-sizing: border-box;
#     }
#     .send-btn {
#         position: absolute;
#         bottom: 12px;
#         right: 12px;
#         background: none;
#         border: none;
#         cursor: pointer;
#     }
#     .send-btn svg {
#         width: 24px;
#         height: 24px;
#         fill: #1f77b4;
#     }
#     </style>

#     <div class="chat-wrapper">
#         <textarea id="userInput" class="chat-input" placeholder="Tulis pesan..."></textarea>
#         <button class="send-btn" onclick="sendMessage()">
#             <svg viewBox="0 0 24 24">
#                 <path d="M2 21l21-9L2 3v7l15 2-15 2v7z"></path>
#             </svg>
#         </button>
#     </div>

#     <script>
#     function sendMessage() {
#         const input = document.getElementById("userInput").value;
#         const query = new URLSearchParams();
#         query.set("user_input", input);
#         window.location.href = window.location.pathname + "?" + query.toString();
#     }
#     </script>
#     """,
#     height=130,
# )

# # Tangkap input dari query params (setelah tombol diklik)
# query_params = st.query_params
# if "user_input" in query_params and query_params["user_input"]:
#     st.session_state.user_input = query_params["user_input"]
#     handle_send()

#     # Hapus param setelah dikirim agar tidak terkirim ulang saat refresh
#     st.experimental_set_query_params()    
# chat_input = components.html(
#     """
#     <style>
#     .chat-wrapper {
#         position: relative;
#         width: 100%;
#         margin-bottom: 1rem;
#     }
#     .chat-input {
#         width: 100%;
#         height: 120px;
#         padding: 12px 48px 12px 12px;
#         font-size: 16px;
#         resize: none;
#         border-radius: 8px;
#         border: 1px solid #ccc;
#         box-sizing: border-box;
#         font-family: inherit;
#     }
#     .send-btn {
#         position: absolute;
#         bottom: 16px;
#         right: 12px;
#         background: none;
#         border: none;
#         cursor: pointer;
#         padding: 8px;
#         border-radius: 50%;
#         transition: background 0.2s;
#     }
#     .send-btn:hover {
#         background: rgba(0,0,0,0.05);
#     }
#     .send-btn svg {
#         width: 24px;
#         height: 24px;
#         fill: #1f77b4;
#     }
#     </style>

#     <div class="chat-wrapper">
#         <textarea id="userInput" class="chat-input" placeholder="Tulis pesan..." rows="4"></textarea>
#         <button class="send-btn" id="sendButton">
#             <svg viewBox="0 0 24 24">
#                 <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"></path>
#             </svg>
#         </button>
#     </div>

#     <script>
#     const sendButton = document.getElementById('sendButton');
#     const userInput = document.getElementById('userInput');
    
#     function sendMessage() {
#         const input = userInput.value.trim();
#         if (input) {
#             // Kirim ke Streamlit
#             window.parent.postMessage({
#                 isStreamlitMessage: true,
#                 type: "streamlit:setComponentValue",
#                 api: "component_value",
#                 value: input
#             }, "*");
            
#             // Clear input (optional)
#             userInput.value = '';
#         }
#     }
    
#     // Handle klik tombol
#     sendButton.addEventListener('click', sendMessage);
    
#     // Handle Enter key (tanpa Shift)
#     userInput.addEventListener('keydown', function(e) {
#         if (e.key === 'Enter' && !e.shiftKey) {
#             e.preventDefault();
#             sendMessage();
#         }
#     });
#     </script>
#     """,
#     height=170
# )

# # Tangkap input dan panggil handle_send
# if chat_input is not None and chat_input != "":
#     st.session_state.user_input = chat_input
#     handle_send()
    
col_left, col_right = st.columns([1, 2])

with col_left:
    st.button("🔄 Delete Chat History", on_click=lambda: st.session_state.update(chat_history=[]))

#with col_right:
    # st.markdown(f"<div style='text-align:right; color: yellow; padding-top: 8px;'>🧠 Mode Aktif: <b>{option}</b>{' - ' + mode_bahasa if mode_bahasa else ''}</div>", unsafe_allow_html=True)

# Tambah anchor di akhir chat
st.markdown('<a name="scroll-bottom"></a>', unsafe_allow_html=True)
st.markdown("""
    <style>
    .scroll-down-btn {
        position: fixed;
        bottom: 80px;
        right: 20px;
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 16px;
        font-size: 16px;
        cursor: pointer;
        z-index: 1000;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.3);
    }
    </style>
    <a href="#scroll-bottom"><button class="scroll-down-btn">⬇️</button></a>
""", unsafe_allow_html=True)

components.html("""
    <script>
        setInterval(function() {
            fetch(window.location.href);
        }, 1000 * 60 * 1);  // ping setiap 1 menit
    </script>
""", height=0)
st.markdown("</div>", unsafe_allow_html=True)
