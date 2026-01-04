import pickle
import json
import random


class PengenalanIntent:
    def __init__(self, intent_path, model_path, vectorizer_path, template_path):
        file_intent = open(intent_path, "r", encoding="utf-8")
        self.data_intent = json.load(file_intent)
        file_intent.close()

        file_model = open(model_path, "rb")
        self.model_naive_bayes = pickle.load(file_model)
        file_model.close()
        
        file_vectorizer = open(vectorizer_path, "rb")
        self.vectorizer = pickle.load(file_vectorizer)
        file_vectorizer.close()
        
        file_template = open(template_path, "r", encoding="utf-8")
        self.template_respon = json.load(file_template)
        file_template.close()

        self.list_intent = self.model_naive_bayes.classes_

    def pilih_tag(self, input_bersih):
        vektor = self.vectorizer.transform([input_bersih])
        intent_hasil = self.model_naive_bayes.predict(vektor)[0]
        print("Proba:", self.model_naive_bayes.predict_proba(vektor)[0].max())
        return intent_hasil

    def ambil_respon(self, intent):
        for item in self.data_intent:
            if item["tag"] == intent:
                if len(item["responses"]) > 0:
                    pilihan_random = random.choice(item["responses"])
                    return pilihan_random
        return None