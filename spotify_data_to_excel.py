import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
from datetime import datetime, timedelta

# Spotify API kimlik bilgilerinizi girin
CLIENT_ID = '5f91f924a5174df693ec978b9943e5b3'
CLIENT_SECRET = '29d945c12d1543e5ab44dc429507a1cd'
REDIRECT_URI = 'http://localhost:8080/callback/'

# Spotify API'ye bağlanmak için izinleri tanımlayın
scope = "user-read-recently-played"

# Spotipy istemcisini oluştur
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=scope))

# Son 30 gün içinde dinlenen tüm şarkıları çekmek için bir fonksiyon
def fetch_all_recently_played():
    tracks_data = []
    last_30_days_timestamp = int((datetime.now() - timedelta(days=30)).timestamp() * 1000)
    last_played_at = None

    while True:
        print(f"Fetching batch... Last played at: {last_played_at}")

        # API çağrısını yap
        if last_played_at:
            results = sp.current_user_recently_played(limit=50, before=last_played_at)
        else:
            results = sp.current_user_recently_played(limit=50)

        items = results.get('items', [])
        print(f"Fetched {len(items)} items")

        if not items:  # Eğer daha fazla veri yoksa döngüyü durdur
            print("No more items found from Spotify API.")
            break

        for item in items:
            played_at = datetime.strptime(item['played_at'], "%Y-%m-%dT%H:%M:%S.%fZ")
            
            # 30 günden eski verileri filtrele
            if int(played_at.timestamp() * 1000) < last_30_days_timestamp:
                print("Reached songs older than 30 days. Stopping.")
                return tracks_data

            track = item['track']
            track_name = track['name']
            artist_id = track['artists'][0]['id']
            
            # Sanatçı türlerini al
            try:
                artist_info = sp.artist(artist_id)
                genres = ", ".join(artist_info.get('genres', []))  # Tür bilgisi
            except Exception as e:
                print(f"Error fetching artist info for {track_name}: {e}")
                genres = "Unknown"

            track_info = {
                'Track Name': track_name,
                'Genres': genres,
                'Played At': played_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            tracks_data.append(track_info)

        # Son çekilen şarkının zamanını güncelle
        last_played_at = items[-1]['played_at']
        print(f"Total tracks fetched so far: {len(tracks_data)}")

    return tracks_data

# Şarkıları çek ve bir DataFrame oluştur
tracks = fetch_all_recently_played()
df = pd.DataFrame(tracks)

# Veriyi Excel dosyasına kaydet
excel_file = "recently_played_last_30_days.xlsx"
df.to_excel(excel_file, index=False)

print(f"Son 30 gün içinde dinlenen şarkılar {excel_file} dosyasına başarıyla kaydedildi.")

