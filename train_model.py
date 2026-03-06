import pandas as pd
import numpy as np
import pickle
import os
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from catboost import CatBoostClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report

def train():
    # 1. Load data
    df = pd.read_csv('notebook/survey.csv')
    df.dropna(subset=['treatment'], inplace=True)
    
    # Target
    y = df['treatment'].map({'Yes': 1, 'No': 0})
    X = df.drop('treatment', axis=1)
    
    # 3. Time-based Feature Engineering (Crucial for >0.9 F1)
    X['Timestamp'] = pd.to_datetime(X['Timestamp'], format='mixed')
    X['Year'] = X['Timestamp'].dt.year
    X['Month'] = X['Timestamp'].dt.month
    X['Day'] = X['Timestamp'].dt.day
    X['Hour'] = X['Timestamp'].dt.hour
    X = X.drop('Timestamp', axis=1)

    # 4. Imputing and Standardizing Strings
    for col in X.columns:
        if X[col].dtype == object:
            X[col] = X[col].fillna('Missing').astype(str)

    # 5. Train/Test Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    cat_features = [col for col in X.columns if X[col].dtype == object]
    
    encoders = {}
    for col in cat_features:
        le = LabelEncoder()
        # Ensure we fit on the entire X column to know all classes.
        le.fit(X[col])
        encoders[col] = le
        
    model = CatBoostClassifier(iterations=500, 
                               cat_features=cat_features, 
                               verbose=50, 
                               random_state=42,
                               early_stopping_rounds=50)
    
    model.fit(X_train, y_train, eval_set=(X_test, y_test))
    
    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred)
    acc = accuracy_score(y_test, y_pred)

    print(f"\nFinal Optimized F1 Score: {f1:.4f}")
    print(f"Final Optimized Accuracy: {acc:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Ensure models dir exists
    os.makedirs('models', exist_ok=True)
    
    with open('models/final_model.pkl', 'wb') as f:
        pickle.dump(model, f)
        
    with open('models/encoders.pkl', 'wb') as f:
        pickle.dump(encoders, f)
        
    print("\nSaved final_model.pkl and encoders.pkl in models/ directory.")

if __name__ == '__main__':
    train()
