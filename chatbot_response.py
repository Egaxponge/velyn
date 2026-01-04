import json
import pandas as pd
import random
from genre_explanations import GENRE_EXPLANATIONS

class ChatbotResponse:
    def __init__(self, template_path):
        file_template = open(template_path, "r", encoding="utf-8")
        self.template_respon = json.load(file_template)
        file_template.close()

    def ambil_template_respon(self, key): 
        # ambil response berdasarkan key 
        pilihan = self.template_respon[key]
        
        # kalo responsenya list, pilih random biar ga monoton
        if isinstance(pilihan, list):
            return random.choice(pilihan)
        else:
            # kalo cuma string biasa, langsung return aja
            return pilihan

    def ambil_penjelasan_genre(self, nama_genre):
        # ubah genre jadi lowercase buat pencocokan dengan dictionary
        genre_lower = nama_genre.lower()
        
        # cek apakah genre ini ada penjelasannya
        if genre_lower in GENRE_EXPLANATIONS:
            penjelasan = GENRE_EXPLANATIONS[genre_lower]
            # format jadi HTML dengan nama genre di-bold
            hasil = "<b>" + nama_genre.title() + "</b> " + penjelasan
            return hasil
        
        # kalo ga ada penjelasan, return None
        return None

    def format_stock_habis(self, genre_str):
        """Format response kalau stock anime habis"""
        template = self.ambil_template_respon("stock_habis")
        return template.format(criteria=genre_str)
    
    def format_respon_komplain_spesifik(self, df_hasil, anime_name):
        """Format response komplain spesifik (ada 1 nomor)"""
        # Header
        header = self.ambil_template_respon("komplain_spesifik_header")
        respon = header.format(anime_name=anime_name)
        
        # Cards
        respon += self._build_anime_cards(df_hasil)
        
        # Footer
        footer = self.ambil_template_respon("soft_footer")
        respon += footer
        
        return respon.strip()
    
    def format_respon_komplain_multiple(self, df_hasil, anime_names):
        """Format response komplain multiple (ada 2+ nomor)"""
        # Format nama anime jadi string natural
        if len(anime_names) == 2:
            # "X dan Y"
            anime_str = f"{anime_names[0]} dan {anime_names[1]}"
        else:
            # "X, Y, dan Z"
            anime_str = ", ".join(anime_names[:-1]) + f", dan {anime_names[-1]}"
        
        # Header
        header = f"Noted! Kalau {anime_str} bukan tipe kamu, aku cariin alternatif lain ya:\n\n"
        
        # Cards
        respon = header + self._build_anime_cards(df_hasil)
        
        # Footer
        footer = self.ambil_template_respon("soft_footer")
        respon += footer
        
        return respon.strip()
    
    def format_respon_udah_nonton_spesifik(self, df_hasil, anime_name):
        """Format response udah pernah nonton spesifik (ada 1 nomor)"""
        header = f"Baiklah! Kalau {anime_name} udah pernah ditonton, ini aku kasih alternatif lain ya:\n\n"
        respon = header + self._build_anime_cards(df_hasil)
        footer = self.ambil_template_respon("soft_footer")
        return (respon + footer).strip()

    def format_respon_udah_nonton_multiple(self, df_hasil, anime_names):
        """Format response udah pernah nonton multiple (ada 2+ nomor)"""
        if len(anime_names) == 2:
            anime_str = f"{anime_names[0]} dan {anime_names[1]}"
        else:
            anime_str = ", ".join(anime_names[:-1]) + f", dan {anime_names[-1]}"
        
        header = f"Baiklah! Kalau {anime_str} udah pernah ditonton, ini alternatif lainnya:\n\n"
        respon = header + self._build_anime_cards(df_hasil)
        footer = self.ambil_template_respon("soft_footer")
        return (respon + footer).strip()
    
    def format_respon_komplain_umum(self, df_hasil):
        """Format response komplain umum (ga ada nomor)"""
        # Header
        header = self.ambil_template_respon("komplain_umum_header")
        respon = header
        
        # Cards
        respon += self._build_anime_cards(df_hasil)
        
        # Footer
        footer = self.ambil_template_respon("soft_footer")
        respon += footer
        
        return respon.strip()

    def format_respon_rekomendasi(self, df_hasil, genre_dicari=None):
        # kalo hasil kosong, kasih response ga ketemu
        if df_hasil.empty:
            return self.ambil_template_respon("gak_ada_hasil")

        # bikin header response
        if genre_dicari:
            # ambil template header
            template = self.ambil_template_respon("header_kasih_rekomendasi")
            
            # gabungin genre yang dicari jadi string (misal: "action, romance, comedy")
            kriteria = ""
            for i in range(len(genre_dicari)):
                if i == 0:
                    kriteria = genre_dicari[i]
                else:
                    kriteria = kriteria + ", " + genre_dicari[i]
            
            # format template dengan kriteria yang dicari
            respon = template.format(criteria=kriteria)
        else:
            respon = self.ambil_template_respon("header_kasih_rekomendasi")

        # Build cards
        respon += self._build_anime_cards(df_hasil)
        
        # tambahin footer di akhir response
        footer = self.ambil_template_respon("soft_footer")
        respon = respon + footer
        
        # hapus spasi di awal/akhir
        respon = respon.strip()
        return respon

    def _build_anime_cards(self, df_hasil):
        """Build HTML cards untuk anime"""
        cards_html = ""
        no = 1
        
        for index in range(len(df_hasil)):
            anime = df_hasil.iloc[index]
            
            # ambil data genres dan themes dari anime
            genres_raw = anime.get("genres", "")
            themes_raw = anime.get("themes", "")
            
            # split genres jadi list
            genre_list = []
            if pd.notna(genres_raw) and genres_raw:
                genre_split = str(genres_raw).split(",")
                for g in genre_split:
                    genre_list.append(g.strip())
            
            # split themes jadi list
            tema_list = []
            if pd.notna(themes_raw) and themes_raw:
                tema_split = str(themes_raw).split(",")
                for t in tema_split:
                    tema_list.append(t.strip())
            
            # gabungin list genre jadi string (action, romance, comedy)
            teks_genre = ""
            if len(genre_list) > 0:
                for i in range(len(genre_list)):
                    if i == 0:
                        teks_genre = genre_list[i]
                    else:
                        teks_genre = teks_genre + ", " + genre_list[i]
            
            # gabungin list tema jadi string
            teks_tema = ""
            if len(tema_list) > 0:
                for i in range(len(tema_list)):
                    if i == 0:
                        teks_tema = tema_list[i]
                    else:
                        teks_tema = teks_tema + ", " + tema_list[i]
            
            # bikin HTML buat info genre dan tema
            info_parts = []
            if teks_genre != "":
                part_genre = '<span class="info-label">Genre:</span> <span class="info-value">' + teks_genre + '</span>'
                info_parts.append(part_genre)
            if teks_tema != "":
                part_tema = '<span class="info-label">Tema:</span> <span class="info-value">' + teks_tema + '</span>'
                info_parts.append(part_tema)
            
            # gabungin genre dan tema dengan separator bullet
            html_info = ""
            for i in range(len(info_parts)):
                if i == 0:
                    html_info = info_parts[i]
                else:
                    html_info = html_info + ' <span class="info-separator">•</span> ' + info_parts[i]
            
            # format jumlah episode
            # kalo episode > 100 berarti ada masalah data, bagi 100
            episode_display = "Tidak tersedia"
            if pd.notna(anime.get("episodes")) and anime["episodes"] != "":
                try:
                    ep = float(anime["episodes"])
                    if ep < 100:
                        episode_display = str(int(ep))
                    else:
                        episode_display = str(int(round(ep / 100)))
                except:
                    pass
            
            # kumpulin semua data anime ke dictionary
            # data ini nanti bakal di-encode jadi JSON buat tombol detail
            data_anime = {}
            
            if anime.get("name"):
                data_anime["name"] = str(anime.get("name"))
            else:
                data_anime["name"] = "Tidak tersedia"
            
            if pd.notna(anime.get("english_name")) and anime.get("english_name"):
                data_anime["english_name"] = str(anime["english_name"])
            else:
                data_anime["english_name"] = "Tidak tersedia"
            
            if pd.notna(anime.get("score")):
                data_anime["score"] = float(anime["score"])
            else:
                data_anime["score"] = "Tidak tersedia"
            
            if pd.notna(anime.get("premiered")) and anime.get("premiered"):
                data_anime["premiered"] = str(anime["premiered"])
            else:
                data_anime["premiered"] = "Tidak tersedia"
            
            data_anime["episodes"] = episode_display
            
            if pd.notna(anime.get("duration")) and anime.get("duration"):
                data_anime["duration"] = str(anime["duration"])
            else:
                data_anime["duration"] = "Tidak tersedia"
            
            if teks_genre != "":
                data_anime["genres"] = teks_genre
            else:
                data_anime["genres"] = "Tidak ada"
            
            if teks_tema != "":
                data_anime["themes"] = teks_tema
            else:
                data_anime["themes"] = "Tidak ada"
            
            if pd.notna(anime.get("synopsis")) and anime.get("synopsis"):
                data_anime["synopsis"] = str(anime["synopsis"])
            else:
                data_anime["synopsis"] = "Sinopsis tidak tersedia"
            
            if pd.notna(anime.get("image_url")) and anime.get("image_url"):
                data_anime["image_url"] = str(anime["image_url"])
            else:
                data_anime["image_url"] = ""
            
            if pd.notna(anime.get("anime_url")) and anime.get("anime_url"):
                data_anime["anime_url"] = str(anime["anime_url"])
            else:
                data_anime["anime_url"] = ""
            
            # convert dictionary jadi JSON string
            json_str = json.dumps(data_anime)
            # ganti double quote jadi HTML entity biar aman di attribute HTML
            json_encoded = json_str.replace('"', "&quot;")
            
            # bikin HTML card buat setiap anime
            card_html = '<div class="anime-card">'
            # judul anime dengan nomor urut
            card_html = card_html + '<div class="anime-title">' + str(no) + '. ' + anime['name'] + '</div>'
            # info genre dan tema
            card_html = card_html + '<div class="anime-info-row">' + html_info + '</div>'
            # tombol lihat detail (data anime disimpen di attribute data-anime)
            card_html = card_html + '<button class="detail-btn" data-anime="' + json_encoded + '">Lihat Detail</button>'
            card_html = card_html + '</div>'
            
            # tambahin card ke cards_html
            cards_html = cards_html + card_html
            no = no + 1
        
        return cards_html