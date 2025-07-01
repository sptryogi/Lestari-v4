import streamlit as st
import pandas as pd

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

    # Cari hanya kata yang cocok persis (bukan mirip)
    cocok = df_kamus[
        df_kamus['LEMA_LOWER'].str.contains(fr'\b{kata_input_norm}\b', na=False) |
        df_kamus['SUBLEMA_LOWER'].str.contains(fr'\b{kata_input_norm}\b', na=False)
    ]

    if not cocok.empty:
        st.success(f"✅ Ditemukan {len(cocok)} hasil.")
        st.dataframe(
            cocok[
                ['LEMA', 'SUBLEMA', '(HALUS/LOMA/KASAR)', 'KLAS.', 'ARTI EKUIVALEN 1', 'ARTI 1', 'SINONIM']
            ].reset_index(drop=True),
            use_container_width=True
        )
    else:
        st.error(f"🚫 Tidak ditemukan hasil untuk kata: '{kata_input}'")

else:
    st.info("Masukkan kata di atas untuk mulai mencari.")

# --- Footer ---
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray'>© 2025 SundaLex by Lestari Bahasa</p>",
    unsafe_allow_html=True
)
