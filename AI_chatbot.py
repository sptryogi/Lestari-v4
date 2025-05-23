from openai import OpenAI
import os
import streamlit as st
import re
import string

# Fungsi untuk memanggil Deepseek API
def call_deepseek_api(history, prompt):
    # Ganti ini dengan API key kamu
    client = OpenAI(
        api_key=st.secrets["API_KEY"],  # Simpan API key DeepSeek di secrets Streamlit
        base_url="https://api.deepseek.com"
    )

    # Menyusun format pesan sesuai dengan DeepSeek
    messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    if history:
        for user_msg, bot_msg, _ in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})

    # Tambahkan prompt terbaru dari user
    messages.append({"role": "user", "content": prompt})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.7,
            stream=False
        )
        return response.choices[0].message.content

    except Exception as e:
        print(f"Error saat memanggil DeepSeek API: {e}")
        return "Maaf, terjadi kesalahan saat memproses permintaan Anda."

def generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa="Sunda", history=None):
    # Instruksi berdasarkan fitur dan mode bahasa
    if fitur == "chatbot":
        if mode_bahasa == "Sunda":
            instruksi_bahasa = "Jawablah hanya dalam Bahasa Sunda LOMA. Jawab pertanyaannya mau itu Bahasa Sunda, Bahasa Indonesia atau English tapi tetap jawab pakai Bahasa Sunda Loma. Gunakan tata bahasa sunda yang baik dan benar."
        elif mode_bahasa == "Indonesia":
            instruksi_bahasa = "Jawablah hanya dalam Bahasa Indonesia. Jawab pertanyaannya mau itu Bahasa Indonesia, Bahasa Sunda atau English tapi tetap jawab pakai Bahasa Indonesia."
        elif mode_bahasa == "English":
            instruksi_bahasa = "Please respond only in English. Answer the questions whether it is in Indonesian, Sundanese or English but always answer in English"
        else:
            instruksi_bahasa = ""
        
        final_prompt = f"""
        {instruksi_bahasa}
        Kamu adalah Lestari, chatbot yang interaktif dan talkactive membantu pengguna menjawab pertanyaan secara ramah dan jelas informasinya.
        Jawab pertanyaan secara sederhana saja jangan terlalu panjang dan jangan cerewet.
        Jangan gunakan huruf-huruf aneh seperti kanji korea, kanji jepang, atau kanji china.
        Pertanyaan dari pengguna: "{user_input}"
        """

    elif fitur == "terjemahindosunda":
        final_prompt = f"""Kamu adalah penerjemah yang ahli bahasa sunda dan bahasa indonesia.
        Terjemahkan kalimat berikut ke dalam Bahasa Sunda LOMA secara alami seperti digunakan dalam kehidupan sehari-hari.     
        Jangan mengajak mengobrol seperti fitur chatbot. anda hanya menterjemahkan input dari user seperti google translater.
        Jangan menambahkan kata bahasa sunda yang memang bukan arti dari kalimat bahasa indonesia tersebut.
        Sesuaikan gaya bahasanya agar cocok dengan konteks relasi antarpenutur dalam hal ini teman sebaya anak-anak umur 7 - 10 tahun.
        Perintah anda hanya terjemahkan dari input user, bukan menjawab hal lain. Jangan menggunakan kata awalan atau sapaan sebagai tambahan jawaban.
        Jangan beri penjelasan atau keterangan tambahan, langsung berikan hasil terjemahannya saja. 
        Jangan jadikan semua huruf pada awal kata huruf kapital kecuali nama tempat dan nama orang.
        Huruf pada awal kalimat dan setelah titik harus huruf kapital.
        Nama orang dan nama tempat juga harus berawalan huruf kapital.
        Kalimat: {user_input}"""
        
    elif fitur == "terjemahsundaindo":
        final_prompt = f"""Kamu adalah penerjemah yang ahli bahasa indonesia dan bahasa sunda.
        Terjemahkan kalimat berikut ke dalam Bahasa Indonesia yang baku dan mudah dimengerti.
        Jangan mengajak mengobrol seperti fitur chatbot, anda hanya menterjemahkan input dari user seperti google translate.
        Jangan tambahkan penjelasan atau keterangan apa pun. Langsung tampilkan hasil terjemahannya.
        Jangan jadikan semua huruf pada awal kata huruf kapital, kecuali nama orang dan nama tempat.
        Huruf pada awal kalimat dan setelah titik harus huruf kapital.
        Nama orang dan nama tempat juga harus berawalan huruf kapital.
        Kalimat: {user_input}"""

    else:
        # fallback
        final_prompt = f"Jawablah dengan sopan dan informatif: {user_input}"

    # === Panggil LLM Deepseek API di sini ===
    response = call_deepseek_api(history=history, prompt=final_prompt)  # Fungsi ini kamu sesuaikan dengan API Groq kamu
    return response
    
def kapitalisasi_awal_kalimat(teks):
    # Pecah teks berdasarkan titik
    kalimat_list = re.split(r'([.!?])', teks)
    hasil = ""
    for i in range(0, len(kalimat_list), 2):
        kalimat = kalimat_list[i].strip()
        if kalimat:
            kapital = kalimat[0].upper() + kalimat[1:] if len(kalimat) > 1 else kalimat.upper()
            hasil += kapital
        if i+1 < len(kalimat_list):
            hasil += kalimat_list[i+1] + " "
    return hasil.strip()

