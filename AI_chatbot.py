from groq import Groq
import os
import streamlit as st
import re
import string
#from dotenv import load_dotenv

#load_dotenv()
#api_key = os.getenv("api_key")

def generate_text_groq(prompt, fitur, kata_terdapat_cag):
    client = Groq(
        # ================ STREAMLIT ================
        api_key=st.secrets["api_key"],
        # ================ STREAMLIT ================

        # ================ LOKAL ================
        # api_key=api_key,
        # ================ LOKAL ================
    )

    tugas = {
        "chatbot": "Jawab ini Menggunakan Bahasa Sunda Loma",
        "terjemahindosunda": "Terjemahkan Kalimat Bahasa Indonesia ini ke Bahasa Sunda Loma.",
        "terjemahsundaindo": "Terjemahkan Kalimat Bahasa Sunda Loma ini ke Bahasa Sunda Indonesia.",
    }

    print(tugas[fitur])

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Namamu adalah Lestari. Kamu berperan sebagai teman ngobrol bahasa sunda. Kamu selalu mengajukan pertanyaan di akhir pembicaraan dan memiliki gaya berbicara yang ramah, aktif, serta sesuai dengan konteks.",
            },
            {
                "role": "user",
                "content": f""" {tugas[fitur]}
            Pertanyaan:
            {prompt}
            Jawaban:""",
            },
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )

    return chat_completion.choices[0].message.content

def generate_text_groq_2prompt(prompt, fitur, kata_terdapat_cag):
    client = Groq(
        # ================ STREAMLIT ================
        # This is the default and can be omitted
        api_key=st.secrets["api_key"],
        # ================ STREAMLIT ================

        # ================ LOKAL ================
        #api_key=api_key,
        # ================ LOKAL ================
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Namamu adalah Lestari. Kamu berperan sebagai teman ngobrol. Kamu selalu mengajukan pertanyaan di akhir pembicaraan dan memiliki gaya berbicara yang ramah, aktif, serta sesuai dengan konteks.",
            },
            {
                "role": "user",
                "content": prompt
            },
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )

    chatbot_respons = chat_completion.choices[0].message.content

    tugas = {
        "chatbot": "Jawab ini Menggunakan Bahasa Sunda Loma",
        "terjemahindosunda": "Terjemahkan Kalimat Bahasa Indonesia ini ke Bahasa Sunda Loma.",
        "terjemahsundaindo": "Terjemahkan Kalimat Bahasa Sunda Loma ini ke Bahasa Sunda Indonesia.",
    }

    print(tugas[fitur])

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "Namamu adalah Lestari. Kamu berperan sebagai teman ngobrol. Kamu selalu mengajukan pertanyaan di akhir pembicaraan dan memiliki gaya berbicara yang ramah, aktif, serta sesuai dengan konteks.",
            },
            {
                "role": "user",
                "content": f""" {tugas[fitur]}
            Pertanyaan:
            {prompt}
            Jawaban:""",
            },
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )
    return chat_completion.choices[0].message.content

# Fungsi untuk memanggil Groq API
def call_groq_api(history, prompt):
    client = Groq(
        # ================ STREAMLIT ================
        api_key=st.secrets["api_key"],
        # ================ STREAMLIT ================

        # ================ LOKAL ================
        # api_key=api_key,
        # ================ LOKAL ================
    )
    messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
    if history:
        for user_msg, bot_msg, _ in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": bot_msg})

    messages.append({"role": "user", "content": prompt})
    try:
        response = client.chat.completions.create(
            messages=messages,
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.7
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error saat memanggil Groq API: {e}")
        return "Maaf, terjadi kesalahan saat memproses permintaan Anda."

def generate_text_groq2(user_input, fitur, pasangan_cag, mode_bahasa="Sunda", history=None):
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
        Jawab pertanyaan secara sederhana saja jangan terlalu panjang dan jangan cerewet. Ingat kamu dibangun menggunakan Llama4-scout.
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

    # === Panggil LLM Groq API di sini ===
    response = call_groq_api(history=history, prompt=final_prompt)  # Fungsi ini kamu sesuaikan dengan API Groq kamu
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

