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
    url = data.get('url')

    if not url:
        return jsonify({'error': 'يرجى إدخال رابط صحيح'}), 400

    try:
        # استخدام API معالجة مجاني وداعم لجميع المنصات وبدون حظر IP
        api_url = f"https://api.cobalt.tools/api/json"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = {
            "url": url,
            "vQuality": "720"
        }

        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        res_data = response.json()

        if response.status_code == 200 and "url" in res_data:
            return jsonify({
                'title': 'جاهز للتحميل',
                'thumbnail': '',
                'formats': [{
                    'quality': 'HD Video',
                    'ext': 'mp4',
                    'url': res_data['url']
                }]
            })
        elif "picker" in res_data:
            # في حالة وجود أكثر من جودة أو صور/صوت متفرق
            formats = []
            for item in res_data["picker"]:
                formats.append({
                    'quality': item.get('type', 'Media'),
                    'ext': 'mp4',
                    'url': item.get('url')
                })
            return jsonify({
                'title': 'اختر الجودة للتحميل',
                'thumbnail': '',
                'formats': formats
            })
        else:
            error_msg = res_data.get('text', 'تعذر جلب رابط التحميل، تأكد من صحة الرابط.')
            return jsonify({'error': error_msg}), 400

    except Exception as e:
        return jsonify({'error': f'حدث خطأ في الاتصال بالخادم: {str(e)}'}), 500
