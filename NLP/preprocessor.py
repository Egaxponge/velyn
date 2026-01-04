import re
import nltk
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

KAMUS_NORMALISASI = {
    # Pronoun - unifikasi variasi sapaan (PENTING untuk intent yang subjeknya bot)
    "gue": "aku",
    "gw": "aku",
    "ane": "aku",
    "saya": "aku",
    "lu": "kamu",
    "lo": "kamu",
    "elu": "kamu",
    "elo": "kamu",
    "anda": "kamu",
    
    # Salam - unifikasi
    "halo": "hai",
    "hello": "hai",
    "helo": "hai",
    "hi": "hai",
    "hey": "hai",
    
    # Kata tanya - gaul ke formal
    "gimana": "bagaimana",
    "gmn": "bagaimana",
    "gmana": "bagaimana",
    "kenapa": "mengapa",
    "knp": "mengapa",
    "knapa": "mengapa",
    "apaan": "apa",
    "brp": "berapa",
    "dmn": "dimana",
    "dmana": "dimana",
    
    # Negasi - unifikasi SEMUA variasi ke "tidak"
    "gak": "tidak",
    "ga": "tidak",
    "gk": "tidak",
    "ngga": "tidak",
    "nggak": "tidak",
    "enggak": "tidak",
    "gada": "tidak ada",
    "gausah": "tidak usah",
    
    # Kata kerja informal - gaul ke formal (JANGAN langsung stem!)
    "rekomendasiin": "rekomendasikan",
    "rekomenin": "rekomendasikan",
    "rekomen": "rekomendasi",
    "saranin": "sarankan",
    "cariin": "carikan",
    "pilihin": "pilihkan",
    "jelasin": "jelaskan",
    "kasih": "berikan",
    "nanya": "bertanya",
    "nanyain": "tanyakan",
    "ceritain": "ceritakan",
    "tambahin": "tambahkan",
    "nambah": "menambah",
    "tentuin": "tentukan",
    "nentuin": "menentukan",
    "gunain": "gunakan",
    "nggunain": "menggunakan",
    "lakuin": "lakukan",
    "operasiin": "operasikan",
    "tunjukin": "tunjukkan",
    "bikinin": "bikinkan",
    
    # Kata bantu/modal
    "pengen": "ingin",
    "pengin": "ingin",
    "pgn": "ingin",
    "mau": "mau",
    "mo": "mau",
    
    # Kata hubung informal ke formal
    "buat": "untuk",
    "bt": "untuk",
    "utk": "untuk",
    "ama": "dengan",
    "sama": "dengan",
    "dgn": "dengan",
    
    # Status waktu
    "udah": "sudah",
    "udh": "sudah",
    "dah": "sudah",
    "blm": "belum",
    "blum": "belum",
    "belom": "belum",
    "lagi": "sedang",
    "lg": "sedang",
    
    # Kata keterangan jumlah
    "cuma": "hanya",
    "cuman": "hanya",
    "doang": "saja",
    "aja": "saja",
    "banget": "sangat",
    "bgt": "sangat",
    "bnyk": "banyak",
    "byk": "banyak",
    "dikit": "sedikit",
    
    # Kata sifat - HANYA yang beda
    "mantul": "mantap",
    "ok": "oke",
    "okay": "oke",
    "okeh": "oke",
    "seneng": "senang",
    "bete": "kesal",
    "males": "malas",
    "capek": "capai",
    "cape": "capai",
    
    # Kata afirmatif
    "iya": "ya",
    "iye": "ya",
    "yoi": "ya",
    "yap": "ya",
    "yup": "ya",
    "yep": "ya",
    "siap": "ya",
    
    # Kata waktu - HANYA singkatan
    "skrg": "sekarang",
    "skr": "sekarang",
    
    # Typo/singkatan umum
    "bsa": "bisa",
    "klo": "kalau",
    "kalo": "kalau",
    "makasih": "terima kasih",
    "makasi": "terima kasih",
    "thx": "terima kasih",
    "thanks": "terima kasih",
    
    # Domain specific
    "drakor": "drama korea",
    "eps": "episode",
    "ep": "episode",
    
    # Kata khusus untuk disambiguasi intent
    "sinopsis": "sinopsis",  # tetap sinopsis, jangan dinormalisasi
    "sinopsisnya": "sinopsis",
    "bahasa": "bahasa",  # tetap bahasa
    "tamat": "selesai",
    "finish": "selesai",
    "ongoing": "berlanjut",
    "nomer": "nomor",
    "no": "nomor",
    "nmr": "nomor",
    "pertama": "satu",
    "kedua": "dua", 
    "ketiga": "tiga",
    "keempat": "empat",
    "kelima": "lima",
    "1":"satu",
    "2":"dua",
    "3":"tiga",
    "4":"empat",
    "5":"lima",
}

STOPWORDS = {
    # Partikel penegas/emosional (noise yang ga penting)
    "nih", "sih", "dong", "deh", "yah", 
    "loh", "lah", "lho",
    "weh", "wih", "pun", "kah", "kok",
    
    # Interjeksi/filler words (NEW!)
    "ah", "eh", "oh", "hmm", "hm", "um", "uh",
    "aduh", "waduh", "astaga", "duh",
    
    # Kata sopan santun redundan
    "please", "pls", "plis",
    
    # Kata tambahan redundan
    "juga", "kan",
    
    # Kata ganti posesif ambigu
    "nya",

}




class TextPreprocessor:
    def __init__(self):
        factory = StemmerFactory()
        self.stemmer = factory.create_stemmer()
        self.kamus = KAMUS_NORMALISASI
        self.stopwords = STOPWORDS

    def case_folding(self, text):
        if not isinstance(text, str):
            return ""

        text = text.lower()
        text = re.sub(r"[^a-zA-Z0-9\s-]", " ", text)
        text = text.replace("-", " ")
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        return text

    def tokenization(self, text):
        tokens = word_tokenize(text)
        hasil = [t for t in tokens if t.isalnum()]
        return hasil

    def normalization(self, tokens):
        hasil = []
        for token in tokens:
            if token in self.kamus:
                hasil.append(self.kamus[token])
            else:
                hasil.append(token)
        return hasil

    def stopwords_removal(self, tokens):
        hasil = [t for t in tokens if t not in self.stopwords]
        return hasil

    def stemming(self, text):
        hasil = self.stemmer.stem(text)
        return hasil

    def text_preprocessing(self, text):
        if not isinstance(text, str):
            return ""

        text = self.case_folding(text)
        tokens = self.tokenization(text)
        tokens = self.normalization(tokens)
        tokens = self.stopwords_removal(tokens)
        text_gabung = " ".join(tokens)
        input_bersih = self.stemming(text_gabung)

        return input_bersih
