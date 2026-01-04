import json
import pickle
from rekomendasi import Recommender
from chatbot_response import ChatbotResponse
from NLP.intent_handler import PengenalanIntent


class Chatbot:
    def __init__(self, dataset_path, intent_path, template_path, 
                 preprocessor_path, model_path, vectorizer_path):

        # load preprocessor yang udah dilatih buat bersihin text
        file_preprocessor = open(preprocessor_path, "rb")
        self.preprocessor = pickle.load(file_preprocessor)
        file_preprocessor.close()
        
        self.intent_handler = PengenalanIntent(
            intent_path=intent_path,
            model_path=model_path,
            vectorizer_path=vectorizer_path,
            template_path=template_path,
        )
        
        # bikin object recommender buat nyari anime dari dataset
        self.core = Recommender(dataset_path)
        
        # bikin object generator buat format response chatbot
        self.generator = ChatbotResponse(template_path)
        
        # maksimal 5 anime yang ditampilin
        self.max_hasil = 5

    def chat(self, input_user, excluded_names=None, last_recommendations=None, last_genre=None):
        if excluded_names is None:
            excluded_names = []
        if last_recommendations is None:
            last_recommendations = []
        if last_genre is None:
            last_genre = []
        
        print("Input:", input_user)
        print("Excluded names:", excluded_names)
        print("Last genre:", last_genre)
        
        input_bersih = self.preprocessor.text_preprocessing(input_user)
        print("Input bersih:", input_bersih)
        
        intent = self.intent_handler.pilih_tag(input_bersih)
        print("Intent:", intent)
        
        # Handler nanyain genre
        if intent == "nanyain_genre":
            penjelasan = self._handle_nanyain_genre(input_bersih)
            return penjelasan
        
        # Handler minta rekomendasi
        if intent == "minta_rekomendasi":
            return self._handle_rekomendasi(input_bersih, excluded_names, last_genre)
        
        # Handler komplain hasil
        if intent == "komplain_hasil":
            return self._handle_komplain(input_bersih, excluded_names, 
                                        last_recommendations, last_genre, "komplain")
        
        # Handler udah pernah nonton
        if intent == "udah_pernah_nonton":
            return self._handle_komplain(input_bersih, excluded_names, 
                                        last_recommendations, last_genre, "udah_nonton")
        
        # Intent lainnya
        return self.intent_handler.ambil_respon(intent)
    
    def _extract_nomor_multiple(self, input_bersih):
        """Extract SEMUA nomor dari input yang udah di-preprocess"""
        import re
        
        nomor_list = []
        
        # Mapping kata ke angka
        kata_ke_angka = {
            'satu': 1,
            'dua': 2,
            'tiga': 3,
            'empat': 4,
            'lima': 5,
            'semua': [1, 2, 3, 4, 5],
            'semuanya': [1, 2, 3, 4, 5]
        }
        
        # Split input jadi tokens
        tokens = input_bersih.split()
        
        # 1. Extract dari kata mapping
        for token in tokens:
            if token in kata_ke_angka:
                nilai = kata_ke_angka[token]
                
                if isinstance(nilai, list):
                    for angka in nilai:
                        if angka not in nomor_list:
                            nomor_list.append(angka)
                else:
                    if nilai not in nomor_list:
                        nomor_list.append(nilai)
        
        # 2. Extract angka langsung dari input
        angka_matches = re.findall(r'\d+', input_bersih)
        for match in angka_matches:
            angka = int(match)
            if angka not in nomor_list:
                nomor_list.append(angka)
        
        return nomor_list if nomor_list else None
    
    def _handle_komplain(self, input_bersih, excluded_names, 
                        last_recommendations, last_genre, intent_type="komplain"):
        """Handle komplain hasil & udah pernah nonton"""
        
        # Extract nomor
        nomor_list = self._extract_nomor_multiple(input_bersih)
        print("Nomor terdeteksi:", nomor_list)
        
        # IF: Ada nomor → Process exclusion
        if nomor_list is not None and len(nomor_list) > 0:
            # Cek apakah ada last_recommendations
            if len(last_recommendations) == 0 or len(last_genre) == 0:
                if intent_type == "udah_nonton":
                    return self.generator.ambil_template_respon("belum_ada_rekomendasi_udah_nonton")
                else:
                    return self.generator.ambil_template_respon("belum_ada_rekomendasi_komplain")
            
            anime_ditolak_names = []
            invalid_numbers = []
            
            # Loop semua nomor
            for nomor in nomor_list:
                # Validasi nomor
                if nomor < 1 or nomor > len(last_recommendations):
                    invalid_numbers.append(nomor)
                    continue
                
                # Ambil anime
                anime_ditolak = last_recommendations[nomor - 1]
                anime_name = anime_ditolak.get('name', '')
                
                # Exclude
                if anime_name and anime_name not in excluded_names:
                    excluded_names.append(anime_name)
                    anime_ditolak_names.append(anime_name)
            
            # Kalau semua nomor invalid
            if len(anime_ditolak_names) == 0:
                if len(invalid_numbers) == 1:
                    return f"Hmm, kayaknya ga ada nomor {invalid_numbers[0]} di rekomendasi terakhir deh 😅"
                else:
                    return f"Hmm, kayaknya ga ada nomor {', '.join(map(str, invalid_numbers))} di rekomendasi terakhir deh 😅"
            
            # Generate rekomendasi baru
            df_hasil = self.core.recommender(last_genre, excluded_names)
            
            if df_hasil.empty:
                genre_str = ", ".join(last_genre)
                return self.generator.format_stock_habis(genre_str)
            
            df_top = df_hasil.head(self.max_hasil)
            
            # Format response (single vs multiple)
            if len(anime_ditolak_names) == 1:
                if intent_type == "udah_nonton":
                    return self.generator.format_respon_udah_nonton_spesifik(
                        df_top, anime_ditolak_names[0]
                    )
                else:
                    return self.generator.format_respon_komplain_spesifik(
                        df_top, anime_ditolak_names[0]
                    )
            else:
                if intent_type == "udah_nonton":
                    return self.generator.format_respon_udah_nonton_multiple(
                        df_top, anime_ditolak_names
                    )
                else:
                    return self.generator.format_respon_komplain_multiple(
                        df_top, anime_ditolak_names
                    )
        
        # ELSE: Ga ada nomor → Intent response
        else:
            # Kalau belum pernah ada rekomendasi, kasih response khusus
            if len(last_recommendations) == 0:
                if intent_type == "udah_nonton":
                    return self.generator.ambil_template_respon("belum_ada_rekomendasi_udah_nonton")
                else:
                    return self.generator.ambil_template_respon("belum_ada_rekomendasi_komplain")
            
            # Kalau udah pernah ada rekomendasi, kasih response dari intent
            if intent_type == "udah_nonton":
                return self.intent_handler.ambil_respon("udah_pernah_nonton")
            else:
                return self.intent_handler.ambil_respon("komplain_hasil")
    
    def _handle_rekomendasi(self, input_bersih, excluded_names, last_genre):
        """Handle minta rekomendasi"""
        genre = self.core.ekstrak_genre(input_bersih)
        
        if len(genre) == 0:
            return self.intent_handler.ambil_respon("minta_rekomendasi")
        
        # Update last_genre
        last_genre.clear()
        last_genre.extend(genre)
        
        df_hasil = self.core.recommender(genre, excluded_names)
        
        if df_hasil.empty:
            return self.generator.ambil_template_respon("gak_ada_hasil")
        
        df_top = df_hasil.head(self.max_hasil)
        return self.generator.format_respon_rekomendasi(df_top, genre)
    
    def _handle_nanyain_genre(self, input_bersih):
        """Handle pertanyaan tentang genre"""
        # Extract genre dari input
        genre = self.core.ekstrak_genre(input_bersih)
        
        if len(genre) == 0:
            return self.generator.ambil_template_respon("genre_ga_ketemu")
        
        # Ambil penjelasan genre pertama yang ditemukan
        penjelasan = self.generator.ambil_penjelasan_genre(genre[0])
        
        if penjelasan:
            return penjelasan
        else:
            return self.generator.ambil_template_respon("genre_ga_ada_penjelasan")