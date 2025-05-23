import streamlit as st
import pandas as pd
import re

@st.cache_data
def load_kamus():
    df = pd.read_excel('data_kamus_full_14-5-25.xlsx')
    df['LEMA'] = df['LEMA'].astype(str).str.lower()
    df['SUBLEMA'] = df['SUBLEMA'].astype(str).str.lower()
    df['(HALUS/LOMA/KASAR)'] = df['(HALUS/LOMA/KASAR)'].astype(str).str.upper()

    df_halus = df[df['(HALUS/LOMA/KASAR)'] == 'HALUS']

    lema_split = df_halus['LEMA'].dropna().str.split(',')
    sublema_split = df_halus['SUBLEMA'].dropna().str.split(',')

    halus_kata = set()
    for row in lema_split:
        halus_kata.update([k.strip() for k in row])
    for row in sublema_split:
        halus_kata.update([k.strip() for k in row])

    return halus_kata

halus_kata = load_kamus()

st.title("🟡 Deteksi & Highlight Kata HALUS dari Kalimat Bahasa Sunda")

user_input = st.text_area("Masukkan kalimat dalam Bahasa Sunda...", height=200)

if st.button("🔍 Deteksi Kata HALUS"):
    if user_input.strip():

        def highlight_paragraphs(text, halus_kata):
            paragraphs = text.split('\n')  # jaga struktur per baris/paragraf

            highlighted_paragraphs = []

            for para in paragraphs:
                def replacer(match):
                    word = match.group(0)
                    core = re.sub(r"^[\"'.,!?;:()]*|[\"'.,!?;:()]*$", "", word).lower()
                    if core in halus_kata:
                        return f"<span style='background-color: yellow'>{word}</span>"
                    else:
                        return word

                highlighted = re.sub(r"\b[\w\'\-]+[.,!?\"']*", replacer, para)
                highlighted_paragraphs.append(highlighted)

            return "<br>".join(highlighted_paragraphs)

        hasil_output = highlight_paragraphs(user_input, halus_kata)

        st.markdown(f"<p style='font-size: 18px; line-height: 1.8'><strong>Output:</strong><br>{hasil_output}</p>", unsafe_allow_html=True)
    else:
        st.warning("Mohon masukkan kalimat terlebih dahulu.")
