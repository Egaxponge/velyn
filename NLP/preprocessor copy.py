import re
import nltk
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

KAMUS_NORMALISASI = {
    # Variasi kata ganti orang
    "kau": "kamu",
    "lu": "kamu",
    "loe": "kamu",
    "lo": "kamu",
    "kmu": "kamu",
    "anda": "kamu",
    "bro": "kamu",
    "sis": "kamu",
    "gan": "kamu",
    "min": "kamu",
    "gw": "saya",
    "gua": "saya",
    "gue": "saya",
    "aku": "saya",
    
    # Variasi salam
    "hi": "hai",
    "hey": "hai",
    "hei": "hai",
    "helo": "hai",
    "hello": "hai",
    "halo": "hai",
    "woy": "hai",
    "vel": "velyn",
    "bot": "velyn",
    
    # Variasi kata hubung
    "aja": "saja",
    "ampe": "sampai",
    "sampe": "sampai",
    "ama": "sama",
    "sm": "sama",
    "dgn": "dengan",
    "dg": "dengan",
    "utk": "untuk",
    "buat": "untuk",
    "bwt": "untuk",
    "bt": "untuk",
    "krn": "karena",
    "dri": "dari",
    "dr": "dari",
    "ke": "kepada",
    "tapi": "tetapi",
    "ato": "atau",
    "yg": "yang",
    
    # Variasi kata negatif
    "gak": "tidak",
    "nggak": "tidak",
    "ga": "tidak",
    "ngga": "tidak",
    "engga": "tidak",
    "enggak": "tidak",
    "gk": "tidak",
    "g": "tidak",
    "tdk": "tidak",
    "kagak": "tidak",
    "kaga": "tidak",
    "gada": "tidak ada",
    "jgn": "jangan",
    "jan": "jangan",
    "jngan": "jangan",
    
    # Variasi kata positif/modal
    "udah": "sudah",
    "dah": "sudah",
    "udh": "sudah",
    "dh": "sudah",
    "boleh": "bisa",
    "blh": "bisa",
    "bs": "bisa",
    "bsa": "bisa",
    "bis": "bisa",
    
    # Variasi kata tanya
    "gimana": "bagaimana",
    "gmn": "bagaimana",
    "gmana": "bagaimana",
    "gimna": "bagaimana",
    "bgmn": "bagaimana",
    "bgaimana": "bagaimana",
    "apaan": "apa",
    "apasih": "apa",
    "apasi": "apa",
    "knp": "kenapa",
    "knapa": "kenapa",
    "napa": "kenapa",
    "dmn": "dimana",
    "dmana": "dimana",
    "mana": "dimana",
    "mn": "dimana",
    "brp": "berapa",
    "brapa": "berapa",
    "brpa": "berapa",
    
    # Variasi kata kerja ingin/mau
    "pengen": "ingin",
    "pgn": "ingin",
    "mo": "mau",
    "mw": "mau",
    "pingin": "ingin",
    "pen": "ingin",
    "pgen": "ingin",
    "gamau": "tidak mau",
    "gmau": "tidak mau",
    "gkmau": "tidak mau",
    "gakmau": "tidak mau",
    "nggamau": "tidak mau",
    "ogah": "tidak mau",
    
    # Variasi kata kerja umum
    "gitu": "begitu",
    "liat": "lihat",
    "ngeliat": "melihat",
    "nonton": "menonton",
    "nnton": "menonton",
    "tonton": "menonton",
    "cari": "mencari",
    "cri": "mencari",
    "nyari": "mencari",
    "pilih": "memilih",
    "milih": "memilih",
    "mili": "memilih",
    "cobain": "coba",
    "nyoba": "mencoba",
    "nyobain": "mencoba",
    "kasih": "memberikan",
    "ngasih": "memberikan",
    "tunjukin": "tunjukkan",
    "tampilin": "tampilkan",
    "nanya": "bertanya",
    "nanyain": "menanyakan",
    "nyeritain": "menceritakan",
    
    # Variasi kata sifat perbandingan
    "kaya": "seperti",
    "kayak": "seperti",
    "kyak": "seperti",
    "kyk": "seperti",
    "lbih": "lebih",
    "lbh": "lebih",
    "lbih": "lebih",
    "paling": "paling",
    "plg": "paling",
    
    # Variasi kata intensitas
    "banget": "sangat",
    "bgt": "sangat",
    "bngt": "sangat",
    "bingit": "sangat",
    "banged": "sangat",
    "bener": "benar",
    "bener2": "benar",
    "bnr": "benar",
    "cuman": "hanya",
    "cuma": "hanya",
    
    # Variasi kata sifat kualitas
    "mantap": "bagus",
    "mantul": "bagus",
    "keren": "bagus",
    "top": "bagus",
    "oke": "bagus",
    "ok": "bagus",
    "okay": "bagus",
    "okeh": "bagus",
    "nice": "bagus",
    "good": "bagus",
    "great": "bagus",
    "amazing": "bagus",
    "bgs": "bagus",
    "bgus": "bagus",
    "jelek": "buruk",
    "jlk": "buruk",
    "seru": "menarik",
    "asik": "menarik",
    "asick": "menarik",
    "asyk": "menarik",
    "mnrik": "menarik",
    "boring": "membosankan",
    "bosen": "bosan",
    "bosanin": "membosankan",
    "perfect": "sempurna",
    
    # Variasi kata perintah dengan imbuhan -in
    "rekomendasiin": "rekomendasikan",
    "rekomendain": "rekomendasikan",
    "rekomenin": "rekomendasikan",
    "saranin": "sarankan",
    "cariin": "carikan",
    "bandingin": "bandingkan",
    "jelasin": "jelaskan",
    "lanjutin": "lanjutkan",
    "kenalin": "kenalkan",
    "perkenalin": "perkenalkan",
    
    # Variasi terima kasih
    "thx": "terimakasih",
    "tengkyu": "terimakasih",
    "tengkiu": "terimakasih",
    "thanks": "terimakasih",
    "makasi": "terimakasih",
    "makasih": "terimakasih",
    "trimakasih": "terimakasih",
    "trimakasi": "terimakasih",
    "maksih": "terimakasih",
    "tq": "terimakasih",
    "teerima": "terima",
    
    # Variasi kata keadaan waktu
    "emang": "memang",
    "skrg": "sekarang",
    "skrng": "sekarang",
    "skg": "sekarang",
    "kapan": "waktu",
    "saat": "waktu",
    "lagi": "sedang",
    "nanti": "lain waktu",
    "besok": "lain waktu",
    "tar": "nanti",
    "trs": "terus",
    "trus": "terus",
    
    # Variasi kata kondisi
    "kalo": "kalau",
    "klo": "kalau",
    "klau": "kalau",
    "blm": "belum",
    "blom": "belum",
    "msh": "masih",
    "masi": "masih",
    "udahan": "selesai",
    "tamat": "selesai",
    "tmt": "selesai",
    "finish": "selesai",
    "done": "selesai",
    "kelar": "selesai",
    "beres": "selesai",
    
    # Variasi konfirmasi
    "ya": "iya",
    "iyah": "iya",
    "yoi": "iya",
    "yup": "iya",
    "yep": "iya",
    "yes": "iya",
    "yaps": "iya",
    "met": "selamat",
    "slamat": "selamat",
    "samlekom": "assalamualaikum",
    
    # Variasi kata pemahaman
    "ngerti": "mengerti",
    "ngarti": "mengerti",
    "paham": "mengerti",
    "phm": "mengerti",
    "mudeng": "mengerti",
    "tau": "tahu",
    "tw": "tahu",
    
    # Variasi kata emosi/sikap
    "males": "malas",
    "mls": "malas",
    "suka": "suka",
    "demen": "suka",
    "doyan": "suka",
    "puas": "senang",
    "ragu": "ragu",
    "bingung": "bingung",
    "bgung": "bingung",
    "bingun": "bingung",
    "penasaran": "ingin tahu",
    "pnasaran": "ingin tahu",
    "kepo": "ingin tahu",
    "anjir": "wow",
    "anjay": "wow",
    
    # Variasi kata kepemilikan/jumlah
    "pnya": "punya",
    "pny": "punya",
    "byk": "banyak",
    "bnyk": "banyak",
    "bnyak": "banyak",
    "dikit": "sedikit",
    "dkit": "sedikit",
    
    # Variasi kata perintah halus
    "tolong": "mohon",
    "tlg": "mohon",
    "tlong": "mohon",
    "minta": "mohon",
    "mnt": "mohon",
    "nolak": "tolak",
    
    # Variasi kata aksi/proses
    "gajadi": "tidak jadi",
    "gajd": "tidak jadi",
    "skip": "lewati",
    "ganti": "ubah",
    
    # Variasi kata penunjuk
    "tuh": "itu",
    "ni": "ini",
    "ayok": "ayo",
    "yuk": "ayo",
    "ayuk": "ayo",
    
    # Variasi kata definisi/informasi
    "pengertian": "definisi",
    "arti": "definisi",
    "info": "informasi",
    "tutorial": "panduan",
    "tutor": "panduan",
    "mekanisme": "cara",
    
    # Variasi kata detail/nama
    "judulnya": "judul",
    "jdl": "judul",
    "jdul": "judul",
    "nmnya": "namanya",
    "detil": "detail",
    "rincian": "detail",
    "hsl": "hasil",
    "outputnya": "hasilnya",
    
    # Variasi kata penilaian/perbandingan
    "cocok": "sesuai",
    "pas": "sesuai",
    "akurat": "tepat",
    "presisi": "tepat",
    "sesuai": "tepat",
    "berbeda": "beda",
    "compare": "bandingkan",
    
    # Variasi kata pilihan
    "preferensi": "pilihan",
    "opsi": "pilihan",
    "option": "pilihan",
    "serah": "terserah",
    "trsrh": "terserah",
    "list": "daftar",
    "random": "acak",
    
    # Variasi kata rekomendasi (konteks chatbot)
    "req": "request",
    "rekomen": "rekomendasi",
    "recom": "rekomendasi",
    "rekomend": "rekomendasi",
    "rekom": "rekomendasi",
    "recommend": "rekomendasi",
    "recommended": "direkomendasikan",
    "rekomended": "direkomendasikan",
    "worth": "layak",
    
    # Variasi kata manfaat/bantuan
    "worthit": "bermanfaat",
    "berguna": "bermanfaat",
    "berfaedah": "bermanfaat",
    "ngbantu": "membantu",
    "ngebantu": "membantu",
    "nolongin": "membantu",
    "nolong": "membantu",
    "antarmuka": "tampilan",
    "interface": "tampilan",
    
    # Variasi kata kualitas sistem
    "responsif": "cepat",
    "efisien": "cepat",
    "gampang": "mudah",
    "simple": "mudah",
    "user": "pengguna",
    "friendly": "ramah",
    "lengkap": "banyak",
    "beragam": "bervariasi",
    "solusi": "jawaban",
    "pakenya": "pakainya",
    "eps": "episode",
    "ep": "episode",
    "episod": "episode",
    "epsd": "episode",
}

STOPWORDS = {
    "pun",
    "kah",
    "nih",
    "sih",
    "dong",
    "deh",
    "yah",
    "oh",
    "eh",
    "nah",
    "kok",
    "kan",
    "juga",
    "loh",
    "lah",
    "lho",
    "weh",
    "wih",
    "wah",
    "nya",
    "please",
    "pls",
    "plis",
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
        text = re.sub(r"[^a-zA-Z\s-]", " ", text)
        text = text.replace("-", " ")
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        return text

    def tokenization(self, text):
        tokens = word_tokenize(text)
        hasil = [t for t in tokens if t.isalpha()]
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
