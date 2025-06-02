from openai import OpenAI
import os
import streamlit as st
import re
import string
from supabase_helper import *

# GET AGE FROM EMAIL
# def get_age_by_email(email):
#     # Dapatkan user berdasarkan email
#     user_data = supabase.auth.admin.get_user_by_email(email)
#     user_id = user_data.user.id
    
#     # Ambil age dari tabel profiles berdasarkan id
#     profile_data = supabase.table("profiles").select("age").eq("id", user_id).single().execute()
#     age = profile_data.data["age"]
    
#     return age

# # GET AGE FROM ID
# def get_age_by_id(user_id):
#     try:
#         # Ambil age dari tabel profiles berdasarkan id
#         response = supabase.table("profiles").select("age").eq("id", user_id).single().execute()

#         if response.data and "age" in response.data:
#             return response.data["age"]
#         else:
#             print("Data umur tidak ditemukan.")
#             return None
#     except Exception as e:
#         print(f"Terjadi kesalahan: {e}")
#         return None


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

def generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa="Sunda", chat_mode = "Ngobrol", history=None):
    # age = get_age_by_id("fd5a8287-e65e-466a-8ef2-b99ab5808d81")
    age = 30

    klasifikasi_bahasa = "LOMA"
    
    if age >= 30:
        klasifikasi_bahasa = "HALUS"
    elif age < 30:
        klasifikasi_bahasa = "LOMA"
    
    # Instruksi berdasarkan fitur dan mode bahasa
    if fitur == "chatbot":
        if mode_bahasa == "Sunda":
            instruksi_bahasa = f"Jawablah hanya dalam Bahasa Sunda {klasifikasi_bahasa}. Jawab pertanyaannya mau itu Bahasa Sunda, Bahasa Indonesia atau English tapi tetap jawab pakai Bahasa Sunda Loma. Gunakan tata bahasa sunda yang baik dan benar."
        elif mode_bahasa == "Indonesia":
            instruksi_bahasa = "Jawablah hanya dalam Bahasa Indonesia. Jawab pertanyaannya mau itu Bahasa Indonesia, Bahasa Sunda atau English tapi tetap jawab pakai Bahasa Indonesia."
        elif mode_bahasa == "English":
            instruksi_bahasa = "Please respond only in British English. Answer the questions whether it is in Indonesian, Sundanese or English but always answer in English"
        else:
            instruksi_bahasa = ""

        final_prompt = f"""
        {instruksi_bahasa}
        Anda adalah Lestari, chatbot yang interaktif membantu pengguna belajar bahasa Indonesia, English, dan Sunda serta menjawab pertanyaan secara ramah dan jelas informasinya.
        Anda berumur 30 tahun. Jika anda ditanya "Kumaha damang?" tolong jawab "Sae, anjeun kumaha?" tapi selain ditanya itu jangan jawab "Sae, anjeun kumaha?".
        Lawan bicara anda berumur {age} tahun. tolong sesuaikan gaya bicara anda dengan umur lawan bicara anda.
        
        Jangan memberikan informasi yang tidak tentu kebenarannya.
        Jangan gunakan huruf-huruf aneh seperti kanji korea, kanji jepang, atau kanji china.
        Kenali format paragraf kalimat teks dari user.
        Gunakan huruf kapital pada awal kalimat dan setelah tanda titik serta setelah petik dua atau setelah paragraf.
        Gunakan huruf kapital pada awal nama orang dan nama tempat.
        Gunakan huruf kapital yang sama jika pada kalimat atau kata pada input user menggunakan huruf kapital.
        Jika diperintahkan untuk terjemahkan atau translate, jaga format paragrafnya. Tiap paragraf dalam teks asli harus menjadi paragraf yang terpisah dalam hasil terjemahan.
        Jangan menggabungkan paragraf.
        Selalu akhiri dengan pertanyaan. 
        Pertanyaan dari pengguna: "{user_input}"
        """
