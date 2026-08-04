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

    try:
        # استخدام API المباشر لجلب روابط التحميل المباشرة
        api_url = "https://download-video-api.p.rapidapi.com/process"
        
        headers = {
            "x-rapidapi-key": "a2d320d7b9msh75c16116931fc44p118354jsn0ea5c9e194d4",
            "x-rapidapi-host": "download-video-api.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        payload = {"url": url}
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        res_data = response.json()

        if response.status_code == 200 and "url" in res_data:
            return jsonify({
                'title': res_data.get('title', 'فيديو جاهز للتحميل'),
                'download_url': res_data.get('url')
            })

    except Exception:
        pass

    return jsonify({'error': 'تعذر استخراج الفيديو، تأكد من صحة الرابط.'}), 400
