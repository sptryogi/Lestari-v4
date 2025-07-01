import streamlit as st
import pandas as pd
import difflib

# --- Konfigurasi halaman ---
st.set_page_config(page_title="SundaLex", page_icon="🔍", layout="wide")

# --- CSS Kustom ---
st.markdown("""
    <style>
    .main {
        background-color: #f9f9f9;
    }
    .title-style {
        font-size: 42px;
        font-weight: bold;
        color: #2c3e50;
        text-align: center;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    .subtitle-style {
        font-size: 18px;
        text-align: center;
        color: #7f8c8d;
        margin-bottom: 30px;
    }
    .search-box input {
        font-size: 18px !important;
        padding: 0.5em 1em !important;
    }
    .stDataFrame {
        background-color: white;
        border-radius: 10px;
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="title-style">📚 SundaLex - Kamus Digital Basa Sunda</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-style">Cari padanan kata Sunda dari kolom <b>LEMA</b> atau <b>SUBLEMA</b></div>', unsafe_allow_html=True)

# --- Load Dataset ---
@st.cache_data
def load_kamus():
    return pd.read_excel("dataset/hasil_gabungan16Jun.xlsx")

df_kamus = load_kamus()
df_kamus['LEMA_LOWER'] = df_kamus['LEMA'].fillna("").str.lower()
df_kamus['SUBLEMA_LOWER'] = df_kamus['SUBLEMA'].fillna("").str.lower()

# --- Pencarian Kata ---
st.markdown("### 🔎 Cari Kata Sunda")
kata_input = st.text_input("Masukkan kata Sunda yang ingin dicari:", "", key="input_kata")

if kata_input:
    kata_input_norm = kata_input.strip().lower()

    cocok = df_kamus[
        df_kamus['LEMA_LOWER'].str.contains(kata_input_norm) |
        df_kamus['SUBLEMA_LOWER'].str.contains(kata_input_norm)
    ]

    if cocok.empty:
        semua_kata = pd.concat([df_kamus['LEMA_LOWER'], df_kamus['SUBLEMA_LOWER']]).dropna().unique()
        kata_mirip = difflib.get_close_matches(kata_input_norm, semua_kata, n=5, cutoff=0.6)

        if kata_mirip:
            st.warning(f"🙁 Tidak ditemukan kata persis '{kata_input}'. Namun mirip dengan: {', '.join(kata_mirip)}")
            cocok = df_kamus[
                df_kamus['LEMA_LOWER'].isin(kata_mirip) | df_kamus['SUBLEMA_LOWER'].isin(kata_mirip)
            ]
        else:
            st.error(f"🚫 Tidak ditemukan hasil untuk kata: '{kata_input}'")

    if not cocok.empty:
        st.success(f"✅ Ditemukan {len(cocok)} hasil yang relevan.")
        st.dataframe(
            cocok[
                ['LEMA', 'SUBLEMA', '(HALUS/LOMA/KASAR)', 'KLAS.', 'ARTI EKUIVALEN 1', 'ARTI 1', 'SINONIM']
            ].reset_index(drop=True),
            use_container_width=True
        )

else:
    st.info("Masukkan kata di atas untuk mulai mencari.")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray'>© 2025 SundaLex by Lestari Bahasa</p>",
    unsafe_allow_html=True
)
