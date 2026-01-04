import json
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import matplotlib.pyplot as plt
from NLP.preprocessor import TextPreprocessor
import warnings
warnings.filterwarnings('ignore')

def prepare_data(preprocessor):
    dataset_percakapan = open("dataset/intent7.json", "r", encoding="utf-8")
    intents = json.load(dataset_percakapan)
    dataset_percakapan.close()
    
    texts = []
    labels = []
    
    for intent in intents:
        for pattern in intent["patterns"]:
            input_bersih = preprocessor.text_preprocessing(pattern)
            texts.append(input_bersih)
            labels.append(intent["tag"])
    
    return texts, labels, len(intents)


def plot_confusion_matrix(y_true, y_pred, labels):
    cm = confusion_matrix(y_true, y_pred, labels=labels)
    
    plt.figure(figsize=(10, 8))
    plt.imshow(cm, interpolation='nearest', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.colorbar()
    
    tick_marks = list(range(len(labels)))
    plt.xticks(tick_marks, labels, rotation=45, ha='right')
    plt.yticks(tick_marks, labels)
    
    for i in range(len(labels)):
        for j in range(len(labels)):
            color = 'white' if cm[i, j] > cm.max() / 2 else 'black'
            plt.text(j, i, str(cm[i, j]), ha='center', va='center', color=color)
    
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.tight_layout()
    plt.savefig('confusion_matrix.png', dpi=100)
    plt.close()


def train_model():
    preprocessor = TextPreprocessor()
    X, y, n_intents = prepare_data(preprocessor)
    
    print("Total " + str(len(X)) + " samples dari " + str(n_intents) + " intent classes")
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Train: " + str(len(X_train)) + " samples")
    print("Test: " + str(len(X_test)) + " samples")
    
    vectorizer = CountVectorizer()
    X_train_vec = vectorizer.fit_transform(X_train)
    
    print("Vocabulary size: " + str(len(vectorizer.vocabulary_)) + " features")
    
    model = MultinomialNB()
    model.fit(X_train_vec, y_train)
    
    X_test_vec = vectorizer.transform(X_test)
    y_pred = model.predict(X_test_vec)
    
    # hitung accuracy (persamaan 2.3)
    accuracy = accuracy_score(y_test, y_pred)
    
    # dapetin classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    
    # print hasil evaluasi
    print("")
    print("=== CLASSIFICATION REPORT ===")
    print(f"{'Intent':<30} {'Precision':<12} {'Recall':<12} {'F1-Score':<12} {'Support':<12}")
    print("-" * 77)
    
    # print hanya per-class metrics (skip accuracy, macro avg, micro avg, weighted avg)
    for class_name, metrics in sorted(report.items()):
        if class_name not in ['accuracy', 'macro avg', 'micro avg', 'weighted avg']:
            print(f"{class_name:<30} {metrics['precision']:<12.3f} {metrics['recall']:<12.3f} {metrics['f1-score']:<12.3f} {int(metrics['support']):<12}")
    
    print("-" * 77)
    print(f"{'Accuracy':<30} {accuracy:.3f}")
    print(f"Total samples: {len(y_test)}")
    
    # bikin confusion matrix
    plot_confusion_matrix(y_test, y_pred, model.classes_)
    
    # simpan model
    with open("NLP/model.pkl", "wb") as f:
        pickle.dump(model, f)
    
    with open("NLP/vectorizer.pkl", "wb") as f:
        pickle.dump(vectorizer, f)
    
    with open("NLP/preprocessor.pkl", "wb") as f:
        pickle.dump(preprocessor, f)
    
    print("\nModel, vectorizer, dan preprocessor berhasil disimpan!")

train_model()