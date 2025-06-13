from openai import OpenAI
import os
import streamlit as st
import re
import string
from supabase_helper import *
import requests
import json
import fitz  # PyMuPDF
import docx
from PIL import Image
import easyocr
import tiktoken

relasi_tutur = {
    "bapak": {"anak": "LOMA", "istri": "LOMA", "teman": "LOMA", "atasan": "HALUS"},
    "ibu": {"anak": "LOMA", "suami": "LOMA", "teman": "LOMA", "atasan": "HALUS"},
    "anak": {"bapak": "HALUS", "ibu": "HALUS", "teman": "LOMA/KASAR", "guru": "HALUS"},
    "atasan": {"bawahan": "LOMA"}
}

def deteksi_relasi_kutipan(teks):
    hasil = []
    pola = r"(\w+)\s+berkata\s+kepada\s+(\w+):\s+\"(.*?)\""
    cocok = re.findall(pola, teks, flags=re.IGNORECASE)

    for pembicara, pendengar, kutipan in cocok:
        pembicara = pembicara.lower()
        pendengar = pendengar.lower()
        tingkat = relasi_tutur.get(pembicara, {}).get(pendengar, "L1")
        hasil.append({
            "pembicara": pembicara,
            "pendengar": pendengar,
            "kutipan": kutipan,
            "tingkat": tingkat
        })
    return hasil

# Fungsi untuk memanggil Deepseek API
def call_deepseek_api(prompt, history=None,  system_instruction=None):
    api_key = st.secrets["API_KEY"]
    url = "https://api.deepseek.com/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    else:
        messages.append({"role": "system", "content": "You are a helpful assistant."})
        
    if history:
        for msg in history:
            messages.append({"role": "user", "content": msg["message"]})
            messages.append({"role": "assistant", "content": msg["response"]})

    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.5,
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()  # trigger exception if HTTP error
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        st.error(f"Error DeepSeek: {e}")
        return "Maaf, terjadi kesalahan saat memproses permintaan Anda."

def generate_text_deepseek(user_input, fitur, pasangan_cag, mode_bahasa="Sunda", chat_mode = "Ngobrol", history=None):
    user_age = 30  # Default
    if "user" in st.session_state:
        try:
            profile = supabase.table("profiles").select("age").eq("id", st.session_state.user.id).execute()
            if profile.data:
                user_age = profile.data[0]["age"]
        except:
            pass

    klasifikasi_bahasa = "LOMA" if user_age < 30 else "HALUS"

    system_instruction = ""
    user_prompt = user_input

    # ✨ Tambahan: Deteksi kutipan langsung dan sisipkan ke system_instruction
    kutipan_terdeteksi = deteksi_relasi_kutipan(user_prompt)
    if kutipan_terdeteksi:
        info_kutipan = "\n".join([
            f"Pembicara: {k['pembicara']}, Pendengar: {k['pendengar']}, Tingkat tutur: {k['tingkat']}, Kutipan: \"{k['kutipan']}\""
            for k in kutipan_terdeteksi
        ])
        system_instruction = f"Tolong pahami dan gunakan tingkat tutur dalam bahasa Sunda sesuai relasi berikut:\n{info_kutipan}\n\n" + system_instruction
        
    # Instruksi berdasarkan fitur dan mode bahasa
    if fitur == "chatbot":
        if mode_bahasa == "Sunda":
            if chat_mode == "Ngobrol":
                system_instruction = f"Jawablah hanya dalam Bahasa Sunda {klasifikasi_bahasa}. Jawab pertanyaannya mau itu Bahasa Sunda, Bahasa Indonesia atau English tapi tetap jawab pakai Bahasa Sunda Loma. Gunakan tata bahasa sunda yang baik dan benar."
            elif chat_mode == "Belajar":
                system_instruction = f"""Anda adalah asisten untuk pelajar Bahasa Sunda.
                                    Jawablah hanya dalam Bahasa Sunda {klasifikasi_bahasa}, dengan gaya edukatif dan mudah dipahami oleh pelajar berusia {user_age} tahun.
                                    """
        elif mode_bahasa == "Indonesia":
            if chat_mode == "Ngobrol":
                system_instruction = "Jawablah hanya dalam Bahasa Indonesia. Jawab pertanyaannya mau itu Bahasa Indonesia, Bahasa Sunda atau English tapi tetap jawab pakai Bahasa Indonesia."
            elif chat_mode == "Belajar":
                system_instruction = "Anda adalah asisten untuk pelajar."
        elif mode_bahasa == "English":
            if chat_mode == "Ngobrol":
                system_instruction = "Please respond only in British English. Answer the questions whether it is in Indonesian, Sundanese or English but always answer in English"
            elif chat_mode == "Belajar":
                system_instruction = "You are an assistant for students."
        else:
            system_instruction = ""
                    
        system_instruction += f"""
        Anda adalah Lestari, chatbot yang interaktif membantu pengguna belajar bahasa Indonesia, English, dan Sunda serta menjawab pertanyaan secara ramah dan jelas informasinya.
        Anda berumur 30 tahun. Jika anda ditanya "Kumaha damang?" tolong jawab "Sae, anjeun kumaha?" tapi selain ditanya itu jangan jawab "Sae, anjeun kumaha?".
        Lawan bicara anda berumur {user_age} tahun. tolong sesuaikan gaya bicara anda dengan umur lawan bicara anda.
        Jangan memberi keterangan catatan dibawahnya.
        Jangan memberikan informasi yang tidak tentu kebenarannya.
        Jangan gunakan huruf-huruf aneh seperti kanji korea, kanji jepang, atau kanji china.
        Jangan gunakan asterisk atau tanda ** sebagai penekanan pada suatu kata, lebih baik hindari penekanan terhadap suatu kata.
        tolong sesuaikan format paragraf kalimat teks dari user dengan jawaban anda.
        Gunakan huruf kapital pada awal kalimat dan setelah tanda titik serta setelah petik dua atau setelah paragraf.
        Gunakan huruf kapital pada awal nama orang dan nama tempat.
        Gunakan huruf kapital yang sama jika pada kalimat atau kata pada input user menggunakan huruf kapital.
        Jangan menggabungkan paragraf.
        Selalu akhiri dengan pertanyaan. "
        """
        # Pertanyaan dari pengguna: "{user_prompt}
