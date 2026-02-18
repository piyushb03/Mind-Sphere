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
