import streamlit as st
import pandas as pd
import re
import pybase64
from AI_chatbot import generate_text_deepseek, call_deepseek_api, kapitalisasi_awal_kalimat, bersihkan_superscript
from constraint1 import highlight_text, constraint_text, ubah_ke_lema, find_the_lema_pair, cari_arti_lema
import streamlit.components.v1 as components

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
    
    /* Hilangkan elemen GitHub (termasuk avatar foto) */
    a[href*="github.com"], img[src*="githubusercontent"] {
        display: none !important;
    }

    /* Target tombol collapse/expand sidebar */
    [data-testid="stSidebarCollapsedControl"] button {
        color: green !important;  /* ganti warna ikon */
        background-color: #e6ffe6 !important;  /* opsional: latar belakang tombol */
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

    # .stChatInputContainer {
    #     position: fixed;
    #     bottom: 0;
    #     left: 0;
    #     right: 0;
    #     background-color: #1E1E2F;
    #     padding: 10px 20px;
    #     z-index: 999;
    #     border-top: 1px solid #444;
    # }
    
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
        max-width: 70%;
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

def handle_send(user_input):
    pasangan_cag = {}
    history_for_prompt = st.session_state.chat_history[-50:]
    # user_input = st.session_state.user_input
    
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

user_input = st.chat_input("Ketik sesuatu...")

st.markdown("""
<style>
    /* Ganti background input box */
    [data-testid="stBottom"] > div {
        background-color: transparent !important; 
    }
    
    # /* Ganti background input box */
    # [data-testid="stChatInput"] > div {
    #     background-color: black !important; 
    # }

    /* Ganti warna text */
    [data-testid="stChatInput"] input {
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

# Inject JavaScript untuk cegah Enter submit (tidak bikin newline)
st.markdown("""
<script>
const input = window.parent.document.querySelector('[data-testid="stChatInput"] input');
if(input){
    input.addEventListener('keydown', function(event) {
        if(event.key === 'Enter'){
            event.preventDefault();
            // Bisa tambahkan custom aksi di sini, misal fokus ke elemen lain
            console.log("Enter ditekan tapi tidak submit");
        }
    });
}
</script>
""", unsafe_allow_html=True)

# Menjalankan fungsi handle_send saat pesan dikirim
if user_input:
    handle_send(user_input)
    
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

# Tambah anchor di akhir chat
st.markdown('<a name="scroll-bottom"></a>', unsafe_allow_html=True)
st.markdown("""
    <style>
    .scroll-down-btn {
        position: fixed;
        bottom: 200px;
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