#        Jawab pertanyaan secara sederhana saja jangan terlalu panjang dan jangan cerewet.


    elif fitur == "terjemahindosunda":
        final_prompt = f"""Kamu adalah penerjemah yang ahli bahasa sunda dan bahasa indonesia.
        Terjemahkan kalimat berikut ke dalam Bahasa Sunda LOMA secara alami seperti digunakan dalam kehidupan sehari-hari.
        Kenali format paragraf kalimat teks dari pengguna.
        Jaga agar format paragraf dan barisnya tetap sama persis seperti teks asli atau input user.
        Jangan menggabungkan paragraf.
        Gunakan huruf kapital yang sama jika pada kalimat atau kata pada input user menggunakan huruf kapital.
        Jangan mengajak mengobrol seperti fitur chatbot. anda hanya menterjemahkan input dari user seperti google translater.
        Jangan menambahkan kata bahasa sunda yang memang bukan arti dari kalimat bahasa indonesia tersebut.
        Sesuaikan gaya bahasanya agar cocok dengan konteks relasi antarpenutur dalam hal ini teman sebaya anak-anak umur 7 - 10 tahun.
        Perintah anda hanya terjemahkan dari input user, bukan menjawab hal lain. Jangan menggunakan kata awalan atau sapaan sebagai tambahan jawaban.
        Jangan beri penjelasan atau keterangan tambahan, langsung berikan hasil terjemahannya saja. 
        Jangan jadikan semua huruf pada awal kata huruf kapital kecuali nama tempat dan nama orang.
        Huruf pada awal kalimat dan setelah titik serta setelah petik dua atau setelah paragraf harus huruf kapital.
        Nama orang dan nama tempat juga harus berawalan huruf kapital.
        Kalimat: {user_input}"""
        
    elif fitur == "terjemahsundaindo":
        final_prompt = f"""Kamu adalah penerjemah yang ahli bahasa indonesia dan bahasa sunda.
        Terjemahkan kalimat berikut ke dalam Bahasa Indonesia yang baku dan mudah dimengerti.
        Jaga agar format paragraf dan barisnya tetap sama persis seperti teks asli atau input user.
        Jangan menggabungkan paragraf.
        Gunakan huruf kapital yang sama jika pada kalimat atau kata pada input user menggunakan huruf kapital.
        Jangan mengajak mengobrol seperti fitur chatbot, anda hanya menterjemahkan input dari user seperti google translate.
        Jangan tambahkan penjelasan atau keterangan apa pun. Langsung tampilkan hasil terjemahannya.
        Jangan jadikan semua huruf pada awal kata huruf kapital, kecuali nama orang dan nama tempat.
        Huruf pada awal kalimat dan setelah titik serta setelah petik dua atau setelah paragraf harus huruf kapital.
        Nama orang dan nama tempat juga harus berawalan huruf kapital.
        Kalimat: {user_input}"""

    else:
        # fallback
        final_prompt = f"Jawablah dengan sopan dan informatif: {user_input}"

    # === Panggil LLM Deepseek API di sini ===
    response = call_deepseek_api(history=history, prompt=final_prompt)  # Fungsi ini kamu sesuaikan dengan API Groq kamu
    return response

def bersihkan_superscript(teks):
    # Menghapus superscript angka ¹²³⁴⁵⁶⁷⁸⁹⁰ atau angka biasa setelah huruf
    return re.sub(r'([^\d\s])[\u00B9\u00B2\u00B3\u2070\u2074-\u2079\d]+', r'\1', teks)

def kapitalisasi_awal_kalimat(teks):
    # Bersihkan superscript dulu
    teks = bersihkan_superscript(teks)

    # Pecah berdasarkan paragraf (baris kosong)
    paragraf_list = teks.split("\n\n")
    paragraf_hasil = []

    for paragraf in paragraf_list:
        # Bagi kalimat dalam paragraf berdasarkan tanda baca yang diikuti spasi atau akhir kalimat
        kalimat_list = re.split(r'([.!?]["\']?\s+)', paragraf)
        kalimat_terformat = ""

        for i in range(0, len(kalimat_list), 2):
            if i < len(kalimat_list):
                kalimat = kalimat_list[i].strip()
                if kalimat:
                    kapital = kalimat[0].upper() + kalimat[1:] if len(kalimat) > 1 else kalimat.upper()
                    kalimat_terformat += kapital
            if i + 1 < len(kalimat_list):
                kalimat_terformat += kalimat_list[i+1]

        paragraf_hasil.append(kalimat_terformat.strip())

    # Gabungkan kembali paragraf dengan \n\n
    return "\n\n".join(paragraf_hasil)
    
# def kapitalisasi_awal_kalimat(teks):
#     # Pecah teks berdasarkan titik
#     kalimat_list = re.split(r'([.!?])', teks)
#     hasil = ""
#     for i in range(0, len(kalimat_list), 2):
#         kalimat = kalimat_list[i].strip()
#         if kalimat:
#             kapital = kalimat[0].upper() + kalimat[1:] if len(kalimat) > 1 else kalimat.upper()
#             hasil += kapital
#         if i+1 < len(kalimat_list):
#             hasil += kalimat_list[i+1] + " "
#     return hasil.strip()

