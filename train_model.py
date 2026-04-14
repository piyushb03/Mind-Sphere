import pandas as pd
import numpy as np
import pickle
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, f1_score

def clean_gender(val):
    val = str(val).lower().strip()
    if val in ['male', 'm', 'man', 'cis male']: return 'Male'
    elif val in ['female', 'f', 'woman', 'cis female']: return 'Female'
    else: return 'Other'

def train():
    # 1. Load data
    df = pd.read_csv('notebook/survey.csv')
    df.dropna(subset=['treatment'], inplace=True)
    
    # Target
    y = df['treatment'].map({'Yes': 1, 'No': 0})
    
    features = [
        'Gender', 'Country', 'Occupation', 'self_employed', 'family_history',
        'Days_Indoors', 'Growing_Stress', 'Changes_Habits', 'Mental_Health_History',
        'Mood_Swings', 'Coping_Struggles', 'Work_Interest', 'Social_Weakness',
        'mental_health_interview', 'care_options'
    ]
    
    X = df[features].copy()
    
    # Preprocess Gender
    X['Gender'] = X['Gender'].apply(clean_gender)
    
    encoders = {}
    for col in features:
        # Fill missing values with 'Missing' or mode
        X.fillna({col: 'Missing'}, inplace=True)
        # Ensure string type
        X[col] = X[col].astype(str)
        
        le = LabelEncoder()
        # Fit on unique values and append an "Unknown" class to handle unseen data during inference
        # Actually simplest to just fit on the column, inference in app.py handles unseen by defaulting to 0
        X[col] = le.fit_transform(X[col])
        encoders[col] = le
        
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train XGBoost
    model = XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print(f"F1 Score: {f1_score(y_test, y_pred):.4f}")
    
    # Ensure models dir exists
    os.makedirs('models', exist_ok=True)
    
    # Save model and encoders
    # model_utils.py expects the model to have feature_names_in_ or it will fallback.
    # XGBoost saves feature_names_in_ by default in newer versions.
    with open('models/final_model.pkl', 'wb') as f:
        pickle.dump(model, f)
        
    with open('models/encoders.pkl', 'wb') as f:
        pickle.dump(encoders, f)
        
    print("Saved final_model.pkl and encoders.pkl in models/ directory.")

if __name__ == '__main__':
    train()
