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
    
