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
                    'Mood_Swings', 'Coping_Struggles', 'Work_Interest', 'Social_Weakness',
                    'mental_health_interview', 'care_options'
                ]
            
            # Initialize SHAP explainer
            try:
                self.explainer = shap.TreeExplainer(self.model)
            except Exception as e:
                print(f"SHAP Warning: {e}")
            
            print("Real XGBoost Model Loaded Successfully.")
        else:
            print(f"WARNING: Model files not found at {model_path}. Please run train_model.py and move files to 'models/' folder.")

    def preprocess_input(self, input_data):
        """
        Converts raw text input into numbers using the saved encoders.
        """
        processed_data = {}
        
        # We must iterate through the features in the exact order the model expects
        for col in self.feature_names:
            raw_val = input_data.get(col)
            
            # Handle standard cleaning matching training script
            if col == 'Gender':
                raw_val = str(raw_val).lower().strip()
                if raw_val in ['male', 'm', 'man', 'cis male']: raw_val = 'Male'
                elif raw_val in ['female', 'f', 'woman', 'cis female']: raw_val = 'Female'
                else: raw_val = 'Other'

            # Encode
            encoder = self.encoders.get(col)
            if encoder:
                try:
                    # Transform using the encoder
                    processed_val = encoder.transform([str(raw_val)])[0]
                except (ValueError, AttributeError, IndexError):
                    # Robust fallback for unseen values (defaults to 0 or most common)
                    # print(f"Warning: Unseen label '{raw_val}' for column '{col}'. Using default.")
                    processed_val = 0
            else:
                processed_val = 0
            
            processed_data[col] = processed_val
            
        return pd.DataFrame([processed_data], columns=self.feature_names)

    def predict_risk(self, input_data):
        if not self.model:
            return {"score": 0, "level": "Error", "color": "dark", "message": "Model not loaded."}

        # 1. Preprocess
        data_df = self.preprocess_input(input_data)
        
        # 2. Predict Probability (Risk Score)
        # Class 1 is usually "Yes" (Needs treatment)
        try:
            prob = self.model.predict_proba(data_df)[0][1] 
            risk_score = round(prob * 100, 2)
        except Exception as e:
            print(f"Prediction Error: {e}")
            risk_score = 50 # Default fallback
        
        # 3. Determine Level
        if risk_score < 30:
            level, color, msg = "Minimal", "success", "Your responses suggest a healthy mental state."
        elif risk_score < 60:
            level, color, msg = "Moderate", "warning", "You are showing signs of stress. Monitoring is advised."
        else:
            level, color, msg = "High", "danger", "High probability of needing support. Professional consultation recommended."

        return {
            "score": risk_score,
            "level": level,
            "color": color,
            "message": msg
        }

    def generate_shap_plot(self, input_data):
        if not self.model or not self.explainer: return ""
        
        try:
            data_df = self.preprocess_input(input_data)
            shap_values = self.explainer.shap_values(data_df)
            
            plt.figure(figsize=(10, 5))
            
            # Create a simple bar chart of feature importance for this specific prediction
            # We match features to their SHAP impact
            if isinstance(shap_values, list): # Handling different SHAP versions
                vals = shap_values[0]
            else:
                vals = shap_values[0]

            feature_importance = pd.DataFrame(list(zip(self.feature_names, vals)), columns=['feature', 'value'])
            feature_importance['abs_value'] = feature_importance['value'].abs()
            
            # Plot top 7 most influential factors
            top_features = feature_importance.sort_values(by='abs_value', ascending=True).tail(7)
            
            colors = ['#ef4444' if x > 0 else '#0d9488' for x in top_features['value']]
            
            top_features.plot(kind='barh', x='feature', y='value', color=colors, legend=False)
            plt.title("Factors Influencing Your Result (Red=Risk, Teal=Safety)")
            plt.xlabel("Impact on Risk Score")
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', bbox_inches='tight', dpi=100, transparent=True)
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"SHAP Plot Error: {e}")
            return ""

engine = MentalHealthPredictor()