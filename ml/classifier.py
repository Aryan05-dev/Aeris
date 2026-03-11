import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

class PollutionClassifier:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.classes = ['Construction Dust', 'Biomass Burning', 'Vehicular Emissions', 'Industrial Discharge', 'Clear']
        self.model_path = os.path.join(os.path.dirname(__file__), 'classifier.pkl')

    def generate_synthetic_data(self, n_samples=1000):
        data = []
        for _ in range(n_samples):
            source = np.random.choice(self.classes)
            if source == 'Clear':
                pm25 = np.random.uniform(5, 20)
                pm10 = np.random.uniform(10, 30)
                co = np.random.uniform(0.1, 0.5)
                no2 = np.random.uniform(5, 15)
            elif source == 'Construction Dust':
                pm25 = np.random.uniform(30, 80)
                pm10 = np.random.uniform(100, 300)
                co = np.random.uniform(0.1, 0.4)
                no2 = np.random.uniform(10, 25)
            elif source == 'Biomass Burning':
                pm25 = np.random.uniform(100, 500)
                pm10 = np.random.uniform(120, 550)
                co = np.random.uniform(1.0, 5.0)
                no2 = np.random.uniform(20, 60)
            elif source == 'Vehicular Emissions':
                pm25 = np.random.uniform(40, 120)
                pm10 = np.random.uniform(50, 150)
                co = np.random.uniform(0.8, 2.5)
                no2 = np.random.uniform(40, 100)
            elif source == 'Industrial Discharge':
                pm25 = np.random.uniform(50, 200)
                pm10 = np.random.uniform(60, 250)
                co = np.random.uniform(0.5, 3.0)
                no2 = np.random.uniform(50, 120)
            
            data.append([pm25, pm10, co, no2, source])
        
        return pd.DataFrame(data, columns=['pm25', 'pm10', 'co', 'no2', 'source'])

    def train(self):
        df = self.generate_synthetic_data()
        X = df[['pm25', 'pm10', 'co', 'no2']]
        y = df['source']
        self.model.fit(X, y)
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"Model trained and saved to {self.model_path}")

    def predict(self, pm25, pm10, co, no2):
        if not os.path.exists(self.model_path):
            self.train()
        
        with open(self.model_path, 'rb') as f:
            model = pickle.load(f)
        
        prediction = model.predict([[pm25, pm10, co, no2]])
        return prediction[0]

if __name__ == "__main__":
    clf = PollutionClassifier()
    clf.train()
