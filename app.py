# app.py

from flask import Flask, render_template, request
import pandas as pd
import folium
import pickle
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = 'movement_data'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load trained DBSCAN model and scaler
with open('dbscan_model.pkl', 'rb') as f:
    dbscan, scaler = pickle.load(f)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    # Load and process file
    df = pd.read_csv(filepath)
    coords = df[['Latitude', 'Longitude']]
    coords_scaled = scaler.transform(coords)
    cluster_labels = dbscan.fit_predict(coords_scaled)
    df['Cluster'] = cluster_labels

    # Create map centered on first point
    center_lat = df['Latitude'].mean()
    center_lon = df['Longitude'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=13)

    # Add crime points to map
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightblue']
    for _, row in df.iterrows():
        cluster = row['Cluster']
        color = 'gray' if cluster == -1 else colors[cluster % len(colors)]
        folium.CircleMarker(
            location=(row['Latitude'], row['Longitude']),
            radius=5,
            popup=f"{row['Crime_Type']} (Cluster {cluster})",
            color=color,
            fill=True,
            fill_color=color
        ).add_to(m)

    # Save map to HTML string
    map_html = m._repr_html_()

    return render_template('result.html', map=map_html)

if __name__ == '__main__':
    app.run(debug=True)
