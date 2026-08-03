from flask import Flask, render_template, request, jsonify
import requests
import re
from urllib.parse import urlparse, parse_qs

app = Flask(__name__, template_folder='../templates')

RAPIDAPI_KEY = "a2d320d7b9msh75c16116931fc44p118354jsn0ea5c9e194d4"

def get_youtube_id(url):
    """دالة احترافية لاستخراج id الفيديو من أي نوع رابط يوتيوب"""
    parsed_url = urlparse(url)
    if parsed_url.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed_url.path == '/watch':
            return parse_qs(parsed_url.query).get('v', [None])[0]
        elif parsed_url.path.startswith('/embed/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/v/'):
            return parsed_url.path.split('/')[2]
        elif parsed_url.path.startswith('/shorts/'):
            return parsed_url.path.split('/')[2]
    elif parsed_url.hostname == 'youtu.be':
        return parsed_url.path[1:].split('?')[0]
    
    # محاولة مطابقة أخير باستخدام Regex
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url)
    return match.group(1) if match else None

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_video():
    data = request.get_json() or {}
    url = data.get('url')

    if not url:
        return jsonify({'error': 'يرجى إدخال رابط صحيح'}), 400

    video_id = get_youtube_id(url)
    if not video_id:
        return jsonify({'error': 'تعذر التعرف على معرّف الفيديو، تأكد من صحة رابط يوتيوب.'}), 400

    try:
        api_url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "youtube-media-downloader.p.rapidapi.com"
        }
        params = {"videoId": video_id}

        response = requests.get(api_url, headers=headers, params=params, timeout=15)
        res_data = response.json()

        if response.status_code == 200:
            formats = []
            
            # جلب روابط الفيديو والتشغيل المباشر
            videos = res_data.get('videos', {}).get('items', [])
            for item in videos:
                if item.get('url'):
                    formats.append({
                        'quality': item.get('quality', 'HD Video'),
                        'ext': 'mp4',
                        'url': item.get('url')
                    })

            if formats:
                return jsonify({
                    'title': res_data.get('title', 'YouTube Video'),
                    'thumbnail': res_data.get('thumbnails', [{}])[-1].get('url', ''),
                    'formats': formats
                })

        return jsonify({'error': 'تأكد من صحة الرابط أو أن الفيديو غير خاص.'}), 400

    except Exception as e:
        return jsonify({'error': f'حدث خطأ أثناء جلب الفيديو: {str(e)}'}), 500
