import streamlit as st

st.title("Chat Bot dengan Toggle")

# Buat 2 kolom: kiri untuk input, kanan untuk toggle
col1, col2 = st.columns([4, 1])  # proporsi 4:1

with col1:
    user_input = st.text_area("Ketik pesan Anda:", height=100, label_visibility="collapsed")

with col2:
    option = st.toggle("Mode Bot")

if st.button("Kirim"):
    if user_input:
        with st.chat_message("user"):
            st.markdown(user_input)

        # Contoh balasan tergantung toggle
        with st.chat_message("assistant"):
            if option:
                st.markdown("Mode Bot AKTIF 🚀")
            else:
                st.markdown("Mode Bot NON-AKTIF 😴")
