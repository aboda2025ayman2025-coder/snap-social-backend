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
    url = data.get('url')

    if not url:
        return jsonify({'error': 'يرجى إدخال رابط صحيح'}), 400

    try:
        # استخدام API شغال مباشرة بياخد الرابط الكامل (URL) من غير قص ID
        api_url = "https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink"
        
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "social-download-all-in-one.p.rapidapi.com",
            "Content-Type": "application/json"
        }
        
        payload = {"url": url}
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        res_data = response.json()

        # في حالة وجود روابط
        if response.status_code == 200 and "medias" in res_data:
            formats = []
            for item in res_data.get("medias", []):
                formats.append({
                    'quality': item.get('quality', 'Video HD'),
                    'ext': item.get('extension', 'mp4'),
                    'url': item.get('url')
                })
            
            if formats:
                return jsonify({
                    'title': res_data.get('title', 'فيديو جاهز للتحميل'),
                    'thumbnail': res_data.get('thumbnail', ''),
                    'formats': formats
                })

        # سيرفر إضافي احتياطي ممتاز ومستقر
        fallback_url = "https://yt-stream-downloader.p.rapidapi.com/dl"
        fb_headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": "yt-stream-downloader.p.rapidapi.com"
        }
        fb_res = requests.get(fallback_url, headers=fb_headers, params={"url": url}, timeout=10)
        fb_data = fb_res.json()

        if fb_res.status_code == 200 and "formats" in fb_data:
            formats = []
            for fmt in fb_data.get("formats", []):
                if fmt.get("url"):
                    formats.append({
                        'quality': fmt.get('qualityLabel', 'Video'),
                        'ext': 'mp4',
                        'url': fmt.get('url')
                    })
            if formats:
                return jsonify({
                    'title': fb_data.get('title', 'فيديو جاهز'),
                    'thumbnail': fb_data.get('thumb', ''),
                    'formats': formats
                })

        return jsonify({'error': 'تعذر استخراج الفيديو، تأكد من صحة الرابط أو أن الفيديو غير خاص.'}), 400

    except Exception as e:
        return jsonify({'error': f'حدث خطأ أثناء جلب الفيديو: {str(e)}'}), 500
