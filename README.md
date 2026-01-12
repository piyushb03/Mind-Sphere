# 🧠 MindSphere : AI based Mental Health Assessment

A full-stack machine learning application demonstrating XGBoost classification and SHAP-based model explainability for mental health screening.

## 📌 Overview

MindSphere is a web application that assesses mental health risk based on lifestyle, demographic, and psychological factors. It prioritizes explainable AI (XAI), providing users with risk scores and visual explanations of predictions.

## 🌟 Features

- **Advanced AI Engine**: XGBoost classifier with SMOTE for class imbalance handling
- **SHAP Explainability**: Shapley Additive Explanations for feature importance visualization
- **Dynamic Dashboard**: Real-time assessment form mapped to model features
- **Secure Authentication**: Hashed passwords and Google OAuth 2.0 integration
- **PDF Reports**: Professional assessment report generation
- **Responsive Design**: Mobile and desktop optimization

## 🛠️ Tech Stack

**Frontend**: HTML5, CSS3, JavaScript

**Backend**: Flask, Flask-SQLAlchemy, Flask-Login, Authlib

**Data Science**: XGBoost, SHAP, Pandas, NumPy, Scikit-learn

## 🚀 Installation

### 1. Clone Repository
```bash
git clone https://github.com/piyushb03/Mind-Sphere.git
cd MindSphere
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create `.env`:
```
SECRET_KEY=your_secret_key_here
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret
FORMSPREE_ENDPOINT=https://formspree.io/f/your_form_id
```

### 5. Run Application
```bash
python app.py
```
Visit `http://127.0.0.1:5000`


## 📂 Project Structure

```
MindSphere/
├── app.py                 # Flask entry point
├── model_utils.py         # AI logic and SHAP visualization
├── train_model.py         # Model training script
├── requirements.txt       # Dependencies
├── .env                   # Environment variables (gitignored)
├── models/                # Serialized models
│   ├── final_model.pkl
│   └── encoders.pkl
├── static/                # Assets
│   ├── css/style.css
│   └── brain.png
├── templates/             # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   └── result.html
└── instance/site.db       # SQLite database (gitignored)
```

## Screenshots 
### Home Page

<img width="1851" height="832" alt="Screenshot 2026-01-13 024613" src="https://github.com/user-attachments/assets/0bab117b-99dc-45fd-9fc8-99bfc656cc96" />
<img width="1818" height="837" alt="Screenshot 2026-01-13 024628" src="https://github.com/user-attachments/assets/d0b6a1ea-e894-4ade-93a3-967be0334743" />
<img width="1796" height="704" alt="Screenshot 2026-01-13 024640" src="https://github.com/user-attachments/assets/93bf0307-8c80-449f-8022-56124fe7d7a6" />
<img width="1836" height="590" alt="Screenshot 2026-01-13 024653" src="https://github.com/user-attachments/assets/b95c821d-b752-4413-b87c-e0a3b76b9b67" />


### Dashboard
The main assessment interface where users input their mental health metrics and receive risk evaluations with visual feedback.

<img width="1871" height="847" alt="image" src="https://github.com/user-attachments/assets/18ff6ee9-66c0-48fd-8b06-40782c8bd66e" />
<img width="1847" height="853" alt="image" src="https://github.com/user-attachments/assets/68be8fae-acfc-4427-873b-250929f593f9" />


### Results Page
Displays personalized risk scores, SHAP force plots explaining individual predictions, and actionable insights based on feature contributions.

<img width="1843" height="856" alt="Screenshot 2026-01-13 024923" src="https://github.com/user-attachments/assets/337e0c5a-3115-48e7-9365-1a2107778acd" />
<img width="1002" height="825" alt="Screenshot 2026-01-13 024952" src="https://github.com/user-attachments/assets/630fb98f-4d55-4197-af7b-b8614e59f343" />


### History Page
Provides a chronological record of past assessments, allowing users to revisit previous risk scores, explanations, and generated reports. 

<img width="1862" height="869" alt="Screenshot 2026-01-13 024853" src="https://github.com/user-attachments/assets/e1f072ea-f08e-492e-83fc-5eb3dcdd05f9" />

### Report Generation
PDF export functionality showcasing professional assessment summaries with graphs and detailed explanations.

<img width="1862" height="731" alt="image" src="https://github.com/user-attachments/assets/2e954ca8-321c-4946-acb2-996d40951430" />
<img width="1866" height="862" alt="image" src="https://github.com/user-attachments/assets/816ae81c-868a-4c02-ae44-cedb2af340a9" />



## ⚖️ Legal Disclaimer

**MindSphere is not a diagnostic tool.** Results are statistical estimations, not medical advice. Consult qualified mental health professionals for clinical concerns.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/YourFeature`
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin feature/YourFeature`
5. Open a pull request



