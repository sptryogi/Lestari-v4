import streamlit as st

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
.content { color: white; font-size: 1em; }
label, input, ::placeholder { color: white !important; background-color: black !important; }
</style>
""",
    unsafe_allow_html=True,
)

# Judul aplikasi
st.title("Typo Checker")

## ========================= User Input =========================
# Input teks dari pengguna
chat_user = st.text_input("Masukkan teks 'Sunda' yang Ingin dicek Typo:")
DEEPSEEK_API_KEY = st.secrets["API_KEY"]
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# Tampilkan hasil input
if chat_user:
    st.write("Teks yang Anda masukkan adalah:")
    st.success(chat_user)

    ## ========================= AI TERJEMAH =========================
    import os
   

    ## ========================= Check Kata tidak ada di kamus =========================
    import pandas as pd
    import re
    import unicodedata

    # Baca data kamus
    df_kamus = pd.read_excel("dataset/dataset_lengkap.xlsx")

    # Isi NaN dengan string kosong lalu split
    # Pastikan SUBLEMA string dan split
    df_kamus["SUBLEMA"] = df_kamus["SUBLEMA"].fillna("").astype(str)
    sublema_list = df_kamus["SUBLEMA"].str.split(",").sum()
    
    # Gabungkan dengan LEMA, pastikan semua string dan tidak NaN
    lema_list = df_kamus["LEMA"].fillna("").astype(str).tolist()
    
    # Gabungkan dan bersihkan
    combined_raw = lema_list + sublema_list
    combined_raw = [str(kata).strip() for kata in combined_raw if isinstance(kata, str)]


    # Fungsi untuk menghapus aksen dari karakter
    def remove_accents(input_str):
        nfkd_form = unicodedata.normalize("NFKD", input_str)
        return "".join([c for c in nfkd_form if not unicodedata.combining(c)])

    # Kalimat asal
    kalimat_asal = re.sub(r"[^a-zA-Z0-9\s\-\u00C0-\u00FF]", "", kalimat_asal)

    # Normalisasi aksen (ubah 'é' menjadi 'e', dll.)
    kalimat_asal = remove_accents(kalimat_asal.lower())

    # Ubah ke list kata
    kata_kalimat = kalimat_asal.split()

    # Cari kata yang tidak ada di combined_raw
    kata_tidak_ada = [
        kata
        for kata in kata_kalimat
        if remove_accents(kata) not in [remove_accents(k) for k in combined_raw]
    ]

    # Output
    print("Kata yang tidak ada di combined_raw:")
    print(kata_tidak_ada)
    st.write(f"Kata Tidak Terdapat:")
    st.success(kata_tidak_ada)

    if kata_tidak_ada:

        ## ========================= Difflib - get_close_matches =========================
        from difflib import get_close_matches

        kata_tidak_ada_dan_calon = {}

        for kata in kata_tidak_ada:
            difflib_calon_kata_pengganti = get_close_matches(
                kata, combined_raw, n=5, cutoff=0.8
            )
            kata_tidak_ada_dan_calon[kata] = difflib_calon_kata_pengganti
            # difflib_calon_kata_pengganti = difflib_calon_kata_pengganti[0]

        kata_tidak_ada_dan_calon = {
            k: v for k, v in kata_tidak_ada_dan_calon.items() if v
        }

        # st.write(f"Calon Kata ± 2-3 Kata: {kata_tidak_ada_dan_calon}")
        # Mengubah ke dalam bentuk list of tuples
        st.write("🧠 Kata tidak ditemukan dan Calon Kata ± 2-3 Kata:")
        for kata, calon_list in kata_tidak_ada_dan_calon.items():
            with st.expander(f"Kata: {kata}"):
                for calon in calon_list:
                    st.markdown(f"- {calon}")

        ## ========================= Cek Struktur =========================
        import pandas as pd
        import string
        import re

        kata_tidak_ada_dan_calon_final = {}

        for kata, list_calon in kata_tidak_ada_dan_calon.items():
            struktur_calon_kata_pengganti = []
            print(f"================={kata}")
            for i, k in enumerate(kata_kalimat):
                if k == kata:
                    kata_sebelum = kata_kalimat[i - 1] if i > 0 else ""
                    kata_setelah = (
                        kata_kalimat[i + 1] if i < len(kata_kalimat) - 1 else ""
                    )
                    for calon in list_calon:
                        kalimat_baru = " ".join(
                            [kata_sebelum, calon, kata_setelah]
                        ).strip()
                        # print(kalimat_baru)
                        # Kalimat yang akan diperiksa
                        # kalimat = f"{kata} dahar imah"
                        # kalimat = f"{kalimat_asal} {kata}"
                        kalimat_baru = "".join(
                            char
                            for char in kalimat_baru
                            if char not in string.punctuation
                        )
                        kalimat_baru = kalimat_baru.lower()

                        # Tokenisasi kalimat (memisahkan berdasarkan spasi)
                        tokens = kalimat_baru.split()
                        print(f"==={kalimat_baru}===")

                        # Fungsi untuk mencari lema dan POS Tag dari kata
                        def get_pos_tag(word):
                            # Cek apakah kata ada di kolom LEMA
                            match_lema = df_kamus[df_kamus["LEMA"] == word]
                            if not match_lema.empty:
                                return match_lema.iloc[0]["KLAS."]

                            # Cek apakah kata ada di dalam daftar SUBLEMA (dipisahkan koma)
                            for _, row in df_kamus.iterrows():
                                sublema_val = row["SUBLEMA"]
                                if isinstance(
                                    sublema_val, str
                                ):  # hanya proses jika SUBLEMA adalah string
                                    sublemas = [
                                        s.strip() for s in sublema_val.split(",")
                                    ]
                                    if word in sublemas:
                                        return row["KLAS."]

                            return None  # Jika tidak ditemukan di LEMA maupun SUBLEMA

                        # Mendapatkan POS Tag untuk setiap token dalam kalimat
                        pos_tags = [get_pos_tag(token) for token in tokens]

                        print("Urutan POS Tag:", pos_tags)

                        # # Menampilkan pasangan kata dan POS Tag
                        # for token, pos_tag in zip(tokens, pos_tags):
                        #     print(f'Kata: {token}, POS Tag: {pos_tag}')

                        # Mengecek urutan POS Tag yang masuk akal
                        def is_pos_tag_sequence_valid(pos_tags):
                            # Aturan urutan POS Tag yang masuk akal
                            valid_sequence = {
                                "N": [
                                    "V",
                                    "Adj",
                                    "P",
                                    "Pro",
                                    None,
                                ],  # Nomina bisa diikuti oleh Verba, Adjektiva, Partikel, atau Numeralia
                                "Pro": [
                                    "V",
                                    "Adj",
                                    "Adv",
                                    "P",
                                    "Modal",
                                    None,
                                ],  # Pronomina bisa diikuti oleh Verba, Adjektiva, Adverbia, atau Partikel
                                "V": [
                                    "N",
                                    "Pro",
                                    "Num",
                                    "Adv",
                                    "Adj",
                                    None,
                                ],  # Verba bisa diikuti oleh Nomina, Numeralia, Adverbia, atau Adjektiva
                                "Adj": [
                                    "P",
                                    "N",
                                    None,
                                ],  # Adjektiva bisa diikuti oleh Partikel atau Nomina
                                "Adv": [
                                    "V",
                                    "Adj",
                                    "Adv",
                                    "Modal",
                                    None,
                                ],  # Adverbia bisa diikuti oleh Verba, Adjektiva, atau Adverbia lain
                                "Num": [
                                    "N",
                                    None,
                                ],  # Numeralia biasanya diikuti oleh Nomina
                                # 'P': ['N', 'Adj', 'Pro', 'Modal', None],            # Partikel bisa diikuti oleh Nomina, Adjektiva, atau Pronomina (misalnya "yang tinggi", "itu besar")
                                "P": [
                                    "N",
                                    "V",
                                    "Adj",
                                    "Pro",
                                    "Modal",
                                    None,
                                ],  # Partikel bisa diikuti oleh Nomina, Adjektiva, atau Pronomina (misalnya "yang tinggi", "itu besar")
                                "Modal": ["V", None],
                                None: [
                                    "N",
                                    "V",
                                    "Adj",
                                    "P",
                                    "Pro",
                                    "Adv",
                                    "Num",
                                    "Modal",
                                    None,
                                ],
                            }

                            for i in range(len(pos_tags) - 1):
                                if pos_tags[i + 1] not in valid_sequence.get(
                                    pos_tags[i], []
                                ):
                                    return (
                                        False  # Jika urutan tidak valid, return False
                                    )
                            return True  # Jika semua urutan valid, return True

                        # Memeriksa apakah urutan POS Tag valid
                        if is_pos_tag_sequence_valid(pos_tags):
                            struktur_calon_kata_pengganti.append(calon)
                            print("Urutan POS Tag valid.")
                        else:
                            print("Urutan POS Tag tidak valid.")

            kata_tidak_ada_dan_calon_final[kata] = struktur_calon_kata_pengganti
            print(f"")

        print(kata_tidak_ada_dan_calon_final)

        # Hapus key dengan list kosong
        kata_tidak_ada_dan_calon_final = {
            k: v for k, v in kata_tidak_ada_dan_calon_final.items() if v
        }

        st.write("🧠 Calon Kata Setelah Validasi Struktur Kata:")
        for kata, calon_list in kata_tidak_ada_dan_calon_final.items():
            with st.expander(f"Kata: {kata}"):
                for calon in calon_list:
                    st.markdown(f"- {calon}")

        ## ========================= Mengambil Arti =========================
        final_dict = {}

        for kata_asli, kandidat_list in kata_tidak_ada_dan_calon_final.items():
            final_dict[kata_asli] = {}
            for kandidat in kandidat_list:
                # Cari di kolom LEMA
                arti_lema = df_kamus.loc[df_kamus["LEMA"] == kandidat]
                
                if not arti_lema.empty:
                    arti1 = arti_lema["ARTI 1"].values[0]
                    if pd.isna(arti1) or str(arti1).strip() == "":
                        arti = arti_lema["ARTI EKUIVALEN 1"].values[0] if "ARTI EKUIVALEN 1" in arti_lema else "Tidak ditemukan"
                    else:
                        arti = arti1
                else:
                    # Cek setiap baris apakah kandidat termasuk dalam SUBLEMA
                    mask_sublema = df_kamus["SUBLEMA"].apply(lambda x: isinstance(x, str) and kandidat in [s.strip() for s in x.split(",")])
                    arti_sublema = df_kamus.loc[mask_sublema]

                    if not arti_sublema.empty:
                        arti1 = arti_sublema["ARTI 1"].values[0]
                        if pd.isna(arti1) or str(arti1).strip() == "":
                            arti = arti_sublema["ARTI EKUIVALEN 1"].values[0] if "ARTI EKUIVALEN 1" in arti_sublema else "Tidak ditemukan"
                        else:
                            arti = arti1
                    else:
                        arti = "Tidak ditemukan"

                final_dict[kata_asli][kandidat] = arti

        # Tampilkan final_dict
        import pprint

        pprint.pprint(final_dict)

        st.write("📘 Calon Kata + Arti:")
        for kata_asli, calon_dict in final_dict.items():
            with st.expander(f"Kata: {kata_asli}"):
                for calon, final in calon_dict.items():
                    st.markdown(f"- **Calon**: `{calon}` → **Arti**: `{final}`")

        ## ========================= AI Checker =========================
        def format_kandidat_kata(kata_asal, kandidat_dict):
            # Check if the value of kandidat_dict is a dictionary
            if isinstance(kandidat_dict, dict):
                hasil = f'Berikut ini adalah kandidat kata pengganti "{kata_asal}":\n'
                for i, (kata, arti) in enumerate(kandidat_dict.items(), start=1):
                    hasil += f"{i}. kata sunda: {kata} - arti dalam bahasa indonesia : {arti}\n"
                return hasil
            else:
                return f"Error: '{kata_asal}' tidak memiliki kandidat kata pengganti yang valid atau data tidak sesuai."

        import time

        kata_pengganti = {}
        # st.write("zzzzz")
        # Iterating over final_dict, which is a dictionary of dictionaries
        for kata_x_ditemukan, sub_dict in final_dict.items():
            start_time = time.time()

            headers = {
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            }
            
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {
                        "role": "user",
                        "content": f"""
                        Pertanyaan: Kata Kata Sunda: '{terjemahan_user}'
                        {format_kandidat_kata(kata_x_ditemukan, sub_dict)}
            
                        Berdasarkan konteks Jawaban Sunda, kata bahasa sunda mana yang paling cocok menggantikan '{kata_x_ditemukan}'? JAWAB HANYA DENGAN 1 KATA BAHASA SUNDA.
                        Jika tidak ada yang cocok TETAP gunakan kata ini '{kata_x_ditemukan}'
                        """,
                    },
                ],
                "temperature": 0.7
            }

            response = requests.post(DEEPSEEK_API_URL, headers=headers, json=payload)
            hasil = response.json()

            kata_pengganti[kata_x_ditemukan] = hasil["choices"][0]["message"]["content"]

        # Ganti kata sesuai kamus kata_pengganti
        for kata_lama, kata_baru in kata_pengganti.items():
            terjemahan_user = terjemahan_user.replace(kata_lama, kata_baru)
        print(terjemahan_user)

        st.write(f"Pasangan Kata dan Kata Pengganti:")
        st.success(kata_pengganti)

        st.write(f"Hasil Terjemahan - Typo Checker:")
        st.success(terjemahan_user)

    else:
        st.write(f"Tidak ada Kata tidak ditemukan")
