# 🛡️ Phishing Website Detection Using Machine Learning

<p align="center">
  <b>A Machine Learning-Based Web Application for Detecting Phishing Websites</b>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.x-blue?logo=python" />
  <img src="https://img.shields.io/badge/Flask-Web%20Framework-black?logo=flask" />
  <img src="https://img.shields.io/badge/Machine-Learning-orange" />
  <img src="https://img.shields.io/badge/Status-Completed-success" />
</p>

## 📌 Project Overview

Phishing attacks are one of the most common cybersecurity threats on the internet. Attackers create fraudulent websites that imitate legitimate platforms to steal sensitive information such as usernames, passwords, and financial details.

This project aims to identify potentially malicious websites using Machine Learning techniques.

The application analyzes URL-related features and uses a trained classification model to predict whether a website is **Phishing** or **Legitimate**.

The project combines Machine Learning with Flask to provide a web-based interface for phishing website detection.

## 🎯 Problem Statement

With the increasing number of phishing attacks, identifying malicious websites has become an important cybersecurity challenge.

Traditional detection methods may struggle to identify newly created phishing URLs.

This project explores Machine Learning techniques to classify website URLs based on extracted features and identify potentially fraudulent websites.

## ✨ Key Features

- Phishing and legitimate website classification.
- URL feature extraction.
- Machine Learning-based prediction.
- Flask-based web application.
- Trained Machine Learning models.
- Dataset analysis and model evaluation.
- Jupyter notebooks for experimentation and training.

## 🧰 Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Flask | Web application framework |
| Pandas | Data manipulation |
| Scikit-learn | Machine Learning |
| XGBoost | Classification algorithm |
| Jupyter Notebook | Model development and experimentation |
| HTML | Web interface |
| CSS | Interface styling |
| JavaScript | Frontend functionality |

## 🧠 Machine Learning Approach

This project uses supervised Machine Learning classification techniques.

### Dataset

The dataset consists of:

- 5,000 phishing URLs.
- 5,000 legitimate URLs.
- 10,000 total URL records.

The original project documentation identifies PhishTank and the University of New Brunswick's URL dataset as data sources.

### Algorithms Explored

The following algorithms were investigated:

1. Decision Tree
2. Random Forest
3. Multilayer Perceptron (MLP)
4. XGBoost
5. Autoencoder Neural Network
6. Support Vector Machine (SVM)

### Feature Extraction

A total of 17 URL and website-related features were explored during model development.

These features belong to three major categories:

- Address Bar-Based Features
- Domain-Based Features
- HTML and JavaScript-Based Features

### Model Performance

According to the original project experiments, the XGBoost Classifier achieved the highest reported performance of **86.4%**.

The trained models are included in the repository.

*Note: This is the result reported in the original project experiments, not a guarantee of real-world detection accuracy.*

## 🏗️ Project Structure

```text
Phishing-Website-Detection/
│
├── DataFiles/
│   └── Dataset files
│
├── static/
│   └── images/
│
├── templates/
│   └── HTML templates
│
├── app.py
├── URLFeatureExtraction.py
├── model.pkl
├── XGBoostClassifier.pickle.dat
│
├── Phishing Website Detection_Models & Training.ipynb
├── URL Feature Extraction.ipynb
│
├── inspect_model.py
├── start.bat
├── start_admin.bat
│
├── README.md
└── requirements.txt
```

## ⚙️ Installation and Setup

Follow these steps to run the project locally.

### 1. Clone the Repository

```bash
git clone https://github.com/OwaisGit12/Phishing-Website-Detection-Using-Machine-Learning.git
```

### 2. Navigate to the Project Directory

```bash
cd Phishing-Website-Detection-Using-Machine-Learning
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
python app.py
```

### 7. Open in Browser

Visit:

```text
http://127.0.0.1:5000/
```

## 📸 Application Screenshots

Screenshots of the working application will be added here.

Home Page
<img width="946" height="486" alt="image" src="https://github.com/user-attachments/assets/3d5d54d0-1873-4741-8d36-dbaef2f06e88" />

Safe Website
<img width="983" height="547" alt="image" src="https://github.com/user-attachments/assets/3ded130f-75c5-47ed-aa18-f70430664f1a" />

Unsafe Website
<img width="983" height="592" alt="image" src="https://github.com/user-attachments/assets/92d1f1ab-41db-40b6-a16e-cca222239bfb" />


## 📚 Learning Outcomes

Through this project, I gained practical exposure to:

- Machine Learning classification techniques.
- Data preprocessing and feature extraction.
- Training and evaluating classification models.
- Integrating Machine Learning models with Flask.
- Developing Python-based web applications.
- Understanding phishing attacks and cybersecurity concepts.

## 🚀 Future Enhancements

Potential improvements include:

- Integrating real-time threat intelligence feeds.
- Improving URL feature extraction.
- Evaluating additional Machine Learning models.
- Developing a browser extension.
- Improving model accuracy and generalization.
- Deploying the application to a secure cloud environment.

## ⚠️ Disclaimer

This project is developed for educational and research purposes.

Machine Learning predictions are not guaranteed to identify every phishing website. Users should not rely solely on this application for cybersecurity decisions.

## 👨‍💻 Author

**Syed Owais Ahmed**

B.E. Computer Science and Engineering Graduate  
Currently pursuing M.Tech in Artificial Intelligence at REVA University.

- GitHub: [@OwaisGit12](https://github.com/OwaisGit12)
- LinkedIn: [Connect with me](https://www.linkedin.com/in/syedowaisahmed)


## ⭐ Support

If you find this project interesting, consider giving this repository a star!

Your support is appreciated.
