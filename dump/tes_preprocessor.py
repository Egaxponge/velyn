import json
import pickle
import pandas as pd

# Load preprocessor
with open("NLP/preprocessor.pkl", "rb") as f:
    preprocessor = pickle.load(f)

# Load intent.json
with open("dataset/intent.json", "r", encoding="utf-8") as f:
    intents = json.load(f)

# Siapkan data
data = []
for intent in intents:
    tag = intent["tag"]
    for pattern in intent["patterns"]:
        hasil_preprocessing = preprocessor.text_preprocessing(pattern)
        data.append({
            "Tag": tag,
            "Sebelum Preprocessing": pattern,
            "Sesudah Preprocessing": hasil_preprocessing
        })

# Buat DataFrame
df = pd.DataFrame(data)

# Save ke CSV
df.to_csv("dump/hasil_preprocessing.csv", index=False, encoding="utf-8-sig")