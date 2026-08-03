from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, template_folder='../templates')

# المفتاح بتاعك جاهز ومتركب هنا
RAPIDAPI_KEY = "a2d320d7b9msh75c16116931fc44p118354jsn0ea5c9e194d4"

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

    try:
        api_url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"
        
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "youtube-media-downloader.p.rapidapi.com"
        }
        
        # استخراج ID الفيديو من الرابط
        video_id = url.split('/')[-1].split('?')[0].replace('watch?v=', '')
        
        params = {"videoId": video_id}
        response = requests.get(api_url, headers=headers, params=params, timeout=15)
        res_data = response.json()

        if response.status_code == 200:
            formats = []
            
            # استخراج روابط الفيديو
            videos = res_data.get('videos', {}).get('items', [])
            for item in videos:
                formats.append({
                    'quality': item.get('quality', 'Video'),
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
