from NLP.preprocessor import KAMUS_NORMALISASI, STOPWORDS

# Hitung total pasangan kamus normalisasi
total_kamus = len(KAMUS_NORMALISASI)

# Hitung total stopwords
total_stopwords = len(STOPWORDS)

# Tampilkan hasil
print("=" * 50)
print("STATISTIK PREPROCESSING")
print("=" * 50)
print(f"Total pasangan Kamus Normalisasi: {total_kamus}")
print(f"Total Stopwords: {total_stopwords}")
print("=" * 50)

# Opsional: Tampilkan beberapa contoh
print("\nContoh Kamus Normalisasi (5 pertama):")
for i, (key, value) in enumerate(list(KAMUS_NORMALISASI.items())[:5]):
    print(f"  {i+1}. '{key}' -> '{value}'")

print("\nContoh Stopwords (10 pertama):")
stopwords_list = list(STOPWORDS)[:10]
print(f"  {', '.join(stopwords_list)}")
print("=" * 50)