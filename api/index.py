from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, template_folder='../templates')

RAPIDAPI_KEY = "a2d320d7b9msh75c16116931fc44p118354jsn0ea5c9e194d4"

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
        # استخدام API المخصص والسهل من RapidAPI
        api_url = "https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink"
        
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "social-download-all-in-one.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        # إضافة https:// لو مش موجودة في الرابط
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

        payload = {"url": url}
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        res_data = response.json()

        if response.status_code == 200 and "medias" in res_data:
            formats = []
            for item in res_data.get("medias", []):
                if item.get("url"):
                    formats.append({
                        'quality': item.get('quality', 'Download MP4'),
                        'url': item.get('url')
                    })
            
            if formats:
                return jsonify({
                    'title': res_data.get('title', 'فيديو جاهز للتحميل'),
                    'formats': formats
                })

        return jsonify({'error': 'تعذر استخراج الفيديو، تأكد من صحة الرابط أو أن الفيديو عام.'}), 400

    except Exception as e:
        return jsonify({'error': f'حدث خطأ في السيرفر: {str(e)}'}), 500
