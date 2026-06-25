# Fake News Detector

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)](#)
[![Machine Learning](https://img.shields.io/badge/Machine%20Learning-Random%20Forest-orange?style=for-the-badge)](#)

## 📌 Project Overview

**Fake News Detector** is a machine-learning-powered web application that analyzes and predicts whether a news article is **Real** or **Fake**. By utilizing advanced Natural Language Processing (NLP), TF-IDF feature extraction, and an optimized **Random Forest classifier**, the application decodes underlying linguistic patterns to verify content authenticity. 

The app features a highly sophisticated, custom UI built on top of Streamlit, and is designed to provide immediate, actionable insights into news credibility alongside live fact-checking integrations.

---

## 🚀 Key Features

* **Intelligent Analysis**: Instantly processes news text, calculating authenticity and presenting visual AI confidence scores.
* **Live Fact-Checking Integration**: Connects with the Google Fact Check Tools API to provide real-time context and fact-checks from sources like PolitiFact and Snopes.
* **Robust NLP Pipeline**: Implements advanced text preprocessing (URL/character stripping, stopword removal, stemming) and TF-IDF vectorization.
* **High Accuracy Deployment**: Deploys a highly accurate serialized Random Forest model for real-time inference.
* **Educational Insights**: Features dynamic warnings and media literacy tips to guide users on manual verification.

---

## 🧠 Under the Hood

### NLP Preprocessing
Before the model can understand the text, the raw news is cleaned through a stringent NLP pipeline using NLTK:
1. Removing URLs, special characters, and punctuation
2. Filtering out English stopwords
3. Applying the Porter Stemmer to reduce words to their root forms

### Machine Learning Models
The accompanying Jupyter Notebook (`Fake_News_Detection.ipynb`) explores 7 different classification algorithms, including Logistic Regression, SVM, Naive Bayes, Decision Trees, Gradient Boosting, and KNN. 

For the production web application (`app.py`), the **Random Forest Classifier** was selected and serialized (`rf_model.pkl`) alongside the TF-IDF vectorizer (`vectorizer.pkl`) due to its robustness and excellent generalization on text data.

### Real-Time Fact-Checking
To complement the model's analysis, the application integrates with the Google Fact Check Tools API. It queries the API using the user-provided text to retrieve existing, verified fact-checks from independent, accredited news organizations like Snopes, PolitiFact, and FactCheck.org. This adds an extra layer of real-time credibility verification to the model's classification results.

---

## 📊 Dataset Information

The machine learning models are trained on the [Fake and Real News Dataset](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset) sourced from Kaggle. This dataset contains:

- **Total Articles:** 44,898 records
- **Class Distribution:**
  - **Fake News:** 23,481 articles (flagged and collected from websites flagged by truth-checking organizations)
  - **Real News:** 21,417 articles (extracted directly from Reuters.com)
- **Data Attributes:** Title, text, subject, and publication date
- **Raw Files:** `Fake.csv`, `True.csv`

---

## 🛠️ Technology Stack

* **Language**: Python
* **Web Framework**: Streamlit
* **Machine Learning**: Scikit-Learn
* **NLP**: NLTK (Natural Language Toolkit)
* **Data Processing**: Pandas, NumPy
* **Serialization**: Pickle

---

## 📂 Project Structure

```text
fake-news-detection-nlp-main/
│
├── app.py                      # Main Streamlit web application
├── Fake_News_Detection.ipynb   # Jupyter Notebook with EDA, training & evaluation
├── rf_model.pkl                # Serialized Random Forest model
├── vectorizer.pkl              # Serialized TF-IDF vectorizer
├── requirements.txt            # Python dependencies
├── .streamlit/                 # Streamlit configuration & api
└── README.md                   # Project documentation
```

---

## ▶️ Installation & Usage

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/fake-news-detection.git
   cd fake-news-detection
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Add API Keys (Optional):**
   To enable live fact-checking, add your Google Fact Check API key to `.streamlit/secrets.toml`:
   ```toml
   GOOGLE_API_KEY = "your-api-key-here"
   ```

4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```

---

## ⚠️ Disclaimer

*This tool analyzes linguistic style and structural patterns, it does not perform semantic fact-checking by itself. Uncharacteristic writing styles in legitimate journalism may trigger false alerts. Always use the suggested links to independently verify all findings.*
