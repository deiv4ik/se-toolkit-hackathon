import os
import logging
import json
from pathlib import Path
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from geo_utils import format_distance, find_all_nearby_places
from gigachat_api import GigaChatClient
from gtts import gTTS
from database import Database

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUDIO_CACHE_DIR = Path("audio_cache")
AUDIO_CACHE_DIR.mkdir(exist_ok=True)

gigachat = GigaChatClient()
db = Database()

# Загружаем места из БД
raw_places = db.get_places()
places_db = []
for p in raw_places:
    places_db.append({
        'id': p['place_id'],
        'name': p['name'],
        'coordinates': {
            'latitude': p['latitude'],
            'longitude': p['longitude'],
            'radius_meters': p['radius_meters']
        },
        'description_short': p['description']
    })

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/get_fact', methods=['POST'])
def get_fact():
    try:
        data = json.loads(request.data)
        lat, lon = float(data['lat']), float(data['lon'])

        nearby = find_all_nearby_places(lat, lon, places_db)
        if not nearby:
            return jsonify({'status': 'error', 'message': 'Место не найдено'}), 404
        
        selected = nearby[0]
        prompts = db.get_prompts(selected['id'])
        selected['context_for_llm'] = {'science_prompts': prompts}

        # Сохраняем запрос в БД
        db.log_request(selected['id'], lat, lon)

        fact = gigachat.generate_science_fact(selected)
        if not fact: fact = f"{selected['name']} - интересное место в Иннополисе"

        audio_filename = None
        try:
            tts = gTTS(fact, lang='ru', slow=False)
            audio_filename = f"fact_{selected['id']}.mp3"
            tts.save(str(AUDIO_CACHE_DIR / audio_filename))
        except Exception as e:
            logger.error(f"Audio error: {e}")

        return jsonify({
            'status': 'ok',
            'place_name': selected['name'],
            'distance': format_distance(selected['distance']),
            'fact': fact,
            'audio_filename': audio_filename
        })
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/popular', methods=['GET'])
def get_popular():
    try:
        return jsonify({'status': 'ok', 'places': db.get_popular_places()})
    except Exception as e:
        logger.error(f"Popular error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/places', methods=['GET'])
def get_all_places():
    try:
        return jsonify({'status': 'ok', 'places': db.get_places()})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    from flask import send_file
    path = AUDIO_CACHE_DIR / filename
    if path.exists(): return send_file(str(path), mimetype='audio/mpeg')
    return 'Not found', 404

if __name__ == '__main__':
    logger.info("🚀 Научный гид по Иннополису (PostgreSQL) запущен!")
    app.run(host='0.0.0.0', port=8080, debug=False)
