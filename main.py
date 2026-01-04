from flask import Flask, render_template, request, jsonify
from chatbot import Chatbot

app = Flask(__name__)

chatbot = Chatbot(
    dataset_path="dataset/top_anime_dataset_v2.csv",
    intent_path="dataset/intent6.json",
    template_path="dataset/template_respon.json",
    preprocessor_path="NLP/preprocessor.pkl",
    model_path="NLP/model.pkl",
    vectorizer_path="NLP/vectorizer.pkl",
)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def handle_chat():
    try:
        data = request.json
        input_user = data.get("message", "").strip()
        excluded_names = data.get("excluded_names", [])
        last_recommendations = data.get("last_recommendations", [])
        last_genre = data.get("last_genre", [])
        
        balasan = chatbot.chat(
            input_user, 
            excluded_names, 
            last_recommendations, 
            last_genre
        )
        
        # Return juga excluded_names dan last_genre yang mungkin diupdate
        return jsonify({
            "reply": balasan,
            "excluded_names": excluded_names,  # <-- BARU: Return excluded_names yang udah diupdate
            "last_genre": last_genre
        })
    
    except Exception as e:
        print("Error:", e)
        return jsonify({"reply": "Maaf, ada error nih"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)