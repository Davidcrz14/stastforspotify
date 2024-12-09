from flask import Flask, render_template, request, jsonify
import requests
from io import BytesIO
import base64
from PIL import Image
# Importar las funciones necesarias del script original
from main import (create_top_artists_image, create_top_tracks_image,
                 create_genres_image, create_recent_tracks_image,
                 get_top_artists, get_top_tracks, get_recently_played)
import os

app = Flask(__name__)

# Obtener variables de entorno
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/callback')
def callback():
    return render_template('index.html')

@app.route('/api/token', methods=['POST'])
def get_token():
    code = request.json.get('code')

    response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    })

    return jsonify(response.json())

@app.route('/api/stats')
def get_stats():
    token = request.headers.get('Authorization').split(' ')[1]

    try:
        # Obtener datos
        top_artists = get_top_artists(token)
        top_tracks = get_top_tracks(token)
        recent = get_recently_played(token)

        # Crear imágenes
        images = {
            'artists': create_top_artists_image(top_artists),
            'tracks': create_top_tracks_image(top_tracks),
            'genres': create_genres_image(top_artists),
            'recent': create_recent_tracks_image(recent)
        }

        # Convertir imágenes a base64
        encoded_images = []
        for img in images.values():
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            encoded_images.append(img_str)

        return jsonify({
            'images': encoded_images
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Importante: Esto es para desarrollo local
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
