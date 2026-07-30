from flask import Flask, render_template, request, jsonify
import yt_dlp

app = Flask(__name__, template_folder='../templates')

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

    # إعدادات التمويه للتغلب على حظر يوتيوب والسيرفرات
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['ios', 'mweb'],
                'skip': ['hls', 'dash']
            }
        },
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            clean_formats = []
            for f in formats:
                if f.get('vcodec') != 'none' and f.get('acodec') != 'none':
                    clean_formats.append({
                        'quality': f.get('format_note') or f.get('resolution') or 'Video',
                        'ext': f.get('ext', 'mp4'),
                        'url': f.get('url')
                    })

            if not clean_formats and 'url' in info:
                clean_formats.append({
                    'quality': 'Best Quality',
                    'ext': info.get('ext', 'mp4'),
                    'url': info['url']
                })

            return jsonify({
                'title': info.get('title', 'Video'),
                'thumbnail': info.get('thumbnail'),
                'formats': clean_formats
            })

    except Exception as e:
        return jsonify({'error': f'حدث خطأ أثناء معالجة الرابط: {str(e)}'}), 500
