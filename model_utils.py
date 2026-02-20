import pickle
import pandas as pd
import numpy as np
import shap
import matplotlib
import matplotlib.pyplot as plt
import io
import base64
import os

# Prevent GUI errors
matplotlib.use('Agg')

class MentalHealthPredictor:
    def __init__(self):
        self.model = None
        self.encoders = None
        self.feature_names = None
        self.explainer = None
        self.load_artifacts()

    def load_artifacts(self):
        # Look for files in the 'models' folder as you specified
        model_path = os.path.join('models', 'final_model.pkl')
        encoders_path = os.path.join('models', 'encoders.pkl')

        if os.path.exists(model_path) and os.path.exists(encoders_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            with open(encoders_path, 'rb') as f:
                self.encoders = pickle.load(f)
            
            # Get feature names from the model to ensure correct order
            try:
                self.feature_names = self.model.feature_names_in_
            except AttributeError:
                # Fallback if attribute missing (older sklearn/xgboost versions)
                self.feature_names = [
                    'Gender', 'Country', 'Occupation', 'self_employed', 'family_history',
                    'Days_Indoors', 'Growing_Stress', 'Changes_Habits', 'Mental_Health_History',
