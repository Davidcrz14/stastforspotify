import requests
from urllib.parse import urlencode
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from collections import Counter
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io
from datetime import datetime
import os

# Credenciales de tu aplicación
CLIENT_ID = "09ad32ff6cd44f92af6deb600e170ac9"
CLIENT_SECRET = "5990d5fae92842c3929807c8e19409cd"
REDIRECT_URI = "https://statsspoti.vercel.app/callback"
SCOPE = "user-top-read user-read-recently-played"

# Añadir constantes para la generación de imágenes
IMAGES_DIR = "wrapped_images"
FONT_SIZE_TITLE = 120
FONT_SIZE_TEXT = 72
FONT_SIZE_SUBTITLE = 90
BACKGROUND_COLOR = (25, 20, 20)
SPOTIFY_GREEN = (30, 215, 96)

def download_image(url):
    response = requests.get(url)
    return Image.open(io.BytesIO(response.content))

def create_directory():
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)

def create_top_artists_image(top_artists):
    width, height = 1080, 1920
    image = Image.new('RGB', (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    try:
        # Efecto de fondo con la imagen del artista top
        top_artist = top_artists["items"][0]
        artist_image_url = top_artist["images"][0]["url"]
        background = download_image(artist_image_url)
        background = background.resize((width, height)).convert('RGBA')
        # Aplicar efecto de desenfoque y oscurecimiento
        background = background.filter(ImageFilter.GaussianBlur(radius=10))
        background = Image.blend(Image.new('RGB', (width, height), (0,0,0)), background.convert('RGB'), 0.3)
        image.paste(background, (0,0))

        # Imagen principal del artista
        artist_image = download_image(artist_image_url)
        artist_image = artist_image.resize((800, 800))
        # Crear máscara circular
        mask = Image.new('L', (800, 800), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 800, 800), fill=255)
        # Aplicar máscara circular
        image.paste(artist_image, (140, 200), mask)

        try:
            font_title = ImageFont.truetype("arial.ttf", FONT_SIZE_TITLE)
            font_text = ImageFont.truetype("arial.ttf", FONT_SIZE_TEXT)
            font_subtitle = ImageFont.truetype("arial.ttf", FONT_SIZE_SUBTITLE)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()

        # Añadir un fondo semi-transparente detrás del texto para mejorar la legibilidad
        text_background = Image.new('RGBA', (width, 200), (0, 0, 0, 180))
        image.paste(text_background, (0, 0), text_background)
        image.paste(text_background, (0, height-200), text_background)

        # Título con estilo y mayor contraste
        draw.text((width//2, 80), "TOP ARTISTAS 2024", fill='white',
                  font=font_title, anchor="mm", stroke_width=2, stroke_fill='black')

        # Artista principal
        draw.text((width//2, 1050), "Tu Artista Favorito", fill=SPOTIFY_GREEN,
                 font=font_subtitle, anchor="mm")
        draw.text((width//2, 1120), top_artist["name"], fill='white',
                 font=font_title, anchor="mm")

        # Lista de artistas con números estilizados
        y_position = 1250
        for i, artist in enumerate(top_artists["items"][1:6], 2):
            # Círculo numerado
            circle_x = width//2 - 200
            circle_radius = 25
            draw.ellipse((circle_x-circle_radius, y_position-circle_radius,
                         circle_x+circle_radius, y_position+circle_radius),
                        fill=SPOTIFY_GREEN)
            draw.text((circle_x, y_position), str(i), fill='black',
                     font=font_text, anchor="mm")
            # Nombre del artista
            draw.text((circle_x + 100, y_position), artist["name"],
                     fill='white', font=font_text, anchor="lm")
            y_position += 80

        # Pie de imagen personalizado con mayor contraste
        draw.text((width//2, height-120), "Spotify Wrapped",
                 fill='white', font=font_text, anchor="mm", stroke_width=2, stroke_fill='black')
        draw.text((width//2, height-70), "For DavC",
                 fill='white', font=font_subtitle, anchor="mm", stroke_width=2, stroke_fill='black')

    except Exception as e:
        print(f"Error creando imagen de artistas: {str(e)}")

    return image

def create_top_tracks_image(top_tracks):
    width, height = 1080, 1920
    image = Image.new('RGB', (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    try:
        # Efecto de fondo con la imagen de la canción top
        top_track = top_tracks["items"][0]
        track_image_url = top_track["album"]["images"][0]["url"]
        background = download_image(track_image_url)
        background = background.resize((width, height)).convert('RGBA')
        background = background.filter(ImageFilter.GaussianBlur(radius=15))
        background = Image.blend(Image.new('RGB', (width, height), (0,0,0)),
                               background.convert('RGB'), 0.15)
        image.paste(background, (0,0))

        try:
            font_title = ImageFont.truetype("arial.ttf", FONT_SIZE_TITLE)
            font_text = ImageFont.truetype("arial.ttf", FONT_SIZE_TEXT)
            font_subtitle = ImageFont.truetype("arial.ttf", FONT_SIZE_SUBTITLE)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()

        # Añadir un fondo semi-transparente detrás del texto para mejorar la legibilidad
        text_background = Image.new('RGBA', (width, 200), (0, 0, 0, 180))
        image.paste(text_background, (0, 0), text_background)
        image.paste(text_background, (0, height-200), text_background)

        # Título con mayor contraste
        draw.text((width//2, 80), "TOP CANCIONES 2024", fill='white',
                 font=font_title, anchor="mm", stroke_width=2, stroke_fill='black')

        # Canción principal
        main_album_image = download_image(track_image_url)
        main_album_image = main_album_image.resize((400, 400))
        image.paste(main_album_image, (width//2-200, 200))

        # Info de canción principal
        draw.text((width//2, 650), "Tu Canción Más Escuchada",
                 fill=SPOTIFY_GREEN, font=font_subtitle, anchor="mm")
        draw.text((width//2, 700), top_track["name"],
                 fill='white', font=font_title, anchor="mm")
        artists = ", ".join([artist["name"] for artist in top_track["artists"]])
        draw.text((width//2, 770), artists,
                 fill='gray', font=font_subtitle, anchor="mm")

        # Lista de canciones con miniaturas
        y_position = 900
        for i, track in enumerate(top_tracks["items"][1:6], 2):
            # Miniatura del álbum
            album_image = download_image(track["album"]["images"][0]["url"])
            album_image = album_image.resize((100, 100))
            image.paste(album_image, (50, y_position))

            # Número en círculo
            circle_x = 200
            circle_radius = 25
            draw.ellipse((circle_x-circle_radius, y_position+25-circle_radius,
                         circle_x+circle_radius, y_position+25+circle_radius),
                        fill=SPOTIFY_GREEN)
            draw.text((circle_x, y_position+25), str(i),
                     fill='black', font=font_text, anchor="mm")

            # Información de la canción
            draw.text((250, y_position+10), track["name"],
                     fill='white', font=font_text, anchor="lm")
            artists = ", ".join([artist["name"] for artist in track["artists"]])
            draw.text((250, y_position+50), artists,
                     fill='gray', font=font_subtitle, anchor="lm")

            # Línea divisoria
            draw.line((50, y_position+120, width-50, y_position+120),
                     fill=(40, 40, 40), width=2)

            y_position += 160

        # Pie de imagen personalizado con mayor contraste
        draw.text((width//2, height-120), "Spotify Wrapped",
                 fill='white', font=font_text, anchor="mm", stroke_width=2, stroke_fill='black')
        draw.text((width//2, height-70), "For DavC",
                 fill='white', font=font_subtitle, anchor="mm", stroke_width=2, stroke_fill='black')

    except Exception as e:
        print(f"Error creando imagen de canciones: {str(e)}")

    return image

def create_genres_image(top_artists):
    width, height = 1080, 1920
    image = Image.new('RGB', (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    try:
        # Obtener géneros
        genres = get_favorite_genres(top_artists)

        # Crear fondo con degradado simple
        background = Image.new('RGB', (width, height), BACKGROUND_COLOR)
        for i in range(0, height, 2):
            alpha = int(255 * (1 - i/height))
            draw.line((0, i, width, i), fill=(30, 215, 96, alpha), width=1)
        image.paste(background)

        try:
            font_title = ImageFont.truetype("arial.ttf", FONT_SIZE_TITLE)
            font_text = ImageFont.truetype("arial.ttf", FONT_SIZE_TEXT)
            font_genre = ImageFont.truetype("arial.ttf", 70)
            font_subtitle = ImageFont.truetype("arial.ttf", FONT_SIZE_SUBTITLE)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_genre = ImageFont.load_default()
            font_subtitle = ImageFont.load_default()

        # Banners decorativos
        draw.rectangle((0, 0, width, 150), fill=(0,0,0,180))
        draw.rectangle((0, height-200, width, height), fill=(0,0,0,180))

        # Título y subtítulo
        draw.text((width//2, 80), "TUS GÉNEROS TOP", fill=SPOTIFY_GREEN,
                 font=font_title, anchor="mm")
        draw.text((width//2, 150), "Los géneros que más escuchaste",
                 fill='white', font=font_subtitle, anchor="mm")

        # Imagen principal del género top
        main_size = 400
        main_box = Image.new('RGB', (main_size, main_size), (40, 40, 40))
        draw_box = ImageDraw.Draw(main_box)
        draw_box.text((main_size//2, main_size//2), genres[0][0].title(),
                     fill=SPOTIFY_GREEN, font=font_genre, anchor="mm")
        image.paste(main_box, (width//2-main_size//2, 250))

        # Texto del género principal
        draw.text((width//2, 700), "Tu Género Favorito",
                 fill=SPOTIFY_GREEN, font=font_subtitle, anchor="mm")
        draw.text((width//2, 750), genres[0][0].title(),
                 fill='white', font=font_title, anchor="mm")

        # Lista de géneros restantes
        y_position = 900
        for i, (genre, count) in enumerate(genres[1:], 2):
            # Rectángulo de fondo
            draw.rectangle((50, y_position, width-50, y_position+100),
                         fill=(40, 40, 40))

            # Número en círculo
            circle_x = 100
            circle_radius = 25
            draw.ellipse((circle_x-circle_radius, y_position+50-circle_radius,
                         circle_x+circle_radius, y_position+50+circle_radius),
                        fill=SPOTIFY_GREEN)
            draw.text((circle_x, y_position+50), str(i),
                     fill='black', font=font_text, anchor="mm")

            # Nombre del género
            draw.text((circle_x + 100, y_position+50), genre.title(),
                     fill='white', font=font_genre, anchor="lm")

            y_position += 150

        # Pie de imagen personalizado
        draw.text((width//2, height-120), "Spotify Wrapped",
                 fill=SPOTIFY_GREEN, font=font_text, anchor="mm")
        draw.text((width//2, height-70), "For DavC",
                 fill='white', font=font_subtitle, anchor="mm")

    except Exception as e:
        print(f"Error creando imagen de géneros: {str(e)}")

    return image

def create_recent_tracks_image(recent_tracks):
    width, height = 1080, 1920
    image = Image.new('RGB', (width, height), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(image)

    try:
        # Usar la imagen del track más reciente como fondo
        recent_track = recent_tracks["items"][0]["track"]
        track_image_url = recent_track["album"]["images"][0]["url"]
        background = download_image(track_image_url)
        background = background.resize((width, height)).convert('RGBA')
        background = background.filter(ImageFilter.GaussianBlur(radius=15))
        background = Image.blend(Image.new('RGB', (width, height), (0,0,0)),
                               background.convert('RGB'), 0.2)
        image.paste(background, (0,0))

        try:
            font_title = ImageFont.truetype("arial.ttf", FONT_SIZE_TITLE)
            font_text = ImageFont.truetype("arial.ttf", FONT_SIZE_TEXT)
            font_time = ImageFont.truetype("arial.ttf", 30)
        except:
            font_title = ImageFont.load_default()
            font_text = ImageFont.load_default()
            font_time = ImageFont.load_default()

        # Título
        draw.text((width//2, 100), "REPRODUCIDO RECIENTEMENTE",
                 fill=SPOTIFY_GREEN, font=font_title, anchor="mm")

        # Lista de canciones recientes con portadas
        y_position = 300
        for i, item in enumerate(recent_tracks["items"][:5]):
            track = item["track"]
            # Portada del álbum
            album_image = download_image(track["album"]["images"][0]["url"])
            album_image = album_image.resize((200, 200))
            image.paste(album_image, (50, y_position))

            # Información de la canción
            draw.text((280, y_position+50), track["name"],
                     fill='white', font=font_text, anchor="lm")
            draw.text((280, y_position+100),
                     ", ".join([artist["name"] for artist in track["artists"]]),
                     fill='gray', font=font_text, anchor="lm")

            # Línea divisoria
            draw.line((50, y_position+220, width-50, y_position+220),
                     fill='gray', width=1)

            y_position += 300

        # Pie de imagen
        draw.text((width//2, height-100), "Spotify Wrapped",
                 fill=SPOTIFY_GREEN, font=font_text, anchor="mm")

    except Exception as e:
        print(f"Error creando imagen de reproducciones recientes: {str(e)}")

    return image

def save_wrapped_images(token):
    create_directory()

    # Obtener todos los datos necesarios
    top_artists = get_top_artists(token)
    top_tracks = get_top_tracks(token)
    recent = get_recently_played(token)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Crear y guardar todas las imágenes
    images = {
        'artists': create_top_artists_image(top_artists),
        'tracks': create_top_tracks_image(top_tracks),
        'genres': create_genres_image(top_artists),
        'recent': create_recent_tracks_image(recent)
    }

    for name, img in images.items():
        img.save(f"{IMAGES_DIR}/{name}_{timestamp}.png")

# Servidor para manejar la redirección
class AuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if '/callback' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.server.auth_code = self.path.split('code=')[1].split('&')[0]
            self.wfile.write("Autorización completada! Puedes cerrar esta ventana.".encode('utf-8'))

def get_auth_code():
    # Crear URL de autorización
    auth_params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE
    }
    auth_url = f"https://accounts.spotify.com/authorize?{urlencode(auth_params)}"

    # Abrir navegador y esperar código
    webbrowser.open(auth_url)
    server = HTTPServer(('localhost', 8888), AuthHandler)
    server.auth_code = None
    server.handle_request()
    return server.auth_code

def get_access_token(auth_code):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]

def get_top_artists(access_token, time_range="medium_term"):
    url = "https://api.spotify.com/v1/me/top/artists"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "time_range": time_range,
        "limit": 10
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_top_tracks(access_token, time_range="medium_term"):
    url = "https://api.spotify.com/v1/me/top/tracks"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "time_range": time_range,
        "limit": 20
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_recently_played(access_token):
    url = "https://api.spotify.com/v1/me/player/recently-played"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "limit": 50
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

def get_favorite_genres(top_artists):
    genres = []
    for artist in top_artists["items"]:
        genres.extend(artist["genres"])

    genre_count = Counter(genres)
    return genre_count.most_common(5)

def print_wrapped_stats(token):
    print("\n=== 🎵 Tu Wrapped Personal 🎵 ===\n")

    # Top Artistas
    print("👥 Tus Artistas Más Escuchados:")
    top_artists = get_top_artists(token)
    for i, artist in enumerate(top_artists["items"][:10], 1):
        print(f"{i}. {artist['name']}")

    # Top Canciones
    print("\n🎵 Tus Canciones Más Escuchadas:")
    top_tracks = get_top_tracks(token)
    for i, track in enumerate(top_tracks["items"][:10], 1):
        artists = ", ".join([artist["name"] for artist in track["artists"]])
        print(f"{i}. {track['name']} - {artists}")

    # Géneros Favoritos
    print("\n🎸 Tus Géneros Favoritos:")
    favorite_genres = get_favorite_genres(top_artists)
    for i, (genre, count) in enumerate(favorite_genres, 1):
        print(f"{i}. {genre.title()}")

    # Últimas reproducciones
    print("\n🕒 Tus Últimas Reproducciones:")
    recent = get_recently_played(token)
    for i, item in enumerate(recent["items"][:5], 1):
        track = item["track"]
        artists = ", ".join([artist["name"] for artist in track["artists"]])
        print(f"{i}. {track['name']} - {artists}")

    # Añadir generación de imágenes
    print("\n📸 Generando imágenes del Wrapped...")
    save_wrapped_images(token)
    print(f"✅ Imágenes guardadas en la carpeta '{IMAGES_DIR}'")

if __name__ == "__main__":
    try:
        auth_code = get_auth_code()
        token = get_access_token(auth_code)
        print_wrapped_stats(token)
    except Exception as e:
        print(f"Error: {str(e)}")
