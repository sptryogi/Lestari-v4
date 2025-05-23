# ========== chabotSyahmi.py ==========
import streamlit as st
import pandas as pd
import re
from AI_chatbot import generate_text_groq,generate_text_groq_2prompt
from constraint1 import highlight_text, constraint_text, ubah_ke_lema, find_the_lema_pair, cari_arti_lema
st.set_page_config(layout="centered")  # atau "centered"

# UI Styling
st.markdown(
    """
    <style>
    .stApp {
        background-color: #1E1E2F;
        color: white;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
    }
    .title {
        color: white;
        font-size: 4em;
        text-align: center;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .chat-bubble-user {
        background-color: #4CAF50;
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 70%;
        align-self: flex-end;
    }
    .chat-bubble-bot {
        background-color: #2E2E3E;
        color: white;
        padding: 10px 15px;
        border-radius: 15px;
        margin: 5px 0;
        max-width: 70%;
        align-self: flex-start;
    }
    .chat-container {
        display: flex;
        flex-direction: column;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Load kamus
df_kamus = pd.read_excel("dataset/data_kamus (32).xlsx")
df_kamus[['ARTI EKUIVALEN 1', 'ARTI 1']] = df_kamus[['ARTI EKUIVALEN 1', 'ARTI 1']].apply(lambda col: col.str.lower())
df_idiom = pd.read_excel("dataset/data_idiom (3).xlsx")
# df_paribasa = pd.read_excel("dataset/paribasa 27-3-25.xlsx")

st.title("Chatbot Bahasa Sunda Loma")
st.write("Selamat datang! Silakan ajukan pertanyaan dalam bahasa Sunda.")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# st.markdown(f"**Hasil ekuivalen:** {user_input_ekuivalen}")

# Menampilkan label dengan warna putih
st.markdown(
    '<p style="color:white; font-size:16px; margin:0px; padding:0px">Tulis pesan Anda:</p>',
    unsafe_allow_html=True,
)

# Input tanpa label karena sudah ditampilkan sebelumnya
user_input = st.text_input(label="", key="user_input")

# user_input_ekuivalen = ubah_ke_lema(user_input, df_kamus)

# Buat 2 kolom
col1, col2, col3 = st.columns([1, 3, 5])  # Atur proporsi jika mau

with col3:
    # Radio button
    option = st.radio(
        "",
        [
            ":blue[Chatbot]",
            ":blue[Terjemah Indo -> Sunda]",
            ":blue[Terjemah Sunda -> Indo]",
        ],
        index=0,
        horizontal=True,
        label_visibility="collapsed",
    )

fitur = "chatbot"
if option == ":blue[Chatbot]":
    fitur = "chatbot"
    # st.info(":blue[Chatbot]")
elif option == ":blue[Terjemah Indo -> Sunda]":
    fitur = "terjemahindosunda"
    # st.info(":blue[Terjemah Indo -> Sunda]")
else:
    fitur = "terjemahsundaindo"
    # st.info(":blue[Terjemah Sunda -> Indo]")

status = st.toggle(":blue[Liat Constraint]")

with col1:
    if st.button("Kirim") and user_input:
        # Pastikan respons terbaru diproses
        # fitur = "chatbot"

        # # Pastikan respons terbaru diproses
        # words_user_input = user_input.split()
        # pasangan_cag = find_the_lema_pair(df_kamus, words_user_input)
        # print(f"========> PS CAG{pasangan_cag}")
        
        # dict_sunda_indo = cari_arti_lema(user_input, df_kamus)
        # terjemahan_user_input = ' '.join([dict_sunda_indo.get(kata, kata) for kata in user_input.split()])
        # print(f"=========< dict_sunda_indo {dict_sunda_indo}")
        # print(f"=========< terjemahan_user_input {terjemahan_user_input}")

        pasangan_cag = {}
        bot_response = generate_text_groq(user_input, fitur, pasangan_cag)
        bot_response = bot_response.lower()

        bot_response_ekuivalen, pasangan_ganti_ekuivalen = ubah_ke_lema(
            bot_response, df_kamus
        )

        if option == ":blue[Terjemah Sunda -> Indo]":
            fitur = "terjemah"
            text_constraint, kata_terdapat, kata_tidak_terdapat, pasangan_kata, pasangan_ekuivalen = (
                highlight_text(bot_response, df_kamus, df_idiom, fitur)
            )
        else:
            fitur = "chatbot"
            text_constraint, kata_terdapat, kata_tidak_terdapat, pasangan_kata, pasangan_ekuivalen = (
                highlight_text(bot_response_ekuivalen, df_kamus, df_idiom, fitur)
            )

        # Update chat history dengan hasil terbaru
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

        # Menambahkan input dan respons ke dalam chat_history
        st.session_state.chat_history.append((user_input, text_constraint, html_block))

with col2:
    # Tombol untuk mereset chat history
    if st.button("🔄 Refresh Chat History"):
        st.session_state.chat_history = []

st.write("Pilihan kamu:", option)

for user_msg, bot_msg, html_block in st.session_state.chat_history:
    st.markdown(
        f"<div class='chat-container'><div class='chat-bubble-user'>{user_msg}</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='chat-container'><div class='chat-bubble-bot'>{bot_msg}</div></div>",
        unsafe_allow_html=True,
    )

    if status:
        for html in html_block:
            st.markdown(
                f"<div class='chat-container'><div class='chat-bubble-bot'>{html}</div></div>",
                unsafe_allow_html=True,
            )
