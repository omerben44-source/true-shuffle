import os
import json
import random
import time
import requests
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheHandler
import extra_streamlit_components as stx

st.set_page_config(page_title="True Shuffle", layout="wide")

# ==========================================
# 1. עיצוב הממשק (CSS)
# ==========================================
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"], .stApp {
        background: linear-gradient(-45deg, #1b0a2a, #0b2416, #2d1010, #0c1a2e, #180a26) !important;
        background-size: 350% 350% !important;
        animation: vibrantGlow 18s ease infinite !important;
        color: #FFFFFF !important;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }

    @keyframes vibrantGlow {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    [data-testid="stHeader"] {
        background: transparent !important;
    }

    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        max-width: 1440px;
    }

    /* כותרת ראשית מרכזית ודומיננטית */
    .header-box {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 0px;
        margin-bottom: 35px;
        padding-bottom: 5px;
    }
    .header-title {
        font-size: 5rem;
        font-weight: 900;
        letter-spacing: -2px;
        color: #1DB954;
        text-shadow: 0px 0px 30px rgba(29, 185, 84, 0.5);
        text-transform: uppercase;
        margin: 0;
    }

    /* נגן מרחף (Sticky) שזז עם הגלילה */
    div[data-testid="column"]:has(.sticky-marker) {
        position: -webkit-sticky;
        position: sticky;
        top: 25px;
        align-self: flex-start;
        z-index: 999;
    }

    /* כרטיסיות גריד */
    .playlist-card-container {
        background-color: rgba(22, 17, 28, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 10px;
        text-align: center;
        transition: all 0.2s ease;
        margin-bottom: 8px;
    }
    .playlist-card-container:hover {
        background-color: rgba(35, 28, 45, 0.9);
        border-color: #1DB954;
        transform: translateY(-2px);
    }
    .playlist-card-container.active-card {
        border: 2px solid #1DB954 !important;
        background-color: rgba(29, 185, 84, 0.15) !important;
    }
    .card-cover {
        width: 100%;
        aspect-ratio: 1 / 1;
        object-fit: cover;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.6);
    }
    .card-title {
        color: #FFFFFF;
        font-weight: 700;
        font-size: 0.85rem;
        margin-top: 8px;
        margin-bottom: 6px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .playlist-select-btn button {
        background-color: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        color: #FFFFFF !important;
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        border-radius: 20px !important;
        padding: 4px 10px !important;
        margin-top: -4px !important;
    }
    .playlist-select-btn button:hover {
        background-color: #1DB954 !important;
        border-color: #1DB954 !important;
        color: #000000 !important;
    }

    /* כפתורי Mood */
    button[kind="secondary"] {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 25px !important;
        font-size: 0.84rem !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }
    button[kind="secondary"]:hover {
        border-color: #1DB954 !important;
        color: #1DB954 !important;
        background-color: rgba(29, 185, 84, 0.15) !important;
    }

    button[kind="primary"] {
        background-color: #1DB954 !important;
        color: #000000 !important;
        border: 2px solid #1ed760 !important;
        border-radius: 25px !important;
        font-size: 0.86rem !important;
        font-weight: 800 !important;
        box-shadow: 0 0 16px rgba(29, 185, 84, 0.6) !important;
        transform: scale(1.02);
    }
    button[kind="primary"]:hover {
        background-color: #1ed760 !important;
        color: #000000 !important;
    }

    /* נגן Now Playing */
    .now-playing-card {
        background: linear-gradient(135deg, rgba(22, 16, 28, 0.9), rgba(12, 10, 16, 0.95));
        border: 1px solid #1DB954;
        border-radius: 16px;
        padding: 18px;
        margin-top: 18px;
        box-shadow: 0 10px 35px rgba(0,0,0,0.65);
    }
    .player-deck {
        display: flex;
        align-items: center;
        gap: 20px;
    }
    .vinyl-wrapper {
        position: relative;
        width: 88px;
        height: 88px;
        min-width: 88px;
    }
    .vinyl-disk {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: radial-gradient(circle, #080808 30%, #222222 32%, #0d0d0d 48%, #252525 55%, #080808 65%);
        box-shadow: 0 0 16px rgba(0,0,0,0.85);
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .vinyl-spinning {
        animation: spin 5s linear infinite;
    }
    .vinyl-label {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #000;
    }
    @keyframes spin {
        100% { transform: rotate(360deg); }
    }

    .track-info-deck {
        flex-grow: 1;
    }
    .track-tag {
        color: #1ed760;
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    .track-title {
        color: #FFFFFF;
        font-size: 1.15rem;
        font-weight: 700;
        margin: 2px 0;
    }
    .track-artist {
        color: #C0C0C0;
        font-size: 0.88rem;
    }

    .progress-bar-bg {
        width: 100%;
        height: 5px;
        background-color: rgba(255,255,255,0.12);
        border-radius: 4px;
        margin-top: 10px;
        overflow: hidden;
    }
    .time-indicators {
        display: flex;
        justify-content: space-between;
        font-size: 0.72rem;
        color: #AAAAAA;
        margin-top: 4px;
    }

    .media-controls-container div.stButton > button {
        background-color: rgba(255, 255, 255, 0.08) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        border-radius: 50px !important;
        font-size: 0.95rem !important;
        padding: 6px 14px !important;
    }
    .media-controls-container div.stButton > button:hover {
        background-color: #1DB954 !important;
        color: #000000 !important;
        border-color: #1DB954 !important;
    }

    .footer-credit {
        position: fixed;
        bottom: 12px;
        left: 20px;
        font-size: 0.8rem;
        color: #AAAAAA;
        letter-spacing: 0.3px;
        z-index: 999;
        pointer-events: none;
    }
    .footer-credit span {
        color: #1DB954;
        font-weight: 600;
    }
    
    /* תור שירים (Up Next) */
    .up-next-section {
        margin-top: 18px;
        border-top: 1px solid rgba(255,255,255,0.08);
        padding-top: 14px;
    }
    .up-next-title {
        font-size: 0.75rem;
        color: #AAAAAA;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 10px;
    }
    .up-next-item {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 10px;
        padding: 6px;
        border-radius: 8px;
        transition: background 0.2s;
    }
    .up-next-item:hover {
        background-color: rgba(255,255,255,0.05);
    }
    .up-next-img {
        width: 38px;
        height: 38px;
        border-radius: 4px;
        object-fit: cover;
    }
    .up-next-text {
        line-height: 1.3;
        overflow: hidden;
    }
    .up-next-name {
        color: #FFFFFF;
        font-size: 0.85rem;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .up-next-artist {
        color: #888888;
        font-size: 0.75rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
</style>

<div class="footer-credit">
    Created by <span>Omer Ben Shabat</span>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 2. אתחול Auth עם Cookie Manager
# ==========================================
load_dotenv()
CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")
LASTFM_KEY = os.getenv("LASTFM_API_KEY")

SCOPE = "user-read-playback-state user-modify-playback-state playlist-read-private playlist-read-collaborative playlist-modify-private playlist-modify-public user-library-read"

cookie_manager = stx.CookieManager()

cached_cookie = cookie_manager.get(cookie="sp_token")
if cached_cookie and "spotify_token" not in st.session_state:
    try:
        if isinstance(cached_cookie, str):
            st.session_state["spotify_token"] = json.loads(cached_cookie)
        elif isinstance(cached_cookie, dict):
            st.session_state["spotify_token"] = cached_cookie
    except Exception:
        pass

class StreamlitCookieCacheHandler(CacheHandler):
    def get_cached_token(self):
        return st.session_state.get("spotify_token", None)

    def save_token_to_cache(self, token_info):
        st.session_state["spotify_token"] = token_info
        try:
            cookie_manager.set("sp_token", json.dumps(token_info))
        except Exception:
            pass

sp_oauth = SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE,
    cache_handler=StreamlitCookieCacheHandler()
)

if "code" in st.query_params:
    code = st.query_params["code"]
    token_info = sp_oauth.get_access_token(code)
    st.session_state["spotify_token"] = token_info
    cookie_manager.set("sp_token", json.dumps(token_info))
    st.query_params.clear()
    st.rerun()

token_info = sp_oauth.validate_token(st.session_state.get("spotify_token"))

if not token_info:
    auth_url = sp_oauth.get_authorize_url()
    st.markdown(f'''
        <div style="display:flex; justify-content:center; align-items:center; height:60vh; flex-direction:column; text-align:center;">
            <h1 style="font-size: 5rem; font-weight: 900; margin-bottom: 30px; color: #1DB954; text-transform: uppercase; text-shadow: 0px 0px 30px rgba(29, 185, 84, 0.5);">TRUE SHUFFLE</h1>
            <a href="{auth_url}" style="background-color:#1DB954; color:black; padding:16px 32px; text-decoration:none; border-radius:50px; font-weight:800; font-size:1.2rem; transition: transform 0.2s;">
                LOG IN WITH SPOTIFY
            </a>
        </div>
    ''', unsafe_allow_html=True)
    st.stop()

sp = spotipy.Spotify(
    auth_manager=sp_oauth,
    requests_timeout=20,
    retries=3
)

TARGET_PLAYLIST_NAME = "True Shuffle - Mix"
MAX_SAMPLE_COUNT = 200
CACHE_FILE = "genres_cache.json"

# קטגוריות מצומצמות (ללא אימוג'ים)
GENRE_MOOD_MAP = {
    "Drive": ["pop", "dance pop", "electropop", "synthpop", "indie pop", "funk"],
    "Chill": ["acoustic", "ambient", "chillout", "lo-fi", "lofi", "piano", "downtempo", "relax", "chill", "sleep"],
    "Rock": ["rock", "classic rock", "hard rock", "alternative rock", "grunge", "punk rock", "indie rock"],
    "Metal": ["metal", "metalcore", "post-hardcore", "nu metal", "heavy metal", "deathcore", "djent", "thrash metal"],
    "Party": ["dance", "club", "edm", "house", "electro", "hip hop", "rap", "trap"]
}

MOOD_BLACKLIST = {
    "Chill": {"metal", "heavy metal", "death metal", "metalcore", "hard rock", "screamo", "hardstyle", "soundtrack", "ost", "epic"}
}

# ==========================================
# 3. פונקציות API
# ==========================================
def format_ms(ms):
    seconds = int((ms / 1000) % 60)
    minutes = int((ms / (1000 * 60)) % 60)
    return f"{minutes}:{seconds:02d}"

def get_or_create_target_playlist(_sp):
    try:
        offset = 0
        while True:
            res = _sp.current_user_playlists(limit=50, offset=offset)
            items = res.get('items', [])
            if not items:
                break
            for p in items:
                if p and p.get('name') == TARGET_PLAYLIST_NAME:
                    return p['id']
            offset += len(items)
            if not res.get('next'):
                break
    except Exception:
        pass

    try:
        new_playlist = _sp.current_user_playlist_create(
            name=TARGET_PLAYLIST_NAME,
            public=False,
            collaborative=False,
            description="Auto-generated true randomized subset shuffle."
        )
        return new_playlist['id']
    except Exception:
        try:
            curr_user = _sp.current_user()['id']
            new_playlist = _sp.user_playlist_create(
                user=curr_user,
                name=TARGET_PLAYLIST_NAME,
                public=False,
                description="Auto-generated true randomized subset shuffle."
            )
            return new_playlist['id']
        except Exception as e:
            st.error(f"Failed to create playlist on Spotify: {e}")
            st.stop()

@st.cache_data(ttl=1800, show_spinner=False)
def fetch_user_playlists(_sp, user_id):
    playlists = []
    offset = 0
    while True:
        res = _sp.current_user_playlists(limit=50, offset=offset)
        items = res.get('items', [])
        if not items:
            break
        for p in items:
            if p['name'] != TARGET_PLAYLIST_NAME:
                img_url = p['images'][0]['url'] if p.get('images') and len(p['images']) > 0 else "https://community.spotify.com/t5/image/serverpage/image-id/25294iA2807C22F2D4D360"
                playlists.append({
                    'name': p['name'],
                    'id': p['id'],
                    'image': img_url,
                    'owner': p.get('owner', {}).get('display_name', 'Spotify User')
                })
        offset += len(items)
        if not res.get('next'):
            break
    return playlists

def load_cached_genres():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_cached_genres(cache):
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def fetch_artist_genres_lastfm(artist_name):
    if not LASTFM_KEY:
        return []
    try:
        url = "http://ws.audioscrobbler.com/2.0/"
        params = {"method": "artist.gettoptags", "artist": artist_name, "api_key": LASTFM_KEY, "format": "json"}
        r = requests.get(url, params=params, timeout=4.0)
        if r.status_code == 200:
            tags = r.json().get('toptags', {}).get('tag', [])
            if isinstance(tags, list):
                return [t['name'].lower() for t in tags[:10] if 'name' in t]
    except Exception:
        pass
    return []

@st.cache_data(show_spinner=False)
def load_and_classify_tracks(_sp, user_id, playlist_id):
    tracks = []
    offset = 0
    artist_id_map = {}

    while True:
        try:
            res = _sp.playlist_items(playlist_id, offset=offset, limit=100)
        except Exception:
            break

        items = res.get('items', [])
        if not items:
            break
        for entry in items:
            track = entry.get('item') or entry.get('track')
            if track and track.get('uri', '').startswith("spotify:track:"):
                artist_names = []
                for a in track.get('artists', []):
                    if 'name' in a:
                        artist_names.append(a['name'])
                        if 'id' in a and a['id']:
                            artist_id_map[a['name']] = a['id']

                album_img = track.get('album', {}).get('images', [{}])[0].get('url', '')
                tracks.append({
                    'name': track.get('name', 'Unknown'),
                    'uri': track['uri'],
                    'artists': artist_names,
                    'album': track.get('album', {}).get('name', ''),
                    'image': album_img,
                    'duration_ms': track.get('duration_ms', 210000),
                    'genres': []
                })
        offset += len(items)
        if not res.get('next'):
            break

    cached_genres = load_cached_genres()
    unique_artists = list({a for t in tracks for a in t['artists']})
    new_fetches = 0

    for artist in unique_artists:
        if artist not in cached_genres:
            genres = fetch_artist_genres_lastfm(artist)
            cached_genres[artist] = genres
            new_fetches += 1
            if new_fetches % 20 == 0:
                save_cached_genres(cached_genres)

    missing_artists = [a for a in unique_artists if not cached_genres.get(a) and a in artist_id_map]
    if missing_artists:
        for i in range(0, len(missing_artists), 50):
            chunk = missing_artists[i:i+50]
            chunk_ids = [artist_id_map[a] for a in chunk]
            try:
                sp_res = _sp.artists(chunk_ids)
                for a_data in sp_res.get('artists', []):
                    if a_data and 'name' in a_data:
                        sp_genres = [g.lower() for g in a_data.get('genres', [])]
                        if sp_genres:
                            cached_genres[a_data['name']] = sp_genres
            except Exception:
                pass

    if new_fetches > 0:
        save_cached_genres(cached_genres)

    for t in tracks:
        track_genres = set()
        for a in t['artists']:
            track_genres.update(cached_genres.get(a, []))
        t['genres'] = list(track_genres)

    return tracks

def filter_tracks_by_tags(tracks, selected_tags, active_mood=None):
    if not selected_tags and not active_mood:
        return tracks

    blacklist = MOOD_BLACKLIST.get(active_mood, set())
    filtered = []

    for t in tracks:
        track_genres = set(t.get('genres', []))
        
        if blacklist:
            is_blacklisted = any(bad in g for bad in blacklist for g in track_genres)
            if is_blacklisted:
                continue

        if selected_tags:
            if any(tag in g for tag in selected_tags for g in track_genres):
                filtered.append(t)
        else:
            filtered.append(t)

    return filtered

# ==========================================
# 4. ניהול מצב (State Management)
# ==========================================
st.markdown("""
<div class="header-box">
    <h1 class="header-title">TRUE SHUFFLE</h1>
</div>
""", unsafe_allow_html=True)

try:
    current_user_profile = sp.current_user()
    current_user_id = current_user_profile['id']
    available_playlists = fetch_user_playlists(sp, current_user_id)
except Exception as e:
    st.error(f"Spotify API Error: ({e})")
    st.stop()

if not available_playlists:
    st.error("No playlists found in your account.")
    st.stop()

if "selected_playlist_id" not in st.session_state:
    st.session_state.selected_playlist_id = available_playlists[0]['id']

if "active_mood" not in st.session_state:
    st.session_state.active_mood = None

# ניהול מיקום קרוסלת הפלייליסטים
if "pl_offset" not in st.session_state:
    st.session_state.pl_offset = 0

max_offset = max(0, len(available_playlists) - 6)

# ==========================================
# 5. קרוסלת פלייליסטים אופקית (Playlist Carousel)
# ==========================================
h_col1, h_col2, h_col3 = st.columns([10, 1, 1])
with h_col1:
    st.markdown("#### Your Library")
with h_col2:
    if st.button("<", key="prev_pl", use_container_width=True):
        st.session_state.pl_offset = max(0, st.session_state.pl_offset - 2)
        st.rerun()
with h_col3:
    if st.button(">", key="next_pl", use_container_width=True):
        st.session_state.pl_offset = min(max_offset, st.session_state.pl_offset + 2)
        st.rerun()

# הצגת 6 פלייליסטים בו זמנית בשורה אחת
visible_playlists = available_playlists[st.session_state.pl_offset : st.session_state.pl_offset + 6]
pl_cols = st.columns(6)

for idx, p in enumerate(visible_playlists):
    with pl_cols[idx]:
        is_active = (p['id'] == st.session_state.selected_playlist_id)
        active_class = "active-card" if is_active else ""
        
        st.markdown(f"""
        <div class="playlist-card-container {active_class}">
            <img src="{p['image']}" class="card-cover">
            <div class="card-title">{p['name']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="playlist-select-btn">', unsafe_allow_html=True)
        btn_label = "Active" if is_active else "Select"
        if st.button(btn_label, key=f"sel_p_{p['id']}", use_container_width=True):
            st.session_state.selected_playlist_id = p['id']
            st.session_state.active_mood = None
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

# ==========================================
# 6. אזור מרכזי: סינונים (שמאל) ונגן מרחף (ימין)
# ==========================================
col_left, col_right = st.columns([1.1, 1.3], gap="large")

# חיפוש הפלייליסט הנבחר
active_p_index = next((i for i, p in enumerate(available_playlists) if p['id'] == st.session_state.selected_playlist_id), 0)
active_p = available_playlists[active_p_index]

with st.spinner(f"Loading {active_p['name']}..."):
    all_tracks = load_and_classify_tracks(sp, current_user_id, active_p['id'])

with col_left:
    try:
        devices_res = sp.devices().get('devices', [])
    except Exception:
        devices_res = []
        
    device_options = {f"{d['name']} ({d['type']})": d['id'] for d in devices_res}

    selected_device_id = None
    if device_options:
        selected_device_name = st.selectbox("Active Device", list(device_options.keys()))
        selected_device_id = device_options[selected_device_name]

    st.markdown("#### Mood Filter")

    if not all_tracks:
        st.warning("We couldn't load tracks from this playlist. Spotify restricts API access to certain personalized playlists (like Daily Mixes), or the playlist might be empty. Please choose a different playlist.")
        pool_tracks = []
    else:
        available_subgenres = sorted(list({g for t in all_tracks for g in t['genres']}))
        mood_keys = list(GENRE_MOOD_MAP.keys())
        mood_cols = st.columns(len(mood_keys))

        for i, m in enumerate(mood_keys):
            is_mood_active = (st.session_state.active_mood == m)
            btn_type = "primary" if is_mood_active else "secondary"
            if mood_cols[i].button(m, key=f"mood_{m}", type=btn_type, use_container_width=True):
                st.session_state.active_mood = None if is_mood_active else m
                st.rerun()

        valid_defaults = []
        if st.session_state.active_mood:
            raw_tags = GENRE_MOOD_MAP.get(st.session_state.active_mood, [])
            for tag_word in raw_tags:
                for g in available_subgenres:
                    if tag_word in g:
                        if g not in valid_defaults:
                            valid_defaults.append(g)

        safe_defaults = [v for v in valid_defaults if v in available_subgenres]

        selected_subgenres = st.multiselect(
            "Active Genre Tags:",
            options=available_subgenres,
            default=safe_defaults
        )

        if selected_subgenres or st.session_state.active_mood:
            pool_tracks = filter_tracks_by_tags(all_tracks, selected_subgenres, st.session_state.active_mood)
        else:
            pool_tracks = all_tracks

        st.markdown(f"""
        <div style="font-size: 0.88rem; color: #DDDDDD; margin-top: -6px; margin-bottom: 16px;">
            Pool Size: <strong style="color: #1DB954;">{len(pool_tracks)}</strong> tracks ready for true random shuffle
        </div>
        """, unsafe_allow_html=True)

        if st.button("True Shuffle & Play", type="primary", use_container_width=True):
            if not pool_tracks:
                st.error("No tracks match your genre criteria.")
            else:
                sample_size = min(len(pool_tracks), MAX_SAMPLE_COUNT)
                sampled_tracks = random.sample(pool_tracks, sample_size)
                random.shuffle(sampled_tracks)
                track_uris = [t['uri'] for t in sampled_tracks]

                with st.spinner(f"Queuing {len(track_uris)} randomized tracks..."):
                    target_id = get_or_create_target_playlist(sp)
                    
                    success = False
                    for attempt in range(2):
                        try:
                            sp.playlist_replace_items(target_id, track_uris[:100])
                            if len(track_uris) > 100:
                                sp.playlist_add_items(target_id, track_uris[100:200])
                            success = True
                            break
                        except Exception:
                            time.sleep(1)
                    
                    if not success:
                        st.error("Spotify API took too long to respond. Please try clicking the button again.")
                        st.stop()

                if selected_device_id:
                    time.sleep(0.5)
                    try:
                        sp.shuffle(state=False, device_id=selected_device_id)
                    except Exception:
                        pass
                    try:
                        sp.start_playback(
                            device_id=selected_device_id,
                            context_uri=f"spotify:playlist:{target_id}",
                            offset={"position": 0}
                        )
                    except Exception:
                        try:
                            sp.start_playback(device_id=selected_device_id, uris=track_uris[:100])
                        except Exception:
                            pass
                st.rerun()

with col_right:
    # סמן נסתר ל-CSS שמייצר את האפקט המרחף (Sticky) לכל העמודה הימנית
    st.markdown('<div class="sticky-marker"></div>', unsafe_allow_html=True)

    playback_state = None
    upcoming_tracks = []
    try:
        playback_state = sp.current_playback()
        queue_data = sp.queue()
        upcoming_tracks = queue_data.get('queue', [])[:3]
    except Exception:
        pass

    if playback_state and playback_state.get('item'):
        item = playback_state['item']
        is_playing = playback_state.get('is_playing', False)
        progress_ms = playback_state.get('progress_ms', 0)
        total_ms = item.get('duration_ms', 1)
        track_title = item.get('name', 'Unknown')
        track_artists = ', '.join([a['name'] for a in item.get('artists', [])])
        album_name = item.get('album', {}).get('name', '')
        album_img = item.get('album', {}).get('images', [{}])[0].get('url', 'https://community.spotify.com/t5/image/serverpage/image-id/25294iA2807C22F2D4D360')
        tag_status = 'PLAYING ON SPOTIFY' if is_playing else 'PAUSED ON SPOTIFY'
    else:
        fallback_track = all_tracks[0] if all_tracks else {
            "name": "Ready to Shuffle",
            "artists": ["Select a track"],
            "album": "True Shuffle",
            "image": "https://community.spotify.com/t5/image/serverpage/image-id/25294iA2807C22F2D4D360",
            "duration_ms": 180000
        }
        is_playing = False
        progress_ms = 0
        total_ms = fallback_track.get('duration_ms', 180000)
        track_title = fallback_track.get('name')
        track_artists = ', '.join(fallback_track.get('artists', []))
        album_name = fallback_track.get('album', '')
        album_img = fallback_track.get('image', 'https://community.spotify.com/t5/image/serverpage/image-id/25294iA2807C22F2D4D360')
        tag_status = 'READY TO PLAY'

    progress_pct = min(100, max(0, int((progress_ms / total_ms) * 100)))
    spinning_class = "vinyl-spinning" if is_playing else ""
    remaining_ms = total_ms - progress_ms

    if is_playing and remaining_ms > 0:
        animation_css = f"""
        <style>
            @keyframes liveProgress {{
                from {{ width: {progress_pct}%; }}
                to {{ width: 100%; }}
            }}
            .progress-bar-fill {{
                animation: liveProgress {remaining_ms}ms linear forwards;
                background-color: #1DB954;
                height: 100%;
                border-radius: 4px;
            }}
        </style>
        """
    else:
        animation_css = f"""
        <style>
            .progress-bar-fill {{
                width: {progress_pct}%;
                background-color: #1DB954;
                height: 100%;
                border-radius: 4px;
            }}
        </style>
        """

    up_next_html = ""
    if upcoming_tracks:
        up_next_items = "".join([
            f"<div class='up-next-item'>"
            f"<img src='{t.get('album', {}).get('images', [{}])[0].get('url', 'https://community.spotify.com/t5/image/serverpage/image-id/25294iA2807C22F2D4D360')}' class='up-next-img'>"
            f"<div class='up-next-text'>"
            f"<div class='up-next-name'>{t.get('name', 'Unknown')}</div>"
            f"<div class='up-next-artist'>{', '.join([a['name'] for a in t.get('artists', [])])}</div>"
            f"</div></div>"
            for t in upcoming_tracks
        ])
        up_next_html = f"<div class='up-next-section'><div class='up-next-title'>UP NEXT</div>{up_next_items}</div>"

    card_html = (
        f"{animation_css}"
        f"<div class='now-playing-card'>"
        f"<div class='player-deck'>"
        f"<div class='vinyl-wrapper'><div class='vinyl-disk {spinning_class}'><img src='{album_img}' class='vinyl-label'></div></div>"
        f"<div class='track-info-deck'>"
        f"<div class='track-tag'>{tag_status}</div>"
        f"<div class='track-title'>{track_title}</div>"
        f"<div class='track-artist'>{track_artists} — {album_name}</div>"
        f"<div class='progress-bar-bg'><div class='progress-bar-fill'></div></div>"
        f"<div class='time-indicators'><span>{format_ms(progress_ms)}</span><span>{format_ms(total_ms)}</span></div>"
        f"</div></div>"
        f"{up_next_html}"
        f"</div>"
    )

    st.markdown(card_html, unsafe_allow_html=True)

    st.markdown('<div class="media-controls-container">', unsafe_allow_html=True)
    spacer_left, btn_col1, btn_col2, btn_col3, spacer_right = st.columns([1.6, 1, 1.2, 1, 1.6])
    
    with btn_col1:
        if st.button("Prev", key="btn_prev", use_container_width=True):
            try:
                sp.previous_track(device_id=selected_device_id)
                st.rerun()
            except Exception:
                pass
    with btn_col2:
        play_label = "Pause" if is_playing else "Play"
        if st.button(play_label, key="btn_play_pause", use_container_width=True):
            try:
                if is_playing:
                    sp.pause_playback(device_id=selected_device_id)
                else:
                    sp.start_playback(device_id=selected_device_id)
                st.rerun()
            except Exception:
                pass
    with btn_col3:
        if st.button("Next", key="btn_nxt", use_container_width=True):
            try:
                sp.next_track(device_id=selected_device_id)
                st.rerun()
            except Exception:
                pass
    st.markdown('</div>', unsafe_allow_html=True)

    if is_playing and remaining_ms > 0:
        auto_refresh_delay_ms = remaining_ms + 1500
        components.html(
            f"""
            <script>
                setTimeout(function() {{
                    window.parent.location.reload();
                }}, {auto_refresh_delay_ms});
            </script>
            """,
            height=0,
            width=0
        )
