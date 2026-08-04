from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, template_folder='../templates')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template('index.html')

@app.route('/extract', methods=['POST'])
def extract_video():
    data = request.get_json() or {}
    url = data.get('url', '').strip()

    if not url:
        return jsonify({'error': 'يرجى إدخال رابط صحيح'}), 400

    # قائمة بسيرفرات Cobalt العامة والمجانية والسريعة جداً
    cobalt_instances = [
        "https://api.cobalt.tools/api/json",
        "https://cobalt.api.sc7.io/api/json",
        "https://co.wuk.sh/api/json"
    ]

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    payload = {
        "url": url,
        "vQuality": "720"
    }

    for instance in cobalt_instances:
        try:
            res = requests.post(instance, json=payload, headers=headers, timeout=10)
            if res.status_code == 200:
                res_data = res.json()
                video_url = res_data.get('url')
                
                if video_url:
                    return jsonify({
                        'title': 'فيديو جاهز للتحميل',
                        'thumbnail': '',
                        'formats': [{
                            'quality': 'HD Video (MP4)',
                            'ext': 'mp4',
                            'url': video_url
                        }]
                    })
        except Exception:
            continue

    return jsonify({'error': 'تعذر جلب الفيديو، تأكد من صحة الرابط أو جرب رابط فيديو آخر.'}), 400