#        Jawab pertanyaan secara sederhana saja jangan terlalu panjang dan jangan cerewet.


    elif fitur == "terjemahindosunda":
        system_instruction = f"""Kamu adalah penerjemah yang ahli bahasa sunda dan bahasa indonesia.
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
        """
        
    elif fitur == "terjemahsundaindo":
        system_instruction = f"""Kamu adalah penerjemah yang ahli bahasa indonesia dan bahasa sunda.
        Terjemahkan kalimat berikut ke dalam Bahasa Indonesia yang baku dan mudah dimengerti.
        Jaga agar format paragraf dan barisnya tetap sama persis seperti teks asli atau input user.
        Jangan menggabungkan paragraf.
        Gunakan huruf kapital yang sama jika pada kalimat atau kata pada input user menggunakan huruf kapital.
        Jangan mengajak mengobrol seperti fitur chatbot, anda hanya menterjemahkan input dari user seperti google translate.
        Jangan tambahkan penjelasan atau keterangan apa pun. Langsung tampilkan hasil terjemahannya.
        Jangan jadikan semua huruf pada awal kata huruf kapital, kecuali nama orang dan nama tempat.
        Huruf pada awal kalimat dan setelah titik serta setelah petik dua atau setelah paragraf harus huruf kapital.
        Nama orang dan nama tempat juga harus berawalan huruf kapital.
        """
        # Kalimat: {user_prompt}"""

    else:
        # fallback
        system_instruction = f"Jawablah dengan sopan dan informatif: {user_prompt}"

    formatted_history = [{"message": m[0], "response": m[1]} for m in history] if history else None

    response = call_deepseek_api(prompt=user_prompt, history=formatted_history, system_instruction=system_instruction)
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

def hitung_token(teks):
    enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(teks))

reader = easyocr.Reader(['id', 'en'])  # Tambahkan 'su' untuk Bahasa Sunda

def ekstrak_teks(file):
    if file.type == "application/pdf":
        import fitz  # PyMuPDF
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "\n".join(page.get_text() for page in doc)

    elif file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        import docx
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])

    elif file.type.startswith("image/"):
        from PIL import Image
        import numpy as np
        img = Image.open(file).convert("RGB")
        img_array = np.array(img)
        results = reader.readtext(img_array, detail=0)
        return "\n".join(results)

    else:
        return "❌ Jenis file tidak didukung."
    

