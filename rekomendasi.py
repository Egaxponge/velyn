import pandas as pd
import re
from mapping import GENRE_MAPPING, THEME_MAPPING


class Recommender:
    # list kata kunci buat deteksi anime sequel
    # anime dengan keyword ini bakal difilter biar ga masuk rekomendasi
    SEQUEL_KEYWORDS = [
        ' season', ' part', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9', 's10',
        ' 2nd season', ' 3rd season', ' 4th season', ' final season',
        ' 2nd', ' 3rd', ' 4th', ' 5th', ' 6th', ' 7th', ' 8th', ' 9th', ' 10th',
        ' ii', ' iii', ' iv', ' v', ' vi', ' vii', ' viii', ' ix', ' x',
        ' the movie', ' avenging battle', ' progressive movie', ' movie', ' episode nagi', ' returns',
        ' shippuden', ' brotherhood', ' kai', 'the last', 'boruto',
        'enchousen', 'yorinuki', 'porori', 'jump festa', ' hen','horimiya: piece', ': prelude', ': after story' 
        ,'one piece: ', 'one piece film:', 'film', 'shingeki no kyoujin: ', ' alternative: ', ': sinbad', ' nube: '
        ,'haikyuu to the top', ': the final', 'tamayura: ', ' chronicle: ', 'ginyuu mokushiroku meine liebe wieder'
        ,' ippo: ', ' tsubasa: ', 'violet evergarden gaiden: '
    ]
    
    def __init__(self, dataset_path):
        # load dataset anime dari file csv
        self.df_anime = pd.read_csv(dataset_path, sep=",")

        # normalisasi skor anime yang kebesaran (ada skor yang dalam bentuk 800 harusnya 8.00)
        skor_baru = []
        for skor in self.df_anime['score']:
            if skor > 10:
                # bagi 100 buat skor yang kebesaran
                skor_baru.append(float(skor) / 100)
            else:
                skor_baru.append(float(skor))
        self.df_anime['score'] = skor_baru
        
        # gabungin kolom genres sama themes jadi satu
        # biar lebih gampang pas nyari anime berdasarkan genre
        gabungan_list = []
        for index in range(len(self.df_anime)):
            row = self.df_anime.iloc[index]
            hasil_gabung = self._gabungkan_genre_tema(row)
            gabungan_list.append(hasil_gabung)
        self.df_anime['genre_tema_gabungan'] = gabungan_list
        
        # buang anime yang ga punya genre/tema sama sekali
        df_baru = []
        for index in range(len(self.df_anime)):
            if pd.notna(self.df_anime.iloc[index]['genre_tema_gabungan']):
                df_baru.append(self.df_anime.iloc[index])
        self.df_anime = pd.DataFrame(df_baru)
        self.df_anime = self.df_anime.reset_index(drop=True)

        # ubah semua genre jadi huruf kecil biar pencocokan lebih gampang
        gabungan_lower = []
        for gabung in self.df_anime['genre_tema_gabungan']:
            gabungan_lower.append(gabung.lower())
        self.df_anime['genre_tema_gabungan'] = gabungan_lower
        
        # bersihin genre dari karakter aneh (tanda hubung, kurung, spasi dobel)
        # terus pisahin per genre jadi list
        genre_normalized_list = []
        for gabung in self.df_anime['genre_tema_gabungan']:
            genre_split = str(gabung).split(",")
            genre_bersih = []
            for g in genre_split:
                g = g.strip()
                g = g.replace("-", " ")  # ganti - jadi spasi
                g = g.replace("(", "")   # hapus kurung buka
                g = g.replace(")", "")   # hapus kurung tutup
                g = re.sub(r"\s+", " ", g)  # hapus spasi dobel/tripel jadi satu spasi
                g = g.strip()
                genre_bersih.append(g)
            genre_normalized_list.append(genre_bersih)
        self.df_anime['genres_normalized'] = genre_normalized_list
        
        # filter cuma ambil anime tipe TV sama Movie aja
        # buang yang OVA, ONA, Special, dll
        df_filtered_type = []
        for index in range(len(self.df_anime)):
            tipe = self.df_anime.iloc[index]['type']
            if tipe in ['TV', 'Movie']:
                df_filtered_type.append(self.df_anime.iloc[index])
        self.df_anime = pd.DataFrame(df_filtered_type)
        
        # buang anime yang punya genre ini
        blacklist = {"boys love", "ecchi", "erotica", "girls love", "hentai"}
        df_filtered = []
        for index in range(len(self.df_anime)):
            genres = self.df_anime.iloc[index]['genres_normalized']
            punya_blacklist = False
            for g in genres:
                if g in blacklist:
                    punya_blacklist = True
                    break
            if not punya_blacklist:
                df_filtered.append(self.df_anime.iloc[index])
        
        self.df_anime = pd.DataFrame(df_filtered)
        self.df_anime = self.df_anime.reset_index(drop=True)
        
        # filter anime sequel
        # cuma ambil anime season pertama aja biar rekomendasinya ga banyak sequel
        df_no_sequel = []
        for index in range(len(self.df_anime)):
            title = self.df_anime.iloc[index]['name']
            title_lower = str(title).lower()
            
            # cek apakah judulnya mengandung keyword sequel
            ada_keyword = False
            for keyword in self.SEQUEL_KEYWORDS:
                if keyword in title_lower:
                    ada_keyword = True
                    break
            
            # kalo ga ada keyword sequel, masukkan ke list
            if not ada_keyword:
                df_no_sequel.append(self.df_anime.iloc[index])
        
        self.df_anime = pd.DataFrame(df_no_sequel)
        self.df_anime = self.df_anime.reset_index(drop=True)
        
        # kumpulin semua genre unik dari dataset
        self.semua_genre_tema = self._kumpulkan_genre()
        
        # gabungin mapping genre dari file mapping.py
        # ini buat handle sinonim genre (misal: romansa ke romance)
        self.normalisasi_genre = {}
        for key in GENRE_MAPPING:
            self.normalisasi_genre[key] = GENRE_MAPPING[key]
        for key in THEME_MAPPING:
            self.normalisasi_genre[key] = THEME_MAPPING[key]
        
        # urutkan genre multi-kata dari yang paling panjang
        # biar pas ekstraksi, genre panjang diproses duluan (misal: "slice of life" sebelum "action")
        genre_panjang_temp = []
        for g in self.semua_genre_tema:
            if len(g.split()) > 1:
                genre_panjang_temp.append(g)
        
        # sorting manual dari panjang ke pendek
        genre_panjang_sorted = []
        while len(genre_panjang_temp) > 0:
            terpanjang = genre_panjang_temp[0]
            for g in genre_panjang_temp:
                if len(g.split()) > len(terpanjang.split()):
                    terpanjang = g
            genre_panjang_sorted.append(terpanjang)
            genre_panjang_temp.remove(terpanjang)
        
        self.genre_panjang = genre_panjang_sorted

    def _gabungkan_genre_tema(self, row):
        # ambil kolom genres dari row
        genres = ""
        if pd.notna(row['genres']):
            genres = str(row['genres']).strip()
        
        # ambil kolom themes dari row
        themes = ""
        if pd.notna(row['themes']):
            themes = str(row['themes']).strip()
        
        # gabungin genres sama themes jadi satu string
        hasil = []
        if genres != "":
            hasil.append(genres)
        if themes != "":
            hasil.append(themes)
        
        if len(hasil) > 0:
            return ", ".join(hasil)
        else:
            return None
    
    def _kumpulkan_genre(self):
        # kumpulin semua genre unik dari semua anime
        genre_unik = []
        
        for baris in self.df_anime["genre_tema_gabungan"]:
            if pd.notna(baris):
                # split per koma buat dapetin tiap genre
                genre_split = baris.split(",")
                for genre in genre_split:
                    # bersihin karakter aneh
                    genre = genre.strip()
                    genre = genre.replace("-", " ")
                    genre = genre.replace("(", "")
                    genre = genre.replace(")", "")
                    genre = re.sub(r"\s+", " ", genre)
                    genre = genre.strip()
                    
                    # masukin ke list kalo belum ada (biar ga duplikat)
                    if genre != "" and genre not in genre_unik:
                        genre_unik.append(genre)
        
        return genre_unik

    def ekstrak_genre(self, input_bersih):
        # fungsi buat deteksi genre dari input user yang udah dibersihkan
        genre_ketemu = []
        
        # cek dulu genre multi-kata (kayak "slice of life", "martial arts")
        # diproses duluan biar ga kepotong jadi kata-kata terpisah
        for genre_multi in self.genre_panjang:
            if genre_multi in input_bersih:
                if genre_multi not in genre_ketemu:
                    genre_ketemu.append(genre_multi)
        
        # tandain kata-kata yang udah kepake di genre multi-kata
        # biar ga diproses lagi sebagai genre sendiri
        kata_kepake = []
        for genre in genre_ketemu:
            kata_split = genre.split()
            for kata in kata_split:
                if kata not in kata_kepake:
                    kata_kepake.append(kata)
        
        # sekarang cek genre kata tunggal (kayak "action", "romance")
        tokens = input_bersih.split()
        for kata in tokens:
            # skip kalo kata ini udah dipake di genre multi-kata
            if kata in kata_kepake:
                continue
            
            # cek apakah kata ini adalah genre
            if kata in self.semua_genre_tema:
                if kata not in genre_ketemu:
                    genre_ketemu.append(kata)
            else:
                # cek apakah kata ini sinonim dari genre
                # misal user bilang "romansa", diubah jadi "romance"
                if kata in self.normalisasi_genre:
                    standar = self.normalisasi_genre[kata]
                    if standar in self.semua_genre_tema:
                        if standar not in genre_ketemu:
                            genre_ketemu.append(standar)
        
        return genre_ketemu

    def seleksi_anime(self, genre_dicari, excluded_names=None):
        # fungsi utama buat nyari anime berdasarkan genre yang diminta user
        if excluded_names is None:
            excluded_names = []
        
        hasil = []
        
        # loop semua anime di dataset
        for index in range(len(self.df_anime)):
            anime = self.df_anime.iloc[index]
            
            # Skip anime yang di-exclude
            anime_name = anime.get('name', '')
            if anime_name in excluded_names:
                continue
            
            genre_anime = anime["genres_normalized"]
            
            # hitung berapa genre yang cocok
            cocok = 0
            for g in genre_dicari:
                if g in genre_anime:
                    cocok = cocok + 1
            
            # kalo ada yang cocok, masukin ke hasil
            if cocok > 0:
                data = {}
                # copy semua kolom dari anime
                for col in self.df_anime.columns:
                    data[col] = anime[col]
                # tambahin info jumlah genre yang cocok
                data["jumlah_cocok"] = cocok
                # tambahin info total genre anime ini punya
                data["total_genre"] = len(genre_anime)
                hasil.append(data)
        
        # kalo ga ada hasil, return dataframe kosong
        if len(hasil) == 0:
            return pd.DataFrame()
        
        # convert list jadi dataframe
        df = pd.DataFrame(hasil)
        # sorting berdasarkan:
        # 1. jumlah_cocok (descending) = makin banyak genre cocok makin di atas
        # 2. total_genre (ascending) = yang punya genre lebih sedikit lebih di atas (lebih spesifik)
        # 3. score (descending) = rating lebih tinggi lebih di atas
        df = df.sort_values(by=["jumlah_cocok", "total_genre", "score"], ascending=[False, True, False])
        
        return df

    def recommender(self, genre_dicari, excluded_names=None):
        # fungsi buat manggil seleksi_anime
        # kalo genre kosong langsung return kosong
        if len(genre_dicari) == 0:
            return pd.DataFrame()
        return self.seleksi_anime(genre_dicari, excluded_names)