# model_train.py

import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
import pickle

# Load dataset
df = pd.read_csv('movement_data/store_movements.csv')

# Extract coordinates
coords = df[['Latitude', 'Longitude']]

# Normalize coordinates
scaler = StandardScaler()
coords_scaled = scaler.fit_transform(coords)

# DBSCAN clustering
dbscan = DBSCAN(eps=0.5, min_samples=2)
clusters = dbscan.fit_predict(coords_scaled)

# Save model
with open('dbscan_model.pkl', 'wb') as f:
    pickle.dump((dbscan, scaler), f)

# Optional: Save clustered data for offline analysis
df['Cluster'] = clusters
df.to_csv('movement_data/clustered_data.csv', index=False)

print("Model trained and saved as dbscan_model.pkl")
